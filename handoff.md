# Handoff — Facade of Jade (Voice Pipeline)

## Goal
Add voice to Master Liang so he speaks his dialogue aloud after each response. Focus on TTS (text-to-speech) only for now. ASR (speech-to-text / mic input) is deprioritized.

## Current State
- **TTS endpoint**: VoxCPM2 deployed on Modal (A10G GPU), live and healthy
  - URL: `https://t-abdullah-rashid--facade-of-jade-tts-serve.modal.run`
  - Cold start: ~2-3 min, warm: ~3-4s per request
  - Returns 48kHz WAV audio
- **ASR endpoint**: Nemotron 3 ASR also deployed on Modal (separate endpoint)
  - URL: `https://t-abdullah-rashid--facade-of-jade-asr-serve.modal.run`
  - Working but NOT wired to frontend (ASR deprioritized)
- **Frontend**: TTS auto-plays after each Liang response with 🔊 loading indicator
  - Warmup ping on page load + every 5 min to prevent Modal cold starts
  - Mic button and all ASR code removed from UI
- **Backend**: `/api/tts` proxies to Modal VoxCPM2, `/api/asr` proxies to Modal Nemotron
- **Tests**: All 28 tests passing
- **Deployed**: Live on HF Spaces `https://build-small-hackathon-facade-of-jade.hf.space`

## Files in Flight
- `modal_tts.py` — Modal deployment for VoxCPM2 TTS
- `modal_asr.py` — Modal deployment for Nemotron ASR
- `server_app.py` — HF Space backend, `/api/tts` and `/api/asr` endpoints
- `server_static/scene3d.js` — Frontend TTS playback + warmup pings
- `server_static/scene3d.html` — UI (mic button removed)

## Changed This Session
- Created `modal_tts.py` with VoxCPM2 on Modal A10G
- Created `modal_asr.py` with Nemotron 3 ASR on Modal A10G
- Wired `/api/tts` and `/api/asr` in `server_app.py`
- Added `speakWithTTS()` to frontend with 🔊 indicator
- Added warmup pings every 5 min to prevent cold starts
- Removed all mic/ASR code from frontend
- Committed and deployed to HF Spaces + GitHub

## Key Decisions
- **TTS-only for now** — ASR/mic input deprioritized to focus on making Liang speak
- **Modal over free APIs** — VoxCPM2 has no free hosted API; Modal gives reliable, controllable infrastructure
- **Warmup pings** — Simple keep-alive to avoid 2-3 min cold starts during gameplay
- **Pre-recorded vs TTS** — Original Façade used 8,524 pre-recorded WAVs with human voice actors. For our generative AI game, TTS is the only practical approach.

## Pitfalls Learned
- VoxCPM2 `from_pretrained()` with `local_dir` causes volume mount conflicts on Modal — must use `snapshot_download` or load from HF Hub directly
- Nemotron ASR returns `Hypothesis` objects, not plain strings — need `.text` or `str()` extraction
- Modal returns 303 redirects during cold start — `follow_redirects=True` required in httpx
- Base64 encoding adds ~33% overhead to audio transfer — acceptable for hackathon demo

## Next Steps (Priority Order)
1. **Speed up TTS** — Currently 3-4s warm, investigate:
   - Modal `keep_warm` or cron job to ping every 5 min
   - Switch to A100 GPU for faster inference (costs more)
   - Cache common greetings ("Welcome, traveler", etc.) as pre-generated WAVs
2. **Add lip-sync / visual feedback** — While TTS generates, show Liang "preparing to speak" animation
3. **ASR (future)** — Re-add mic button when ASR latency is acceptable
4. **Voice quality** — Test VoxCPM2 with different voice descriptions for better Liang character match

## Config Verification
- [ ] Modal endpoints healthy: `curl /healthz` on both TTS and ASR
- [ ] HF Space env vars: `VOXCPM_API_URL` and `ASR_API_URL` set correctly
- [ ] Frontend warmup ping working (check browser Network tab)

## Prize Stack Status
- ✅ NVIDIA (Nemotron ASR deployed)
- ✅ OpenBMB (VoxCPM2 TTS deployed)
- ✅ Modal (all three models: LLM + TTS + ASR)
- ✅ Well-Tuned (LoRA on Qwen3-4B)
- ✅ Off-Brand (custom gr.Server UI)
