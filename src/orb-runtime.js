const eventLog = [];
const root = document.querySelector('#orb-root');
const orb = document.querySelector('#orb-body');
const status = document.querySelector('#orb-status');
const speech = document.querySelector('#orb-speech-bubble');
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
let position = { x: innerWidth * 0.72, y: innerHeight * 0.48 };
let targetPosition = { ...position };
let moveFrame;
let lastTargetId = null;

function record(type, detail = {}) {
  const event = { type, detail, at: new Date().toISOString() };
  eventLog.push(event);
  window.dispatchEvent(new CustomEvent(`orbweaver:${type}`, { detail: event }));
  return event;
}

function setStatus(message, active = false) {
  status.textContent = message;
  status.classList.toggle('is-active', active);
}

function safeRect(rect, margin = 92) {
  return { left: rect.left - margin, right: rect.right + margin, top: rect.top - margin, bottom: rect.bottom + margin };
}

function isBlocked(x, y) {
  const rects = [...document.querySelectorAll('[data-orb-obstacle]')].map((node) => safeRect(node.getBoundingClientRect()));
  const radius = 42;
  return rects.some((rect) => x + radius > rect.left && x - radius < rect.right && y + radius > rect.top && y - radius < rect.bottom);
}

function chooseSafePosition(preferred = position) {
  const candidates = [];
  const columns = 6;
  const rows = 5;
  for (let row = 1; row < rows; row += 1) {
    for (let column = 1; column < columns; column += 1) {
      candidates.push({ x: (innerWidth / columns) * column, y: (innerHeight / rows) * row });
    }
  }
  candidates.sort((a, b) => Math.hypot(a.x - preferred.x, a.y - preferred.y) - Math.hypot(b.x - preferred.x, b.y - preferred.y));
  return candidates.find((point) => !isBlocked(point.x, point.y)) || { x: innerWidth * .8, y: innerHeight * .55 };
}

function render() {
  position.x += (targetPosition.x - position.x) * 0.045;
  position.y += (targetPosition.y - position.y) * 0.045;
  root.style.setProperty('--orb-x', `${position.x}px`);
  root.style.setProperty('--orb-y', `${position.y}px`);
  root.style.setProperty('--bubble-x', `${position.x}px`);
  root.style.setProperty('--bubble-y', `${position.y}px`);
  moveFrame = requestAnimationFrame(render);
}

function moveTo(next, reason = 'ambient') {
  const safe = isBlocked(next.x, next.y) ? chooseSafePosition(next) : next;
  targetPosition = { x: Math.max(50, Math.min(innerWidth - 50, safe.x)), y: Math.max(110, Math.min(innerHeight - 80, safe.y)) };
  record('orb_moved', { reason, target: targetPosition });
}

function ambientMove() {
  const next = chooseSafePosition({ x: position.x + (Math.random() - .5) * 240, y: position.y + (Math.random() - .5) * 180 });
  moveTo(next, 'independent_ambient_motion');
}

function showSpeech(text) {
  speech.textContent = text;
  speech.setAttribute('aria-hidden', 'false');
  speech.classList.add('is-speaking');
}

function hideSpeech() {
  speech.classList.remove('is-speaking');
  speech.setAttribute('aria-hidden', 'true');
}

async function speakApproved(text) {
  const voice = window.ORB_WEAVER_VOICE_RUNTIME;
  if (!voice || typeof voice.speak !== 'function') {
    setStatus('approved voice runtime not connected', true);
    record('voice_unavailable', { reason: 'approved_runtime_missing' });
    return false;
  }
  showSpeech(text);
  record('voice_started', { text });
  try {
    await voice.speak(text);
    record('voice_completed', { text });
  } catch {
    setStatus('approved voice unavailable / please try again', true);
    record('voice_unavailable', { reason: 'approved_runtime_failed' });
    return false;
  } finally {
    hideSpeech();
  }
  return true;
}

async function guideToTarget(id) {
  const updateProof = (state, values = {}) => {
    if (id !== 'proof-target') return;
    document.querySelector('.console-state').textContent = state;
    for (const [key, value] of Object.entries(values)) {
      document.querySelector(`[data-proof="${key}"]`).textContent = value;
    }
  };
  updateProof('CHECKING', { identity: 'checking', location: 'checking', pointer: 'not checked', outcome: 'not observed' });
  const target = document.querySelector(`[data-orb-target="${CSS.escape(id)}"]`);
  if (!target) {
    updateProof('RECOVERY REQUIRED', { identity: 'missing' });
    setStatus(`target ${id} unresolved`, true);
    record('target_unresolved', { id });
    return false;
  }
  lastTargetId = id;
  record('target_discovered', { id });
  target.scrollIntoView({ behavior: prefersReducedMotion ? 'auto' : 'smooth', block: 'center' });
  await new Promise((resolve) => setTimeout(resolve, prefersReducedMotion ? 20 : 650));
  const rect = target.getBoundingClientRect();
  const visible = rect.top >= 0 && rect.bottom <= innerHeight && rect.left >= 0 && rect.right <= innerWidth;
  if (!visible) {
    updateProof('RECOVERY REQUIRED', { identity: 'resolved', location: 'attached', pointer: 'not visible' });
    setStatus(`target ${id} needs recovery`, true);
    record('target_recovery_required', { id, rect: { top: rect.top, bottom: rect.bottom } });
    return false;
  }
  record('target_resolved', { id });
  moveTo({ x: Math.max(56, rect.left - 58), y: Math.max(128, rect.top + rect.height * .25) }, 'verified_guidance');
  target.classList.remove('target-ping');
  void target.offsetWidth;
  target.classList.add('target-ping');
  record('ping_emitted', { id });
  setStatus(`verified guidance / ${id}`, true);
  await new Promise((resolve) => setTimeout(resolve, 950));
  const finalRect = target.getBoundingClientRect();
  const finalStyle = getComputedStyle(target);
  const stillVisible = target.isConnected && finalRect.width > 0 && finalRect.height > 0
    && finalRect.top >= 0 && finalRect.bottom <= innerHeight
    && finalRect.left >= 0 && finalRect.right <= innerWidth
    && finalStyle.visibility === 'visible' && finalStyle.display !== 'none' && Number(finalStyle.opacity) > 0;
  if (!stillVisible) {
    updateProof('RECOVERY REQUIRED', { outcome: 'not observed' });
    setStatus(`target ${id} changed / guidance not verified`, true);
    record('guidance_failed', { id, reason: 'destination_changed' });
    return false;
  }
  updateProof('VISIBLE', { identity: 'resolved', location: 'attached', pointer: 'visible', outcome: 'observed this pass' });
  record('guidance_verified', { id, evidence: 'target_visible_and_pinged' });
  return true;
}

function politeNudge(event) {
  const dx = position.x - event.clientX;
  const dy = position.y - event.clientY;
  const distance = Math.hypot(dx, dy);
  if (distance > 120 || distance === 0) return;
  const scale = (125 - distance) / distance;
  moveTo({ x: position.x + dx * scale * .6, y: position.y + dy * scale * .6 }, 'polite_nudge');
  record('polite_nudge', { distance: Math.round(distance) });
}

export function startOrbRuntime() {
  moveTo(chooseSafePosition({ x: innerWidth * .72, y: innerHeight * .48 }), 'initial_presence');
  render();
  window.setInterval(ambientMove, prefersReducedMotion ? 9000 : 4600);
  window.addEventListener('pointermove', politeNudge, { passive: true });
  window.addEventListener('resize', () => moveTo(chooseSafePosition(position), 'viewport_recalibration'));
  orb.addEventListener('click', () => {
    const voice = window.ORB_WEAVER_VOICE_RUNTIME;
    if (voice && typeof voice.requestConsent === 'function') voice.requestConsent();
    else setStatus('voice consent control / approved runtime required', true);
    record('presence_invoked', { target: lastTargetId });
  });
  setStatus('presence active / voice-ready when approved runtime connects');
}

export { guideToTarget, speakApproved, record };
export const getEventLog = () => [...eventLog];
