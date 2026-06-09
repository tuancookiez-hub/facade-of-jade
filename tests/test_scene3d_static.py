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
    assert "message-input" in html
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


def test_scene3d_css_supports_fullscreen_canvas_and_layout() -> None:
    css = read_static("scene3d.css")

    assert "#scene-canvas" in css
    assert "#hud" in css
    assert "#npc-bubble" in css
    assert "grid-template-columns" in css
    assert "pointer-events" in css


def test_scene3d_html_has_history_and_stats_panels() -> None:
    html = read_static("scene3d.html")

    assert "history-panel" in html
    assert "history-log" in html
    assert "stats-panel" in html
    assert "trust-bar" in html
    assert "respect-bar" in html
    assert "suspicion-bar" in html
    assert "objective-text" in html
    assert "interaction-bar" in html
    assert "suggestions" in html


def test_scene3d_js_has_facade_style_keyboard_controls_and_bounds() -> None:
    js = read_static("scene3d.js")

    assert "updatePlayer" in js
    assert "clampPlayerToRoom" in js
    assert "ArrowUp" in js
    assert "ArrowDown" in js
    assert "ArrowLeft" in js
    assert "ArrowRight" in js
    assert "TURN_SPEED" in js
    assert "player.yaw +=" in js
    assert "player.yaw -=" in js
    assert "KeyW" not in js
    assert "KeyA" not in js
    assert "KeyS" not in js
    assert "KeyD" not in js
    assert "camera.getWorldDirection" in js
    assert "forward.y = 0" in js
    assert "forward.normalize()" in js
    assert "player.pitch" in js
    assert "pointermove" not in js
    assert "mouse.dragging" not in js
    assert "player.pitch = THREE.MathUtils.clamp" not in js


def test_scene3d_js_has_conversation_history_and_stats() -> None:
    js = read_static("scene3d.js")

    assert "addHistoryEntry" in js
    assert "history-log" in js
    assert "trust-bar" in js
    assert "respect-bar" in js
    assert "suspicion-bar" in js
    assert "historyEntry" in js or "history-entry" in js


def test_scene3d_js_projects_npc_speech_bubble_and_gates_talking() -> None:
    js = read_static("scene3d.js")

    assert "updateNpcBubble" in js
    assert ".project(camera)" in js
    assert "distanceToLiang" in js
    assert "canTalk" in js
    assert "npcLine" in js
    assert "__scene3dDebug" in js
