"""Read-only diagnostics for the Windows ORB runtime. No model downloads."""
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone


def command(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return {"ok": result.returncode == 0, "output": result.stdout.strip(),
                "error": result.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc)}


def main():
    report = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "python": sys.executable, "python_version": sys.version,
              "cuda_toolkit": os.environ.get("CUDA_PATH"),
              "nvidia": command(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"]),
              "packages": {}}
    for name in ("torch", "torchaudio", "qwen-tts", "faster-whisper", "fastapi", "uvicorn"):
        try:
            report["packages"][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            report["packages"][name] = None
    sox = shutil.which("sox")
    if not sox:
        alias = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Links/sox.exe"
        if alias.exists():
            sox = str(alias)
    if not sox:
        packages = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"
        sox = next((str(p) for p in packages.glob("ChrisBagwell.SoX_*/sox-*/sox.exe") if p.is_file()), None)
    report["sox"] = command([sox, "--version"]) if sox else {"ok": False, "error": "SoX not on PATH"}
    cache = Path(os.environ.get("HF_HUB_CACHE", str(Path.home() / ".cache/huggingface/hub")))
    report["cached_tts_models"] = [str(p) for p in cache.glob("models--Qwen--Qwen3-TTS*/snapshots/*") if p.is_dir()]
    try:
        import torch
        available = torch.cuda.is_available()
        report["gpu"] = {"available": available, "torch_cuda": torch.version.cuda,
                         "architectures": torch.cuda.get_arch_list()}
        if available:
            x = torch.randn(512, 512, device="cuda")
            y = x @ x
            torch.cuda.synchronize()
            report["gpu"].update(name=torch.cuda.get_device_name(0),
                                 matrix_test=bool(torch.isfinite(y).all()))
    except Exception as exc:
        report["gpu"] = {"available": False, "error": str(exc)}
    print(json.dumps(report, indent=2))
    return 0 if report["gpu"].get("matrix_test") and report["sox"].get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
