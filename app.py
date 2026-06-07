"""Facade of Jade — Gradio Space app.

Hosts a custom Wuxia-themed chat UI inside a Gradio Blocks container.
The frontend JS talks directly to the Modal backend (bypasses the
Gradio queue because @server.api routes don't reliably register in
Gradio 6.16 on HF Spaces). All CSS and JS are inlined so the Space
is fully self-contained — no external CDN, no asset routing.
"""
import os

import gradio as gr

MODAL_URL = os.environ.get(
    "MODAL_URL",
    "https://t-abdullah-rashid--facade-of-jade-backend-serve.modal.run",
)

INDEX_HTML = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Facade of Jade — A Wuxia Drama</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Serif:ital,wght@0,400;0,700;1,400&display=swap"
    rel="stylesheet"
  />
  <style>
    :root {{
      --paper: #f5ecd7;
      --paper-2: #ebdfc1;
      --walnut: #5a3a22;
      --bark: #2a1a10;
      --ink: #0e0a06;
      --vermilion: #b8392a;
      --vermilion-2: #8a2418;
      --jade: #5a7a3a;
      --gold: #c98a3c;
      --mist: rgba(255, 248, 230, 0.6);
      --line: rgba(42, 26, 16, 0.35);
    }}
    * {{ box-sizing: border-box; }}
    html, body {{
      margin: 0; padding: 0; height: 100%;
      font-family: "Noto Serif", Georgia, serif;
      color: var(--ink);
      background:
        radial-gradient(ellipse at 12% 0%, rgba(184, 57, 42, 0.12), transparent 55%),
        radial-gradient(ellipse at 92% 100%, rgba(90, 122, 58, 0.10), transparent 55%),
        repeating-linear-gradient(0deg, rgba(42, 26, 16, 0.02) 0 1px, transparent 1px 3px),
        var(--paper);
    }}
    #app {{
      min-height: 100vh; max-width: 1200px; margin: 0 auto;
      padding: 28px 24px 24px;
      display: flex; flex-direction: column; gap: 20px;
    }}
    .ink-header {{ text-align: center; padding: 18px 0 8px; border-bottom: 1px dashed var(--line); position: relative; }}
    .ink-header::after {{
      content: "❋ ❋ ❋"; position: absolute; bottom: -10px; left: 50%;
      transform: translateX(-50%); background: var(--paper);
      padding: 0 12px; color: var(--vermilion); font-size: 12px; letter-spacing: 0.6em;
    }}
    .title-stack {{ display: flex; flex-direction: column; align-items: center; gap: 4px; }}
    .title-zh {{
      margin: 0; font-family: "Ma Shan Zheng", "Noto Serif", serif;
      font-size: clamp(40px, 6vw, 64px); color: var(--vermilion-2);
      letter-spacing: 0.05em; line-height: 1;
    }}
    .title-en {{
      margin: 0; font-style: italic; font-size: 18px; color: var(--walnut);
      letter-spacing: 0.18em; text-transform: uppercase;
    }}
    .subtitle {{ margin-top: 8px; font-size: 13px; color: var(--walnut); opacity: 0.85; }}
    .stage {{ flex: 1; display: grid; grid-template-columns: 280px 1fr; gap: 20px; min-height: 0; }}
    @media (max-width: 800px) {{ .stage {{ grid-template-columns: 1fr; }} .npc-panel {{ order: 2; }} }}
    .npc-panel {{
      background: var(--paper-2); border: 2px solid var(--walnut);
      border-radius: 8px; padding: 18px;
      box-shadow: inset 0 0 0 1px var(--paper), inset 0 0 0 5px var(--walnut),
        inset 0 0 0 7px var(--paper), inset 0 0 0 8px var(--gold);
      display: flex; flex-direction: column; gap: 10px;
    }}
    .npc-portrait {{
      width: 100%; aspect-ratio: 1;
      background: linear-gradient(180deg, rgba(184, 57, 42, 0.18), rgba(90, 122, 58, 0.10));
      border: 1px dashed var(--walnut); border-radius: 4px;
      display: flex; align-items: center; justify-content: center;
      font-size: 84px; filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.15));
    }}
    .npc-name {{ margin: 6px 0 0; font-family: "Ma Shan Zheng", serif; font-size: 28px; color: var(--vermilion-2); text-align: center; }}
    .npc-title {{ margin: 0; text-align: center; font-size: 12px; font-style: italic; color: var(--walnut); letter-spacing: 0.08em; }}
    .meters {{ margin-top: 12px; display: flex; flex-direction: column; gap: 10px; font-size: 13px; }}
    .meter {{ display: flex; flex-direction: column; gap: 4px; }}
    .meter-label {{ color: var(--walnut); text-transform: uppercase; letter-spacing: 0.16em; font-size: 10px; }}
    .meter-value {{ color: var(--bark); font-weight: 700; font-size: 14px; }}
    .meter-bar {{ height: 4px; background: rgba(42, 26, 16, 0.1); border-radius: 2px; overflow: hidden; }}
    .meter-fill {{ height: 100%; background: linear-gradient(90deg, var(--vermilion), var(--gold)); transition: width 0.4s ease; }}
    .chat {{
      background: var(--paper-2); border: 2px solid var(--walnut);
      border-radius: 8px;
      box-shadow: inset 0 0 0 1px var(--paper), inset 0 0 0 5px var(--walnut),
        inset 0 0 0 7px var(--paper), inset 0 0 0 8px var(--vermilion);
      display: flex; flex-direction: column; min-height: 480px;
    }}
    .chat-log {{
      flex: 1; padding: 20px; overflow-y: auto;
      display: flex; flex-direction: column; gap: 14px;
      scrollbar-width: thin; scrollbar-color: var(--walnut) transparent;
    }}
    .chat-log::-webkit-scrollbar {{ width: 6px; }}
    .chat-log::-webkit-scrollbar-thumb {{ background: var(--walnut); border-radius: 3px; }}
    .msg {{
      max-width: 78%; padding: 10px 14px; border-radius: 10px;
      line-height: 1.55; font-size: 15px;
      white-space: pre-wrap; word-wrap: break-word; position: relative;
    }}
    .msg.user {{
      align-self: flex-end; background: var(--vermilion); color: var(--paper);
      border: 1px solid var(--vermilion-2); border-bottom-right-radius: 2px;
    }}
    .msg.npc {{
      align-self: flex-start; background: var(--paper); color: var(--bark);
      border: 1px solid var(--walnut); border-bottom-left-radius: 2px;
      font-style: italic;
    }}
    .msg.system {{
      align-self: center; background: transparent; color: var(--walnut);
      font-size: 12px; font-style: italic;
      border: 1px dashed var(--line); border-radius: 0; padding: 4px 10px;
    }}
    .msg.npc.streaming::after {{
      content: "▍"; display: inline-block; margin-left: 2px;
      color: var(--vermilion); animation: blink 0.9s steps(2) infinite;
    }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    .composer {{
      display: flex; gap: 8px; padding: 14px;
      border-top: 1px dashed var(--line);
      background: rgba(245, 236, 215, 0.6);
      border-bottom-left-radius: 6px; border-bottom-right-radius: 6px;
    }}
    #input {{
      flex: 1; padding: 10px 12px; background: var(--paper);
      border: 1px solid var(--walnut); border-radius: 4px;
      font-family: inherit; font-size: 15px; color: var(--bark);
    }}
    #input:focus {{
      outline: none; border-color: var(--vermilion);
      box-shadow: 0 0 0 2px rgba(184, 57, 42, 0.2);
    }}
    #send-btn {{
      padding: 10px 18px; background: var(--vermilion-2); color: var(--paper);
      border: 1px solid var(--vermilion-2); border-radius: 4px;
      font-family: inherit; font-size: 14px; font-weight: 700;
      letter-spacing: 0.1em; text-transform: uppercase; cursor: pointer;
      transition: background 0.15s ease;
    }}
    #send-btn:hover:not(:disabled) {{ background: var(--vermilion); }}
    #send-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}
    .ink-footer {{
      text-align: center; font-size: 11px; color: var(--walnut);
      opacity: 0.7; padding: 8px 0 0; border-top: 1px dashed var(--line);
    }}
  </style>
</head>
<body data-modal-url="{MODAL_URL}">
  <main id="app">
    <header class="ink-header">
      <div class="title-stack">
        <h1 class="title-zh">玉面樓</h1>
        <h2 class="title-en">Facade of Jade</h2>
      </div>
      <div class="subtitle">An interactive Wuxia drama · Qwen3-4B on llama.cpp</div>
    </header>

    <section class="stage">
      <aside class="npc-panel">
        <div class="npc-portrait" aria-hidden="true">🗡</div>
        <h3 class="npc-name" id="npc-name">Shen Wuqing</h3>
        <p class="npc-title" id="npc-title">The Swordsman of No Emotion</p>
        <div class="meters">
          <div class="meter">
            <span class="meter-label">Mood</span>
            <span class="meter-value" id="mood-value">wary</span>
            <div class="meter-bar"><div class="meter-fill" id="mood-bar" style="width:30%"></div></div>
          </div>
          <div class="meter">
            <span class="meter-label">Trust</span>
            <span class="meter-value" id="trust-value">0</span>
            <div class="meter-bar"><div class="meter-fill" id="trust-bar" style="width:0%"></div></div>
          </div>
          <div class="meter">
            <span class="meter-label">Beat</span>
            <span class="meter-value" id="beat-value">intro</span>
          </div>
        </div>
      </aside>

      <section class="chat">
        <div class="chat-log" id="chat-log" aria-live="polite"></div>
        <form class="composer" id="composer">
          <input type="text" id="input" name="message"
                 placeholder="Speak to the swordsman..."
                 autocomplete="off" autofocus required />
          <button type="submit" id="send-btn">Send</button>
        </form>
      </section>
    </section>

    <footer class="ink-footer">
      <span>Built for the Build Small Hackathon · Track 2: An Adventure in Thousand Token Wood</span>
    </footer>
  </main>

  <script>
    const $ = (id) => document.getElementById(id);
    const log = $("chat-log");
    const form = $("composer");
    const input = $("input");
    const sendBtn = $("send-btn");
    const MODAL_URL = document.body.dataset.modalUrl;

    const messages = [];
    const npcState = { mood: "wary", trust: 0, current_beat: "intro", mood_score: 30 };

    function addMessage(role, content) {{
      const el = document.createElement("div");
      el.className = `msg ${{role}}`;
      el.textContent = content;
      log.appendChild(el);
      log.scrollTop = log.scrollHeight;
      return el;
    }}

    function updateMeters(s) {{
      $("mood-value").textContent = s.mood ?? "wary";
      $("trust-value").textContent = String(s.trust ?? 0);
      $("beat-value").textContent = s.current_beat ?? "intro";
      const moodPct = Math.max(0, Math.min(100, (s.mood_score ?? 30)));
      $("mood-bar").style.width = `${{moodPct}}%`;
      const trustPct = Math.max(0, Math.min(100, ((s.trust ?? 0) + 5) * 10));
      $("trust-bar").style.width = `${{trustPct}}%`;
    }}

    async function callBackend(messages, state) {{
      const r = await fetch(`${{MODAL_URL}}/chat`, {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ messages, state }}),
      }});
      if (!r.ok || !r.body) throw new Error(`chat ${{r.status}}`);
      const reader = r.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      let final = "";
      while (true) {{
        const {{ value, done }} = await reader.read();
        if (done) break;
        buf += decoder.decode(value, {{ stream: true }});
        const lines = buf.split("\\n");
        buf = lines.pop() ?? "";
        for (const line of lines) {{
          const m = line.match(/^data: (.*)$/);
          if (!m) continue;
          if (m[1] === "[DONE]") return final;
          try {{
            const obj = JSON.parse(m[1]);
            if (obj.token) final += obj.token;
          }} catch (e) {{}}
        }}
      }}
      return final;
    }}

    async function sendNpcTurn(isFirst) {{
      sendBtn.disabled = true;
      input.disabled = true;
      const placeholder = addMessage("npc", "");
      placeholder.classList.add("streaming");

      try {{
        const reply = await callBackend(isFirst ? [] : messages, npcState);
        placeholder.classList.remove("streaming");
        placeholder.textContent = reply;
        if (!isFirst && reply) messages.push({{ role: "assistant", content: reply }});

        // Crude beat inference from the reply, so the UI feels alive
        const lower = reply.toLowerCase();
        if (/(drink|tea|rest)/.test(lower)) npcState.current_beat = "offer_drink";
        else if (/(what do you|why have you|trouble|problem)/.test(lower)) npcState.current_beat = "ask_problem";
        else if (/(leave|go|farewell)/.test(lower)) npcState.current_beat = "farewell";
        // Crude trust heuristic
        if (/(please|thank|i beg|honor|swear)/.test(reply.toLowerCase())) npcState.trust = Math.min(5, (npcState.trust || 0) + 1);
        if (/(liar|fool|insult|shame)/.test(reply.toLowerCase())) npcState.trust = Math.max(-5, (npcState.trust || 0) - 1);
        updateMeters(npcState);
      }} catch (e) {{
        placeholder.classList.remove("streaming");
        placeholder.textContent = `[error: ${{e.message}}]`;
      }} finally {{
        sendBtn.disabled = false;
        input.disabled = false;
        input.focus();
      }}
    }}

    form.addEventListener("submit", async (e) => {{
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      input.value = "";
      addMessage("user", text);
      messages.push({{ role: "user", content: text }});
      await sendNpcTurn(false);
    }});

    addMessage("system", "A swordsman sits across from you, his hand resting on the hilt of his blade. The teahouse is quiet. The rain has stopped.");
    updateMeters(npcState);
    sendNpcTurn(true);
  </script>
</body>
</html>
"""


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="Facade of Jade", theme=gr.themes.Soft()) as demo:
        gr.HTML(value=INDEX_HTML, sanitize_html=False)
    return demo


demo = build_demo()


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
