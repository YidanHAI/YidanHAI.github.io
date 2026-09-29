#!/usr/bin/env python3
"""Render both public CV PDFs from the site's print layout."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "build_site.py")], check=True)

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            pass

    old_cwd = Path.cwd()
    os.chdir(ROOT)
    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        browser_path = os.environ.get("CHROME_BIN") or shutil.which("google-chrome") or shutil.which("chromium")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                executable_path=browser_path,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            try:
                address = f"http://127.0.0.1:{server.server_port}/cv/"
                for language in ("en", "zh"):
                    page = browser.new_page(viewport={"width": 1200, "height": 900})
                    page.goto(address, wait_until="networkidle")
                    if language == "zh":
                        page.locator("#lang-toggle").click()
                    page.evaluate("document.fonts.ready")
                    target = ROOT / "assets" / f"Yidan-Huang-CV-{language}.pdf"
                    page.pdf(
                        path=str(target),
                        format="A4",
                        print_background=True,
                        prefer_css_page_size=True,
                        display_header_footer=False,
                    )
                    page.close()
                    print(f"Wrote {target.relative_to(ROOT)}")
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        os.chdir(old_cwd)


if __name__ == "__main__":
    main()
