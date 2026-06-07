// Facade of Jade — frontend chat logic
// Uses the native fetch + ReadableStream to consume the Gradio /chat
// generator (which proxies a Modal SSE stream and yields cumulative text).

const $ = (id) => document.getElementById(id);
const log = $("chat-log");
const form = $("composer");
const input = $("input");
const sendBtn = $("send-btn");

const messages = []; // { role, content }
let npcState = {
  mood: "wary",
  trust: 0,
  current_beat: "intro",
};

function addMessage(role, content) {
  const el = document.createElement("div");
  el.className = `msg ${role}`;
  el.textContent = content;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
  return el;
}

function updateMeters(state) {
  $("mood-value").textContent = state.mood ?? "wary";
  $("trust-value").textContent = String(state.trust ?? 0);
  $("beat-value").textContent = state.current_beat ?? "intro";
  const moodPct = Math.max(0, Math.min(100, (state.mood_score ?? 30)));
  $("mood-bar").style.width = `${moodPct}%`;
  const trustPct = Math.max(0, Math.min(100, ((state.trust ?? 0) + 5) * 10));
  $("trust-bar").style.width = `${trustPct}%`;
}

async function loadInitialState() {
  try {
    const r = await fetch("/gradio_api/npc_state");
    if (!r.ok) throw new Error("state fetch failed");
    npcState = await r.json();
    updateMeters(npcState);
  } catch (e) {
    addMessage("system", `Could not load NPC state: ${e.message}`);
  }
}

async function bootstrap() {
  addMessage(
    "system",
    "A swordsman sits across from you, his hand resting on the hilt of his blade. The teahouse is quiet. The rain has stopped.",
  );
  await loadInitialState();
  // First NPC line — a greeting in character
  await sendNpcTurn(true);
}

async function sendNpcTurn(isFirst = false) {
  sendBtn.disabled = true;
  input.disabled = true;
  const placeholder = addMessage("npc", "");
  placeholder.classList.add("streaming");

  try {
    const body = {
      messages: isFirst ? [] : messages,
      state: npcState,
    };
    const r = await fetch("/gradio_api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!r.ok || !r.body) throw new Error(`chat ${r.status}`);

    const reader = r.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    let final = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      // The /chat endpoint yields cumulative text snapshots. Each newline is
      // a full snapshot. Render the last complete line.
      const lines = buf.split("\n");
      buf = lines.pop() ?? "";
      for (const line of lines) {
        if (line.trim()) final = line;
      }
      placeholder.textContent = final;
      log.scrollTop = log.scrollHeight;
    }
    placeholder.classList.remove("streaming");
    if (final && !isFirst) messages.push({ role: "assistant", content: final });
  } catch (e) {
    placeholder.classList.remove("streaming");
    placeholder.textContent = `[error: ${e.message}]`;
  } finally {
    sendBtn.disabled = false;
    input.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  addMessage("user", text);
  messages.push({ role: "user", content: text });
  await sendNpcTurn(false);
});

bootstrap();
