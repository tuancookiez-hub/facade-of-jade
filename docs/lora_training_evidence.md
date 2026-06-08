# LoRA training evidence

Facade of Jade LoRA adapter training completed on Modal A100.

- Base model: `Qwen/Qwen3-4B-Instruct-2507`
- Dataset: `loRA_training_data_v1_gpt5.jsonl`
- Training records: 50
- Epochs: 3
- Final train loss: `2.969015`
- Adapter size reported by runner: `483.63 MB`
- Modal output volume: `facade-of-jade-lora-out`
- Modal adapter path: `facade-of-jade-qwen3-4b-lora`
- Modal run: https://modal.com/apps/t-abdullah-rashid/main/ap-W54lCMfJu4eu3UCVQvVpQK
- Public adapter: https://huggingface.co/build-small-hackathon/facade-of-jade-qwen3-4b-lora

Remote dry-run validated before training:

```text
Dataset path: /data/loRA_training_data_v1_gpt5.jsonl
Number of records: 50
Base model name: Qwen/Qwen3-4B-Instruct-2507
Output dir: /outputs/facade-of-jade-qwen3-4b-lora
Dry run: validated dataset and Modal config without starting training.
```

Training completion evidence:

```text
train_loss: 2.969015
Adapter size MB: 483.63
```
