from __future__ import annotations

from scripts.evaluate_story_core import (
    SCENARIOS,
    evaluate_scenario_expectations,
    score_response_text,
    summarize_results,
)


def test_eval_scenarios_cover_core_routes() -> None:
    names = {scenario.name for scenario in SCENARIOS}

    assert {"revelation", "alliance", "duel", "betrayal", "silence"}.issubset(names)
    assert all(len(scenario.turns) >= 2 for scenario in SCENARIOS)


def test_response_text_scoring_flags_long_vague_and_broken_character() -> None:
    good = score_response_text("The seal is succession, not treasure. Ask why your hand trembles when I name it.")
    bad = score_response_text(
        "As an AI language model, I can explain that ancient power and destiny are complicated "
        + "and mysterious. " * 80
    )

    assert good["word_count"] < 30
    assert good["too_long"] is False
    assert good["breaks_character"] is False
    assert bad["too_long"] is True
    assert bad["too_vague"] is True
    assert bad["breaks_character"] is True


def test_evaluate_scenario_expectations_checks_story_spine_state() -> None:
    state = {
        "memory_flags": {"asked_about_seal": True, "pressed_seal_twice": True},
        "route_milestones": {"revelation": 2},
        "known_truths": ["The jade seal is proof of succession, not just a relic."],
        "dramatic_notes": ["The player keeps trying to circle the seal; Liang should notice the pattern."],
        "trust": 31,
        "tension": 35,
    }

    result = evaluate_scenario_expectations(
        scenario_name="revelation",
        final_state=state,
        responses=["The seal is succession, not treasure. Why do you circle it again?"],
    )

    assert result["passed"] is True
    assert result["checks"]["asked_about_seal"] is True
    assert result["checks"]["pressed_seal_twice"] is True
    assert result["checks"]["revelation_milestone"] is True


def test_summarize_results_computes_latency_and_failure_counts() -> None:
    results = [
        {"scenario": "a", "turns": [{"latency_s": 1.2, "word_count": 12, "flags": []}], "expectations": {"passed": True}},
        {"scenario": "b", "turns": [{"latency_s": 3.4, "word_count": 100, "flags": ["too_long"]}], "expectations": {"passed": False}},
    ]

    summary = summarize_results(results)

    assert summary["scenario_count"] == 2
    assert summary["turn_count"] == 2
    assert summary["median_latency_s"] == 2.3
    assert summary["mean_word_count"] == 56
    assert summary["failed_scenarios"] == ["b"]
    assert summary["flag_counts"]["too_long"] == 1
