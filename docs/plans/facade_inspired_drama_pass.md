# Facade-Inspired Drama Pass Implementation Plan

**Goal:** Make Facade of Jade visibly closer to Playabl Studios' Façade: player utterances should affect social games, hot-button topics, beat goals, and route endings.

**Research basis:** Façade uses discourse acts, drama-manager beat sequencing, social games, hot-button topics, beat mix-ins, transition/reestablish behavior, and multiple endings.

## Source mechanics to adapt

1. **Discourse acts** — map free text to a limited set of player intentions.
2. **Beat goals** — each beat has a current dramatic purpose, not just a label.
3. **Beat mix-ins** — player raises a topic; system acknowledges it, then returns to main arc.
4. **Social games** — hidden counters track affinity, therapy/self-realization, and tension.
5. **Hot buttons** — topics like secrets, betrayal, sect allegiance, or the jade seal provoke stronger reactions.
6. **Readable endings** — reconciliation/alliance, revelation, duel, betrayal/ejection.

## Hackathon-focused implementation

No full ABL clone. Add a lightweight version that judges can see:

- `affinity`: whether player is earning Master Liang's trust.
- `self_realization`: how close Liang is to admitting the Jade Mountain truth.
- `tension`: how close the scene is to confrontation.
- `hot_button`: current sensitive topic detected from player input.
- `mix_in`: short label explaining why the drama manager reacted this turn.
- `beat_goal`: current dramatic goal shown in UI and included in prompt.

## Files to modify

- `beats.py`
- `server_app.py`
- `server_static/index.html`
- `server_static/app.js`
- tests for state and UI metadata

## Verification

- `python -m py_compile server_app.py app.py beats.py`
- `python beats.py`
- `PYTHONPATH=. python -m pytest tests -q`
- deploy and verify production after tests pass
