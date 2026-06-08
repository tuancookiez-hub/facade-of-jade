# Future LoRA work

This note tracks the next fine-tuning work so it does not get lost while UI/model-runtime work continues.

## Current artifact

- Public adapter: https://huggingface.co/build-small-hackathon/facade-of-jade-qwen3-4b-lora
- Base model: `Qwen/Qwen3-4B-Instruct-2507`
- Dataset: `loRA_training_data_v1_gpt5.jsonl`
- Training records: 50
- Epochs: 3
- Final train loss: `2.969015`
- Adapter size reported by Modal runner: `483.63 MB`
- Modal run: https://modal.com/apps/t-abdullah-rashid/main/ap-W54lCMfJu4eu3UCVQvVpQK

## Important caveat

The live app currently serves a Q4_K_M GGUF base model through `llama.cpp` on Modal. The LoRA adapter is published as a Well-Tuned artifact, but it is not yet proven to be loaded by the live `llama.cpp` backend.

Use honest wording in README/demo until this is solved:

> The LoRA adapter is a published fine-tuning artifact for Master Liang's voice. The live Space currently uses the stable Q4_K_M GGUF base model through llama.cpp for runtime reliability.

## Next fine-tuning goals

1. Expand dataset from 50 examples to 150-300 examples.
2. Include full multi-turn traces, not only isolated turns.
3. Balance paths:
   - respectful / alliance
   - hostile / duel
   - apology / repair
   - lore / revelation
   - betrayal / terminal endings
4. Add negative examples where the model should stay concise and avoid generic assistant phrasing.
5. Train a v2 adapter and publish as a separate HF revision or repo.
6. Add before/after eval prompts comparing:
   - base Qwen3-4B
   - LoRA v1
   - LoRA v2
7. Investigate live integration options:
   - convert/merge adapter to GGUF if compatible with llama.cpp
   - use a transformers/PEFT Modal backend for tuned mode
   - expose a "Base vs Tuned" comparison route if latency is acceptable

## Decision rule

Do not replace the stable live backend until the tuned path is verified on Modal with:

- successful cold start
- successful streaming response
- acceptable latency
- better character voice on at least 6/8 fixed bakeoff prompts
- clear README wording about runtime model
