import { startOrbRuntime, guideToTarget, speakApproved, getEventLog } from './orb-runtime.js';

document.querySelectorAll('[data-guidance]').forEach((button) => {
  button.addEventListener('click', async () => {
    const id = button.dataset.guidance;
    button.disabled = true;
    try {
      const success = await guideToTarget(id);
      if (success && id === 'proof-target') {
        await speakApproved('This target is resolved, pinged, and visible. That is guidance with evidence.');
      }
    } finally {
      button.disabled = false;
    }
  });
});

window.orbWeaver = { guideToTarget, speakApproved, getEventLog };
startOrbRuntime();
