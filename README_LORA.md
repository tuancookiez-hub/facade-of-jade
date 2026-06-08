# LoRA Fine-Tuning Quickstart

This project trained a PEFT/LoRA adapter for `Qwen/Qwen3-4B-Instruct-2507` using 50 curated Facade of Jade dialogue examples.

## Published adapter

https://huggingface.co/build-small-hackathon/facade-of-jade-qwen3-4b-lora

## Training evidence

- Host: Modal A100-80GB
- Modal app: `facade-of-jade-lora-train`
- Modal volume: `facade-of-jade-lora-out`
- Output path: `/outputs/facade-of-jade-qwen3-4b-lora`
- Final loss: `2.969015`
- Adapter size: `483.63 MB`
- Evidence doc: `docs/lora_training_evidence.md`

## Local validation

```powershell
python train_lora.py --dry-run
python -m pytest tests/test_lora_data.py tests/test_lora_modal_static.py -q
```

## Modal training

Validate remote wiring without training:

```powershell
python -m modal run train_lora_modal.py --dry-run
```

Run training:

```powershell
python -m modal run train_lora_modal.py
```

## Publish adapter

After training, download from the Modal volume and publish with:

```powershell
python scripts/publish_adapter.py
```

The script uploads to:

```text
build-small-hackathon/facade-of-jade-qwen3-4b-lora
```

## Required packages

- `torch`
- `transformers>=4.51`
- `peft>=0.11`
- `trl>=0.12`
- `datasets>=3.0`
- `accelerate>=1.0`
- `huggingface_hub`
