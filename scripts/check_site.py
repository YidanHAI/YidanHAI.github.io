#!/usr/bin/env python3
"""Check generated pages for broken internal links and missing image text."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys


ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "index.html",
    ROOT / "work/index.html",
    ROOT / "writing/index.html",
    ROOT / "about/index.html",
    ROOT / "cv/index.html",
    *(ROOT / "writing").glob("*/index.html"),
    ROOT / "404.html",
]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.images_without_alt: list[str] = []
        self.assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        properties = dict(attrs)
        if properties.get("id"):
            self.ids.add(properties["id"] or "")
        if tag == "a" and properties.get("href"):
            self.links.append(properties["href"] or "")
        if tag == "img":
            if not properties.get("alt"):
                self.images_without_alt.append(properties.get("src") or "")
            if properties.get("src"):
                self.assets.append(properties["src"] or "")
        if tag == "script" and properties.get("src"):
            self.assets.append(properties["src"] or "")
        if tag == "link" and properties.get("rel") in {"stylesheet", "icon", "preload"}:
            if properties.get("href"):
                self.assets.append(properties["href"] or "")


def find_file(path: str) -> Path:
    local = ROOT / unquote(path).lstrip("/")
    if local.is_dir():
        local /= "index.html"
    return local


def main() -> None:
    errors: list[str] = []
    parsed: dict[Path, PageParser] = {}
    for page in PAGES:
        if not page.is_file():
            errors.append(f"Missing page: {page.relative_to(ROOT)}")
            continue
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        parsed[page] = parser
        for source in parser.images_without_alt:
            errors.append(f"{page.relative_to(ROOT)}: image lacks alt: {source}")
        for source in parser.assets:
            if source.startswith("/") and not find_file(source).is_file():
                errors.append(f"{page.relative_to(ROOT)}: missing asset {source}")

    for page, parser in list(parsed.items()):
        for link in parser.links:
            if not link.startswith(("/", "#")):
                continue
            path, fragment = urlsplit(link).path, urlsplit(link).fragment
            target = page if not path else find_file(path)
            if not target.is_file():
                errors.append(f"{page.relative_to(ROOT)}: missing target {link}")
                continue
            if fragment:
                target_parser = parsed.get(target)
                if target_parser is None:
                    target_parser = PageParser()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    parsed[target] = target_parser
                if fragment not in target_parser.ids:
                    errors.append(f"{page.relative_to(ROOT)}: missing anchor {link}")
    for text in ("yourorcidurl", "john+snow", "GitHub University", "future-post"):
        for page in PAGES:
            if page.is_file() and text in page.read_text(encoding="utf-8"):
                errors.append(f"{page.relative_to(ROOT)}: template placeholder {text}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print(f"Checked {len(PAGES)} pages: internal links, anchors, images and placeholders OK.")


if __name__ == "__main__":
    main()
