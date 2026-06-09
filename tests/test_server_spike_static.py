from __future__ import annotations

from pathlib import Path

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
