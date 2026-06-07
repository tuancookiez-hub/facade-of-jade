# LoRA Fine-Tuning Quickstart

To fine-tune locally with a GPU, run `python train_lora.py --dry-run` first and then `python train_lora.py`.

To fine-tune on Modal, run `python -m modal run train_lora_modal.py::train_remote`.

To validate the Modal dataset wiring without training, run `python -m modal run train_lora_modal.py::train_remote --dry-run`.

The trained adapter is written to the Modal volume `facade-of-jade-lora-out` at `/outputs/facade-of-jade-qwen3-4b-lora`.

Required packages:
- `torch`
- `transformers>=4.51`
- `peft>=0.11`
- `trl>=0.12`
- `datasets>=3.0`
- `accelerate>=1.0`

Expected output: a LoRA adapter saved in `./lora-out/` and ready to upload to the Hugging Face Hub.
