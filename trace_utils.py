"""Helpers for persisting and publishing gameplay traces."""

from __future__ import annotations

import json
import os
from typing import Any


def append_session_trace(session_id: str, trace_log: list[dict[str, Any]]) -> None:
    """Append a minimal trace placeholder for a session to an existing trace log."""
    trace_log.append(
        {
            "session_id": session_id,
            "player_input": "",
            "discourse_act": "misc",
            "mood": "",
            "trust": 0,
            "current_beat": "",
            "npc_response": "",
            "is_terminal": False,
        }
    )


def save_traces_locally(trace_log: list, filepath: str = "traces.jsonl") -> int:
    """Write trace entries to a JSONL file and return the number saved."""
    with open(filepath, "w", encoding="utf-8") as handle:
        for entry in trace_log:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return len(trace_log)


def load_traces(filepath: str = "traces.jsonl") -> list[dict]:
    """Load JSONL trace entries from disk."""
    traces: list[dict] = []
    with open(filepath, "r", encoding="utf-8") as handle:
        for line in handle:
            raw = line.strip()
            if raw:
                traces.append(json.loads(raw))
    return traces


def publish_traces_to_hub(
    filepath: str = "traces.jsonl",
    repo_id: str = "build-small-hackathon/facade-of-jade-traces",
    token: str | None = None,
) -> str:
    """Upload the trace file to a Hugging Face dataset repository."""
    resolved_token = token or os.environ.get("HUGGINGFACE_TOKEN")
    if not resolved_token:
        raise ValueError(
            "Hugging Face token required. Pass token=... or set HUGGINGFACE_TOKEN."
        )

    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(repo_id, repo_type="dataset", token=resolved_token, exist_ok=True)
    api.upload_file(
        path_or_fileobj=filepath,
        path_in_repo="traces.jsonl",
        repo_id=repo_id,
        repo_type="dataset",
        token=resolved_token,
    )
    return f"https://huggingface.co/datasets/{repo_id}"
