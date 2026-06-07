"""Tests for trace persistence helpers."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from trace_utils import load_traces, publish_traces_to_hub, save_traces_locally


SAMPLE_TRACES = [
    {
        "session_id": "session-1",
        "player_input": "Who are you?",
        "discourse_act": "ask",
        "mood": "wary",
        "trust": 15,
        "current_beat": "intro",
        "npc_response": "A man with old debts.",
        "is_terminal": False,
    },
    {
        "session_id": "session-1",
        "player_input": "Can I help?",
        "discourse_act": "offer",
        "mood": "curious",
        "trust": 22,
        "current_beat": "opening_up",
        "npc_response": "Perhaps.",
        "is_terminal": False,
    },
]


class TraceUtilsTests(unittest.TestCase):
    def test_save_and_load_round_trip(self) -> None:
        files: dict[str, str] = {}

        class MemoryFile:
            def __init__(self, path: str, mode: str) -> None:
                self.path = path
                self.mode = mode
                self._buffer = "" if "w" in mode else files[path]

            def write(self, text: str) -> int:
                self._buffer += text
                return len(text)

            def __iter__(self):
                return iter(self._buffer.splitlines(True))

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb) -> None:
                if "w" in self.mode:
                    files[self.path] = self._buffer

        def fake_open(path: str, mode: str = "r", encoding: str | None = None):
            del encoding
            return MemoryFile(path, mode)

        filepath = os.path.join(os.getcwd(), "traces.jsonl")
        with patch("builtins.open", fake_open):
            saved = save_traces_locally(SAMPLE_TRACES, filepath)
            loaded = load_traces(filepath)

        self.assertEqual(saved, len(SAMPLE_TRACES))
        self.assertEqual(loaded, SAMPLE_TRACES)

    def test_publish_requires_token(self) -> None:
        previous = os.environ.pop("HUGGINGFACE_TOKEN", None)
        try:
            with self.assertRaisesRegex(ValueError, "Hugging Face token required"):
                publish_traces_to_hub()
        finally:
            if previous is not None:
                os.environ["HUGGINGFACE_TOKEN"] = previous


if __name__ == "__main__":
    unittest.main()
