from __future__ import annotations

from app import _initial_state
from beats import classify_discourse_act, get_system_prompt, get_trace_entry, update_state


def advance(state: dict, text: str) -> dict:
    return update_state(state, classify_discourse_act(text), text)


def test_jade_seal_questions_set_memory_and_advance_revelation_milestone() -> None:
    state = _initial_state()

    state = advance(state, "What really happened the night the jade seal vanished?")

    memory = state["memory_flags"]
    assert memory["asked_about_seal"] is True
    assert memory["seal_questions"] == 1
    assert state["route_milestones"]["revelation"] >= 1
    assert any("jade seal" in truth.lower() for truth in state["known_truths"])


def test_repeated_jade_seal_questions_create_pattern_memory() -> None:
    state = _initial_state()

    state = advance(state, "What happened to the jade seal?")
    state = advance(state, "Tell me again about the seal.")

    memory = state["memory_flags"]
    assert memory["seal_questions"] == 2
    assert memory["pressed_seal_twice"] is True
    assert any("circle the seal" in note.lower() for note in state["dramatic_notes"])


def test_challenge_then_apology_sets_repair_memory() -> None:
    state = _initial_state()

    state = advance(state, "I challenge your judgment — draw your blade if you dare.")
    assert state["memory_flags"]["challenged_liang"] is True
    assert state["player_challenged"] is True

    state = advance(state, "I spoke too harshly. Let me make this right.")

    assert state["memory_flags"]["apologized_after_hostility"] is True
    assert any("apologized after drawing tension" in note.lower() for note in state["dramatic_notes"])


def test_staying_silent_accumulates_observation_pressure() -> None:
    state = _initial_state()

    state = advance(state, "I remain silent.")
    state = advance(state, "I stay silent and watch him.")

    assert state["memory_flags"]["stayed_silent_count"] == 2
    assert state["memory_flags"]["tested_by_silence"] is True
    assert any("silence" in note.lower() for note in state["dramatic_notes"])


def test_system_prompt_includes_only_revealed_truths_and_current_milestone() -> None:
    state = _initial_state()
    initial_prompt = get_system_prompt(state)
    assert "REVEALED CANON TRUTHS" not in initial_prompt
    assert "The jade seal is proof of succession" not in initial_prompt

    state = advance(state, "What really happened the night the jade seal vanished?")
    prompt = get_system_prompt(state)

    assert "STORY SPINE" in prompt
    assert "REVEALED CANON TRUTHS" in prompt
    assert "The jade seal is proof of succession" in prompt
    assert "CURRENT ROUTE MILESTONES" in prompt
    assert "Revelation route" in prompt
    assert "PLAYER MEMORY FLAGS" in prompt
    assert "asked_about_seal" in prompt


def test_trace_entry_records_story_spine_state() -> None:
    state = _initial_state()
    state = advance(state, "What really happened the night the jade seal vanished?")

    trace = get_trace_entry("test-session", "What really happened the night the jade seal vanished?", state, "The seal remembers blood.")

    assert trace["memory_flags"]["asked_about_seal"] is True
    assert trace["route_milestones"]["revelation"] >= 1
    assert any("jade seal" in truth.lower() for truth in trace["known_truths"])
