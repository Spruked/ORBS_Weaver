# ORBS Weaver Build Baseline

## Baseline date

November 1, 2026

## Build location

```text
C:\Users\bryan\Desktop\ORBS_Weaver
```

## Verified current files

```text
index.html
styles.css
assets/orb-body.svg
src/main.js
src/orb-runtime.js
docs/
```

## Runtime observation

The local preview responded successfully at:

```text
http://localhost:4173/
```

Observed response:

```text
HTTP 200 text/html
```

The project currently has no `package.json`. The next Codex must inspect the existing server owner before adding scripts, dependencies, or a new startup path.

## Scope boundary

This is a new from-scratch Windows build. It is independent of:

- The old WSL repository
- The older `website_orb_final` implementation
- Existing Desktop ORB projects
- Historical runtime assumptions and paths

Do not modify those systems as part of this build.

## Architecture boundary

The application must implement Weaver as an autonomous Website ORB presence, not a chatbot. Do not add a chat window, text input, transcript panel, fixed-corner dock, stationary rest state, browser-generated speech, or text-chat fallback.

The authoritative design and build instructions are in:

- `docs/CODEX_VSCODE_HANDOFF.md`
- `docs/ORB_WEAVER_WEB_WEAVER_REVISED_MASTER_BLUEPRINT.docx`
- `docs/WEB_WEAVER_ORB_WEAVER_UNIFIED_BLUEPRINT.md`
- `docs/WEB_WEAVER_ORB_WEAVER_BUILDER_REVIEW.md`

## Starting state for the next builder

The next builder should audit the existing landing slice, compare it to the handoff, and implement only the next approved increment. No secondary pages or broad manufacturing system should be added until the landing vertical slice passes its acceptance checks.
