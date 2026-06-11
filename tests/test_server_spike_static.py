from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

import httpx
import server_app

ROOT = Path(__file__).resolve().parents[1]


def test_server_app_exports_gradio_server() -> None:
    assert type(server_app.app).__name__ == "Server"
    assert server_app.health()["ok"] is True


def test_describe_state_includes_drama_engine_fields() -> None:
    state = server_app.initial_state()
    described = server_app.describe_state(state)
    assert described["mood"] == "wary"
    assert described["trust"] == 15
    assert described["trust_delta"] == 0
    assert described["path_pressure"]
    assert "memory_flags" in described
    assert "route_milestones" in described
    assert "known_truths" in described
    assert {"revelation", "alliance", "duel", "betrayal"}.issubset(
        described["path_pressure"].keys()
    )


def test_prepare_turn_tracks_previous_state_and_delta() -> None:
    sid = "test-server-spike-turn"
    server_app.SESSIONS.pop(sid, None)
    state, messages, system_prompt, previous_mood, previous_trust = server_app.prepare_turn(
        sid,
        "Master Liang, I respect your honor.",
        [],
    )
    assert previous_mood == "wary"
    assert previous_trust == 15
    assert state["previous_mood"] == "wary"
    assert state["previous_trust"] == 15
    assert state["trust_delta"] > 0
    assert messages[-1]["role"] == "user"
    assert "Master Liang" in system_prompt


def test_static_frontend_uses_streaming_endpoint_and_path_pressure() -> None:
    html = (ROOT / "server_static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "server_static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "server_static" / "style.css").read_text(encoding="utf-8")
    assert "Rainy teahouse scene" in html
    assert "Insights" in html
    assert "path-revelation" in html
    assert "path-pressure-meter" in html
    assert "/api/chat_stream" in js
    assert "getReader" in js
    assert "buffer.split('\\n')" in js
    assert ".insights-hud" in css
    assert ".master-liang" in css


def test_scene3d_route_serves_separate_shell() -> None:
    html = server_app.scene3d_page()
    assert "Facade of Jade" in html
    assert "server_static/scene3d.css" in html
    assert "server_static/scene3d.js" in html


def test_tts_warmup_actually_calls_modal(monkeypatch) -> None:
    """Regression: warmup=True must reach Modal so the container stays warm.

    Earlier the server returned early without calling Modal, leaving the
    2-3 min cold start intact. The whole point of the warmup ping is to keep
    VoxCPM2 loaded, so verify the outbound POST fires.
    """
    import json

    captured: dict = {}

    class _Resp:
        status_code = 200
        content = b""

        def raise_for_status(self) -> None:
            return None

    def fake_post(url, json=None, **kwargs):  # noqa: ANN001, ARG001
        captured["url"] = url
        captured["json"] = json
        captured["kwargs"] = kwargs
        return _Resp()

    monkeypatch.setattr(server_app, "VOXCPM_API_URL", "https://example-tts.modal.run")
    monkeypatch.setattr(server_app.httpx, "Client", lambda *a, **kw: _FakeClient(fake_post))

    response = asyncio.run(server_app.api_tts({"warmup": True}))
    result = json.loads(response.body)

    assert captured["json"] == {"text": "Hm."}
    assert captured["url"] == "https://example-tts.modal.run/tts"
    assert result["warmup"] is True
    assert result["audio"] == ""


def test_tts_warmup_silently_swallows_modal_errors(monkeypatch) -> None:
    """Warmup must never crash the frontend; Modal outages are best-effort."""
    import json

    def fake_post(*args, **kwargs):  # noqa: ANN001, ARG001
        raise httpx.ConnectError("modal offline")

    monkeypatch.setattr(server_app, "VOXCPM_API_URL", "https://example-tts.modal.run")
    monkeypatch.setattr(server_app.httpx, "Client", lambda *a, **kw: _FakeClient(fake_post))

    response = asyncio.run(server_app.api_tts({"warmup": True}))
    result = json.loads(response.body)

    assert result["warmup"] is True
    assert result["audio"] == ""


class _FakeClient:
    def __init__(self, post_fn, *args, **kwargs) -> None:  # noqa: ANN001
        self._post_fn = post_fn
        self._args = args
        self._kwargs = kwargs

    def __enter__(self) -> "_FakeClient":
        return self

    def __exit__(self, *args) -> None:
        return None

    def post(self, url, json=None, **kwargs):  # noqa: ANN001
        return self._post_fn(url, json=json, **kwargs)
