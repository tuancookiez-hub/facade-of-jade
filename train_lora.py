import argparse
import json
from pathlib import Path
from typing import Any


def resolve_dataset_path() -> Path:
    base_dir = Path(__file__).resolve().parent
    candidates = (
        (base_dir / "../loRA_training_data_v1_gpt5.jsonl").resolve(),
        (base_dir / "./loRA_training_data_v1_gpt5.jsonl").resolve(),
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    searched = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Could not find training data. Looked for: {searched}")


def _validate_message(message: Any, line_number: int, message_index: int) -> None:
    if not isinstance(message, dict):
        raise ValueError(
            f"Line {line_number}: message {message_index} must be an object with role/content"
        )
    missing = [key for key in ("role", "content") if key not in message]
    if missing:
        raise ValueError(
            f"Line {line_number}: message {message_index} missing keys: {', '.join(missing)}"
        )
    if not isinstance(message["role"], str) or not message["role"].strip():
        raise ValueError(f"Line {line_number}: message {message_index} has invalid role")
    if not isinstance(message["content"], str):
        raise ValueError(f"Line {line_number}: message {message_index} has invalid content")


def load_and_validate_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Line {line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Line {line_number}: top-level entry must be an object")
            messages = record.get("messages")
            if not isinstance(messages, list) or not messages:
                raise ValueError(f"Line {line_number}: messages must be a non-empty array")
            for message_index, message in enumerate(messages):
                _validate_message(message, line_number, message_index)
            records.append({"messages": messages})
    if not records:
        raise ValueError(f"No training records found in {path}")
    return records


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fine-tune a LoRA adapter for Facade of Jade.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the dataset and print what would be trained without loading the model.",
    )
    return parser


def format_messages_as_text(messages: list[dict[str, str]]) -> str:
    parts = []
    for message in messages:
        parts.append(f"{message['role']}: {message['content']}")
    return "\n".join(parts)


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    dataset_path = resolve_dataset_path()
    records = load_and_validate_jsonl(dataset_path)

    if args.dry_run:
        print(f"Validated {len(records)} examples from {dataset_path}")
        print(f"Would train on {len(records)} examples for 3 epochs")
        print("GPU host note: run `python train_lora.py` on a machine with CUDA or a managed GPU runner.")
        print("Modal-style invocation note: `python -m modal run train_lora.py`")
        return 0

    try:
        import torch
        from datasets import Dataset
        from peft import LoraConfig
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
        from trl import SFTTrainer
    except ImportError as exc:
        raise SystemExit(
            "Missing training dependencies. Install: torch, transformers>=4.51, peft>=0.11, "
            "trl>=0.12, datasets>=3.0, accelerate>=1.0"
        ) from exc

    hf_dataset = Dataset.from_list(records)
    use_bf16 = bool(torch.cuda.is_available() and torch.cuda.is_bf16_supported())
    use_fp16 = bool(torch.cuda.is_available() and not use_bf16)

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B-Instruct-2507")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def chat_formatting_func(example: dict[str, Any]) -> str:
        messages = example["messages"]
        if hasattr(tokenizer, "apply_chat_template"):
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False,
            )
        return format_messages_as_text(messages)

    model = AutoModelForCausalLM.from_pretrained(
        "Qwen/Qwen3-4B-Instruct-2507",
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        task_type="CAUSAL_LM",
    )

    training_args = TrainingArguments(
        output_dir="./lora-out",
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=use_fp16,
        bf16=use_bf16,
        logging_steps=5,
        save_strategy="epoch",
        report_to=[],
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=hf_dataset,
        processing_class=tokenizer,
        peft_config=lora_config,
        formatting_func=chat_formatting_func,
        max_seq_length=1024,
    )

    train_result = trainer.train()
    trainer.model.save_pretrained("./lora-out")

    adapter_dir = Path("./lora-out")
    adapter_size_bytes = sum(
        file_path.stat().st_size for file_path in adapter_dir.rglob("*") if file_path.is_file()
    )
    adapter_size_mb = adapter_size_bytes / (1024 * 1024)

    print("Training complete.")
    print(f"Training loss: {train_result.training_loss:.6f}")
    print(f"Adapter size: {adapter_size_mb:.2f} MB")
    print(f"Saved adapter: {adapter_dir.resolve()}")
    print("GPU host note: this workflow is intended to run on a CUDA-capable machine.")
    print("Modal-style invocation note: `python -m modal run train_lora.py`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
