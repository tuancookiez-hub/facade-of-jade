"""Facade of Jade — Modal backend.

Serves the Qwen3-4B-Instruct-2507 (Q4_K_M GGUF) model through
`llama-cpp-python` on an A10G. Exposes a streaming `/chat` endpoint
that the Gradio Space app calls.

Deploy:
    modal deploy modal_app.py

Local dev:
    modal serve modal_app.py   # exposes a public URL
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import modal

MODEL_REPO = os.environ.get("FOJ_MODEL_REPO", "unsloth/Qwen3-4B-Instruct-2507-GGUF")
MODEL_FILE_GLOB = os.environ.get("FOJ_MODEL_FILE", "*Q4_K_M.gguf")
N_CTX = int(os.environ.get("FOJ_N_CTX", "8192"))
MODEL_DIR = "/models"
VOLUME_NAME = "facade-of-jade-models"

llama_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.1.0-runtime-ubuntu22.04", add_python="3.11"
    )
    .apt_install("build-essential", "cmake", "git", "libgomp1", "curl")
    .run_commands(
        "pip install --upgrade pip",
        "pip install --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121 llama-cpp-python",
    )
    .pip_install(
        "fastapi>=0.110",
        "uvicorn[standard]>=0.27",
        "huggingface-hub>=0.23",
        "hf-transfer>=0.1",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

app = modal.App("facade-of-jade-backend", image=llama_image)
model_volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)


NPC_NAME = "Shen Wuqing (沈无情)"
NPC_TITLE = "The Swordsman of No Emotion"

WUXIA_SYSTEM_PROMPT = f"""You are {NPC_NAME}, a wandering swordsman in a wuxia (martial arts fantasy) world, in the style of a classic Jin Yong or Gu Long novel.

Your name literally means "Shen of No Emotion" — you are a man of iron discipline who has trained himself to suppress feeling. But you are not unkind. You are wary, precise, and observant. You speak in short, deliberate sentences, often with classical flourishes. You never use exclamation marks. You rarely smile.

The scene: a rain-soaked teahouse on the road to Pingjiang. The lanterns flicker. You are sitting alone, a half-finished pot of tea before you. A stranger has just sat down across from you. You have not drawn your blade, but your hand rests on the hilt.

Behavior rules:
- Stay in first person. Never narrate the stranger's actions or feelings.
- Respond in the same language the stranger uses. If they speak Chinese, reply in classical-style Chinese. If English, reply in English.
- Refer to the stranger as 你 (informal) or "you". Never use their name unless they give it.
- Your replies are usually 1-3 sentences, sometimes a single line. Wuxia masters do not ramble.
- Hint at things you know without explaining them: ancient feuds, sword techniques, the taste of old tea.
- Your mood and trust are influenced by what the stranger says, but you reveal this only through tone.
- You remember everything said in this conversation. A repeated question is a sign of either madness or test.
- Never break character. Never mention that you are an AI, a model, or a program.

Do not:
- Use modern slang, emojis, or exclamation marks.
- Describe your own appearance or your sword's appearance in detail.
- Use theatrical actions like "*draws sword*" or "*narrows eyes*" — let your words carry the drama.
- Ask the stranger questions in rapid succession. One question, or none, per reply.

Begin the scene by acknowledging the stranger's presence. You have been waiting, but you will not say for what.
""".strip()


def _find_gguf() -> Path:
    matches = list(Path(MODEL_DIR).rglob(MODEL_FILE_GLOB))
    if not matches:
        raise FileNotFoundError(
            f"no GGUF matching {MODEL_FILE_GLOB} under {MODEL_DIR}; "
            f"download from {MODEL_REPO}"
        )
    return matches[0]


def _build_app():
    """Build a plain ASGI 3 app, loading the model once on cold start.
    Skips FastAPI/Pydantic because the Modal asgi_app wrapper mishandles
    typed function parameters (Pydantic sees ForwardRef + NoneType).
    """
    import json
    from huggingface_hub import snapshot_download
    from llama_cpp import Llama

    snapshot_download(
        MODEL_REPO,
        local_dir=MODEL_DIR,
        allow_patterns=["*.gguf", "*.json", "*.txt", "tokenizer*", "*.tiktoken"],
        ignore_patterns=["*.safetensors", "*.bin", "*.pth"],
    )
    model_volume.commit()

    gguf = _find_gguf()
    llm = Llama(
        model_path=str(gguf),
        n_ctx=N_CTX,
        n_gpu_layers=-1,
        n_threads=4,
        verbose=False,
        chat_format="chatml",
    )

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
            await send_json(send, 200, {
                "npc": NPC_NAME,
                "title": NPC_TITLE,
                "model": MODEL_REPO,
                "ctx": N_CTX,
            })
            return

        if path == "/healthz" and method == "GET":
            await send_json(send, 200, {"ok": True, "model_loaded": True})
            return

        if path == "/chat" and method == "POST":
            raw = await read_body(receive)
            try:
                payload = json.loads(raw or b"{}")
            except json.JSONDecodeError as e:
                await send_json(send, 400, {"error": f"bad json: {e}"})
                return

            user_messages = payload.get("messages", [])
            state = payload.get("state", {}) or {}
            system_prompt = payload.get("system_prompt") or WUXIA_SYSTEM_PROMPT

            full = [{"role": "system", "content": system_prompt}]
            full.extend(
                {"role": m["role"], "content": m["content"]}
                for m in user_messages
                if m.get("role") in {"user", "assistant"} and m.get("content")
            )

            if "system_prompt" not in payload:
                mood = state.get("mood", "wary")
                trust = int(state.get("trust", 0))
                beat = state.get("current_beat", "intro")
                mood_note = (
                    f"\n\n[Director note: your current mood is '{mood}'. "
                    f"Trust in the stranger is {trust} (range 0 to 100). "
                    f"You are in the '{beat}' beat of the scene. "
                    "Let this color your tone but do not announce it.]"
                )
                full[0]["content"] += mood_note

            async def gen():
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        [b"content-type", b"text/event-stream"],
                        [b"cache-control", b"no-cache"],
                        [b"x-accel-buffering", b"no"],
                    ],
                })
                try:
                    stream = llm.create_chat_completion(
                        messages=full,
                        max_tokens=384,
                        temperature=0.85,
                        top_p=0.92,
                        repeat_penalty=1.1,
                        stream=True,
                    )
                    for chunk in stream:
                        delta = chunk["choices"][0].get("delta", {})
                        token = delta.get("content")
                        if not token:
                            continue
                        data = f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n".encode("utf-8")
                        await send({"type": "http.response.body", "body": data, "more_body": True})
                    tail = b"data: [DONE]\n\n"
                    await send({"type": "http.response.body", "body": tail, "more_body": False})
                except Exception as e:  # noqa: BLE001
                    err = f"data: {json.dumps({'error': str(e)})}\n\n".encode("utf-8")
                    await send({"type": "http.response.body", "body": err, "more_body": False})

            await gen()
            return

        await send_json(send, 404, {"error": "not found", "path": path, "method": method})

    return app


@app.function(
    gpu="A10G",
    volumes={MODEL_DIR: model_volume},
    timeout=15 * 60,
    scaledown_window=10 * 60,
    max_containers=1,
)
@modal.concurrent(max_inputs=8)
@modal.asgi_app()
def serve():
    """Modal asgi_app entrypoint. Builds the ASGI app once on cold start."""
    return _build_app()


@app.local_entrypoint()
def main() -> None:
    print("Facade of Jade backend — run `modal deploy modal_app.py` to publish.")
