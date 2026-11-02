"""One AIMS writer for the host. Session caches never persist to SQLite."""
import secrets
import os
import sys
import threading
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / "Orbot_Vault-Logic-System/AIMS"))
from memory_core.host_sessions import HostMemory

vault_root = repo.parent / "orbs_vault_system"
root = Path(os.getenv("ORBOT_HOST_MEMORY_ROOT", str(vault_root / ".local/host_memory")))
token_path = Path(os.getenv("ORBOT_VAULT_TOKEN_FILE", str(vault_root / ".local/host-memory.token")))
_memory = None
_lock = threading.Lock()


def get_memory():
    global _memory
    from runtime.cognition_governance.inculcation import loader
    foundation = loader.load()
    with _lock:
        if _memory is None:
            _memory = HostMemory(root)
        _memory.bind_professional_foundation(foundation)
        return _memory


def dock_token():
    with _lock:
        token_path.parent.mkdir(parents=True, exist_ok=True)
        if not token_path.exists():
            try:
                with token_path.open("x", encoding="utf-8") as file:
                    file.write(secrets.token_urlsafe(48))
            except FileExistsError:
                pass
        return token_path.read_text(encoding="utf-8").strip()
