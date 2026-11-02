# Orbot communication: local language and voice

The orb is a provider-agnostic embodiment. Deterministic cognition/governance
owns decisions and authority. An LLM supplies conversational language or advisory
proposals; it never replaces Core-4 or hard admission. This initial communication
slice offers conversation only. Full governance, motion, and tools remain unwired.

The complete Core Four and Desktop professional inculcation v1.2 now load before
interaction. The immutable application snapshot is separate from session caches;
the existing AIMS writer records its content and activation provenance. See
`docs/inculcation_integration.md` and `docs/inculcation_implementation_report.md`.
The llama.cpp adapter measures actual tokens and per-slot capacity, requests
prefix reuse, restores the full prefix on every recreated context, and rejects
overflow without shortening the education or silently dropping supplied history.

Each conversation uses session-isolated High, Medium, and Low AIMS working caches.
High retains completed records immediately. Medium/Low undergo deterministic
SKG-guided review before session purge. Retention includes priority, provenance,
and a reason. See `docs/memory_priority.md` for exact thresholds and failure rules.
The external Dock Station
uses the same AIMS writer through a server-side authenticated Vault adapter.
See `docs/desktop_docking_and_memory.md` for data ownership and lifecycle.

Default text inference uses the existing llama.cpp server at
`http://127.0.0.1:16520/v1`. The adapter discovers its current model rather than
starting a duplicate model server. Qwen3-TTS separately converts returned text
to WAV audio, played only by the operator through the conversation audio controls.

For all three runtime processes, use the supervisor documented in [runtime/README.md](../README.md).

## Run on this workstation

From the repository root, `scripts/setup-communication.ps1` installs/verifies
dependencies and downloads weights. Then:

```powershell
runtime/communication/.venv/Scripts/python -m runtime.communication.main
npm run desktop:web
```

Select Conversation in the dock. The service binds only to `127.0.0.1:16521`.
Only configured local desktop origins are accepted. This loopback boundary is
not authentication against other local processes; no tools or privileged
execution are exposed. Add scoped identity and permits before extending it to
consequential actions. Do not expose this service on a network interface.

One request runs at a time, with bounded input and generation. Voice can be
disabled per request. Inference failure returns an explicit error; speech failure
preserves the text response. Playback can be stopped immediately. Synthesis is
currently non-streaming and cannot be interrupted mid-generation; closing the
panel aborts the client request but does not guarantee server-side cancellation.

## Environment

The local `.venv` reuses this workstation's CUDA PyTorch installation through
`--system-site-packages`; compatible Hugging Face Hub is installed locally to
avoid changing globally installed packages. For another machine install matching
PyTorch and dependencies into a fresh environment, then install `requirements.txt`.
The verified workstation uses Python 3.11 and CUDA-enabled PyTorch.

| Variable | Default |
| --- | --- |
| `ORBOT_INTELLIGENCE_PROVIDER` | `local` |
| `ORBOT_LLAMA_URL` | `http://127.0.0.1:16520/v1` |
| `ORBOT_TTS_MODEL` | `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice` |
| `ORBOT_TTS_DEVICE` | `auto` (CUDA with at least 6 GiB free, otherwise CPU) |
| `ORBOT_TTS_SPEAKER` | `Ryan` |

The 1.7B CustomVoice model and PyTorch SDPA avoid requiring FlashAttention on
Windows. On this workstation weights are in the ignored
`.local/models/Qwen3-TTS-1.7B-CustomVoice/` directory; the adapter prefers that
path and otherwise uses the Hugging Face model ID. Voice is loaded lazily.
Shared GPU capacity and latency must be measured with both
models active; reported free VRAM is not a capacity guarantee.
The automatic device selection protects the existing llama.cpp process by using
CPU when GPU headroom is insufficient. `/status` reports the active voice device.
An explicit `ORBOT_TTS_DEVICE=cuda:0` overrides that selection; CPU synthesis is
slower and uses system RAM.

Remote inference is optional and disabled by default. Selecting `remote`
explicitly requires `ORBOT_REMOTE_URL` (HTTPS compatible `/v1` endpoint) and
`ORBOT_REMOTE_MODEL`; an optional `ORBOT_REMOTE_API_KEY` stays server-side in the
process environment. The same adapter can target larger or legacy models that
implement chat completions. Professional inference now additionally requires a
verified tokenizer, context-capacity and restoration contract. The existing remote
adapter does not provide that contract and fails closed for professional inference;
it is not silently treated as llama.cpp. Other protocols require another adapter. There is no
automatic cloud fallback, no remote TTS, and no credential stored in the frontend.
No remote service or API credential has been configured or contacted.

References: https://github.com/QwenLM/Qwen3-TTS and
https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md.
