from __future__ import annotations

from pathlib import Path

import modal

from train_lora import format_messages_as_text, load_and_validate_jsonl

APP_NAME = "facade-of-jade-lora-train"
VOLUME_NAME = "facade-of-jade-lora-out"
BASE_MODEL_NAME = "Qwen/Qwen3-4B-Instruct-2507"
REMOTE_DATASET_PATH = "/data/loRA_training_data_v1_gpt5.jsonl"
OUTPUT_DIR = "/outputs/facade-of-jade-qwen3-4b-lora"
LOCAL_REPO_DIR = Path(__file__).resolve().parent
LOCAL_DATASET_PATH = (LOCAL_REPO_DIR / "../loRA_training_data_v1_gpt5.jsonl").resolve()
LOCAL_TRAIN_LORA_PATH = LOCAL_REPO_DIR / "train_lora.py"
REMOTE_TRAIN_LORA_PATH = "/root/train_lora.py"


def _build_image() -> modal.Image:
    return (
        modal.Image.from_registry(
            "nvidia/cuda:12.1.0-devel-ubuntu22.04",
            add_python="3.11",
        )
        .apt_install("git")
        .run_commands("pip install --upgrade pip")
        .pip_install(
            "torch",
            "transformers>=4.51",
            "peft>=0.11",
            "trl>=0.12",
            "datasets>=3.0",
            "accelerate>=1.0",
            "huggingface_hub",
        )
        .add_local_file(
            LOCAL_DATASET_PATH,
            REMOTE_DATASET_PATH,
        )
        .add_local_file(
            LOCAL_TRAIN_LORA_PATH,
            REMOTE_TRAIN_LORA_PATH,
        )
    )


image = _build_image()
app = modal.App(APP_NAME, image=image)
output_volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)


@app.function(
    gpu="A100-80GB",
    volumes={"/outputs": output_volume},
    timeout=60 * 60 * 6,
)
def train_remote(dry_run: bool = False) -> None:
    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
    from trl import SFTTrainer

    dataset_path = Path(REMOTE_DATASET_PATH)
    records = load_and_validate_jsonl(dataset_path)

    print(f"Dataset path: {dataset_path}")
    print(f"Number of records: {len(records)}")
    print(f"Base model name: {BASE_MODEL_NAME}")
    print(f"Output dir: {OUTPUT_DIR}")

    if dry_run:
        print("Dry run: validated dataset and Modal config without starting training.")
        return

    hf_dataset = Dataset.from_list(records)
    use_bf16 = bool(torch.cuda.is_available() and torch.cuda.is_bf16_supported())
    use_fp16 = bool(torch.cuda.is_available() and not use_bf16)

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def chat_formatting_func(example: dict[str, object]) -> str:
        messages = example["messages"]
        if hasattr(tokenizer, "apply_chat_template"):
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False,
            )
        return format_messages_as_text(messages)

    model_dtype = torch.bfloat16 if use_bf16 else torch.float16
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        torch_dtype=model_dtype,
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
        output_dir=OUTPUT_DIR,
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
    )

    train_result = trainer.train()
    trainer.model.save_pretrained(OUTPUT_DIR)
    output_volume.commit()

    adapter_dir = Path(OUTPUT_DIR)
    adapter_size_bytes = sum(
        file_path.stat().st_size for file_path in adapter_dir.rglob("*") if file_path.is_file()
    )
    adapter_size_mb = adapter_size_bytes / (1024 * 1024)

    print(f"Training loss: {train_result.training_loss:.6f}")
    print(f"Adapter size MB: {adapter_size_mb:.2f}")


@app.local_entrypoint()
def main(dry_run: bool = False) -> None:
    train_remote.remote(dry_run=dry_run)
