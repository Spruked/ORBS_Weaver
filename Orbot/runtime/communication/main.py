"""Run with the communication environment: python -m runtime.communication.main."""
import uvicorn
import socket
import os

if __name__ == "__main__":
    from .service import app
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=16521, workers=1))
    app.state.server = server
    # Claim the ingress before startup can open the canonical AIMS writer.
    # A competing launch fails here, before initializing memory or education.
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if os.name == "nt":
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    try:
        listener.bind(("127.0.0.1", 16521))
        server.run(sockets=[listener])
    finally:
        listener.close()
