import * as THREE from "three";

const canvas = document.querySelector("#scene-canvas");
const npcBubble = document.querySelector("#npc-bubble");
const npcLine = document.querySelector("#npc-line");
const historyLog = document.querySelector("#history-log");
const trustBar = document.querySelector("#trust-bar");
const respectBar = document.querySelector("#respect-bar");
const suspicionBar = document.querySelector("#suspicion-bar");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const moodValue = document.querySelector("#mood-value");
const trustValue = document.querySelector("#trust-value");
const tensionValue = document.querySelector("#tension-value");
const routeValue = document.querySelector("#route-value");

const sessionId = `scene3d-${crypto.randomUUID?.() ?? Date.now()}`;
const history = [];
const keys = new Set();
const clock = new THREE.Clock();

const player = {
  position: new THREE.Vector3(0, 1.55, 6.55),
  yaw: 0,
  pitch: -0.05,
  speed: 1.85,
};

const TURN_SPEED = 2.15;

const LIANG_POSITION = new THREE.Vector3(0, 0, -0.85);
const LIANG_BUBBLE_POSITION = new THREE.Vector3(0, 2.35, -0.85);
const TALK_DISTANCE = 7.8;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x130906);
scene.fog = new THREE.FogExp2(0x1b0f0a, 0.045);

const camera = new THREE.PerspectiveCamera(52, window.innerWidth / window.innerHeight, 0.1, 100);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const ambient = new THREE.HemisphereLight(0xffe6bf, 0x20100a, 0.72);
scene.add(ambient);

const keyLight = new THREE.DirectionalLight(0xffd7a2, 1.15);
keyLight.position.set(0.2, 2.6, 4.8);
keyLight.castShadow = true;
scene.add(keyLight);

const rimLight = new THREE.PointLight(0x7fc9a7, 0.85, 7, 1.5);
rimLight.position.set(1.8, 1.8, -1.6);
scene.add(rimLight);

const lanternLight = new THREE.PointLight(0xffb15e, 1.3, 9, 1.8);
lanternLight.position.set(-2.3, 2.6, 1.9);
lanternLight.castShadow = true;
scene.add(lanternLight);

const redLight = new THREE.PointLight(0xb7382d, 0.35, 8, 1.7);
redLight.position.set(2.6, 1.7, 0.3);
scene.add(redLight);

const jadeLight = new THREE.PointLight(0x68b08f, 0.45, 5, 1.6);
jadeLight.position.set(0.2, 0.95, 1.15);
scene.add(jadeLight);

const materials = {
  floor: new THREE.MeshStandardMaterial({ color: 0x21150d, roughness: 0.9, metalness: 0.02 }),
  wall: new THREE.MeshStandardMaterial({ color: 0x382315, roughness: 0.86 }),
  paper: new THREE.MeshStandardMaterial({ color: 0xc9aa72, roughness: 1, emissive: 0x241407, emissiveIntensity: 0.18 }),
  wood: new THREE.MeshStandardMaterial({ color: 0x3a1f12, roughness: 0.78 }),
  jade: new THREE.MeshStandardMaterial({ color: 0x4ca67d, roughness: 0.58, emissive: 0x143226, emissiveIntensity: 0.3 }),
  robe: new THREE.MeshStandardMaterial({ color: 0x3a2720, roughness: 0.82, emissive: 0x0b0604, emissiveIntensity: 0.08 }),
  skin: new THREE.MeshStandardMaterial({ color: 0xb88558, roughness: 0.72 }),
  hair: new THREE.MeshStandardMaterial({ color: 0x0c0908, roughness: 0.75 }),
  gold: new THREE.MeshStandardMaterial({ color: 0xd2a24d, roughness: 0.45, metalness: 0.12 }),
};

function mesh(geometry, material, position, scale = [1, 1, 1]) {
  const object = new THREE.Mesh(geometry, material);
  object.position.set(...position);
  object.scale.set(...scale);
  object.castShadow = true;
  object.receiveShadow = true;
  scene.add(object);
  return object;
}

function createRoom() {
  mesh(new THREE.BoxGeometry(10, 0.16, 11), materials.floor, [0, -0.08, 1]);
  mesh(new THREE.BoxGeometry(10, 4, 0.18), materials.wall, [0, 1.9, -3.2]);
  mesh(new THREE.BoxGeometry(10, 4, 0.18), materials.wall, [0, 1.9, 7.3]);
  mesh(new THREE.BoxGeometry(0.18, 4, 10.5), materials.wall, [-4.7, 1.9, 2.05]);
  mesh(new THREE.BoxGeometry(0.18, 4, 10.5), materials.wall, [4.7, 1.9, 2.05]);

  for (let x = -3; x <= 3; x += 1.5) {
    mesh(new THREE.BoxGeometry(0.8, 1.35, 0.06), materials.paper, [x, 2.05, -3.08]);
    mesh(new THREE.BoxGeometry(0.055, 1.55, 0.09), materials.wood, [x - 0.45, 2.05, -3.02]);
    mesh(new THREE.BoxGeometry(0.055, 1.55, 0.09), materials.wood, [x + 0.45, 2.05, -3.02]);
  }

  mesh(new THREE.BoxGeometry(1.2, 2.35, 0.08), materials.wood, [0, 1.15, 7.18]);
  mesh(new THREE.CylinderGeometry(0.95, 1.05, 0.18, 8), materials.wood, [0, 0.55, 1.2]);
  mesh(new THREE.CylinderGeometry(0.14, 0.18, 0.55, 8), materials.wood, [-0.55, 0.22, 0.75]);
  mesh(new THREE.CylinderGeometry(0.14, 0.18, 0.55, 8), materials.wood, [0.55, 0.22, 0.75]);
  mesh(new THREE.CylinderGeometry(0.14, 0.18, 0.55, 8), materials.wood, [-0.55, 0.22, 1.65]);
  mesh(new THREE.CylinderGeometry(0.14, 0.18, 0.55, 8), materials.wood, [0.55, 0.22, 1.65]);

  mesh(new THREE.CylinderGeometry(0.18, 0.22, 0.18, 12), materials.gold, [-0.32, 0.72, 1.05]);
  mesh(new THREE.TorusGeometry(0.12, 0.012, 6, 12), materials.gold, [-0.32, 0.83, 1.05]);
  mesh(new THREE.BoxGeometry(0.26, 0.04, 0.18), materials.jade, [0.24, 0.68, 1.0]);

  const lantern = mesh(new THREE.CylinderGeometry(0.28, 0.34, 0.6, 8), materials.paper, [-2.3, 2.35, 1.9]);
  lantern.material = lantern.material.clone();
  lantern.material.emissiveIntensity = 0.5;
}

const npc = new THREE.Group();
scene.add(npc);

function addNpcPart(geometry, material, position, scale = [1, 1, 1]) {
  const part = new THREE.Mesh(geometry, material);
  part.position.set(...position);
  part.scale.set(...scale);
  part.castShadow = true;
  part.receiveShadow = true;
  npc.add(part);
  return part;
}

function createMasterLiang() {
  npc.position.copy(LIANG_POSITION);
  addNpcPart(new THREE.CylinderGeometry(0.48, 0.68, 1.2, 9), materials.robe, [0, 0.9, 0]);
  addNpcPart(new THREE.SphereGeometry(0.31, 10, 8), materials.skin, [0, 1.66, 0.02]);
  addNpcPart(new THREE.SphereGeometry(0.33, 10, 8, 0, Math.PI * 2, 0, Math.PI * 0.55), materials.hair, [0, 1.76, 0.0]);
  addNpcPart(new THREE.CylinderGeometry(0.07, 0.08, 0.95, 7), materials.robe, [-0.52, 1.08, 0.1]).rotation.z = 0.7;
  addNpcPart(new THREE.CylinderGeometry(0.07, 0.08, 0.95, 7), materials.robe, [0.52, 1.08, 0.1]).rotation.z = -0.7;
  addNpcPart(new THREE.BoxGeometry(0.9, 0.05, 0.08), materials.gold, [0.0, 1.02, 0.39]);
  addNpcPart(new THREE.CylinderGeometry(0.24, 0.26, 0.13, 12), materials.wood, [-0.9, 0.45, -0.02]);
  addNpcPart(new THREE.CylinderGeometry(0.24, 0.26, 0.13, 12), materials.wood, [0.9, 0.45, -0.02]);
}

function clampPlayerToRoom() {
  player.position.x = THREE.MathUtils.clamp(player.position.x, -4.05, 4.05);
  player.position.z = THREE.MathUtils.clamp(player.position.z, -1.75, 6.85);
}

function updatePlayer(delta) {
  camera.position.copy(player.position);
  camera.rotation.set(player.pitch, player.yaw, 0, "YXZ");

  const forward = new THREE.Vector3();
  camera.getWorldDirection(forward);
  forward.y = 0;
  forward.normalize();

  const movement = new THREE.Vector3();

  if (keys.has("ArrowUp")) movement.add(forward);
  if (keys.has("ArrowDown")) movement.addScaledVector(forward, -1);
  if (keys.has("ArrowLeft")) player.yaw += TURN_SPEED * delta;
  if (keys.has("ArrowRight")) player.yaw -= TURN_SPEED * delta;

  if (movement.lengthSq() > 0) {
    movement.normalize();
    player.position.addScaledVector(movement, player.speed * delta);
    clampPlayerToRoom();
    camera.position.copy(player.position);
  }
}

function distanceToLiang() {
  return player.position.distanceTo(LIANG_POSITION);
}

function canTalk() {
  return distanceToLiang() <= TALK_DISTANCE;
}

function dominantRoute(route_milestones = {}) {
  return Object.entries(route_milestones).sort((a, b) => Number(b[1]) - Number(a[1]))[0]?.[0] ?? "intro";
}

function updateInteractionHint() {
  const close = canTalk();
  document.body.classList.toggle("is-far", !close);
  input.disabled = false;
  document.querySelectorAll(".suggestion").forEach((btn) => { btn.disabled = !close || document.body.classList.contains("is-loading"); });
}

function updateNpcBubble() {
  const projected = LIANG_BUBBLE_POSITION.clone().project(camera);
  const x = THREE.MathUtils.clamp((projected.x * 0.5 + 0.5) * window.innerWidth, 300, window.innerWidth - 300);
  const y = THREE.MathUtils.clamp((-projected.y * 0.5 + 0.5) * window.innerHeight, 120, window.innerHeight - 200);
  const behindCamera = projected.z > 1 || projected.z < -1;

  npcBubble.style.transform = `translate(-50%, -100%) translate(${x}px, ${y}px)`;
  npcBubble.classList.toggle("is-hidden", behindCamera || distanceToLiang() > 9.5);
}

/* ── Conversation history panel ── */

function addHistoryEntry(speaker, text) {
  const emptyMsg = historyLog.querySelector(".history-empty");
  if (emptyMsg) emptyMsg.remove();

  const entry = document.createElement("div");
  entry.className = "history-entry";

  const iconClass = speaker === "player" ? "player" : "npc";
  const speakerName = speaker === "player" ? "You" : "Master Liang";

  entry.innerHTML = `
    <div class="history-icon ${iconClass}"></div>
    <div class="history-content">
      <div class="history-speaker ${iconClass}">${speakerName}</div>
      <div class="history-text">${text}</div>
    </div>
  `;

  historyLog.appendChild(entry);
  entry.scrollIntoView({ behavior: "smooth", block: "end" });
}

/* ── Stat bar updates ── */

function applySceneState(state = {}) {
  const mood = state.mood ?? "wary";
  const trust = Number(state.trust ?? 15);
  const tension = Number(state.tension ?? 35);
  const route = dominantRoute(state.route_milestones);
  const memory_flags = state.memory_flags ?? {};

  moodValue.textContent = mood;
  trustValue.textContent = String(Math.round(trust));
  tensionValue.textContent = String(Math.round(tension));
  routeValue.textContent = route;

  /* Update sidebar stat bars */
  trustBar.style.width = `${Math.min(trust, 100)}%`;
  suspicionBar.style.width = `${Math.min(tension, 100)}%`;
  /* Respect is derived from mood + trust inverse of tension */
  const respect = Math.max(0, Math.min(100, Math.round((trust * 0.6 + (100 - tension) * 0.4))));
  respectBar.style.width = `${respect}%`;

  lanternLight.intensity = 0.85 + trust / 85;
  redLight.intensity = 0.18 + tension / 70;
  jadeLight.intensity = memory_flags.asked_about_seal ? 0.95 : 0.38;

  const waryTurn = mood === "wary" ? 0.22 : 0;
  const openTurn = mood === "open" ? -0.08 : 0;
  const duelTurn = route === "duel" ? 0.34 : 0;
  npc.rotation.y = waryTurn + openTurn + duelTurn;

  if (route === "betrayal") {
    redLight.color.set(0xff3328);
    redLight.intensity = Math.max(redLight.intensity, 1.45);
    scene.fog.color.set(0x170504);
  } else if (route === "duel") {
    redLight.color.set(0xd6422e);
    redLight.intensity = Math.max(redLight.intensity, 1.25);
    scene.fog.color.set(0x120707);
  } else {
    redLight.color.set(0xb7382d);
    scene.fog.color.set(0x1b0f0a);
  }

  camera.fov = route === "duel" || tension > 70 ? 44 : 52 - Math.min(trust, 70) / 22;
  camera.updateProjectionMatrix();
}

function setLoading(isLoading) {
  document.body.classList.toggle("is-loading", isLoading);
}

function updateDialogue(text) {
  npcLine.textContent = text || "Master Liang studies you without speaking.";
}

/* ── Typed speech preview (live bottom text while typing) ── */

function updateTypedSpeechPreview() {
  // Player's typed text only appears in the input field and history panel.
  // NPC bubble stays unchanged while typing.
}

/* ── Send message ── */

async function sendMessage(message) {
  const trimmed = message.trim();
  if (!trimmed) return;

  if (!canTalk()) return;

  setLoading(true);
  addHistoryEntry("player", trimmed);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: trimmed, history }),
    });

    if (!response.ok) {
      throw new Error(`Chat failed: ${response.status}`);
    }

    const data = await response.json();
    const reply = data.response ?? "Master Liang says nothing.";
    history.push({ role: "user", content: trimmed }, { role: "assistant", content: reply });
    updateDialogue(reply);
    addHistoryEntry("npc", reply);
    applySceneState(data.state ?? {});
  } catch (error) {
    console.error(error);
    updateDialogue("The lantern gutters. The teahouse cannot reach Master Liang right now.");
  } finally {
    setLoading(false);
    input.focus();
  }
}

/* ── Input handling ── */

function isTextInputActive() {
  return ["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName ?? "");
}

function shouldTreatAsMovementKey(event) {
  const typing = isTextInputActive();
  if (!typing) return true;
  return event.code.startsWith("Arrow") || event.code === "Escape";
}

function isPrintableTypingKey(event) {
  return event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey;
}

function appendTypedCharacter(character) {
  input.focus();
  input.value = `${input.value}${character}`;
  updateTypedSpeechPreview();
}

window.addEventListener("keydown", (event) => {
  if (!isTextInputActive() && isPrintableTypingKey(event)) {
    event.preventDefault();
    appendTypedCharacter(event.key);
    return;
  }
  if (!shouldTreatAsMovementKey(event)) return;
  if (event.code.startsWith("Arrow")) event.preventDefault();
  if (event.code === "Escape") document.activeElement?.blur?.();
  keys.add(event.code);
});

window.addEventListener("keyup", (event) => keys.delete(event.code));

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = input.value;
  input.value = "";
  sendMessage(message);
});

input.addEventListener("input", updateTypedSpeechPreview);

historyLog.addEventListener("click", (event) => {
  const button = event.target.closest(".suggestion");
  if (!button) return;
  sendMessage(button.dataset.prompt ?? "");
});

document.querySelector("#suggestions").addEventListener("click", (event) => {
  const button = event.target.closest(".suggestion");
  if (!button) return;
  sendMessage(button.dataset.prompt ?? "");
});

/* ── Render loop ── */

function animate(time) {
  const delta = Math.min(clock.getDelta(), 0.05);
  const t = time / 1000;
  updatePlayer(delta);
  updateInteractionHint();
  updateNpcBubble();
  npc.position.y = Math.sin(t * 1.15) * 0.018;
  lanternLight.intensity += Math.sin(t * 4.2) * 0.006;
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

window.__scene3dDebug = {
  getPlayer: () => ({
    x: player.position.x,
    y: player.position.y,
    z: player.position.z,
    yaw: player.yaw,
    pitch: player.pitch,
    canTalk: canTalk(),
    distanceToLiang: distanceToLiang(),
  }),
};

createRoom();
createMasterLiang();
applySceneState({ mood: "wary", trust: 15, tension: 35, route_milestones: {}, memory_flags: {} });
updatePlayer(0);
updateInteractionHint();
updateNpcBubble();
input.focus();
requestAnimationFrame(animate);
