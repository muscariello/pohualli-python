"""Desktop launcher for Pohualli when packaged with Briefcase.

Starts the FastAPI web application on an ephemeral port and opens
the system default browser. Provides a minimal fallback CLI help.
"""
from __future__ import annotations

import socket
import threading
import webbrowser
from contextlib import closing

from uvicorn import Config, Server

from .webapp import app


def _find_free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _run_server(port: int):
    config = Config(app=app, host="127.0.0.1", port=port, log_level="info")
    server = Server(config)
    server.run()


def main():  # briefcase entrypoint
    port = _find_free_port()
    url = f"http://127.0.0.1:{port}"
    threading.Timer(0.7, webbrowser.open, args=(url,)).start()
    print(f"Pohualli launching web UI at {url}")
    _run_server(port)


if __name__ == "__main__":  # pragma: no cover
    main()
