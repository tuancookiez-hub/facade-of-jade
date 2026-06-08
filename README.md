---
title: Facade of Jade
emoji: 🗡️
colorFrom: red
colorTo: gray
sdk: gradio
sdk_version: 6.16.0
python_version: '3.13'
app_file: server_app.py
pinned: false
license: mit
tags:
  - thousand-token-wood
  - tiny-titan
  - off-brand
  - llama-champion
  - sharing-is-caring
  - field-notes
  - best-demo
  - best-agent
short_description: Façade-inspired AI Wuxia drama game.
---

# Facade of Jade

**Facade of Jade** is a playable AI Wuxia drama inspired by Playabl Studios' 2005 interactive drama *Façade*.

You speak freely to Master Liang, the last swordsman of the Jade Mountain Sect. Your wording changes his trust, mood, tension, hot-button reactions, story pressure, and possible endings in real time.

This is not a normal chatbot skin. The app combines:

- a custom `gr.Server` browser-game UI
- a Modal-hosted small LLM backend running through `llama.cpp`
- a lightweight Façade-inspired drama manager
- discourse-act classification
- hot-button topic detection
- social-game state tracking
- visible beat goals and path pressure
- gameplay trace publishing
- a trained LoRA adapter artifact for Master Liang's voice

## Live demo

Play here:

https://build-small-hackathon-facade-of-jade.hf.space

Repository:

https://github.com/tuancookiez-hub/facade-of-jade

## Why this is interesting

Most LLM demos are open-ended chat. *Facade of Jade* turns open-ended chat into an interactive drama loop:

1. The player types anything.
2. `beats.py` classifies the line into a discourse act, such as praise, apology, threat, question, challenge, or secret-sharing.
3. The drama manager updates trust, mood, affinity, self-realization, tension, current beat, hot-button topic, and path pressure.
4. The updated state rewrites the model prompt sent to Modal.
5. Master Liang replies in character.
6. The UI exposes the hidden drama state so the player can see that their words are changing the scene.

The result is closer to a small AI drama game than a branching dialogue tree.

## Façade-inspired mechanics

The original *Façade* used discourse acts, beat sequencing, social games, hot-button topics, mix-ins, and multiple endings. This project adapts those ideas into a compact hackathon-sized architecture:

- **Discourse acts** — player text is mapped to intent categories.
- **Beat goals** — each scene has a dramatic purpose, visible in the Drama Engine panel.
- **Hot-button mix-ins** — mentioning topics like the jade seal, Demon Sect, betrayal, or Jade Mountain changes how the scene reacts.
- **Social games** — the app tracks affinity, therapy/self-realization, and tension.
- **Path pressure** — visible meters show pressure toward revelation, alliance, duel, or betrayal.
- **Endings** — player behavior can push the story toward alliance, duel, or broken trust.

## Technical architecture

- **UI:** Gradio `gr.Server` with custom HTML/CSS/JS, not default Gradio Blocks.
- **Model runtime:** Modal-hosted `llama.cpp` backend.
- **Base model:** Qwen3-4B-Instruct GGUF, Q4_K_M quantization.
- **Streaming:** `/api/chat_stream` streams newline-delimited JSON events to the frontend.
- **Drama manager:** `beats.py` controls discourse acts, social games, beats, endings, and prompt shaping.
- **Trace logging:** `trace_utils.py` records gameplay traces for reproducibility and sharing.
- **Training artifact:** A published LoRA adapter exists for Master Liang's voice.

## Public artifacts

- Live Space: https://build-small-hackathon-facade-of-jade.hf.space
- GitHub repo: https://github.com/tuancookiez-hub/facade-of-jade
- Trained LoRA adapter: https://huggingface.co/build-small-hackathon/facade-of-jade-qwen3-4b-lora
- Public gameplay traces: https://huggingface.co/datasets/build-small-hackathon/facade-of-jade-traces
- LoRA training evidence: `docs/lora_training_evidence.md`
- Future LoRA plan: `docs/future_lora_work.md`
- Demo script: `docs/demo_script.md`

## Honest model / LoRA status

The live app currently uses the stable Modal + `llama.cpp` runtime path for reliability.

The LoRA adapter is a real published fine-tuning artifact trained for Master Liang's voice, but the production runtime should only be described as LoRA-powered after the adapter-loading path is verified end-to-end on Modal.

Safe wording:

> We trained and published a LoRA adapter for Master Liang's voice, and the live app uses a stable Modal-hosted `llama.cpp` runtime for the playable demo.

## Prize alignment

**Best Demo / Best Agent**

The app is playable, stateful, and judge-visible. The Drama Engine panel shows how free text changes trust, mood, beat goals, hot-button mix-ins, social-game meters, and route pressure.

**Off-Brand**

The project uses `gr.Server` with fully custom HTML/CSS/JS instead of a standard Gradio chat interface.

**Modal prize**

Inference is hosted on Modal. The live app routes player turns to a Modal backend for streaming model output.

**Llama Champion / small-model angle**

The demo uses a small open model path through `llama.cpp` instead of relying on a hosted frontier-model API for gameplay.

**Well-Tuned**

A Qwen3-4B LoRA adapter was trained on Modal A100 using curated Facade of Jade dialogue examples. Evidence and adapter links are public.

**Sharing is Caring / Field Notes**

Gameplay trace utilities and public trace datasets document how the drama manager responds to player turns.

## Quick local checks

```powershell
python -m py_compile server_app.py app.py beats.py
python beats.py
python -m pytest tests -q
```

Run locally:

```powershell
python server_app.py
```

Then open:

```text
http://127.0.0.1:7860/
```

## Suggested judge path

Use the demo script in:

```text
docs/demo_script.md
```

The fastest way to understand the project is to play four turns:

1. respectful opening
2. question about Jade Mountain
3. mention the jade seal
4. provoke or apologize

Watch the Drama Engine panel change after each line.

## Built during Build Small Hackathon

Built for the June 2026 Build Small Hackathon as a small, playable AI drama game with a custom UI, Modal inference, small-model runtime, LoRA evidence, trace sharing, and a Façade-inspired drama manager.
