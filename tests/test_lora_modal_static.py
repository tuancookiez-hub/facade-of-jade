from pathlib import Path


SOURCE_PATH = Path(__file__).resolve().parent.parent / "train_lora_modal.py"


def test_modal_runner_contains_required_static_markers() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")

    assert "facade-of-jade-lora-train" in source
    assert "facade-of-jade-lora-out" in source
    assert "A100" in source
    assert "/outputs/facade-of-jade-qwen3-4b-lora" in source
    assert "def train_remote" in source
