const messagesEl = document.querySelector('#messages');
const form = document.querySelector('#chat-form');
const input = document.querySelector('#player-input');
const statusEl = document.querySelector('#status');
const sendButton = document.querySelector('#send-button');
const resetButton = document.querySelector('#reset-button');

let sessionId = localStorage.getItem('foj-session-id') || crypto.randomUUID();
localStorage.setItem('foj-session-id', sessionId);
let history = [];

function addMessage(role, text) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  history.push({ role: role === 'user' ? 'user' : 'assistant', content: text });
}

function updateState(state) {
  document.querySelector('#beat').textContent = prettify(state.beat || 'intro');
  document.querySelector('#turns').textContent = state.turns ?? 0;
  document.querySelector('#mood').textContent = state.mood || 'wary';
  document.querySelector('#mood-shift').textContent = `${state.previous_mood || state.mood} → ${state.mood}`;
  document.querySelector('#trust').textContent = state.trust ?? 0;
  document.querySelector('#last-act').textContent = prettify(state.last_act || 'none');
  const delta = Number(state.trust_delta || 0);
  const deltaEl = document.querySelector('#trust-delta');
  deltaEl.textContent = `${delta >= 0 ? '+' : ''}${delta}`;
  deltaEl.classList.toggle('negative', delta < 0);
  document.querySelector('#trust-meter').style.width = `${Math.max(0, Math.min(100, state.trust || 0))}%`;
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
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message: text, history: history.slice(-10) })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || res.statusText);
    sessionId = data.session_id;
    localStorage.setItem('foj-session-id', sessionId);
    addMessage('assistant', data.response || '(silence)');
    updateState(data.state);
    statusEl.textContent = data.state?.game_over ? 'The story has ended.' : 'Ready.';
  } catch (err) {
    addMessage('assistant', `The teahouse falls silent. ${err.message}`);
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
