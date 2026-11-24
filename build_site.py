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
UPDATED = "2026-11-24"
ME = "Yidan Huang"


@dataclass(frozen=True)
class Link:
    label: str
    href: str


@dataclass(frozen=True)
class Paper:
    key: str
    title: str
    authors: str
    role: tuple[str, str]
    venue: str
    status: str
    topic: str
    links: tuple[Link, ...] = ()


def bilingual(en: str, zh: str) -> str:
    return f'<span data-lang="en">{en}</span><span data-lang="zh">{zh}</span>'


REVIEW_ICLR = "ICLR 2027"
REVIEW_AAAI = "AAAI 2027"
FIRST = ("First author", "第一作者")
CO_FIRST = ("Co-first author", "共同第一作者")
THIRD = ("Third author", "第三作者")

# Single source for the publication list on the home page and the CV.
# Under-review venues stay "Under review" until an official decision arrives.
PAPERS = (
    Paper("acts", "ACTS: Controlling Evidence Acquisition Before Writing Questions for Search Agents",
          "", FIRST, REVIEW_ICLR, "review", "agents",
          (Link("Story", "/work/#acts"), Link("Note", "/writing/evidence-paths/"))),
    Paper("cater", "CATER: Competence-Adaptive Training for Efficient Reasoning",
          "", CO_FIRST, REVIEW_ICLR, "review", "reasoning",
          (Link("Story", "/work/#cater"), Link("Note", "/writing/reasoning-budget/"))),
    Paper("sp-opd", "When Teachers Conflict with Verifiers: Support-Preserving On-Policy Distillation",
          "", FIRST, REVIEW_ICLR, "review", "reasoning",
          (Link("Story", "/work/#sp-opd"), Link("Note", "/writing/teacher-verifier-conflict/"))),
    Paper("clueflow", "ClueFlow: Learning Long-Horizon Search through Attributed Research-State Transitions",
          "Yicheng Wang, Wentao Tan, Yidan Huang, Yifei Liu, Qiong Cao", THIRD,
          "arXiv 2026 · ICLR 2027 under review", "preprint", "agents",
          (Link("arXiv", "https://arxiv.org/abs/2610.25980"), Link("PDF", "https://arxiv.org/pdf/2610.25980"),
           Link("Story", "/work/#clueflow"))),
    Paper("crystalbind", "Binding Crystallization: Diagnosing and Guiding Attribute Assignment in Text-to-Image Diffusion",
          "", FIRST, REVIEW_ICLR, "review", "multimodal",
          (Link("Story", "/work/#crystalbind"), Link("Note", "/writing/attribute-binding/"))),
    Paper("svibench", "SVI-Bench: Evaluating Human-Perceived Interaction Trajectories in Streaming Video Systems",
          "", CO_FIRST, REVIEW_ICLR, "review", "multimodal",
          (Link("Project", "https://yidanhai.github.io/SVIbench-project-page/"),
           Link("Code", "https://github.com/YidanHAI/VL-Interaction-interactflow"),
           Link("Note", "/writing/streaming-interaction/"))),
    Paper("teal", "Can Token Backbones Read Fixed Affective Features?",
          "", FIRST, REVIEW_AAAI, "review", "multimodal",
          (Link("Story", "/work/#teal"), Link("Note", "/writing/feature-interface/"))),
    Paper("searchauditor", "SearchAuditor: Auditing and Attributing Failures in Long-Horizon Search Agents",
          "Zhixiang Liang, Yifei Liu, Yidan Huang, Haozhe Zhao, Beichen Huang, Jiaqi Wang, Nan Duan, Qiong Cao",
          THIRD, "arXiv 2026 · AAAI 2027 under review", "preprint", "agents",
          (Link("arXiv", "https://arxiv.org/abs/2608.05212"), Link("Code", "https://github.com/lzzzx666/SearchAuditor"),
           Link("Story", "/work/#searchauditor"))),
    Paper("joyfrontbench", "JoyFrontBench: Evaluating Front-End Coding Agents through Goal-Oriented Acceptance Contracts",
          "Xiaoyi Qiao, Yicheng Wang, Jianan Lin, Xiaoyang Ji, Dongyi Lv, Yidan Huang, Shi Suo, Shiying Fan, Nan Duan, Jiaqi Wang",
          ("Core Contributor", "Core Contributor"), "arXiv 2026", "preprint", "agents",
          (Link("arXiv", "https://arxiv.org/abs/2611.14952"), Link("PDF", "https://arxiv.org/pdf/2611.14952"))),
    Paper("joyai", "JoyAI-LLM Flash: Advancing Mid-Scale LLMs with Token Efficiency",
          "Aichen Cai et al., including Yidan Huang", ("Contributor", "Contributor"),
          "Technical report · arXiv 2026", "preprint", "foundation",
          (Link("arXiv", "https://arxiv.org/abs/2604.03044"),
           Link("Model", "https://huggingface.co/jdopensource/JoyAI-LLM-Flash"))),
    Paper("eggs", "Robust Detection of Cracked Eggs Using a Multi-Domain Training Method for Practical Egg Production",
          "Yuxuan Cheng, Yidan Huang, Jingjing Zhang, Xuehong Zhang, Qiaohua Wang, Wei Fan",
          ("Second author", "第二作者"), "Foods 2024", "published", "vision",
          (Link("DOI", "https://doi.org/10.3390/foods13152313"),)),
    Paper("pv", "A Study of a Photovoltaic Power Prediction Method Combining BiLSTM and GWO",
          "Xiaokang Gui, Lewen Tan, Yidan Huang", CO_FIRST, "ICCEA 2024 · IEEE", "published", "forecasting",
          (Link("DOI", "https://doi.org/10.1109/ICCEA62105.2024.10604113"),)),
)

STATUS_LABEL = {
    "review": ("Under review", "在审"),
    "preprint": ("Preprint", "预印本"),
    "published": ("Published", "已发表"),
}


def render_authors(paper: Paper) -> str:
    if not paper.authors:
        return bilingual("Anonymous submission · author list withheld during review",
                         "双盲评审中 · 暂不公开作者列表")
    return escape(paper.authors).replace(ME, f"<b>{ME}</b>")


def render_links(paper: Paper) -> str:
    items = []
    for link in paper.links:
        external = link.href.startswith("http")
        attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
        items.append(f'<a href="{escape(link.href, quote=True)}"{attrs}>{escape(link.label)}</a>')
    return "".join(items)


def render_publications() -> str:
    rows = []
    for index, paper in enumerate(PAPERS, 1):
        role = f'<span class="pub-role">{bilingual(*paper.role)}</span>' if paper.role[0] else ""
        rows.append(
            f'<article class="pub" id="pub-{paper.key}" data-status="{paper.status}" data-topic="{paper.topic}">'
            f'<span class="pub-index">{index:02d}</span>'
            f'<div class="pub-body">'
            f'<div class="pub-tags"><span class="pub-status pub-status-{paper.status}">{bilingual(*STATUS_LABEL[paper.status])}</span>'
            f'<span class="pub-venue">{escape(paper.venue)}</span>{role}</div>'
            f'<h3>{escape(paper.title)}</h3>'
            f'<p class="pub-authors">{render_authors(paper)}</p>'
            f'<div class="pub-links">{render_links(paper)}</div>'
            f'</div></article>'
        )
    return "\n".join(rows)


def render_cv_publications() -> str:
    rows = []
    for paper in PAPERS:
        role = f" · {bilingual(*paper.role)}" if paper.role[0] else ""
        authors = f"{render_authors(paper)}. " if paper.authors else ""
        link = next((l for l in paper.links if l.label in {"arXiv", "DOI"}), None)
        link_html = f' <a href="{escape(link.href, quote=True)}">{escape(link.label)} ↗</a>' if link else ""
        title = paper.title if paper.title.endswith(("?", ".")) else f"{paper.title}."
        venue = escape(paper.venue)
        if paper.status == "review":
            venue += f" · {bilingual(*STATUS_LABEL['review'])}"
        rows.append(f'<li><em>{escape(title)}</em> {authors}<span class="cv-venue">{venue}{role}</span>{link_html}</li>')
    return '<ol class="cv-pub-list">' + "".join(rows) + "</ol>"


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
        "Yidan Huang — LLM Post-Training & Agents",
        "Yidan Huang works on LLM post-training, efficient reasoning, on-policy distillation, long-horizon search agents, and multimodal models.",
        "home", "home-page",
    ),
    Page(
        "/work/", "work.html",
        "Research — Yidan Huang",
        "Selected research on reasoning efficiency, on-policy distillation, streaming interaction, multimodal interfaces, and search agents.",
        "work", "inner-page",
    ),
    Page(
        "/writing/", "writing.html",
        "Writing — Yidan Huang",
        "Research notes on efficient reasoning, distillation, streaming-video evaluation, generative models, and agents.",
        "writing", "inner-page",
    ),
    Page(
        "/writing/attribute-binding/", "attribute-binding.html",
        "When does a color become the car's? — Yidan Huang",
        "A research note on when diffusion models assign attributes to objects and how to study that decision.",
        "writing", "article-page", "article",
    ),
    Page(
        "/writing/feature-interface/", "feature-interface.html",
        "A vector is not yet a token — Yidan Huang",
        "Why projecting fixed multimodal features into a token backbone is only the beginning of a readable interface.",
        "writing", "article-page", "article",
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
        "/writing/reasoning-budget/", "reasoning-budget.html",
        "When should a model stop thinking? — Yidan Huang",
        "How CATER routes correctness learning and concise self-distillation using the student’s current competence.",
        "writing", "article-page", "article",
    ),
    Page(
        "/writing/teacher-verifier-conflict/", "teacher-verifier-conflict.html",
        "When the teacher disagrees with a correct answer — Yidan Huang",
        "How SP-OPD uses verifier acceptance and KL projection to repair a distillation target.",
        "writing", "article-page", "article",
    ),
    Page(
        "/writing/streaming-interaction/", "streaming-interaction.html",
        "The unit of video interaction is a trajectory — Yidan Huang",
        "How SVI-Bench and InteractFlow evaluate speaking, silence, timing, and memory in streaming video.",
        "writing", "article-page", "article",
    ),
    Page(
        "/about/", "about.html",
        "About — Yidan Huang",
        "About Yidan Huang: researcher and engineer studying efficient reasoning, on-policy distillation, multimodal systems, and agents.",
        "about", "inner-page",
    ),
    Page(
        "/cv/", "cv.html",
        "Curriculum Vitae — Yidan Huang",
        "Yidan Huang’s public CV: research projects, manuscripts under review at ICLR and AAAI 2027, experience, and publications.",
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
    ("/writing/reasoning-budget/", "When should a model stop thinking?",
     "CATER routes reasoning compression by the student’s current competence.",
     datetime(2026, 9, 30, 2, 30, tzinfo=timezone.utc)),
    ("/writing/teacher-verifier-conflict/", "When the teacher disagrees with a correct answer",
     "SP-OPD projects a teacher target to respect a verifier-accepted trajectory.",
     datetime(2026, 9, 30, 2, 30, tzinfo=timezone.utc)),
    ("/writing/streaming-interaction/", "The unit of video interaction is a trajectory",
     "SVI-Bench evaluates when a streaming assistant speaks, stays silent, and remembers.",
     datetime(2026, 9, 30, 2, 30, tzinfo=timezone.utc)),
    ("/writing/attribute-binding/", "When does a color become the car's?",
     "A counterfactual view of attribute assignment during diffusion sampling.",
     datetime(2026, 9, 29, 17, 0, tzinfo=timezone.utc)),
    ("/writing/feature-interface/", "A vector is not yet a token",
     "Designing an interface for fixed multimodal evidence and pretrained token backbones.",
     datetime(2026, 9, 29, 17, 0, tzinfo=timezone.utc)),
    ("/writing/evidence-paths/", "A hard question is not necessarily a hard search",
     "Why answer complexity alone does not teach a search agent to gather evidence step by step.",
     datetime(2026, 9, 29, 8, 0, tzinfo=timezone.utc)),
    ("/writing/persistent-state/", "A search agent needs a ledger, not a longer transcript",
     "Persistent evidence and candidate state make long-horizon decisions traceable.",
     datetime(2026, 9, 29, 8, 0, tzinfo=timezone.utc)),
    ("/writing/training-signals/", "The data contract is part of the model",
     "Masks, packing, tool turns, and evaluation lineage shape what an agent learns.",
     datetime(2026, 9, 29, 8, 0, tzinfo=timezone.utc)),
)


REDIRECTS = {
    "/publications/": "/#publications",
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
    body = body.replace("{{PUBLICATIONS}}", render_publications())
    body = body.replace("{{CV_PUBLICATIONS}}", render_cv_publications())
    body = body.replace("{{UPDATED}}", UPDATED)
    replacements = {
        "{{UPDATED}}": UPDATED,
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
    latest = format_datetime(max(article[3] for article in ARTICLES))
    channel = ET.Element("channel")
    for tag, value in (
        ("title", "Yidan Huang — Writing"),
        ("link", f"{BASE_URL}/writing/"),
        ("description", "Research notes on generative models, multimodal learning, agents, and post-training."),
        ("language", "en"),
        ("lastBuildDate", latest),
    ):
        ET.SubElement(channel, tag).text = value
    for path, title, description, published_at in ARTICLES:
        item = ET.SubElement(channel, "item")
        for tag, value in (
            ("title", title),
            ("link", f"{BASE_URL}{path}"),
            ("guid", f"{BASE_URL}{path}"),
            ("description", description),
            ("pubDate", format_datetime(published_at)),
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
