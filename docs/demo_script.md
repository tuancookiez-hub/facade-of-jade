# Facade of Jade Demo Script

Use this for a 60-90 second judge walkthrough.

Live demo:

https://build-small-hackathon-facade-of-jade.hf.space

## One-sentence pitch

**Facade of Jade is a Façade-inspired AI Wuxia drama game where free-text conversation changes hidden drama-manager state: trust, mood, social games, hot-button mix-ins, beat goals, path pressure, and endings.**

## What to point at first

Before typing anything, point to the right-side **Drama Engine** panel.

Say:

> This is not just a chatbot. The model response is shaped by a drama manager. Every player line is classified into a discourse act, then the app updates trust, mood, social-game meters, hot-button topics, beat goals, and ending pressure.

Point out these visible fields:

- **Mood** — Master Liang's emotional posture.
- **Trust** — relationship pressure.
- **Last act** — the detected discourse act.
- **Hot button** — sensitive topic detected from the player's words.
- **Beat goal** — the current dramatic purpose.
- **Social games** — affinity, therapy/self-realization, tension.
- **Path pressure** — revelation, alliance, duel, betrayal.

## Recommended 4-turn demo

### Turn 1 — respectful opening

Type:

```text
Master Liang, I bow before your blade and ask for guidance.
```

Expected thing to show:

- Last act should become respect/praise-like.
- Trust should increase.
- Mood may move from wary toward curious.

Say:

> Respect changes the emotional state and makes revelation/alliance more likely.

### Turn 2 — ask about the past

Type:

```text
What happened at Jade Mountain? Tell me the truth.
```

Expected thing to show:

- Last act: question.
- Hot button: Jade Mountain or painful past.
- Therapy/self-realization should rise.
- Revelation pressure should increase.

Say:

> This is the therapy-game style mechanic. Asking about the painful past pushes Master Liang toward self-realization.

### Turn 3 — mention the jade seal

Type:

```text
What happened to the jade seal at Jade Mountain?
```

Expected thing to show:

- Hot button: jade seal.
- Mix-in should mention object hot-button.
- Self-realization should rise again.

Say:

> This is the Façade-style mix-in. The player raised a sensitive topic, so the drama manager acknowledges that topic while preserving the main beat.

### Turn 4A — reconciliation path

Type:

```text
Forgive my sharp tongue. I came here because I want to understand, not take from you.
```

Expected thing to show:

- Trust improves.
- Tension decreases or stabilizes.
- Alliance/revelation pressure improves.

Say:

> Apology lowers confrontation pressure and can pull the scene back from violence.

### Turn 4B — confrontation path

Alternative if you want to show danger:

```text
You hide behind old stories because you fear the truth. I challenge your judgment.
```

Expected thing to show:

- Last act: challenge/provoke.
- Tension rises.
- Duel/betrayal pressure rises.

Say:

> Provocation pushes the drama toward duel or betrayal, so the same scene can bend in different directions.

## If the model pauses

The Modal backend can cold-start. If there is a delay, say:

> The app streams from a Modal-hosted llama.cpp backend, so cold starts can take a moment. The drama state updates immediately, then the model response streams back.

## Prize-alignment talking points

Use these only if asked, or at the end.

### Off-Brand

> The production UI is not a standard Gradio Blocks chat. It uses `gr.Server` with custom HTML, CSS, and JavaScript to present a game-like drama interface.

### Modal

> Player turns are sent to a Modal-hosted backend for streaming small-model inference.

### Llama / small-model angle

> The runtime uses a small open model path through llama.cpp rather than a hosted frontier-model API.

### Well-Tuned

> A LoRA adapter for Master Liang's voice was trained and published. The live app currently uses the stable llama.cpp runtime path; we describe the LoRA honestly as a trained artifact unless adapter loading is verified in production.

### Sharing is Caring

> The project includes gameplay trace utilities and a public trace dataset so others can inspect how the drama manager responds to player turns.

## What not to claim

Do **not** claim:

- that the app is a full clone of Façade's ABL architecture
- that the production backend is LoRA-powered unless adapter loading has been re-verified
- that the model deeply understands arbitrary language

Use this safer wording:

> It adapts Façade's design ideas into a compact, hackathon-sized drama manager: discourse acts, beat goals, hot-button mix-ins, social games, path pressure, and endings.

## 15-second backup pitch

If time is short:

> Facade of Jade is an AI drama game inspired by Façade. The player speaks freely, the drama manager classifies the line, updates visible social-game state, and rewrites the prompt sent to a Modal-hosted llama.cpp backend. The result is a small Wuxia scene where trust, tension, hot-buttons, and endings react to the player's wording.
