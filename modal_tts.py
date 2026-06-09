"""Facade of Jade — VoxCPM2 TTS backend on Modal.

Deploys VoxCPM2 (2B params, ~8GB VRAM) on an A10G for text-to-speech.
Exposes a POST /tts endpoint that takes text and returns WAV audio.

Deploy:
    modal deploy modal_tts.py

Local dev:
    modal serve modal_tts.py
"""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path

import modal

MODEL_ID = "openbmb/VoxCPM2"
MODEL_DIR = "/models/voxcpm"
VOLUME_NAME = "facade-of-jade-tts-models"

tts_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("build-essential", "git", "libgomp1", "libsndfile1")
    .pip_install(
        "torch>=2.5.0",
        "torchaudio>=2.5.0",
        "voxcpm",
        "soundfile>=0.12",
        "fastapi>=0.110",
        "uvicorn[standard]>=0.27",
        "huggingface-hub>=0.23",
        "hf-transfer>=0.1",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

app = modal.App("facade-of-jade-tts", image=tts_image)
model_volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)


def _build_app():
    """Build a plain ASGI app, loading VoxCPM2 once on cold start."""
    import soundfile as sf
    from voxcpm import VoxCPM

    print(f"Loading VoxCPM2 from HuggingFace...")
    model = VoxCPM.from_pretrained(MODEL_ID, load_denoiser=False)
    model_volume.commit()
    print("VoxCPM2 loaded successfully.")

    VOICE_PREFIX = "(An older Chinese man, calm and measured voice, slight rasp)"

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

    async def send_audio(send, audio_bytes: bytes) -> None:
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"audio/wav"],
                [b"content-length", str(len(audio_bytes)).encode()],
            ],
        })
        await send({"type": "http.response.body", "body": audio_bytes, "more_body": False})

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

        if path == "/tts" and method == "POST":
            raw = await read_body(receive)
            try:
                payload = json.loads(raw or b"{}")
            except json.JSONDecodeError as e:
                await send_json(send, 400, {"error": f"bad json: {e}"})
                return

            text = payload.get("text", "").strip()
            if not text:
                await send_json(send, 400, {"error": "text required"})
                return

            voice = payload.get("voice", VOICE_PREFIX)
            full_text = f"{voice}{text}"

            try:
                wav = model.generate(
                    text=full_text,
                    cfg_value=2.0,
                    inference_timesteps=10,
                )
                buf = io.BytesIO()
                sf.write(buf, wav, model.tts_model.sample_rate, format="WAV")
                audio_bytes = buf.getvalue()
                await send_audio(send, audio_bytes)
            except Exception as e:  # noqa: BLE001
                await send_json(send, 500, {"error": f"TTS generation failed: {str(e)[:200]}"})
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
    """Modal asgi_app entrypoint. Loads VoxCPM2 once on cold start."""
    return _build_app()


@app.local_entrypoint()
def main() -> None:
    print("Facade of Jade TTS — run `modal deploy modal_tts.py` to publish.")
