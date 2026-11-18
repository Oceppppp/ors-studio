from __future__ import annotations
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

if getattr(sys, "frozen", False):
    app_root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
else:
    app_root = Path(__file__).resolve().parent

backend_path = app_root / "backend"
if backend_path.exists():
    sys.path.insert(0, str(backend_path))
os.environ.setdefault("ORS_APP_ROOT", str(app_root))
def default_data_dir() -> Path:
    """Return a per-user writable location for project files and the SQLite database."""
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "ORS-Studio"
    return Path.home() / ".ors-studio"


os.environ.setdefault("ORS_DATA_DIR", str(default_data_dir()))


def choose_port() -> int:
    requested = os.environ.get("ORS_PORT")
    if requested:
        return int(requested)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def open_browser_when_ready(url: str, port: int) -> None:
    for _ in range(80):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.25):
                webbrowser.open(url)
                return
        except OSError:
            time.sleep(0.25)


def main() -> None:
    import uvicorn
    from orstudio.api import app

    host = "127.0.0.1"  # Keep the unauthenticated local-first service off the LAN.
    port = choose_port()
    url = f"http://{host}:{port}"
    threading.Thread(target=open_browser_when_ready, args=(url, port), daemon=True).start()
    print("=" * 64)
    print(" Operations Research Studio")
    print(f" Local app: {url}")
    print(f" Data directory: {os.environ['ORS_DATA_DIR']}")
    print(" Keep this window open while using ORS. Press Ctrl+C to stop.")
    print("=" * 64)
    uvicorn.run(app, host=host, port=port, log_level="info", access_log=False)


if __name__ == "__main__":
    main()
