"""Experimental gr.Server custom UI for Facade of Jade.

This file is intentionally separate from app.py while we prove whether gr.Server is
safe on HF Spaces. It reuses the existing drama manager and Modal backend.
"""

from __future__ import annotations

import io
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
    default_memory_flags,
    default_route_milestones,
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
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
VOXCPM_API_URL = os.environ.get("VOXCPM_API_URL", "https://t-abdullah-rashid--facade-of-jade-tts-serve.modal.run")

APP_DIR = Path(__file__).resolve().parent
SESSIONS: dict[str, dict[str, Any]] = {}
TRACE_LOG: list[dict[str, Any]] = []

app = Server(title="Facade of Jade")


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
        "affinity": 0,
        "self_realization": 0,
        "tension": 35,
        "hot_button": "none",
        "mix_in": "Main beat continues",
        "beat_goal": "Transition-in: test the visitor and establish suspicion.",
    }


def path_pressure(state: dict[str, Any]) -> dict[str, int]:
    """Return simple visible route pressure for the custom UI."""
    trust = int(state.get("trust", 0))
    mood = state.get("mood", "wary")
    challenged = bool(state.get("player_challenged", False))
    return {
        "revelation": max(0, min(100, trust + (20 if mood in {"curious", "friendly", "open"} else 0))),
        "alliance": max(0, min(100, trust + (30 if mood in {"friendly", "open"} else -10))),
        "duel": max(0, min(100, (100 - trust) + (25 if mood == "hostile" else 0) + (20 if challenged else 0))),
        "betrayal": max(0, min(100, (80 - trust) + (25 if mood == "hostile" else 0) + (15 if challenged else 0))),
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
        "path_pressure": path_pressure(state),
        "affinity": int(state.get("affinity", 0)),
        "self_realization": int(state.get("self_realization", 0)),
        "tension": int(state.get("tension", 35)),
        "hot_button": state.get("hot_button", "none"),
        "mix_in": state.get("mix_in", "Main beat continues"),
        "beat_goal": state.get("beat_goal", "Main beat continues"),
        "memory_flags": state.get("memory_flags", default_memory_flags()),
        "route_milestones": state.get("route_milestones", default_route_milestones()),
        "known_truths": state.get("known_truths", []),
        "dramatic_notes": state.get("dramatic_notes", []),
    }


def prepare_turn(sid: str, message: str, history: list[Any]) -> tuple[dict[str, Any], list[dict[str, str]], str, str, int]:
    """Update state for a player turn and return Modal-ready messages/prompt."""
    state = SESSIONS.setdefault(sid, initial_state())
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
    return next_state, messages, get_system_prompt(next_state), str(previous_mood), previous_trust


def record_turn(sid: str, message: str, next_state: dict[str, Any], response_text: str, previous_mood: str, previous_trust: int) -> dict[str, Any]:
    """Persist session state and append a trace entry."""
    SESSIONS[sid] = next_state
    trace = get_trace_entry(sid, message, next_state, response_text)
    trace.update(
        {
            "previous_mood": previous_mood,
            "previous_trust": previous_trust,
            "trust_delta": next_state["trust_delta"],
            "path_pressure": path_pressure(next_state),
            "affinity": next_state.get("affinity", 0),
            "self_realization": next_state.get("self_realization", 0),
            "tension": next_state.get("tension", 35),
            "hot_button": next_state.get("hot_button", "none"),
            "mix_in": next_state.get("mix_in", "Main beat continues"),
            "beat_goal": next_state.get("beat_goal", "Main beat continues"),
            "source": "gr-server-production",
        }
    )
    TRACE_LOG.append(trace)
    if len(TRACE_LOG) % 10 == 0:
        save_traces_locally(TRACE_LOG, "traces_server_spike.jsonl")
    return trace


# ── Pages ──

@app.get("/", response_class=HTMLResponse)
async def homepage() -> str:
    return (APP_DIR / "server_static" / "scene3d.html").read_text(encoding="utf-8")


@app.get("/scene3d.html", response_class=HTMLResponse)
def scene3d_page() -> str:
    return (APP_DIR / "server_static" / "scene3d.html").read_text(encoding="utf-8")


@app.get("/server_static/{filename}")
async def static_file(filename: str):
    path = APP_DIR / "server_static" / filename
    if not path.exists() or not path.is_file():
        return JSONResponse({"error": "not found"}, status_code=404)
    media_type = "text/css" if filename.endswith(".css") else "application/javascript"
    return HTMLResponse(path.read_text(encoding="utf-8"), media_type=media_type)


# ── API ──

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

    next_state, messages, system_prompt, previous_mood, previous_trust = prepare_turn(sid, message, history)
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

    trace = record_turn(sid, message, next_state, response_text, previous_mood, previous_trust)

    return JSONResponse(
        {
            "session_id": sid,
            "response": response_text,
            "state": describe_state(next_state),
            "trace": trace,
        }
    )


@app.post("/api/chat_stream")
async def api_chat_stream(payload: dict[str, Any]):
    """Stream newline-delimited JSON events for the custom frontend."""
    sid = str(payload.get("session_id") or uuid.uuid4())
    message = str(payload.get("message") or "").strip()
    history = payload.get("history") or []
    if not message:
        return JSONResponse({"error": "message required"}, status_code=400)

    state = SESSIONS.setdefault(sid, initial_state())
    if is_game_over(state):
        async def ended():
            yield json.dumps({"type": "done", "session_id": sid, "response": "The story has ended. Reset to begin again.", "state": describe_state(state)}) + "\n"
        return StreamingResponse(ended(), media_type="application/x-ndjson")

    next_state, messages, system_prompt, previous_mood, previous_trust = prepare_turn(sid, message, history)

    async def events():
        accumulated = ""
        yield json.dumps({"type": "state", "session_id": sid, "state": describe_state(next_state)}) + "\n"
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
                        token = obj.get("token", "")
                        if token:
                            accumulated += token
                            yield json.dumps({"type": "token", "token": token}) + "\n"
        except Exception as exc:  # noqa: BLE001
            accumulated = f"The teahouse falls silent. Backend error: {str(exc)[:120]}"
            yield json.dumps({"type": "token", "token": accumulated}) + "\n"

        trace = record_turn(sid, message, next_state, accumulated, previous_mood, previous_trust)
        yield json.dumps({"type": "done", "session_id": sid, "response": accumulated, "state": describe_state(next_state), "trace": trace}) + "\n"

    return StreamingResponse(events(), media_type="application/x-ndjson")


# ── Voice endpoints ──

@app.post("/api/asr")
async def api_asr(payload: dict[str, Any]):
    """Speech-to-text via NVIDIA Nemotron ASR (free hosted API).

    Expects base64-encoded audio WAV in the request body.
    Returns transcribed text.
    """
    audio_b64 = payload.get("audio")
    if not audio_b64:
        return JSONResponse({"error": "audio (base64) required"}, status_code=400)

    if not NVIDIA_API_KEY:
        return JSONResponse({"error": "NVIDIA_API_KEY not configured on server"}, status_code=503)

    try:
        import base64
        audio_bytes = base64.b64decode(audio_b64)

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                "https://integrate.api.nvidia.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"},
                files={"file": ("audio.wav", io.BytesIO(audio_bytes), "audio/wav")},
                data={"model": "nvidia/nemotron-asr-streaming-en-0.6b"},
            )
            response.raise_for_status()
            result = response.json()
            text = result.get("text", "")
            return JSONResponse({"text": text})
    except Exception as exc:
        return JSONResponse({"error": f"ASR failed: {str(exc)[:200]}"}, status_code=500)


@app.post("/api/tts")
async def api_tts(payload: dict[str, Any]):
    """Text-to-speech via VoxCPM2.

    Expects {"text": "..."} and optional {"voice": "description"}.
    Returns base64-encoded audio WAV.
    """
    text = payload.get("text", "").strip()
    if not text:
        return JSONResponse({"error": "text required"}, status_code=400)

    if not VOXCPM_API_URL:
        return JSONResponse({"error": "VOXCPM_API_URL not configured on server"}, status_code=503)

    try:
        import base64

        voice_desc = payload.get("voice", "(An older Chinese man, calm and measured voice, slight rasp)")

        with httpx.Client(timeout=60.0, follow_redirects=True) as client:
            response = client.post(
                f"{VOXCPM_API_URL}/tts",
                json={"text": f"{voice_desc}{text}"},
            )
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "audio" in content_type or "wav" in content_type or "octet-stream" in content_type:
                audio_b64 = base64.b64encode(response.content).decode("utf-8")
                return JSONResponse({"audio": audio_b64})
            else:
                result = response.json()
                audio_b64 = result.get("audio", "")
                if not audio_b64:
                    return JSONResponse({"error": "No audio in response"}, status_code=500)
                return JSONResponse({"audio": audio_b64})
    except Exception as exc:
        return JSONResponse({"error": f"TTS failed: {str(exc)[:200]}"}, status_code=500)


@app.api(name="health")
def health() -> dict[str, Any]:
    return {"ok": True, "modal_url": MODAL_URL, "sessions": len(SESSIONS)}


if __name__ == "__main__":
    app.launch(show_error=True)
