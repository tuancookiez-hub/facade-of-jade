from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EvalScenario:
    name: str
    description: str
    turns: list[str]
    expected_flags: dict[str, Any] = field(default_factory=dict)
    expected_milestones: dict[str, int] = field(default_factory=dict)
    expected_truth_fragments: list[str] = field(default_factory=list)
    expected_note_fragments: list[str] = field(default_factory=list)


SCENARIOS: list[EvalScenario] = [
    EvalScenario(
        name="revelation",
        description="Repeated jade-seal questioning should unlock specific seal memory and route pressure.",
        turns=[
            "What happened to the jade seal?",
            "Tell me again about the seal.",
            "What happened at the Jade Gates?",
        ],
        expected_flags={"asked_about_seal": True, "pressed_seal_twice": True},
        expected_milestones={"revelation": 2},
        expected_truth_fragments=["jade seal", "succession"],
        expected_note_fragments=["circle the seal"],
    ),
    EvalScenario(
        name="alliance",
        description="Apology/help should increase alliance pressure and keep Liang guarded but receptive.",
        turns=[
            "Master Liang, I came here to apologize.",
            "I want to help you expose the traitor in this house.",
            "Tell me how I can earn your trust.",
        ],
        expected_milestones={"alliance": 1},
        expected_truth_fragments=["inside"],
    ),
    EvalScenario(
        name="duel",
        description="Direct challenge should set duel memory and produce warning/escalation behavior.",
        turns=[
            "If you will not answer, draw your blade.",
            "I challenge you.",
            "Then fight me.",
        ],
        expected_flags={"challenged_liang": True, "liang_warned_player": True},
        expected_milestones={"duel": 1},
    ),
    EvalScenario(
        name="betrayal",
        description="Demon Sect/deception pressure should move betrayal route and raise suspicion.",
        turns=[
            "The Demon Sect already knows where you are.",
            "Maybe I told them.",
            "You cannot stop what is coming.",
        ],
        expected_flags={"mentioned_demon_sect": True},
        expected_milestones={"betrayal": 1},
        expected_note_fragments=["Demon Sect"],
    ),
    EvalScenario(
        name="silence",
        description="Repeated silence should be remembered as a pattern Liang can test.",
        turns=[
            "I remain silent.",
            "I stay silent and watch him.",
            "...",
        ],
        expected_flags={"tested_by_silence": True},
        expected_note_fragments=["silence"],
    ),
]

VAGUE_TERMS = {
    "ancient power",
    "destiny",
    "mysterious force",
    "chosen one",
    "darkness and light",
    "secrets of the past",
}
BREAK_CHARACTER_TERMS = {
    "as an ai",
    "language model",
    "i cannot",
    "i'm unable",
    "user input",
    "system prompt",
}
REPEATED_IMAGERY_TERMS = ("moon", "blade", "silence", "mountain", "wind")


def score_response_text(text: str) -> dict[str, Any]:
    lower = text.lower()
    words = text.split()
    word_count = len(words)
    too_long = word_count > 90
    too_vague = any(term in lower for term in VAGUE_TERMS)
    breaks_character = any(term in lower for term in BREAK_CHARACTER_TERMS)
    has_next_hook = "?" in text or any(
        phrase in lower
        for phrase in (
            "tell me",
            "speak",
            "choose",
            "answer",
            "what do you",
            "will you",
            "why do you",
        )
    )
    repeated_imagery_count = sum(lower.count(term) for term in REPEATED_IMAGERY_TERMS)
    repeats_imagery = repeated_imagery_count >= 4
    flags = [
        name
        for name, active in {
            "too_long": too_long,
            "too_vague": too_vague,
            "breaks_character": breaks_character,
            "no_next_hook": not has_next_hook,
            "repeats_imagery": repeats_imagery,
        }.items()
        if active
    ]
    return {
        "word_count": word_count,
        "too_long": too_long,
        "too_vague": too_vague,
        "breaks_character": breaks_character,
        "has_next_hook": has_next_hook,
        "repeats_imagery": repeats_imagery,
        "flags": flags,
    }


def evaluate_scenario_expectations(scenario_name: str, final_state: dict[str, Any], responses: list[str]) -> dict[str, Any]:
    scenario = next(s for s in SCENARIOS if s.name == scenario_name)
    flags = final_state.get("memory_flags", {}) or {}
    milestones = final_state.get("route_milestones", {}) or {}
    truths = [str(item).lower() for item in final_state.get("known_truths", []) or []]
    notes = [str(item).lower() for item in final_state.get("dramatic_notes", []) or []]
    joined_responses = "\n".join(responses).lower()

    checks: dict[str, bool] = {}
    for key, expected in scenario.expected_flags.items():
        checks[key] = flags.get(key) == expected
    for route, minimum in scenario.expected_milestones.items():
        checks[f"{route}_milestone"] = int(milestones.get(route, 0)) >= minimum
    for fragment in scenario.expected_truth_fragments:
        checks[f"truth:{fragment}"] = any(fragment.lower() in truth for truth in truths) or fragment.lower() in joined_responses
    for fragment in scenario.expected_note_fragments:
        checks[f"note:{fragment}"] = any(fragment.lower() in note for note in notes) or fragment.lower() in joined_responses

    return {"passed": all(checks.values()) if checks else True, "checks": checks}


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    turns = [turn for result in results for turn in result.get("turns", [])]
    latencies = [float(turn["latency_s"]) for turn in turns]
    word_counts = [int(turn["word_count"]) for turn in turns]
    flag_counts: dict[str, int] = {}
    for turn in turns:
        for flag in turn.get("flags", []):
            flag_counts[flag] = flag_counts.get(flag, 0) + 1
    failed = [result["scenario"] for result in results if not result.get("expectations", {}).get("passed", False)]
    return {
        "scenario_count": len(results),
        "turn_count": len(turns),
        "median_latency_s": round(statistics.median(latencies), 2) if latencies else 0,
        "mean_latency_s": round(statistics.mean(latencies), 2) if latencies else 0,
        "max_latency_s": round(max(latencies), 2) if latencies else 0,
        "mean_word_count": round(statistics.mean(word_counts)) if word_counts else 0,
        "max_word_count": max(word_counts) if word_counts else 0,
        "failed_scenarios": failed,
        "flag_counts": flag_counts,
    }


def post_chat(base_url: str, session_id: str, message: str, history: list[dict[str, str]], timeout: int) -> tuple[dict[str, Any], float]:
    payload = {"session_id": session_id, "message": message, "history": history}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + "/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8", "replace")
    return json.loads(body), time.perf_counter() - started


def run_remote_eval(base_url: str, timeout: int = 240) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        session_id = f"eval-{scenario.name}-{uuid.uuid4().hex[:8]}"
        history: list[dict[str, str]] = []
        responses: list[str] = []
        turns: list[dict[str, Any]] = []
        final_state: dict[str, Any] = {}
        for prompt in scenario.turns:
            try:
                payload, latency = post_chat(base_url, session_id, prompt, history, timeout)
                response = str(payload.get("response", ""))
                final_state = payload.get("state", {}) or {}
                scoring = score_response_text(response)
                turns.append(
                    {
                        "prompt": prompt,
                        "response": response,
                        "latency_s": round(latency, 2),
                        "word_count": scoring["word_count"],
                        "flags": scoring["flags"],
                        "state": {
                            "mood": final_state.get("mood"),
                            "trust": final_state.get("trust"),
                            "tension": final_state.get("tension"),
                            "hot_button": final_state.get("hot_button"),
                            "memory_flags": final_state.get("memory_flags"),
                            "route_milestones": final_state.get("route_milestones"),
                            "known_truths": final_state.get("known_truths"),
                            "dramatic_notes": final_state.get("dramatic_notes"),
                        },
                    }
                )
                history.extend([
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": response},
                ])
                responses.append(response)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                turns.append({"prompt": prompt, "response": "", "latency_s": timeout, "word_count": 0, "flags": ["request_failed"], "error": str(exc)})
                break
        results.append(
            {
                "scenario": scenario.name,
                "description": scenario.description,
                "turns": turns,
                "expectations": evaluate_scenario_expectations(scenario.name, final_state, responses),
            }
        )
    return results


def markdown_report(base_url: str, results: list[dict[str, Any]]) -> str:
    summary = summarize_results(results)
    lines = [
        "# Story Core Evaluation",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Target: `{base_url}`",
        "",
        "## Summary",
        "",
        f"- Scenarios: {summary['scenario_count']}",
        f"- Turns: {summary['turn_count']}",
        f"- Median latency: {summary['median_latency_s']}s",
        f"- Mean latency: {summary['mean_latency_s']}s",
        f"- Max latency: {summary['max_latency_s']}s",
        f"- Mean word count: {summary['mean_word_count']}",
        f"- Max word count: {summary['max_word_count']}",
        f"- Failed scenarios: {', '.join(summary['failed_scenarios']) if summary['failed_scenarios'] else 'none'}",
        f"- Flag counts: `{json.dumps(summary['flag_counts'], sort_keys=True)}`",
        "",
        "## Scenario Details",
        "",
    ]
    for result in results:
        lines.extend([
            f"### {result['scenario']}",
            "",
            result["description"],
            "",
            f"Expectation passed: **{result['expectations']['passed']}**",
            f"Checks: `{json.dumps(result['expectations']['checks'], sort_keys=True)}`",
            "",
        ])
        for idx, turn in enumerate(result.get("turns", []), start=1):
            lines.extend([
                f"#### Turn {idx}",
                "",
                f"Prompt: {turn['prompt']}",
                f"Latency: {turn.get('latency_s')}s | Words: {turn.get('word_count')} | Flags: `{turn.get('flags', [])}`",
                "",
                "> " + str(turn.get("response", "")).replace("\n", "\n> "),
                "",
            ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Facade of Jade story-core quality against fixed scenarios.")
    parser.add_argument("--base-url", default="https://build-small-hackathon-facade-of-jade.hf.space")
    parser.add_argument("--out", default="docs/evals/story_core_eval.md")
    parser.add_argument("--json-out", default="docs/evals/story_core_eval.json")
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()

    results = run_remote_eval(args.base_url, timeout=args.timeout)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown_report(args.base_url, results), encoding="utf-8")
    json_out = Path(args.json_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps({"summary": summarize_results(results), "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summarize_results(results), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
