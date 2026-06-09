"""Facade of Jade — Nemotron 3 ASR backend on Modal.

Deploys NVIDIA Nemotron Speech Streaming EN (0.6B params) for speech-to-text.
Exposes a POST /asr endpoint that takes base64 audio and returns text.

Deploy:
    modal deploy modal_asr.py

Local dev:
    modal serve modal_asr.py
"""
from __future__ import annotations

import json
import base64
import io

import modal

MODEL_ID = "nvidia/nemotron-speech-streaming-en-0.6b"
MODEL_DIR = "/models/asr"
VOLUME_NAME = "facade-of-jade-asr-models"

asr_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("build-essential", "git", "libgomp1", "libsndfile1", "ffmpeg")
    .pip_install(
        "torch>=2.5.0",
        "torchaudio>=2.5.0",
        "nemo_toolkit[asr]>=2.0",
        "soundfile>=0.12",
        "fastapi>=0.110",
        "uvicorn[standard]>=0.27",
        "huggingface-hub>=0.23",
        "hf-transfer>=0.1",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

app = modal.App("facade-of-jade-asr", image=asr_image)
model_volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)


def _build_app():
    """Build a plain ASGI app, loading Nemotron ASR once on cold start."""
    import torch
    import nemo.collections.asr as nemo_asr

    print(f"Loading Nemotron 3 ASR from {MODEL_ID}...")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained(MODEL_ID)
    model = model.to(device)
    model.eval()

    model_volume.commit()
    print(f"Nemotron ASR loaded on {device}.")

    async def read_body(receive) -> bytes:
        chunks = []
        more = True
        while more:
            msg = await receive()
            chunks.append(msg.get("body", b""))
            more = msg.get("more_body", False)
        return b"".join(chunks)

    async def send_json(send, status: int, payload) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", b"application/json"],
                [b"content-length", str(len(body)).encode()],
            ],
        })
        await send({"type": "http.response.body", "body": body, "more_body": False})

    async def app(scope, receive, send):
        if scope["type"] != "http":
            return
        path = scope["path"]
        method = scope["method"]

        if path == "/" and method == "GET":
            await send_json(send, 200, {"model": MODEL_ID, "status": "ready"})
            return

        if path == "/healthz" and method == "GET":
            await send_json(send, 200, {"ok": True, "model_loaded": True})
            return

        if path == "/asr" and method == "POST":
            raw = await read_body(receive)
            try:
                payload = json.loads(raw or b"{}")
            except json.JSONDecodeError as e:
                await send_json(send, 400, {"error": f"bad json: {e}"})
                return

            audio_b64 = payload.get("audio", "")
            if not audio_b64:
                await send_json(send, 400, {"error": "audio base64 required"})
                return

            try:
                import soundfile as sf
                import torch
                import torchaudio.functional as F

                audio_bytes = base64.b64decode(audio_b64)
                audio_buf = io.BytesIO(audio_bytes)
                audio_data, sr = sf.read(audio_buf, dtype="float32")

                if sr != 16000:
                    waveform = torch.tensor(audio_data).unsqueeze(0)
                    resampled = F.resample(waveform, sr, 16000)
                    audio_data = resampled.squeeze(0).numpy()

                audio_path = "/tmp/audio.wav"
                sf.write(audio_path, audio_data, 16000)

                result = model.transcribe([audio_path])
                text = str(result[0]) if result else ""
                # Handle Hypothesis object from NeMo
                if hasattr(result[0], 'text'):
                    text = result[0].text
                elif hasattr(result[0], 'hypothesis'):
                    text = str(result[0].hypothesis)
                else:
                    text = str(result[0])
                await send_json(send, 200, {"text": text})
            except Exception as e:
                await send_json(send, 500, {"error": f"ASR failed: {str(e)[:200]}"})
            return

        await send_json(send, 404, {"error": "not found", "path": path, "method": method})

    return app


@app.function(
    gpu="A10G",
    volumes={MODEL_DIR: model_volume},
    timeout=10 * 60,
    scaledown_window=10 * 60,
    max_containers=2,
)
@modal.concurrent(max_inputs=4)
@modal.asgi_app()
def serve():
    """Modal asgi_app entrypoint. Loads Nemotron ASR once on cold start."""
    return _build_app()


@app.local_entrypoint()
def main() -> None:
    print("Facade of Jade ASR — run `modal deploy modal_asr.py` to publish.")
