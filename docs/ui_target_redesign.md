# UI Target Redesign — Ink-Wash Drama Interface

Target reference: screenshot provided on 2026-06-08 showing an art-directed Facade of Jade UI with parchment background, ink-wash scene, three-column composition, status sidebar, and bottom action cards.

## Goal

Move the production custom `gr.Server` UI from a dark card-based prototype into a polished narrative game interface suitable for hackathon judging.

The backend stays unchanged. This is a frontend-only pass over:

- `server_static/index.html`
- `server_static/style.css`
- `server_static/app.js`
- optionally `server_static/assets/*`

## Core design direction

Mood: ink-wash wuxia drama, parchment, sepia, muted jade, moonlight, teahouse, restrained UI chrome.

The current UI already has the right mechanics. The target UI makes those mechanics feel like a real game.

## Layout

Use a desktop-first three-zone layout:

1. **Left identity column**
   - square Liang logo mark
   - small subtitle: `A TINY TITAN DRAMA ENGINE`
   - large stacked `FACADE OF JADE` title
   - short scene-setting copy

2. **Center stage column**
   - large ink-wash visual panel
   - moon / tree / pagoda / Master Liang silhouette
   - current highlighted Master Liang quote
   - compact scrollable dialogue log
   - input field: `What do you say or do?`
   - hint row

3. **Right status column**
   - `STATUS`
   - turn
   - mood with dot
   - trust with progress bar
   - last act
   - hot button / beat goal / mix-in can sit behind `View Insights` or under an expanded section
   - path pressure bars
   - short explanatory footer

4. **Bottom action row**
   - four large action cards:
     - Respect
     - Question
     - Provoke
     - Challenge
   - icon, title, mechanical description, arrow

## Palette

Recommended CSS variables:

```css
:root {
  --paper: #e8dfd2;
  --paper-deep: #d4c8b8;
  --ink: #231d14;
  --ink-soft: #5f5445;
  --line: rgba(55, 45, 31, 0.22);
  --gold: #a98c5f;
  --jade: #6f8a75;
  --danger: #8f4f3f;
  --moon: #f4ead6;
  --panel: rgba(238, 229, 214, 0.72);
}
```

## Typography

Use web-safe fallback first, optionally Google Fonts if network is acceptable.

Recommended:

- Display: `Cormorant Garamond`, `Playfair Display`, Georgia, serif
- Body: `Crimson Text`, Georgia, serif
- UI labels: system sans or small-caps serif with letter spacing

## Artwork strategy

Fastest route: CSS-generated ink-wash scene.

Do not block on image generation. We can create the scene with CSS layers:

- radial moon
- blurred mountain silhouettes
- pagoda block with roof triangles
- lantern glow
- tree silhouette
- Master Liang silhouette
- paper grain overlay
- vignette

Later improvement: replace the CSS scene with a generated/painted image asset once the layout is approved.

## Component mapping from current UI

Current production IDs should be preserved where possible so `app.js` needs minimal change:

- `#messages` remains dialogue log
- `#chat-form` remains form
- `#player-input` remains input
- `#send-button` remains submit
- `#reset-button` remains reset
- `#beat`, `#turns`, `#mood`, `#trust`, `#last-act` remain status fields
- `#path-revelation`, `#path-alliance`, `#path-duel`, `#path-betrayal` remain path meters

New display elements:

- `#current-quote` mirrors latest assistant line
- `#mood-dot` semantic dot class based on mood
- `#insights-panel` contains hot button, beat goal, mix-in, social games

## Implementation phases

### Phase 1 — production-safe visual rewrite

- Replace HTML structure with target layout while preserving JS IDs.
- Replace CSS with parchment/ink-wash design.
- Keep all API and drama-manager behavior unchanged.
- Use CSS-generated artwork.
- Test locally and in browser.

### Phase 2 — richer interactions

- `View Insights` expands/collapses beat goal, mix-in, hot button, social games.
- Action cards show mechanical descriptions.
- Latest assistant response becomes large center quote.
- Dialogue log remains contained and scrollable.

### Phase 3 — art asset polish

- Generate or add a real ink-wash background asset.
- Keep CSS fallback.
- Optimize image size for HF Spaces.

## Acceptance criteria

- Looks closer to the reference than the current dark-card UI.
- No backend changes.
- Chat streaming still works.
- Dialogue panel stays scrollable and does not push input off-screen.
- Status sidebar remains readable at 1440px width.
- Mobile/tablet degrades gracefully into stacked panels.
- Tests still pass:

```powershell
python -m py_compile server_app.py app.py beats.py
python beats.py
python -m pytest tests -q
```

## Recommendation

Implement Phase 1 + Phase 2 immediately. Do not wait for perfect artwork. A CSS-generated ink-wash stage will already be a major upgrade and keeps deployment risk low.
