# LoRA training evidence

## Result

- Adapter repo: https://huggingface.co/build-small-hackathon/facade-of-jade-qwen3-4b-lora
- Base model: `Qwen/Qwen3-4B-Instruct-2507`
- Training data: `loRA_training_data_v1_gpt5.jsonl`
- Examples: `50`
- Host: Modal A100-80GB
- Modal app: `facade-of-jade-lora-train`
- Modal volume: `facade-of-jade-lora-out`
- Output path: `/outputs/facade-of-jade-qwen3-4b-lora`
- Modal run: https://modal.com/apps/t-abdullah-rashid/main/ap-W54lCMfJu4eu3UCVQvVpQK

## Final training output

```text
train_runtime: 49.82
train_samples_per_second: 3.011
train_steps_per_second: 0.783
train_loss: 2.969015
adapter size: 483.63 MB
```

## Verification

The adapter repo was verified through the Hugging Face model API after upload.
It contains root adapter files:

- `adapter_config.json`
- `adapter_model.safetensors`
- `README.md`

It also includes checkpoints 13, 26, and 39 for reproducibility.
