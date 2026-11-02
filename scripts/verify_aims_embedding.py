"""Verify embedded AIMS without starting services or touching customer stores."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COPIES = (ROOT / "AIMS", ROOT / "Orbot/Orbot_Vault-Logic-System/AIMS")

SMOKE = """
import sys, socket, tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
with patch.object(socket.socket, 'bind', side_effect=AssertionError('Unexpected HTTP listener')):
    from memory_core import AIMSMemorySystem, EntryType
    with tempfile.TemporaryDirectory() as directory:
        first = AIMSMemorySystem(Path(directory) / 'customer-a', matrix_id='memory')
        second = AIMSMemorySystem(Path(directory) / 'customer-b', matrix_id='memory')
        entry = first.commit(EntryType.OBSERVATION, {'private': 'customer-a-only'})
        assert second.long_term.read_entry(entry_id=entry.entry_id) is None
        reopened = AIMSMemorySystem(Path(directory) / 'customer-a', matrix_id='memory')
        assert reopened.long_term.read_entry(entry_id=entry.entry_id) is not None
        assert reopened.long_term.verify_chain()[0]
        assert second.long_term.verify_chain()[0]
assert not any(name in sys.modules for name in ('fastapi', 'uvicorn', 'pydantic'))
print('PASS: import, isolation, persistence, integrity, and no-listener check:', sys.argv[1])
"""


def main():
    for directory in COPIES:
        if (directory / "service.py").exists():
            raise AssertionError(f"Standalone startup path still exists: {directory}")
        subprocess.run([sys.executable, "-B", "-S", "-c", SMOKE, str(directory)], check=True)
    print("PASS: both standalone AIMS startup paths are absent")


if __name__ == "__main__":
    main()
