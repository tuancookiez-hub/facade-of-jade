# Handoff — Facade of Jade (Voice Pipeline)

## Goal
Add voice to Master Liang so he speaks his dialogue aloud after each response. Focus on TTS (text-to-speech) only for now. ASR (speech-to-text / mic input) is deprioritized.

## Current State
- **TTS endpoint**: VoxCPM2 deployed on Modal (A10G GPU), live and healthy
  - URL: `https://t-abdullah-rashid--facade-of-jade-tts-serve.modal.run`
  - Cold start: **eliminated** for active use via `min_containers=1` + 5-min warmup pings
  - Warm latency (verified 2026-06-12): **4-5s** per request on A10G (the prior handoff's 3-4s was optimistic)
  - Warmup pings themselves take 2-3s (short "Hm." prompt)
  - Returns 48kHz WAV audio
- **ASR endpoint**: Nemotron 3 ASR also deployed on Modal (separate endpoint)
  - URL: `https://t-abdullah-rashid--facade-of-jade-asr-serve.modal.run`
  - Working but NOT wired to frontend (ASR deprioritized)
- **Frontend**: TTS auto-plays after each Liang response with 🔊 loading indicator
  - Warmup ping on page load + every 5 min — now actually reaches Modal (was a no-op, see pitfalls)
- **Backend**: `/api/tts` proxies to Modal VoxCPM2, `/api/asr` proxies to Modal Nemotron
- **Tests**: 30/30 passing (added 2 warmup regression tests)
- **Deployed**: Live on HF Spaces `https://build-small-hackathon-facade-of-jade.hf.space`

## Files in Flight
- `modal_tts.py` — Modal deployment for VoxCPM2 TTS (now with `min_containers=1`)
- `modal_asr.py` — Modal deployment for Nemotron ASR
- `server_app.py` — HF Space backend, `/api/tts` (warmup now actually calls Modal), `/api/asr` endpoints
- `server_static/scene3d.js` — Frontend TTS playback + warmup pings
- `server_static/scene3d.html` — UI (mic button removed)

## Changed This Session (2026-06-12)
- **Fixed warmup no-op bug**: `server_app.py` warmup branch now actually POSTs to Modal with "Hm." prompt (was returning early without contacting Modal). Two regression tests added.
- **Reordered warmup check** to run before the `text` required check, so warmup-only payloads work.
- **Added `min_containers=1`** to `modal_tts.py` so Modal keeps at least one VoxCPM2 container warm at all times. Renamed from `keep_warm` per Modal 1.0 deprecation.
- **Deployed modal_tts.py** to Modal; **pushed server_app.py + tests** to GitHub + HF Space.
- **Simplified frontend warmup** to send only `{warmup: true}` (no more `text: "."` placeholder).

## Key Decisions
- **TTS-only for now** — ASR/mic input deprioritized to focus on making Liang speak
- **Modal over free APIs** — VoxCPM2 has no free hosted API; Modal gives reliable, controllable infrastructure
- **Two-layer keep-warm** — `min_containers=1` is the primary defense (always one warm container); 5-min frontend pings are belt-and-suspenders (also keep `scaledown_window=600` happy)
- **Pre-recorded vs TTS** — Original Façade used 8,524 pre-recorded WAVs with human voice actors. For our generative AI game, TTS is the only practical approach.

## Pitfalls Learned
- **Warmup was a no-op** — the original `if payload.get("warmup"): return JSONResponse(...)` short-circuited without ever calling Modal, so the 5-min frontend pings never kept VoxCPM2 warm. The cold-start problem was *not actually mitigated* by that commit. Fixed in this session.
- **Warmup check ordering** — placing the `text` required check *before* the `warmup` check made warmup-only payloads return 400. Always check `warmup` first.
- **VoxCPM2 `from_pretrained()` with `local_dir` causes volume mount conflicts on Modal** — must use `snapshot_download` or load from HF Hub directly
- **Nemotron ASR returns `Hypothesis` objects, not plain strings** — need `.text` or `str()` extraction
- **Modal returns 303 redirects during cold start** — `follow_redirects=True` required in httpx
- **Base64 encoding adds ~33% overhead to audio transfer** — acceptable for hackathon demo
- **`keep_warm` deprecated in Modal 1.0** — renamed to `min_containers`. Modal still accepts the old name with a deprecation warning, but new code should use `min_containers=N`.

## Verified Latency (2026-06-12)
| Step | Time |
|---|---|
| Warmup ping (server → Modal → server) | 2-3s |
| TTS request (server → Modal → server) | 4-5s |
| LLM chat (server → Modal LLM → server) | ~15s |
| Full turn (LLM + TTS) | ~20s |
| First TTS after Modal container restart | 8-12s (one-time ramp-up) |

## Next Steps (Priority Order)
1. **A100 GPU** — Would cut warm TTS from 4-5s to ~2-3s. A100 is ~3x A10G cost (~$3/hr vs ~$1/hr) on Modal. The "performance is permanent" heuristic argues for it, but hackathon budget says wait. **Mitigates** but not **fixes** the full-turn latency — LLM (15s) is now the bottleneck.
2. **ASR (future)** — Re-add mic button when ASR latency is acceptable
3. **Voice quality** — Test VoxCPM2 with different voice descriptions for better Liang character match
4. **Lip-sync / visual feedback** — While TTS generates, show Liang "preparing to speak" animation (some indication beyond the 🔊 emoji)
5. **Cache common greetings** — Limited upside since Liang's responses are LLM-generated and not predictable. Skip unless hit-rate data shows otherwise.

## Config Verification
- [x] Modal TTS endpoint healthy, `min_containers=1` active
- [x] HF Space env vars: `VOXCPM_API_URL` and `ASR_API_URL` set correctly
- [x] Frontend warmup ping reaches Modal end-to-end (verified 2026-06-12, ~2-3s)
- [x] Warmup regression tests pass (`test_tts_warmup_actually_calls_modal`, `test_tts_warmup_silently_swallows_modal_errors`)

## Prize Stack Status
- ✅ NVIDIA (Nemotron ASR deployed)
- ✅ OpenBMB (VoxCPM2 TTS deployed)
- ✅ Modal (all three models: LLM + TTS + ASR)
- ✅ Well-Tuned (LoRA on Qwen3-4B)
- ✅ Off-Brand (custom gr.Server UI)
