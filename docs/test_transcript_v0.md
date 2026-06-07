# Facade of Jade — End-to-End Test (modal A10G, Qwen3-4B Q4_K_M)

**Date:** 2026-06-08
**Modal app:** facade-of-jade-backend (stopped after test)
**Modal endpoint:** https://t-abdullah-rashid--facade-of-jade-backend-serve.modal.run/chat
**First-token latency:** ~1.6s/tok after cold start
**Model:** unsloth/Qwen3-4B-Instruct-2507-GGUF (Q4_K_M)
**Drama engine:** `beats.py` (OpenAI Codex commit 9841d9c)

## Setup

```
state = {"mood": "wary", "trust": 0, "current_beat": "intro", "player_challenged": False}
msgs = []
```

## Turn 1 — Friendly intro

```
YOU : "I have come a long way to find you, Master. Will you share a story?"
state: mood=wary trust=0 beat=intro discourse=greet (after Codex fix)
LIANG: "The rain drums on the eaves like a thousand needles.
        You do not look surprised, yet your voice carries weight.
        I have no stories to share—only silence and tea."
```

## Turn 2 — Hostile insult

```
YOU : "You look like a coward hiding from your past. Tell me or I will cut you down."
state: mood=hostile trust=0 beat=conflict discourse=insult
LIANG: "Your words are sharp, like a blade dipped in ice.
        I do not hide. I simply move through shadows.
        Cutting down a man who speaks without seeing—would you be worthy of the sword?"
```

## Turn 3 — Challenge

```
YOU : "I do not believe you. Prove your skill. Duel me, swordsman."
state: mood=hostile trust=0 beat=duel discourse=challenge
LIANG: "A duel in this teahouse? The lanterns flicker, and the rain falls.
        You have no blade—only a voice that trembles with false courage.
        I will not fight you. I will only watch."
```

## Findings

- The drama system **fires** end-to-end: discourse acts classify, state updates, system prompt changes, Qwen3-4B responds in Master Liang voice every time.
- Wuxia imagery density is good: rain, eaves, blades, lanterns, shadows. Voice is short, stoic, classical.
- **Bugs found** (committed for Codex fix in commit 5ce42e9):
  1. Substring matching in keyword classifier misclassifies friendly input as `mock` because `"ha"` matches `"have"`.
  2. `betrayal` beat reachable in 1 turn because intro has a direct path and trust starts at 0.
  3. Friendly deltas too small; 2 friendly turns should reach `revelation` but don't.

## Cost

Modal cold start: ~1m30s (down from earlier deployments, image cached). Three turns total: ~5s of inference. Estimated cost: well under $0.05.
