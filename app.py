"""Facade of Jade — Space app. Gradio ChatInterface calling Modal backend.

The gr.HTML custom-UI approach hit a Gradio 6.16 bug where the value
isn't being passed to the DOM. Falling back to ChatInterface for
v0.1; we'll re-introduce the custom ink-wash UI in v0.2 via the
modal backend's own HTML response.
"""
import os

import gradio as gr
import httpx

MODAL_URL = os.environ.get(
    "MODAL_URL",
    "https://t-abdullah-rashid--facade-of-jade-backend-serve.modal.run",
)

WUXIA_INTRO = (
    "A swordsman sits across from you, his hand resting on the hilt of his blade. "
    "The teahouse is quiet. The rain has stopped."
)


def chat_stream(message, history, request: gr.Request):
    """Stream NPC reply from Modal, yielding cumulative text for the chat UI."""
    msgs = []
    for h in history or []:
        if h.get("role") in ("user", "assistant") and h.get("content"):
            msgs.append({"role": h["role"], "content": h["content"]})
    msgs.append({"role": "user", "content": message})

    accumulated = ""
    with httpx.Client(timeout=120.0, follow_redirects=True) as client:
        with client.stream(
            "POST",
            f"{MODAL_URL}/chat",
            json={"messages": msgs, "state": {"mood": "wary", "trust": 0, "current_beat": "intro"}},
        ) as r:
            r.raise_for_status()
            buf = ""
            for line in r.iter_lines():
                if not line.startswith("data: "):
                    continue
                payload = line[6:].strip()
                if payload == "[DONE]":
                    break
                try:
                    obj = __import__("json").loads(payload)
                except Exception:
                    continue
                tok = obj.get("token")
                if not tok:
                    continue
                accumulated += tok
                yield accumulated


demo = gr.ChatInterface(
    fn=chat_stream,
    title="Facade of Jade",
    description=WUXIA_INTRO,
    examples=[
        "I've come a long way to find you.",
        "Will you hear my problem?",
        "I need a sword.",
        "Farewell.",
    ],
)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
