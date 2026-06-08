from pathlib import Path

from scripts.compare_lora import extract_prompts


def test_extract_prompts_reads_numbered_list(tmp_path: Path) -> None:
    md = tmp_path / "prompts.md"
    md.write_text("""# Demo\n\n1. First prompt\n2. Second prompt\n""", encoding="utf-8")
    assert extract_prompts(md) == ["First prompt", "Second prompt"]
