# ORBS Weaver — New Build

This is a clean Windows-local build created from scratch in `C:\Users\bryan\Desktop\ORBS_Weaver`. It does not use or modify the previous WSL repository.

## Unified repository and authority

This workspace is one repository. AIMS, Correspondence Engine, pointer/escalation,
Orbot, Triple Predicate Cubed, and `orbs_vault_system` are included source
directories, not nested Git repositories or submodules.

`orbs_vault_system/` is the single source of truth for this system. It owns
governed site and commercial records, approved policy, provenance, and acceptance
evidence. Memory and reasoning engines consume that authority; their indexes,
session state, caches, and bundled reference copies do not independently define
system truth. See `orbs_vault_system/AUTHORITY.md`.

The landing page and its complete semantic and spatial mapping come first.
Design for an autonomous ORB generally 80–200 px in diameter, resized by position
and intent, with verified pointer/ping guidance supporting the commercial journey.

## Current vertical slice

- Landing page first: semantic structure, JSON-LD, responsive layout, signature footer.
- Autonomous ORB presence: continuous independent motion, purposeful repositioning, obstacle awareness, and Polite Nudge.
- Pure ORB interface: no chat window, chat icon, text input, transcript, text-chat fallback, fixed dock, or browser-generated voice.
- Pointer/Ping demonstration: mapped target discovery, resolution, ping, and observed guidance evidence.
- Voice boundary: the page accepts an approved runtime through `window.ORB_WEAVER_VOICE_RUNTIME`; if it is absent, the ORB reports a non-chat status and does not substitute browser speech.
- Local-first runtime: no cloud service or external API is required for this slice.

## Run in VS Code

Open this folder in VS Code and serve it with any static HTTP server. For example, from PowerShell in this folder:

```powershell
python -m http.server 4173
```

Then open `http://localhost:4173` in a browser. ES modules require HTTP serving rather than `file://` loading.

## Next build increments

1. Replace the illustrative ORB SVG with the approved production skin.
2. Connect the approved local voice runtime and consent path.
3. Move the target map into a versioned Site World vault.
4. Add the full evidence schema, commercial authority plane, and release checks.
