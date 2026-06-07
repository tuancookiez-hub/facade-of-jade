"""Facade of Jade — Gradio Space app.

Serves a custom Wuxia-themed chat UI via `gr.Server` and proxies
streaming chat completions to a llama.cpp backend running on Modal.
"""
import json
import os

import gradio as gr
import httpx
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse

MODAL_URL = os.environ.get(
    "MODAL_URL",
    "https://t-abdullah-rashid--facade-of-jade-backend-serve.modal.run",
)
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "static", "index.html")

server = gr.Server()


@server.get("/", response_class=HTMLResponse)
async def homepage() -> str:
    with open(FRONTEND_PATH, encoding="utf-8") as f:
        return f.read()


@server.get("/static/{path:path}")
async def static_files(path: str):
    full = os.path.join(os.path.dirname(__file__), "static", path)
    if not os.path.isfile(full):
        return PlainTextResponse("not found", status_code=404)
    return FileResponse(full)


@server.get("/healthz")
def health() -> dict:
    return {"ok": True, "backend": MODAL_URL}


@server.api(name="chat")
async def chat(messages: list, state: dict | None = None) -> str:
    """Stream NPC response from Modal. Yielded chunks are full text snapshots
    (cumulative), which the frontend uses to render the streaming typewriter effect.
    """
    state = state or {"mood": "wary", "trust": 0, "current_beat": "intro"}
    payload = {"messages": messages, "state": state}

    accumulated = ""
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            async with client.stream("POST", f"{MODAL_URL}/chat", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    chunk = line[6:].strip()
                    if chunk == "[DONE]":
                        break
                    try:
                        obj = json.loads(chunk)
                    except json.JSONDecodeError:
                        continue
                    token = obj.get("token")
                    if not token:
                        continue
                    accumulated += token
                    yield accumulated
        except httpx.HTTPError as e:
            yield f"[backend unreachable: {e}]"


@server.api(name="npc_state")
def npc_state() -> dict:
    return {
        "npc_name": "Shen Wuqing (沈无情)",
        "npc_title": "The Swordsman of No Emotion",
        "mood": "wary",
        "trust": 0,
        "current_beat": "intro",
        "beats": [
            "intro",
            "offer_drink",
            "ask_problem",
            "judge_motive",
            "accept_or_refuse",
            "farewell",
        ],
    }


if __name__ == "__main__":
    server.launch(server_name="0.0.0.0", server_port=7860)
