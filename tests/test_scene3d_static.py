from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "server_static"


def read_static(name: str) -> str:
    return (STATIC / name).read_text(encoding="utf-8")


def test_scene3d_static_files_exist() -> None:
    assert (STATIC / "scene3d.html").exists()
    assert (STATIC / "scene3d.css").exists()
    assert (STATIC / "scene3d.js").exists()


def test_scene3d_html_loads_threejs_module_and_hud() -> None:
    html = read_static("scene3d.html")

    assert "three" in html.lower()
    assert "scene3d.js" in html
    assert "scene3d.css" in html
    assert "chat-form" in html
    assert "message-input" in html
    assert "quick-actions" in html
    assert "Facade of Jade" in html


def test_scene3d_js_uses_existing_backend_and_state_driven_scene() -> None:
    js = read_static("scene3d.js")

    assert 'fetch("/api/chat"' in js or "fetch('/api/chat'" in js
    assert "applySceneState" in js
    assert "route_milestones" in js
    assert "memory_flags" in js
    assert "trust" in js
    assert "tension" in js
    assert "mood" in js
    assert "quick-actions" in js


def test_scene3d_css_supports_fullscreen_canvas_and_dialogue_overlay() -> None:
    css = read_static("scene3d.css")

    assert "#scene-canvas" in css
    assert "#hud" in css
    assert "#npc-bubble" in css
    assert "#player-bar" in css
    assert "position: fixed" in css
    assert "pointer-events" in css


def test_scene3d_html_uses_npc_bubble_and_bottom_player_bar() -> None:
    html = read_static("scene3d.html")

    assert "npc-bubble" in html
    assert "npc-line" in html
    assert "player-bar" in html
    assert "interaction-hint" in html
    assert "WASD" in html
    assert "Drag" in html


def test_scene3d_js_has_first_person_controls_and_bounds() -> None:
    js = read_static("scene3d.js")

    assert "updatePlayer" in js
    assert "clampPlayerToRoom" in js
    assert "KeyW" in js
    assert "KeyA" in js
    assert "KeyS" in js
    assert "KeyD" in js
    assert "pointermove" in js
    assert "player.yaw" in js
    assert "player.pitch" in js


def test_scene3d_js_projects_npc_speech_bubble_and_gates_talking() -> None:
    js = read_static("scene3d.js")

    assert "updateNpcBubble" in js
    assert ".project(camera)" in js
    assert "distanceToLiang" in js
    assert "canTalk" in js
    assert "Move closer to Master Liang" in js
    assert "npcLine" in js
    assert "__scene3dDebug" in js
