#!/usr/bin/env python3
"""Render both public CV PDFs from the site's print layout with headless Chrome."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "build_site.py")], check=True)
    browser = os.environ.get("CHROME_BIN") or shutil.which("google-chrome") or shutil.which("chromium")
    if not browser:
        raise SystemExit("Chrome/Chromium not found; set CHROME_BIN.")

    class QuietHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args: object, **kwargs: object) -> None:
            super().__init__(*args, directory=str(ROOT), **kwargs)

        def log_message(self, format: str, *args: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        for language in ("en", "zh"):
            target = ROOT / "assets" / f"Yidan-Huang-CV-{language}.pdf"
            # The layout reads ?lang= before first paint, so no clicks are needed.
            subprocess.run(
                [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                 "--force-prefers-reduced-motion", "--virtual-time-budget=5000", "--no-pdf-header-footer",
                 f"--print-to-pdf={target}", f"http://127.0.0.1:{server.server_port}/cv/?lang={language}"],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120,
            )
            print(f"Wrote {target.relative_to(ROOT)}")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
