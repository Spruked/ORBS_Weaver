# Qwen3-TTS GPU integration - 28 October 2026

## Outcome

The default Orbot Qwen3-TTS adapter now requires CUDA. It no longer silently chooses CPU when the shared GPU has limited free memory. The active Qwen2.5-7B-Instruct llama.cpp service remains unchanged on port 16520, with two 8192-token slots; its process PID 11804 was preserved. No model download, package install, new server, repository merge or permission vocabulary was introduced.

The RTX 5060 has approximately 8 GB of VRAM and shared llama.cpp was using roughly 6.8 GB. The accepted path executes neural inference on CUDA while keeping offloaded weights in system RAM between operations. It is GPU execution with CPU weight storage, not a fully GPU-resident TTS model and not CPU inference fallback.

## Implementation

- `runtime/communication/qwen_gpu.py` (new): explicit capacity checks, a 768 MiB Torch allocator budget plus 256 MiB free-headroom requirement, and Accelerate dispatch for bounded CUDA execution. The small codec quantizer remains GPU-resident because its decode method accesses buffers outside forward hooks. Layer preloading uses the existing Qwen decoder classes.
- `runtime/communication/providers.py`: chooses full CUDA when at least 6 GiB is free, otherwise bounded CUDA weight offloading. No automatic CPU inference fallback. Loads BFloat16 weights directly, records actual CUDA output-device observations and peak allocation, and returns unused Torch cached GPU memory between turns. The configured Qwen3-TTS 1.7B CustomVoice model and Ryan speaker are unchanged.
- `runtime/communication/service.py`: reports execution device, mode, precision, allocator budget, peak GPU allocation, observed output devices and load timing in Diagnostics. GPU capacity failures are actionable rather than silently substituting CPU.
- `scripts/benchmark_qwen_gpu.py` (new): repeatable local adapter probe. It writes generated fixtures only under gitignored `.local/` and reports measurements under `docs/`. It does not restart shared llama.cpp or claim physical playback.
- `runtime/communication/tests/test_qwen_gpu.py` and `test_qwen_cpu_settings.py`: GPU headroom/failure policy, resident codec subtree, CUDA-required behavior and explicit configuration validation.

Dock source was not changed in this phase. Its existing live voice status reads the new runtime measurements. The selected Desktop Microphone preference and voice-first, docked availability remain unchanged.

## Measured results

| Probe | Result |
|---|---|
| Isolated GPU/offload phrase | 41.491 s synthesis, 2.16 s audio, 632.4 MiB peak allocated, 666 MiB peak reserved |
| Actual provider implementation | 48.127 s including setup, 2.16 s audio, output tensors observed on cuda:0, BFloat16, 632.4 MiB peak |
| Local hearing check of GPU audio | Original transcript Hello, I am Orbot. |
| Deployed service fixture | 53.984 s including first-use setup, 2.32 s valid PCM WAV |
| Deployed speech-to-response test | 30.266 s overall; hearing 4.438 s, llama inference 1.765 s, GPU TTS 23.969 s; response Hello!, 1.2 s PCM WAV |
| Live GPU utilization during service synthesis | Approximately 60 percent observed with nvidia-smi |
| Post-cancel GPU reuse | 14.953 s, 0.64 s audio, cuda:0 outputs, 632.4 MiB peak; hands-free listening resumed |
| GPU cancellation | 0.171 s from cancellation request to HTTP 409; active session preserved; one hearing observation pruned, no late assistant reply saved |

The service round trip used an ordinary isolated test session and preserved the active embodiment session. Protected inculcation v1.3 retained SHA256 `2a6642e90053134c6733d408344d228712f82a7b006bfa3e9878d94c14801546`. Execution authority remains false; full TPC/RAL/Doctrine execution integration remains outside this work.

The earlier owner confirmation of audible Tauri output remains valid as a playback baseline. This GPU update independently validated generated audio and service behavior; it does not claim a new owner acoustic confirmation.

## Rejected experiments

- In-place precision conversion caused an access violation in the isolated Windows/PyTorch process. Production never used that conversion.
- A clean INT8 candidate consumed less resident RAM but did not yield usable speech in the bounded experiment; it was rejected.
- CPU FP32 produced correct speech in approximately 17-26 s depending on thread count. It was not deployed because the owner explicitly requires GPU use.

The shipped path uses the original model weights with BFloat16 CUDA operations, not INT8 and not the CPU FP32 experiment.

## Tests and evidence

Communication: 46 passed. Runtime regression: 58 passed. Dock backend: 14 passed. Existing frontend lifecycle tests (10) and initial docked-window Rust test (1) were unchanged and passed in the preceding voice integration phase. Combined coverage is 129 tests. No frontend or native source changed in this GPU phase, so rebuilding those unchanged artifacts was unnecessary.

Evidence files: `qwen_gpu_provider_results.json`, `voice_service_acceptance_results.json`, `qwen_gpu_cancellation_results.json`, `qwen_gpu_post_cancel_results.json`, `qwen_backend_experiment_decisions.json`, and `voice_repository_status.json`. Earlier voice device/playback and three-cycle dock continuity evidence remains in the independent Dock repository.

## Remaining limitations

Synthesis is still slow because this hardware cannot keep both configured models fully resident on the GPU at their current allocations. Weight transfers and framework overhead remain significant; this is not instant voice. Full TTS GPU residency would require rebalancing the shared GPU allocation or different capacity. Shared llama.cpp settings were deliberately left unchanged. Available VRAM can change; the adapter fails explicitly when headroom is insufficient.

The 768 MiB limit applies to the Torch allocator, not driver/context allocations. The helper checks free memory after CUDA initialization and keeps additional headroom; it does not reserve the entire shared GPU or promise protection against arbitrary concurrent third-party GPU workloads.

Development deployment restarted Dock-owned processes through their normal lifecycle; ordinary docking does not stop Communication. Both repositories retain existing dirty working trees and independent ownership. No commits or pushes were made.
