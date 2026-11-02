$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $repoRoot
try {
    if (-not (Test-Path -LiteralPath 'runtime/communication/.venv/Scripts/python.exe')) {
        python -m venv --system-site-packages runtime/communication/.venv
        if ($LASTEXITCODE -ne 0) { throw 'Unable to create communication environment' }
    }
    $commsPython = Join-Path $repoRoot 'runtime/communication/.venv/Scripts/python.exe'
    & $commsPython -m pip install -r runtime/communication/requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Communication dependency installation failed' }
    & $commsPython -c "import torch; print('CUDA available:', torch.cuda.is_available()); from qwen_tts import Qwen3TTSModel; print('Qwen3-TTS ready')"
    if ($LASTEXITCODE -ne 0) { throw 'Qwen3-TTS dependency verification failed' }
    & $commsPython -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice', local_dir='.local/models/Qwen3-TTS-1.7B-CustomVoice', max_workers=2)"
    if ($LASTEXITCODE -ne 0) { throw 'Voice model download failed' }
} finally {
    Pop-Location
}
