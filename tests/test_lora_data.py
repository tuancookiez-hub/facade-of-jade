import json
from pathlib import Path
from typing import Any


def resolve_dataset_path() -> Path:
    repo_dir = Path(__file__).resolve().parent.parent
    candidates = (
        (repo_dir / "../loRA_training_data_v1_gpt5.jsonl").resolve(),
        (repo_dir / "./loRA_training_data_v1_gpt5.jsonl").resolve(),
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    searched = ", ".join(str(candidate) for candidate in candidates)
    raise AssertionError(f"Training data file not found. Looked for: {searched}")


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AssertionError(f"Line {line_number} is not valid JSON: {exc.msg}") from exc
            assert isinstance(record, dict), f"Line {line_number} must be a JSON object"
            assert "messages" in record, f"Line {line_number} missing messages"
            assert isinstance(record["messages"], list), f"Line {line_number} messages must be a list"
            assert record["messages"], f"Line {line_number} messages must not be empty"
            for message_index, message in enumerate(record["messages"]):
                assert isinstance(
                    message, dict
                ), f"Line {line_number} message {message_index} must be an object"
                assert "role" in message, f"Line {line_number} message {message_index} missing role"
                assert (
                    "content" in message
                ), f"Line {line_number} message {message_index} missing content"
            records.append(record)
    return records


def first_user_message(record: dict[str, Any], line_number: int) -> str:
    for message in record["messages"]:
        if message.get("role") == "user":
            content = message.get("content")
            assert isinstance(content, str) and content.strip(), (
                f"Line {line_number} first user message content must be a non-empty string"
            )
            return content
    raise AssertionError(f"Line {line_number} has no user message")


def run_assertions() -> None:
    dataset_path = resolve_dataset_path()
    records = load_records(dataset_path)

    assert len(records) >= 30, f"Expected at least 30 records, found {len(records)}"

    seen_first_user_messages: set[str] = set()
    for line_number, record in enumerate(records, start=1):
        first_user = first_user_message(record, line_number)
        assert (
            first_user not in seen_first_user_messages
        ), f"Duplicate first user message found on line {line_number}: {first_user!r}"
        seen_first_user_messages.add(first_user)

    print(f"Validated {len(records)} JSONL training examples from {dataset_path}")


if __name__ == "__main__":
    run_assertions()
