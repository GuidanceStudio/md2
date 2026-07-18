"""M105: chapter cover — act-divider slide type (:::chapter).

A :::chapter fence wrapping a whole slide becomes a full-height,
left-aligned "act divider": slide["type"]="chapter", the `# ` H1 is the
title (kept for sidebar nav), and everything else inside the fence is the
subtitle (rendered through markdown+bleach). There is no kicker and no
chapter number — a chapter cover is just title + optional subtitle.
Only an explicit :::chapter triggers this — a bare `# ` H1 inside an
ordinary slide (the hero-stat pattern) is NOT a chapter.
"""
import re
from pathlib import Path

import pytest

from md2.core import prepare_context
from md2.cli import render_html

REPO_ROOT = Path(__file__).resolve().parents[2]


def _template_css(name):
    """Locate a template's style.css. The default template ships in this
    repo; guidance/forestvalley live in the sibling md2-templates repo
    (source of truth), with the installed ~/.md2 copy as a fallback."""
    if name == "default":
        return (REPO_ROOT / "md2" / "templates" / "default" / "style.css").read_text()
    for candidate in (
        REPO_ROOT.parent / "md2-templates" / name / "style.css",
        Path.home() / ".md2" / "templates" / name / "style.css",
    ):
        if candidate.exists():
            return candidate.read_text()
    return None


CHAPTER_DECK = """+++
title = "Deck"
+++

# Deck cover

Cover subtitle line.

---

:::chapter
# Le applicazioni
Cosa potete **automatizzare**, in concreto
:::

---

## Un punto normale

- primo
- secondo
"""


# (a) a :::chapter slide renders the right structure (title + subtitle only)
def test_chapter_slide_renders_chapter_class_and_parts():
    html = render_html(CHAPTER_DECK)
    assert 'class="slide chapter"' in html
    assert '<h1 class="chapter-title">Le applicazioni</h1>' in html
    assert 'class="chapter-rule"' in html
    # no kicker element is ever emitted
    assert 'chapter-kicker' not in html
    # subtitle goes through the markdown+bleach pipeline (bold survives)
    m = re.search(r'<div class="chapter-subtitle">(.*?)</div>', html, re.DOTALL)
    assert m, "expected a .chapter-subtitle div"
    assert "<strong>automatizzare</strong>" in m.group(1)


def test_chapter_fields_in_context():
    ctx = prepare_context(
        "# Cover\n\n---\n\n:::chapter\n# Title\nSub line\n:::"
    )
    chapter = ctx["slides"][0]
    assert chapter["type"] == "chapter"
    assert chapter["title"] == "Title"      # kept so the sidebar nav shows it
    assert "kicker" not in chapter          # kicker field removed entirely
    assert "Sub line" in chapter["subtitle"]


def test_chapter_title_appears_in_sidebar_nav():
    html = render_html(CHAPTER_DECK)
    assert 'href="#slide-0"' in html        # nav link to the chapter slide
    assert "Le applicazioni" in html        # its title as the nav label


def test_chapter_subtitle_omitted_when_absent():
    """A chapter with a title only (no subtitle) emits no subtitle div."""
    html = render_html("# Cover\n\n---\n\n:::chapter\n# Solo titolo\n:::")
    assert 'class="slide chapter"' in html
    assert '<h1 class="chapter-title">Solo titolo</h1>' in html
    # optional subtitle not emitted; no kicker element anywhere
    assert '<div class="chapter-subtitle">' not in html
    assert 'chapter-kicker' not in html


# (b) an ordinary '## ' slide gets NO chapter class
def test_ordinary_slide_has_no_chapter_class():
    html = render_html(CHAPTER_DECK)
    assert "<h2>Un punto normale</h2>" in html
    assert '<div class="slide" id="slide-1">' in html   # plain .slide, not chapter


# (c) a hero-stat slide (# H1 inside a normal, non-fenced slide) is NOT a chapter
def test_hero_stat_not_misclassified_as_chapter():
    deck = (
        "# Cover\n\nSub.\n\n---\n\n"
        "## The market is exploding\n\n# +50%\n\nItalian AI market YoY growth.\n"
    )
    html = render_html(deck)
    assert 'class="slide chapter"' not in html
    assert '<h1 class="chapter-title">' not in html   # no chapter element emitted
    # the inner `# +50%` still renders as an ordinary <h1> in the slide content
    assert "<h1>+50%</h1>" in html
    assert "<h2>The market is exploding</h2>" in html


# (d) each of the three style.css files has .slide.chapter + print footer kill
@pytest.mark.parametrize("template", ["default", "forestvalley", "guidance"])
def test_style_css_has_chapter_rules_and_print_suppression(template):
    css = _template_css(template)
    assert css is not None, f"could not locate {template}/style.css"
    assert ".slide.chapter" in css, f"{template}: missing .slide.chapter rules"
    assert ".slide.chapter::before" in css and "content: none" in css, (
        f"{template}: missing chapter print footer suppression"
    )
