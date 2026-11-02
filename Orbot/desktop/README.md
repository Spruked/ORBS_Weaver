# Orbot desktop

Orbot's React/Vite frontend and Tauri 2 Rust host. It starts as the supplied
red/blue floating orb. Click to talk, drag to move, or right-click to dock to the
separate sibling project `../../Orb_Dock_Station_v2.1/`. That station owns its
own Tauri process and tray; it is not included in this repository.
The embodiment grants no execution authority.

From this directory:

```powershell
npm ci
npm run dev
npm run build
npm run desktop:dev
npm run desktop:build
```

Browser preview supports the orb and `?view=conversation`; native window controls require
Tauri. Native builds require Rust/Cargo, Windows C++ build tools, and WebView2.
Bundled installers are disabled until application identity and release assets
are finalized; `desktop:build` builds the native executable.

The web application at the repository root keeps its TanStack Start entrypoint.
This desktop app builds static assets independently and does not run database
migrations. Only local window controls are exposed through Tauri capabilities.
There is no filesystem, shell execution, or provider credential access.
The conversation window connects only to the local Communication service on
port 16521; that service uses the already running llama.cpp server on port 16520
and Qwen3-TTS for optional WAV output. Start it with
`runtime/communication/.venv/Scripts/python -m runtime.communication.main` from
the repository root. See `runtime/communication/README.md` for setup and limits.

Configuration follows https://v2.tauri.app/reference/config/ and
https://v2.tauri.app/start/frontend/vite/.
