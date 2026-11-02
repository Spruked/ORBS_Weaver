"""Start three processes, reject occupied ports, and stop children together."""
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from runtime.shared.health import PORTS, peer_status


def main():
    children = []
    probes = []
    try:
        # Hold all ports until preflight completes. Never attach to an unknown process.
        for port in PORTS.values():
            probe = socket.socket()
            probes.append(probe)
            probe.bind(("127.0.0.1", port))
    finally:
        for probe in probes:
            probe.close()
    root = Path(__file__).resolve().parents[1]
    def stop_requested(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop_requested)
    try:
        for name in PORTS:
            children.append(subprocess.Popen([sys.executable, "-m", f"runtime.{name}.main"], cwd=root,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0))
        deadline = time.monotonic() + 30
        while not all(peer_status(name).get("ready") for name in PORTS):
            if any(child.poll() is not None for child in children) or time.monotonic() > deadline:
                raise RuntimeError("Three-runtime startup failed")
            time.sleep(0.25)
        print("Three runtimes ready. Motion execution remains disabled.", flush=True)
        while True:
            if any(child.poll() is not None for child in children):
                raise RuntimeError("Runtime exited; stopping its peers")
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        # Ask uvicorn to shut down so session review runs before process exit.
        for child in reversed(children):
            if child.poll() is None:
                if sys.platform == "win32":
                    child.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    child.send_signal(signal.SIGTERM)
        for child in children:
            try:
                child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


if __name__ == "__main__":
    main()
