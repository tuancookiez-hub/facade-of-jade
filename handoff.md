# Handoff

## Goal
Build **Facade of Jade** into a browser-playable AI interactive drama inspired by *Façade*: a low-fi 3D teahouse scene where the player can move, speak freely or through quick options, and Master Liang reacts through a stateful Story Spine drama engine.

## Current State
Production is stable and deployed.

- Project path: `F:\HermesVision\SmallHackathon\facade-of-jade`
- Production app: `https://build-small-hackathon-facade-of-jade.hf.space/`
- 3D prototype: `https://build-small-hackathon-facade-of-jade.hf.space/scene3d.html`
- GitHub: `https://github.com/tuancookiez-hub/facade-of-jade.git`
- Latest deployed commit: `e6f41ff fix: show player dialogue in 3d scene`
- HF verified running at: `e6f41ff504d2f32bd25f7be51d28db61543e8277`
- Git status was clean after final verification.

The latest background-process notification was only a temporary local QA server:

```text
proc_b0a923f13090
Command: GRADIO_SERVER_PORT=7863 python server_app.py
Exit code: -15
```

No issue. It was not production. It was not manually killed.

## Files in Flight
No files are currently in flight. Working tree was clean after the last deploy.

Main files for the next session:

```text
server_static/scene3d.html
server_static/scene3d.css
server_static/scene3d.js
tests/test_scene3d_static.py
server_app.py
beats.py
scripts/evaluate_story_core.py
```

## Changed
This session implemented and deployed the 3D prototype path.

### Story/core work already present
The backend has **Story Spine v1**:

- canonical truths
- memory flags
- route milestones
- dramatic notes
- conditional prompt injection based on revealed truths
- trace/state exposure

Important state flags include:

```text
asked_about_seal
seal_questions
pressed_seal_twice
mentioned_demon_sect
asked_about_jade_mountain
challenged_liang
accused_liang
apologized_after_hostility
stayed_silent_count
tested_by_silence
earned_first_truth
liang_warned_player
```

Routes:

```text
revelation
alliance
duel
betrayal
```

### Eval harness
Created and used:

```text
scripts/evaluate_story_core.py
docs/evals/story_core_eval.md
docs/evals/story_core_eval.json
docs/evals/story_core_eval_after_tuning.md
docs/evals/story_core_eval_after_tuning.json
```

After prompt tuning:

- `no_next_hook` improved from `4` to `0`
- `too_long` remained `1`
- `repeats_imagery` remained `1`
- all scenario state expectations structurally passed

### 3D prototype features
Current `/scene3d.html` includes:

- Three.js low-fi teahouse room
- seated primitive Master Liang NPC
- first-person camera
- WASD / arrow key movement
- drag-look camera rotation
- room boundary clamping
- visible movement hint
- NPC dialogue bubble
- **YOU** player dialogue panel
- bottom player controls
- quick actions:
  - Apologize
  - Ask seal
  - Challenge
  - Stay silent
- free text input
- mood/trust/tension/route strip
- `window.__scene3dDebug.getPlayer()` QA helper
- state-driven visuals:
  - trust affects lantern warmth
  - tension affects red light
  - revelation intensifies jade light
  - duel/betrayal alter lighting/fog
  - mood/route alter NPC rotation

### Latest UX fix
User noticed player dialogue was invisible. Fixed in:

```text
e6f41ff fix: show player dialogue in 3d scene
```

Now quick actions and typed input immediately show the player's last utterance in a **YOU** panel before Master Liang replies.

Verified production by clicking **Ask seal**:

```text
YOU
What happened to the jade seal?
```

Then Master Liang responded above it. Visual QA confirmed both lines are readable with no blocking layout issue.

## Failed Attempts
- Initial `scene3d.html` route returned 404 because `server_app.py` only served `/` and `/server_static/{filename}`. Fixed by adding `GET /scene3d.html`.
- Initial 3D scene was too dark; NPC was hard to see. Fixed with warmer key light, rim light, brighter robe material, reduced fog/darker balance.
- NPC speech bubble had text cutoff / positioning issues because CSS `left: 50%` combined with JS projection double-offset the bubble. Fixed by anchoring bubble at `left: 0; top: 0` and using projected screen coordinates.
- Movement hint was too visually hidden in production QA. Fixed by moving it top-left under the title.
- Player utterance was missing entirely. Fixed by adding `#player-utterance`, `#player-line`, and `updatePlayerDialogue()`.

## Key Decisions This Session
- Keep `/` classic view working.
- Keep `/scene3d.html` as experimental 3D page.
- Keep backend/model unchanged while improving 3D controls/UI.
- Use Three.js, not Unity/Godot yet.
- Keep player/NPC dialogue as HTML overlays for readability.
- Current prototype is visually rough but now functionally reads as an early browser game.

## Verification
Latest commands run:

```bash
node --check server_static/scene3d.js
PYTHONPATH=. python -m pytest tests/test_scene3d_static.py -q
PYTHONPATH=. python -m pytest tests -q
```

Latest result:

```text
27 passed
```

Production verified after deploy:

- page loads
- movement hint visible
- NPC visible
- WASD movement works via `window.__scene3dDebug.getPlayer()`
- drag-look works locally
- quick actions call backend
- player line visible
- NPC line visible
- mood/trust/route update
- no blocking layout issue

## Next Step
The user wants the next session to focus on:

> improving the controls to be similar to *Façade*

The user said they will provide details/reference information in the next session. **Do not implement blindly before reading their details.**

Recommended next-session flow:

1. Read this `handoff.md`.
2. Ask the user for their Façade control details/reference, or review what they provide.
3. Summarize the desired control feel.
4. Translate it into a small v2 controls plan.
5. Add tests first in `tests/test_scene3d_static.py`.
6. Modify only:
   ```text
   server_static/scene3d.html
   server_static/scene3d.css
   server_static/scene3d.js
   tests/test_scene3d_static.py
   ```
7. Run:
   ```bash
   node --check server_static/scene3d.js
   PYTHONPATH=. python -m pytest tests -q
   ```
8. Start a temporary QA server on a new port if needed:
   ```bash
   GRADIO_SERVER_PORT=7864 python server_app.py
   ```
9. Browser QA:
   - movement works
   - camera controls feel improved
   - player dialogue still visible
   - NPC dialogue still visible
   - quick actions and typed input still call backend
   - no JS console errors
10. Commit, push to HF and GitHub, then verify production.

## Likely Next Controls Work
Depending on the user's Façade reference/details, likely improvements include:

### Movement/camera feel
- smoother acceleration/deceleration
- better drag-look sensitivity
- optional pointer lock if appropriate
- lower movement speed
- better starting position near doorway
- simple table/NPC collision zones

### Façade-like interaction model
- approach NPC/object to interact
- contextual prompts such as:
  ```text
  E: Talk to Master Liang
  ```
- quick actions only show when interaction context is active
- player can move while dialogue remains visible
- input stays bottom aligned like a game command line

### Spatial conversation feel
- NPC turns to face player based on player position
- if player backs away, dialogue fades or Liang comments
- if player walks too far, input disables or says “Move closer”
- speech bubble stays anchored above Liang

### Social pressure later
Not yet implemented, but likely next after controls:

- silence timer
- Liang reacts if player waits too long
- autonomous remarks
- interrupt-like behavior
- stronger topic transitions

## Constraints / Reminders
- Do not break current working production demo.
- Do not replace `/` classic view.
- Do not touch backend/model unless user specifically asks.
- Do not kill any running process without explicit approval.
- Use PowerShell syntax for user-facing manual commands.
- Terminal tool runs bash/MSYS internally.
- Verify with real tool output before claiming success.
- User values honest claims: say “mitigates” if not fully solved.

## Useful Commands
User-facing PowerShell:

```powershell
cd F:\HermesVision\SmallHackathon\facade-of-jade
$env:PYTHONPATH="."
node --check server_static/scene3d.js
python -m pytest tests -q
```

Internal bash/MSYS terminal tool:

```bash
node --check server_static/scene3d.js
PYTHONPATH=. python -m pytest tests -q
```

Deploy:

```bash
git push origin main
git push github main
```
