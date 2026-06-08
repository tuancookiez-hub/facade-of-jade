from __future__ import annotations

"""Run a fixed-benchmark prompt set against base vs LoRA variants.

This script is a scaffold for the bakeoff step. It does not hard-code any
provider. Instead, it lets you point three model endpoints at the same prompt
set and captures the outputs in a stable JSON structure.

Expected use:

  python scripts/compare_lora.py \
    --input docs/lora_eval_prompts.md \
    --base-cmd "..." \
    --v1-cmd "..." \
    --v2-cmd "..." \
    --out reports/lora_bakeoff.json

Each command should print a single model response to stdout.
"""

import argparse
import json
import re
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

PROMPT_RE = re.compile(r"^\d+\.\s+(.*)$")


@dataclass
class CaseResult:
    prompt: str
    base: str
    v1: str
    v2: str


def extract_prompts(md_path: Path) -> list[str]:
    prompts: list[str] = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        match = PROMPT_RE.match(line.strip())
        if match:
            prompts.append(match.group(1).strip())
    if not prompts:
        raise ValueError(f"No numbered prompts found in {md_path}")
    return prompts


def run_command(command: str, prompt: str) -> str:
    completed = subprocess.run(
        command,
        input=prompt,
        text=True,
        shell=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {command}\nSTDERR:\n{completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare base vs LoRA outputs on fixed prompts.")
    parser.add_argument("--input", type=Path, required=True, help="Markdown file with numbered prompts.")
    parser.add_argument("--base-cmd", required=True, help="Shell command that reads a prompt from stdin and prints the base response.")
    parser.add_argument("--v1-cmd", required=True, help="Shell command for LoRA v1.")
    parser.add_argument("--v2-cmd", required=True, help="Shell command for LoRA v2.")
    parser.add_argument("--out", type=Path, required=True, help="Where to write the JSON result.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    prompts = extract_prompts(args.input)

    results: list[CaseResult] = []
    for prompt in prompts:
        results.append(
            CaseResult(
                prompt=prompt,
                base=run_command(args.base_cmd, prompt),
                v1=run_command(args.v1_cmd, prompt),
                v2=run_command(args.v2_cmd, prompt),
            )
        )

    payload = {
        "input": str(args.input),
        "cases": [asdict(item) for item in results],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(results)} cases to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
