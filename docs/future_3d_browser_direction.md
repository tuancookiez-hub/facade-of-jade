# Future 3D Browser Direction

Facade of Jade does **not** need high-end 3D to move toward the original *Façade* inspiration.

The intended future direction is a lightweight, browser-playable, low-fidelity 3D conversation scene:

- closer to old Flash / early browser games / low-poly PC games than modern AAA
- first-person camera seated across from Master Liang
- simple teahouse room
- idle character pose and a few state-driven expression/posture changes
- dialogue/actions still powered by the existing drama manager and Modal LLM backend
- no heavy graphics ambition until the story loop is stronger

Reference noted by Tuan: Hugging Face Space `inventwithdean/Rizz-Therapy` appears to use a Unity/WebGL-style build layout with `Build/`, `characters/`, and frontend files. This suggests a future browser-3D path could be viable without replacing the current backend:

1. Keep `server_app.py` and `/api/chat` / `/api/chat_stream` as the game backend.
2. Replace or augment `server_static/` with a lightweight WebGL/Unity/Three.js client.
3. Drive character state from existing fields: mood, trust, tension, current beat, hot-button, and memory flags.
4. Start with a tiny proof of concept: static room, seated NPC, text box, four actions, one mood-driven posture change.

Do not start this before the Story Spine / drama core is stable. A weak drama loop in 3D is still weak; the 3D layer should embody stronger story state, not compensate for missing core design.
