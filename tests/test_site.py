"""Structural and truthfulness checks for the static project showcase."""

import re
import struct
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
INDEX = SITE / "index.html"
STYLES = SITE / "styles.css"
SCRIPT = SITE / "script.js"
FAVICON = SITE / "favicon.svg"
ROBOTS = SITE / "robots.txt"
SITEMAP = SITE / "sitemap.xml"
SOCIAL_SVG = SITE / "social-card.svg"
SOCIAL_PNG = SITE / "social-card.png"


class DocumentParser(HTMLParser):
    """Collect the small set of semantics needed by these dependency-free tests."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.ids: set[str] = set()
        self.links: list[dict[str, str | None]] = []
        self.buttons: list[dict[str, str | None]] = []
        self.headings: list[str] = []
        self.tables: list[dict[str, int]] = []
        self._table_index: int | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.tags.append((tag, attributes))
        if identifier := attributes.get("id"):
            self.ids.add(identifier)
        if tag == "a":
            self.links.append(attributes)
        if tag == "button":
            self.buttons.append(attributes)
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(tag)
        if tag == "table":
            self.tables.append({"captions": 0, "scoped_headers": 0})
            self._table_index = len(self.tables) - 1
        elif tag == "caption" and self._table_index is not None:
            self.tables[self._table_index]["captions"] += 1
        elif (
            tag == "th"
            and self._table_index is not None
            and attributes.get("scope") in {"row", "col"}
        ):
            self.tables[self._table_index]["scoped_headers"] += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "table":
            self._table_index = None


def read_site() -> tuple[str, str, str, DocumentParser]:
    html = INDEX.read_text(encoding="utf-8")
    css = STYLES.read_text(encoding="utf-8")
    javascript = SCRIPT.read_text(encoding="utf-8")
    parser = DocumentParser()
    parser.feed(html)
    return html, css, javascript, parser


def test_site_assets_are_local_and_present() -> None:
    assert INDEX.is_file()
    assert STYLES.is_file()
    assert SCRIPT.is_file()
    assert FAVICON.is_file()
    assert ROBOTS.is_file()
    assert SITEMAP.is_file()
    assert SOCIAL_SVG.is_file()
    assert SOCIAL_PNG.is_file()

    html, _, _, _ = read_site()
    assert 'href="favicon.svg"' in html
    assert 'href="styles.css"' in html
    assert 'src="script.js"' in html
    assert not re.search(r'<script[^>]+src="https?://', html)
    assert not re.search(r'<link[^>]+rel="(?:stylesheet|icon)"[^>]+href="https?://', html)

    canonical = "https://z-markus.github.io/Prompt-Refinement-for-AI-Coding-Assistance/"
    assert canonical in html
    assert canonical in ROBOTS.read_text(encoding="utf-8")
    assert canonical in SITEMAP.read_text(encoding="utf-8")


def test_social_preview_is_exact_size_and_linked() -> None:
    png = SOCIAL_PNG.read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", png[16:24])
    assert (width, height) == (1200, 630)

    html, _, _, _ = read_site()
    image_url = (
        "https://z-markus.github.io/Prompt-Refinement-for-AI-Coding-Assistance/social-card.png"
    )
    assert f'property="og:image" content="{image_url}"' in html
    assert f'name="twitter:image" content="{image_url}"' in html
    assert 'name="twitter:image:alt"' in html
    assert 'name="twitter:card" content="summary_large_image"' in html


def test_historical_results_are_exact_and_clearly_labeled() -> None:
    html, _, _, _ = read_site()

    expected_evidence = (
        "134 / 197 accepted",
        "126 / 196 accepted",
        "55 / 199 accepted",
        "68.0%",
        "64.3%",
        "27.6%",
        "67.9%",
        "64.2%",
        "27.5%",
        "193-task common set",
        "p <span>≈</span> 0.34",
        "191 paired tasks",
        "p = 0.4177",
    )
    for evidence in expected_evidence:
        assert evidence in html

    assert html.lower().count("historical") >= 8
    assert "No demonstrated improvement." in html
    assert "not a live model leaderboard" in html
    assert "23 versus 16 refinement-only successes" in html


def test_no_placeholder_content_or_fabricated_showcase_metrics() -> None:
    html, css, javascript, _ = read_site()
    searchable = f"{html}\n{css}\n{javascript}".lower()

    forbidden = (
        "lorem ipsum",
        "placeholder",
        "coming soon",
        "insert metric",
        "todo:",
        "testimonial",
        "75%",
        "90%",
    )
    for text in forbidden:
        assert text not in searchable

    assert "Submit generated code" not in html
    assert "make no submissions" in html
    assert "without model spend, credentials, or judge calls" in html


def test_engineering_rebuild_is_visible_to_reviewers() -> None:
    html, _, _, parser = read_site()

    assert "engineering" in parser.ids
    assert "Built to be audited, not merely admired." in html
    for proof in (
        "Fingerprint every input",
        "Pair before comparing",
        "Fail safely and offline",
        "Codex and Claude ready",
    ):
        assert proof in html

    assert "Role &amp; contribution" in html
    assert "Hehan Zhao" in html
    assert "AI-assisted rebuild" in html


def test_document_has_core_landmarks_and_heading_structure() -> None:
    html, _, _, parser = read_site()
    tags = [tag for tag, _ in parser.tags]

    assert '<html lang="en">' in html
    assert 'name="viewport"' in html
    assert 'property="og:title" content="Prompt Refinement, Tested"' in html
    assert 'rel="canonical"' in html
    assert tags.count("header") == 1
    assert tags.count("nav") == 1
    assert tags.count("main") == 1
    assert tags.count("footer") == 1
    assert parser.headings.count("h1") == 1
    assert parser.headings[0] == "h1"
    assert "main-content" in parser.ids
    assert 'href="#main-content"' in html


def test_all_internal_links_have_targets_and_external_links_are_safe() -> None:
    _, _, _, parser = read_site()

    for link in parser.links:
        href = link.get("href") or ""
        if href.startswith("#"):
            assert href[1:] in parser.ids, f"Missing target for {href}"
        if link.get("target") == "_blank":
            rel_tokens = set((link.get("rel") or "").split())
            assert "noreferrer" in rel_tokens

    repository_url = "https://github.com/Z-MarkUs/Prompt-Refinement-for-AI-Coding-Assistance"
    repo_links = [link for link in parser.links if link.get("href") == repository_url]
    assert len(repo_links) >= 3


def test_interactive_controls_have_accessible_tab_relationships() -> None:
    _, _, javascript, parser = read_site()
    tabs = [attributes for tag, attributes in parser.tags if attributes.get("role") == "tab"]
    panels = [attributes for tag, attributes in parser.tags if attributes.get("role") == "tabpanel"]
    tablists = [
        attributes for tag, attributes in parser.tags if attributes.get("role") == "tablist"
    ]

    assert len(tablists) == 2
    assert len(tabs) == 5
    assert len(panels) == 5
    assert all(button.get("type") == "button" for button in parser.buttons)

    panel_ids = {panel.get("id") for panel in panels}
    tab_ids = {tab.get("id") for tab in tabs}
    for tab in tabs:
        assert tab.get("aria-controls") in panel_ids
        assert tab.get("aria-selected") in {"true", "false"}
    for panel in panels:
        assert panel.get("aria-labelledby") in tab_ids

    assert "ArrowRight" in javascript
    assert "ArrowLeft" in javascript
    assert 'event.key === "Home"' in javascript
    assert 'event.key === "End"' in javascript


def test_result_tables_are_accessible() -> None:
    _, _, _, parser = read_site()
    assert len(parser.tables) == 2
    assert all(table["captions"] == 1 for table in parser.tables)
    assert all(table["scoped_headers"] >= 6 for table in parser.tables)


def test_motion_and_focus_have_accessible_fallbacks() -> None:
    _, css, javascript, _ = read_site()
    assert ":focus-visible" in css
    assert "prefers-reduced-motion: reduce" in css
    assert '"IntersectionObserver" in window' in javascript
    assert "opacity: 1" in css


def test_layout_has_responsive_breakpoints() -> None:
    _, css, _, _ = read_site()
    assert "@media (max-width: 980px)" in css
    assert "@media (max-width: 720px)" in css
    assert "grid-template-columns: 1fr" in css
    assert "overflow-x: auto" in css
