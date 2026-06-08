"""Facade of Jade Gradio app with session drama management."""

from __future__ import annotations

import json
import os
import threading

import gradio as gr
import httpx

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

SESSIONS: dict[str, dict] = {}
TRACE_LOG: list[dict] = []

WUXIA_INTRO = (
    "Master Liang watches you from across a rain-dark teahouse, one hand resting on "
    "the hilt of his blade. Your wording matters: respect can open him, insults can "
    "turn the room hostile, and challenges may draw steel."
)

PLAYER_HINTS = (
    "Try a respectful request, a sharp insult, a direct challenge, an apology, or a "
    "question about Jade Mountain. The state bar updates after every reply."
)

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&display=swap');

:root {
    --jade-ink: #111614;
    --jade-panel: rgba(16, 23, 20, 0.92);
    --jade-panel-soft: rgba(28, 37, 33, 0.78);
    --jade-border: rgba(181, 155, 102, 0.42);
    --jade-gold: #d3b36a;
    --jade-ivory: #ece4d2;
    --jade-muted: #b5ab96;
    --jade-shadow: rgba(0, 0, 0, 0.38);
}

body, .gradio-container {
    background:
        radial-gradient(circle at top, rgba(78, 110, 92, 0.18), transparent 38%),
        linear-gradient(180deg, #08110d 0%, #0f1915 45%, #17221d 100%) !important;
    color: var(--jade-ivory) !important;
    font-family: 'Cormorant Garamond', Georgia, serif !important;
}

.app-shell {
    max-width: 980px;
    margin: 0 auto;
    padding: 20px 16px 32px;
}

.hero {
    padding: 22px 24px 16px;
    border: 1px solid var(--jade-border);
    background:
        linear-gradient(135deg, rgba(211, 179, 106, 0.08), transparent 28%),
        var(--jade-panel);
    box-shadow: 0 18px 40px var(--jade-shadow);
}

.hero h1 {
    margin: 0;
    color: var(--jade-gold);
    font-size: 2.5rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.hero p {
    margin: 10px 0 0;
    color: var(--jade-muted);
    font-size: 1.15rem;
    line-height: 1.5;
}

.hero .player-hints {
    margin-top: 14px;
    padding: 10px 12px;
    border-left: 3px solid var(--jade-gold);
    background: rgba(211, 179, 106, 0.08);
    color: var(--jade-ivory);
    font-size: 1.03rem;
}

.state-bar {
    margin: 14px 0 8px;
    padding: 10px 16px;
    text-align: center;
    border: 1px solid var(--jade-border);
    background: linear-gradient(90deg, rgba(211, 179, 106, 0.08), rgba(17, 22, 20, 0.84));
    color: var(--jade-gold) !important;
    font-size: 1rem;
}

.chat-wrap {
    border: 1px solid var(--jade-border);
    background: var(--jade-panel-soft);
    box-shadow: 0 18px 36px var(--jade-shadow);
}

.chat-wrap .chatbot {
    background: transparent !important;
}

.chat-wrap .message.user {
    background: rgba(211, 179, 106, 0.12) !important;
    color: var(--jade-gold) !important;
}

.chat-wrap .message.bot {
    background: rgba(12, 18, 15, 0.88) !important;
    color: var(--jade-ivory) !important;
}

.chat-wrap .message,
.chat-wrap textarea,
.chat-wrap button,
.chat-wrap .placeholder,
.chat-wrap .examples,
.chat-wrap .icon-button {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
}

.chat-wrap textarea {
    background: rgba(10, 15, 13, 0.9) !important;
    color: var(--jade-ivory) !important;
    border: 1px solid var(--jade-border) !important;
}

.chat-wrap button.primary {
    background: linear-gradient(180deg, #7c6639, #5e4927) !important;
    border: 1px solid rgba(220, 191, 122, 0.55) !important;
    color: #f7eedb !important;
}

.chat-wrap .example-card {
    background: rgba(17, 25, 21, 0.88) !important;
    border: 1px solid var(--jade-border) !important;
    color: var(--jade-muted) !important;
}

.chat-wrap .example-card:hover {
    border-color: rgba(211, 179, 106, 0.72) !important;
    color: var(--jade-gold) !important;
}

.footer-note {
    margin-top: 14px;
    color: var(--jade-muted);
    text-align: center;
    font-size: 0.98rem;
}
"""


def _initial_state() -> dict:
    return {
        "mood": "wary",
        "trust": 15,
        "current_beat": "intro",
        "player_challenged": False,
        "turns": 0,
    }


def _session_id(request: gr.Request | None) -> str:
    if request and request.session_hash:
        return request.session_hash
    return "default"


def _normalize_history(history) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for item in history or []:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": str(content)})
            continue
        if isinstance(item, (list, tuple)) and len(item) == 2:
            user_text, assistant_text = item
            if user_text:
                messages.append({"role": "user", "content": str(user_text)})
            if assistant_text:
                messages.append({"role": "assistant", "content": str(assistant_text)})
    return messages


def _persist_trace_snapshot(trace_log: list[dict]) -> None:
    """Persist a point-in-time trace snapshot without blocking the chat loop."""
    save_traces_locally(trace_log)


def chat_stream(message: str, history, request: gr.Request):
    """Stream NPC reply from Modal while maintaining per-session state."""
    session_id = _session_id(request)
    state = SESSIONS.setdefault(session_id, _initial_state())

    if is_game_over(state):
        yield "*The story has ended. Refresh the page to begin anew.*"
        return

    discourse_act = classify_discourse_act(message)
    next_state = update_state(state, discourse_act, message)
    msgs = _normalize_history(history)
    msgs.append({"role": "user", "content": message})
    system_prompt = get_system_prompt(next_state)

    accumulated = ""
    try:
        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            with client.stream(
                "POST",
                f"{MODAL_URL}/chat",
                json={
                    "messages": msgs,
                    "state": next_state,
                    "system_prompt": system_prompt,
                },
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = line[6:].strip()
                    if payload == "[DONE]":
                        break
                    try:
                        obj = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    token = obj.get("token", "")
                    if not token:
                        continue
                    accumulated += token
                    yield accumulated

        SESSIONS[session_id] = next_state
        TRACE_LOG.append(get_trace_entry(session_id, message, next_state, accumulated))
        if len(TRACE_LOG) % 10 == 0:
            trace_snapshot = TRACE_LOG.copy()
            threading.Thread(
                target=_persist_trace_snapshot,
                args=(trace_snapshot,),
                daemon=True,
            ).start()

        if is_game_over(next_state):
            yield accumulated + "\n\n*The End*"
    except Exception as exc:  # noqa: BLE001
        yield f"*The teahouse falls silent... (error: {str(exc)[:100]})*"


def get_state_display(request: gr.Request):
    """Return the formatted state display for the current session."""
    session_id = _session_id(request)
    state = SESSIONS.get(session_id, _initial_state())
    return format_state_for_display(state)


with gr.Blocks(title="Facade of Jade") as demo:
    gr.HTML(
        f"""
        <style>{CUSTOM_CSS}</style>
        <div class="app-shell">
            <section class="hero">
                <h1>Facade of Jade</h1>
                <p>{WUXIA_INTRO}</p>
                <p class="player-hints">{PLAYER_HINTS}</p>
            </section>
        </div>
        """
    )

    state_display = gr.Markdown(
        format_state_for_display(_initial_state()),
        elem_classes="state-bar",
    )

    chat = gr.ChatInterface(
        fn=chat_stream,
        examples=[
            "Master Liang, I bow before your blade and ask for guidance.",
            "What happened at Jade Mountain? Tell me the truth.",
            "Forgive my sharp tongue. I came here desperate.",
            "You hide behind old stories because you fear the truth.",
            "I challenge your judgment — the seal belongs to the people.",
        ],
    )

    chat.chatbot.change(get_state_display, None, state_display)

    gr.Markdown(
        "Built for the Build Small Hackathon. Qwen3-4B-Instruct via llama.cpp on Modal. "
        "Inspired by Façade.",
        elem_classes="footer-note",
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
