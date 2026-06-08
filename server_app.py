"""Experimental gr.Server custom UI for Facade of Jade.

This file is intentionally separate from app.py while we prove whether gr.Server is
safe on HF Spaces. It reuses the existing drama manager and Modal backend.
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

import httpx
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from gradio import Server

from beats import (
    classify_discourse_act,
    format_state_for_display,
    get_system_prompt,
    get_trace_entry,
    is_game_over,
    update_state,
)
from trace_utils import save_traces_locally

MODAL_URL = os.environ.get(
    "MODAL_URL",
    "https://t-abdullah-rashid--facade-of-jade-backend-serve.modal.run",
)

APP_DIR = Path(__file__).resolve().parent
SESSIONS: dict[str, dict[str, Any]] = {}
TRACE_LOG: list[dict[str, Any]] = []

app = Server(title="Facade of Jade — Server Spike")


def initial_state() -> dict[str, Any]:
    return {
        "mood": "wary",
        "trust": 15,
        "current_beat": "intro",
        "player_challenged": False,
        "turns": 0,
        "discourse_act": "none",
        "previous_mood": "wary",
        "previous_trust": 15,
        "trust_delta": 0,
    }


def describe_state(state: dict[str, Any]) -> dict[str, Any]:
    trust = int(state.get("trust", 0))
    previous_trust = int(state.get("previous_trust", trust))
    return {
        "display": format_state_for_display(state),
        "mood": state.get("mood", "wary"),
        "previous_mood": state.get("previous_mood", state.get("mood", "wary")),
        "trust": trust,
        "previous_trust": previous_trust,
        "trust_delta": trust - previous_trust,
        "beat": state.get("current_beat", "intro"),
        "last_act": state.get("discourse_act", "none"),
        "turns": int(state.get("turns", 0)),
        "game_over": is_game_over(state),
    }


@app.get("/", response_class=HTMLResponse)
async def homepage() -> str:
    return (APP_DIR / "server_static" / "index.html").read_text(encoding="utf-8")


@app.get("/server_static/{filename}")
async def static_file(filename: str):
    path = APP_DIR / "server_static" / filename
    if not path.exists() or not path.is_file():
        return JSONResponse({"error": "not found"}, status_code=404)
    media_type = "text/css" if filename.endswith(".css") else "application/javascript"
    return HTMLResponse(path.read_text(encoding="utf-8"), media_type=media_type)


@app.get("/api/state")
async def api_state(session_id: str | None = None):
    sid = session_id or "preview"
    state = SESSIONS.setdefault(sid, initial_state())
    return JSONResponse({"session_id": sid, "state": describe_state(state)})


@app.post("/api/reset")
async def api_reset(payload: dict[str, Any]):
    sid = str(payload.get("session_id") or uuid.uuid4())
    SESSIONS[sid] = initial_state()
    return JSONResponse({"session_id": sid, "state": describe_state(SESSIONS[sid])})


@app.post("/api/chat")
async def api_chat(payload: dict[str, Any]):
    sid = str(payload.get("session_id") or uuid.uuid4())
    message = str(payload.get("message") or "").strip()
    history = payload.get("history") or []
    if not message:
        return JSONResponse({"error": "message required"}, status_code=400)

    state = SESSIONS.setdefault(sid, initial_state())
    if is_game_over(state):
        return JSONResponse(
            {
                "session_id": sid,
                "response": "The story has ended. Reset to begin again.",
                "state": describe_state(state),
            }
        )

    previous_mood = state.get("mood", "wary")
    previous_trust = int(state.get("trust", 0))
    discourse_act = classify_discourse_act(message)
    next_state = update_state(state, discourse_act, message)
    next_state["previous_mood"] = previous_mood
    next_state["previous_trust"] = previous_trust
    next_state["trust_delta"] = int(next_state.get("trust", 0)) - previous_trust

    messages: list[dict[str, str]] = []
    for item in history[-8:]:
        if isinstance(item, dict) and item.get("role") in {"user", "assistant"}:
            messages.append({"role": item["role"], "content": str(item.get("content", ""))})
    messages.append({"role": "user", "content": message})

    system_prompt = get_system_prompt(next_state)
    response_text = ""
    try:
        with httpx.Client(timeout=180.0, follow_redirects=True) as client:
            with client.stream(
                "POST",
                f"{MODAL_URL}/chat",
                json={"messages": messages, "state": next_state, "system_prompt": system_prompt},
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        obj = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    response_text += obj.get("token", "")
    except Exception as exc:  # noqa: BLE001
        response_text = f"The teahouse falls silent. Backend error: {str(exc)[:120]}"

    SESSIONS[sid] = next_state
    trace = get_trace_entry(sid, message, next_state, response_text)
    trace.update(
        {
            "previous_mood": previous_mood,
            "previous_trust": previous_trust,
            "trust_delta": next_state["trust_delta"],
            "source": "gr-server-spike",
        }
    )
    TRACE_LOG.append(trace)
    if len(TRACE_LOG) % 10 == 0:
        save_traces_locally(TRACE_LOG, "traces_server_spike.jsonl")

    return JSONResponse(
        {
            "session_id": sid,
            "response": response_text,
            "state": describe_state(next_state),
            "trace": trace,
        }
    )


@app.api(name="health")
def health() -> dict[str, Any]:
    return {"ok": True, "modal_url": MODAL_URL, "sessions": len(SESSIONS)}


if __name__ == "__main__":
    app.launch(show_error=True)
