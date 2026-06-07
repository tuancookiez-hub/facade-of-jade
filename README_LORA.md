# LoRA Fine-Tuning Quickstart

To fine-tune locally with a GPU, run `python train_lora.py --dry-run` first and then `python train_lora.py`.

To fine-tune on Modal, see `train_lora_modal.py` as an optional follow-up.

Required packages:
- `torch`
- `transformers>=4.51`
- `peft>=0.11`
- `trl>=0.12`
- `datasets>=3.0`
- `accelerate>=1.0`

Expected output: a LoRA adapter saved in `./lora-out/` and ready to upload to the Hugging Face Hub.
