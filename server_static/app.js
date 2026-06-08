const messagesEl = document.querySelector('#messages');
const form = document.querySelector('#chat-form');
const input = document.querySelector('#player-input');
const statusEl = document.querySelector('#status');
const sendButton = document.querySelector('#send-button');
const resetButton = document.querySelector('#reset-button');

let sessionId = localStorage.getItem('foj-session-id') || crypto.randomUUID();
localStorage.setItem('foj-session-id', sessionId);
let history = [];

function addMessage(role, text, record = true) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  if (record) history.push({ role: role === 'user' ? 'user' : 'assistant', content: text });
  return div;
}

function updateState(state) {
  document.querySelector('#beat').textContent = prettify(state.beat || 'intro');
  document.querySelector('#turns').textContent = state.turns ?? 0;
  document.querySelector('#mood').textContent = state.mood || 'wary';
  document.querySelector('#mood-shift').textContent = `${state.previous_mood || state.mood} → ${state.mood}`;
  document.querySelector('#trust').textContent = state.trust ?? 0;
  document.querySelector('#last-act').textContent = prettify(state.last_act || 'none');
  document.querySelector('#hot-button').textContent = prettify(state.hot_button || 'none');
  document.querySelector('#beat-goal').textContent = state.beat_goal || 'Main beat continues';
  document.querySelector('#mix-in').textContent = state.mix_in || 'Main beat continues';
  setMeter('#social-affinity', state.affinity ?? 0);
  setMeter('#social-realization', state.self_realization ?? 0);
  setMeter('#social-tension', state.tension ?? 35);
  const delta = Number(state.trust_delta || 0);
  const deltaEl = document.querySelector('#trust-delta');
  deltaEl.textContent = `${delta >= 0 ? '+' : ''}${delta}`;
  deltaEl.classList.toggle('negative', delta < 0);
  document.querySelector('#trust-meter').style.width = `${Math.max(0, Math.min(100, state.trust || 0))}%`;
  const pressure = state.path_pressure || {};
  setMeter('#path-revelation', pressure.revelation ?? 0);
  setMeter('#path-alliance', pressure.alliance ?? 0);
  setMeter('#path-duel', pressure.duel ?? 0);
  setMeter('#path-betrayal', pressure.betrayal ?? 0);
}

function setMeter(selector, value) {
  const el = document.querySelector(selector);
  if (el) el.value = Math.max(0, Math.min(100, Number(value || 0)));
}

function prettify(value) {
  return String(value).replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
}

async function sendMessage(text) {
  if (!text.trim()) return;
  addMessage('user', text.trim());
  input.value = '';
  sendButton.disabled = true;
  statusEl.textContent = 'Master Liang is weighing your words...';
  const assistantEl = addMessage('assistant', '', false);
  let responseText = '';
  try {
    const res = await fetch('/api/chat_stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message: text, history: history.slice(-10) })
    });
    if (!res.ok || !res.body) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || res.statusText);
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (!line.trim()) continue;
        const event = JSON.parse(line);
        if (event.type === 'state') {
          sessionId = event.session_id || sessionId;
          localStorage.setItem('foj-session-id', sessionId);
          updateState(event.state);
        } else if (event.type === 'token') {
          responseText += event.token || '';
          assistantEl.textContent = responseText;
          messagesEl.scrollTop = messagesEl.scrollHeight;
        } else if (event.type === 'done') {
          sessionId = event.session_id || sessionId;
          localStorage.setItem('foj-session-id', sessionId);
          responseText = event.response || responseText;
          assistantEl.textContent = responseText || '(silence)';
          updateState(event.state);
          history.push({ role: 'assistant', content: assistantEl.textContent });
          statusEl.textContent = event.state?.game_over ? 'The story has ended.' : 'Ready.';
        }
      }
    }
  } catch (err) {
    assistantEl.textContent = `The teahouse falls silent. ${err.message}`;
    history.push({ role: 'assistant', content: assistantEl.textContent });
    statusEl.textContent = 'Error.';
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  sendMessage(input.value);
});

document.querySelectorAll('[data-prompt]').forEach((button) => {
  button.addEventListener('click', () => sendMessage(button.dataset.prompt));
});

resetButton.addEventListener('click', async () => {
  sessionId = crypto.randomUUID();
  localStorage.setItem('foj-session-id', sessionId);
  history = [];
  messagesEl.innerHTML = '<div class="message assistant">The tea has cooled, yet you remain. Speak carefully.</div>';
  statusEl.textContent = 'Reset.';
  try {
    const res = await fetch('/api/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId })
    });
    const data = await res.json();
    updateState(data.state);
  } catch (_) {
    // UI reset is enough for a spike.
  }
});

fetch(`/api/state?session_id=${encodeURIComponent(sessionId)}`)
  .then(res => res.json())
  .then(data => updateState(data.state))
  .catch(() => {});
