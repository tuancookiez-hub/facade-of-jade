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
    assert "#dialogue" in css
    assert "position: fixed" in css
    assert "pointer-events" in css
