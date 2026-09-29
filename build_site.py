#!/usr/bin/env python3
"""Build the dependency-free static site committed at the repository root."""

from __future__ import annotations

from dataclasses import dataclass
from email.utils import format_datetime
from html import escape
from pathlib import Path
from datetime import datetime, timezone
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "site_src"
BASE_URL = "https://yidanhai.github.io"
UPDATED = "2026-09-29"


@dataclass(frozen=True)
class Page:
    path: str
    source: str
    title: str
    description: str
    section: str
    body_class: str = ""
    kind: str = "website"

    @property
    def url(self) -> str:
        return f"{BASE_URL}{self.path}"

    @property
    def destination(self) -> Path:
        if self.path == "/":
            return ROOT / "index.html"
        if self.path.endswith(".html"):
            return ROOT / self.path.lstrip("/")
        return ROOT / self.path.lstrip("/") / "index.html"


PAGES = (
    Page(
        "/", "home.html",
        "Yidan Huang — Research & Engineering",
        "Yidan Huang works on foundation-model post-training, evidence-grounded search agents, and rigorous agent evaluation.",
        "home", "home-page",
    ),
    Page(
        "/work/", "work.html",
        "Selected Work — Yidan Huang",
        "Selected research and engineering work across long-horizon agents, model post-training, and interactive evaluation.",
        "work", "inner-page",
    ),
    Page(
        "/writing/", "writing.html",
        "Writing — Yidan Huang",
        "Field notes on evidence-grounded search, persistent agent state, and reliable model post-training.",
        "writing", "inner-page",
    ),
    Page(
        "/writing/evidence-paths/", "evidence-paths.html",
        "A hard question is not necessarily a hard search — Yidan Huang",
        "Why answer complexity alone does not teach a search agent to gather evidence step by step.",
        "writing", "article-page", "article",
    ),
    Page(
        "/writing/persistent-state/", "persistent-state.html",
        "A search agent needs a ledger, not a longer transcript — Yidan Huang",
        "Persistent evidence and candidate state make long-horizon agent decisions easier to trace and train.",
        "writing", "article-page", "article",
    ),
    Page(
        "/writing/training-signals/", "training-signals.html",
        "The data contract is part of the model — Yidan Huang",
        "Why masks, packing, tool turns, and evaluation lineage decide what an agent really learns.",
        "writing", "article-page", "article",
    ),
    Page(
        "/about/", "about.html",
        "About — Yidan Huang",
        "About Yidan Huang: researcher and engineer working on foundation models and long-horizon agents.",
        "about", "inner-page",
    ),
    Page(
        "/cv/", "cv.html",
        "Curriculum Vitae — Yidan Huang",
        "A concise public CV for Yidan Huang, covering research, engineering, publications, and education.",
        "cv", "inner-page cv-page",
    ),
    Page(
        "/404.html", "404.html",
        "Page not found — Yidan Huang",
        "This page is unavailable. Return to Yidan Huang's homepage.",
        "", "inner-page",
    ),
)


ARTICLES = (
    ("/writing/evidence-paths/", "A hard question is not necessarily a hard search",
     "Why answer complexity alone does not teach a search agent to gather evidence step by step."),
    ("/writing/persistent-state/", "A search agent needs a ledger, not a longer transcript",
     "Persistent evidence and candidate state make long-horizon decisions traceable."),
    ("/writing/training-signals/", "The data contract is part of the model",
     "Masks, packing, tool turns, and evaluation lineage shape what an agent learns."),
)


REDIRECTS = {
    "/publications/": "/work/#publications",
    "/portfolio/": "/work/",
    "/year-archive/": "/writing/",
    "/resume/": "/cv/",
    "/talks/": "/about/",
    "/teaching/": "/about/",
    "/markdown/": "/writing/",
    "/about.html": "/about/",
}


def write_page(page: Page, layout: str) -> None:
    body = (SOURCE / "pages" / page.source).read_text(encoding="utf-8")
    replacements = {
        "{{TITLE}}": escape(page.title, quote=True),
        "{{DESCRIPTION}}": escape(page.description, quote=True),
        "{{CANONICAL}}": escape(page.url, quote=True),
        "{{OG_TYPE}}": page.kind,
        "{{SECTION}}": page.section,
        "{{BODY_CLASS}}": page.body_class,
        "{{BODY}}": body,
    }
    html = layout
    for marker, value in replacements.items():
        html = html.replace(marker, value)
    page.destination.parent.mkdir(parents=True, exist_ok=True)
    page.destination.write_text(html, encoding="utf-8")


def write_redirects() -> None:
    for old_path, new_path in REDIRECTS.items():
        destination = ROOT / old_path.lstrip("/") / "index.html"
        if old_path.endswith(".html"):
            destination = ROOT / old_path.lstrip("/")
        destination.parent.mkdir(parents=True, exist_ok=True)
        safe_target = escape(new_path, quote=True)
        destination.write_text(
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0;url={safe_target}">'
            f'<link rel="canonical" href="{BASE_URL}{safe_target}">'
            '<title>Redirecting — Yidan Huang</title></head><body>'
            f'<p>Moved to <a href="{safe_target}">{safe_target}</a>.</p>'
            '</body></html>\n',
            encoding="utf-8",
        )


def write_feed() -> None:
    published = format_datetime(datetime(2026, 9, 29, 8, 0, tzinfo=timezone.utc))
    channel = ET.Element("channel")
    for tag, value in (
        ("title", "Yidan Huang — Writing"),
        ("link", f"{BASE_URL}/writing/"),
        ("description", "Research notes on agents, evidence, and post-training."),
        ("language", "en"),
        ("lastBuildDate", published),
    ):
        ET.SubElement(channel, tag).text = value
    for path, title, description in ARTICLES:
        item = ET.SubElement(channel, "item")
        for tag, value in (
            ("title", title),
            ("link", f"{BASE_URL}{path}"),
            ("guid", f"{BASE_URL}{path}"),
            ("description", description),
            ("pubDate", published),
        ):
            ET.SubElement(item, tag).text = value
    rss = ET.Element("rss", {"version": "2.0"})
    rss.append(channel)
    ET.indent(rss, space="  ")
    ET.ElementTree(rss).write(ROOT / "feed.xml", encoding="utf-8", xml_declaration=True)


def write_sitemap() -> None:
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    urlset = ET.Element(f"{{{namespace}}}urlset")
    for page in PAGES:
        if page.path == "/404.html":
            continue
        url = ET.SubElement(urlset, f"{{{namespace}}}url")
        ET.SubElement(url, f"{{{namespace}}}loc").text = page.url
        ET.SubElement(url, f"{{{namespace}}}lastmod").text = UPDATED
    ET.indent(urlset, space="  ")
    ET.ElementTree(urlset).write(ROOT / "sitemap.xml", encoding="utf-8", xml_declaration=True)


def main() -> None:
    layout = (SOURCE / "layout.html").read_text(encoding="utf-8")
    for page in PAGES:
        write_page(page, layout)
    write_redirects()
    write_feed()
    write_sitemap()
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )
    (ROOT / ".nojekyll").touch()
    print(f"Built {len(PAGES)} pages, {len(REDIRECTS)} redirects, RSS, and sitemap.")


if __name__ == "__main__":
    main()
