from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

from huggingface_hub import HfApi

REPO_ID = "build-small-hackathon/facade-of-jade-qwen3-4b-lora"
LOCAL_DIR = Path(r"C:\Users\tuanc\AppData\Local\Temp\foj_adapter_download\facade-of-jade-qwen3-4b-lora")
CRED_FILE = Path("C:/Users/tuanc/.git-credentials-foj")


def read_hf_token() -> str:
    text = CRED_FILE.read_text(encoding="utf-8").strip().splitlines()
    for line in text:
        if "huggingface.co" not in line:
            continue
        parsed = urlparse(line.strip())
        if parsed.password:
            return unquote(parsed.password)
        if parsed.username and parsed.username.startswith("hf_"):
            return unquote(parsed.username)
    raise RuntimeError("No Hugging Face token found in credential helper file")


def main() -> None:
    if not LOCAL_DIR.exists():
        raise SystemExit(f"Adapter directory missing: {LOCAL_DIR}")
    token = read_hf_token()
    api = HfApi(token=token)
    api.create_repo(repo_id=REPO_ID, repo_type="model", exist_ok=True)
    api.upload_folder(
        repo_id=REPO_ID,
        repo_type="model",
        folder_path=str(LOCAL_DIR),
        commit_message="Upload Facade of Jade Qwen3-4B LoRA adapter",
    )
    print(f"published https://huggingface.co/{REPO_ID}")


if __name__ == "__main__":
    main()
