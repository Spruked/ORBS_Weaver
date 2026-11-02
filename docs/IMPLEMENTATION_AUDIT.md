# Landing slice and Windows runtime audit

Audit date: November 1, 2026. Source inspection only unless a runtime check is explicitly recorded below.

## Machine readiness

- GPU: NVIDIA GeForce RTX 5060, 8151 MiB reported by NVIDIA-SMI.
- Driver: 610.88. CUDA Toolkit: 13.4.
- Working Python: `C:\Users\bryan\AppData\Local\Programs\Python\Python311\python.exe` (3.11.9).
- PyTorch and torchaudio: 2.11.0+cu128. CUDA available; native sm_120 support reported; a CUDA 512 by 512 matrix multiplication passed.
- Qwen TTS 0.1.1 imports successfully. `pip check` passed.
- Cached Qwen CustomVoice models: 0.6B and 1.7B. Cache presence does not prove synthesis or approved voice identity.
- The Desktop `qwen3-tts` folder is a separate Python 3.12 environment containing only pip. It is not the working voice runtime.
- SoX was missing. Installed SoX 14.4.2 through WinGet, which verified the download hash. New terminals receive its PATH update.
- No listener was found on port 4173 during inspection. No running Python voice server was found.
- Faster Whisper is absent from the inspected Python environment. STT remains unconnected.

Run `python scripts/check_runtime.py` for repeatable GPU, package, SoX, and cache diagnostics. This command does not download models or select a voice.

## Five-file source audit

| File | Present behavior | Gap before acceptance |
| --- | --- | --- |
| index.html | Semantic landing sections, JSON-LD, signature footer, two guidance controls, ORB body and transient speech surface | Inspector claims resolved/safe/observed before an actual pass; no dismissal control; footer is currently literal page content |
| styles.css | Responsive single-page layout, pointer ping, reduced-motion CSS | JavaScript motion continues under reduced motion; fixed status can overlap footer; visual and keyboard checks outstanding |
| src/main.js | Starts runtime and wires guidance buttons | Missing try/finally can leave a button disabled after failure |
| src/orb-runtime.js | Autonomous movement, proximity nudge, live element lookup, injected voice interface, event log | No voice adapter or microphone pipeline; no single-flight turns; no governed target inventory; no final target revalidation; incomplete collision protection; fallback placement may be blocked; no dismissal or interruption state |
| assets/orb-body.svg | Illustrative body loads from the new project | Production skin remains unapproved/unconnected |

No chatbot or browser speech implementation was found in these files. Runtime event records are not yet the canonical evidence envelope. A ping and viewport check cannot establish understanding or a business outcome.

## Current gate

Landing acceptance remains open. Project Brief and Page Specification approval records were not found in this folder. Voice, responsive behavior, accessible motion, collision recovery, and the full guidance path need runtime evidence. Secondary pages and manufacturing compilers remain outside this increment.

## Next work

Correct premature inspector claims and guidance failure handling, establish the landing specification and target inventory, and validate pointer guidance on desktop and mobile. Bind local voice only after identifying the approved voice asset/speaker and the actual STT/TTS service contract; cached models alone do not supply that contract.

## Changes and verification after audit

- Inspector now starts at NOT CHECKED and reports only the current guidance pass. It no longer preclaims safe pointer geometry.
- Guidance rechecks destination visibility after its delay and records failure when the destination changes.
- Guidance buttons restore their enabled state through `finally`; approved voice failures produce an honest unavailable status.
- Both JavaScript modules passed `node --check`.
- `python scripts/check_runtime.py` passed GPU computation and SoX executable checks.
- Started the project-only static preview on `127.0.0.1:4173` after confirming the port had no listener.
- Visible browser validation is blocked: the browser access host is unavailable and computer-use inventory reports no browsers. Desktop/mobile visual acceptance remains unverified.

These corrections do not complete the landing acceptance gate or connect live speech.
