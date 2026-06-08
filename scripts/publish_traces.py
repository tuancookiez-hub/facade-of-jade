from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import unquote, urlparse

from huggingface_hub import HfApi

REPO_ID = "build-small-hackathon/facade-of-jade-traces"
TRACE_FILE = Path("docs/traces_v0.jsonl")
CRED_FILE = Path("C:/Users/tuanc/.git-credentials-foj")


def read_hf_token() -> str:
    for line in CRED_FILE.read_text(encoding="utf-8").strip().splitlines():
        if "huggingface.co" not in line:
            continue
        parsed = urlparse(line.strip())
        if parsed.password:
            return unquote(parsed.password)
        if parsed.username and parsed.username.startswith("hf_"):
            return unquote(parsed.username)
    raise RuntimeError("No Hugging Face token found in credential helper file")


def main() -> None:
    token = read_hf_token()
    api = HfApi(token=token)
    api.create_repo(repo_id=REPO_ID, repo_type="dataset", exist_ok=True)
    api.upload_file(
        repo_id=REPO_ID,
        repo_type="dataset",
        path_or_fileobj=str(TRACE_FILE),
        path_in_repo="traces_v0.jsonl",
        commit_message="Upload Facade of Jade v0 gameplay traces",
    )
    readme = """---\ntags:\n- gameplay-traces\n- build-small-hackathon\n- facade-of-jade\n---\n\n# Facade of Jade traces\n\nInitial public gameplay trace dataset for the Build Small Hackathon Sharing is Caring badge.\n\nProject: https://github.com/tuancookiez-hub/facade-of-jade\nLive Space: https://build-small-hackathon-facade-of-jade.hf.space\n"""
    api.upload_file(
        repo_id=REPO_ID,
        repo_type="dataset",
        path_or_fileobj=readme.encode("utf-8"),
        path_in_repo="README.md",
        commit_message="Add trace dataset card",
    )
    print(f"published https://huggingface.co/datasets/{REPO_ID}")


if __name__ == "__main__":
    main()
