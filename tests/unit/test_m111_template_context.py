"""M111: template context — front matter, page number, chapter, eyebrow.

A template receives `meta` (the whole front matter, strings HTML-escaped),
`total_pages` (cover + slides) and, per slide, `number`, `chapter`,
`eyebrow`; chapter slides also get `chapter_n` and `chapter_total`.
"""
from pathlib import Path

import pytest

from md2.cli import render_html
from md2.core import BUNDLED_TEMPLATES_DIR, parse_frontmatter, prepare_context


def _context(markdown_text):
    metadata, body = parse_frontmatter(markdown_text)
    return prepare_context(body, metadata=metadata)


# --- meta ---------------------------------------------------------------------

META_DECK = """+++
title = "Deck"
client = "Acme & <Co>"
pages = 12
draft = true
ratio = 1.5
cover_meta = [["Per", "R&D <team>"], ["A cura di", "Guidance"]]

[contact]
name = "Anna \\"AB\\" Bianchi"
+++

# Deck

---

## One
"""


def test_meta_string_values_are_html_escaped():
    meta = _context(META_DECK)["meta"]
    assert meta["client"] == "Acme &amp; &lt;Co&gt;"
    assert meta["title"] == "Deck"


def test_meta_non_string_scalars_keep_their_type():
    meta = _context(META_DECK)["meta"]
    assert meta["pages"] == 12 and type(meta["pages"]) is int
    assert meta["draft"] is True
    assert meta["ratio"] == 1.5


def test_meta_nested_lists_are_escaped_element_by_element():
    meta = _context(META_DECK)["meta"]
    assert meta["cover_meta"] == [
        ["Per", "R&amp;D &lt;team&gt;"],
        ["A cura di", "Guidance"],
    ]


def test_meta_nested_table_strings_are_escaped():
    meta = _context(META_DECK)["meta"]
    assert meta["contact"] == {"name": "Anna &quot;AB&quot; Bianchi"}


def test_meta_is_empty_dict_without_front_matter():
    assert _context("# Deck\n\n---\n\n## One\n")["meta"] == {}


def test_meta_does_not_mutate_the_parsed_front_matter():
    metadata, body = parse_frontmatter(META_DECK)
    prepare_context(body, metadata=metadata)
    assert metadata["client"] == "Acme & <Co>"
    assert metadata["cover_meta"][0][1] == "R&D <team>"


# --- total_pages and number ---------------------------------------------------

CHAPTER_DECK = """# Deck

---

## Before any chapter

---

:::chapter
# Mercato
Sottotitolo
:::

---

## Inside first

---

## Still first

---

:::chapter
# Prodotto
:::

---

## Inside second
"""


def test_total_pages_counts_cover_plus_slides():
    assert _context(CHAPTER_DECK)["total_pages"] == 7


def test_total_pages_is_one_for_a_cover_only_deck():
    ctx = _context("# Only a cover\n\nText.")
    assert ctx["slides"] == []
    assert ctx["total_pages"] == 1


def test_slide_numbers_start_at_two_and_include_chapter_slides():
    numbers = [s["number"] for s in _context(CHAPTER_DECK)["slides"]]
    assert numbers == [2, 3, 4, 5, 6, 7]


# --- chapter ------------------------------------------------------------------

def test_chapter_is_none_before_the_first_chapter():
    assert _context(CHAPTER_DECK)["slides"][0]["chapter"] is None


def test_chapter_slide_points_at_itself():
    slides = _context(CHAPTER_DECK)["slides"]
    assert slides[1]["chapter"] == {"n": 1, "title": "Mercato"}
    assert slides[4]["chapter"] == {"n": 2, "title": "Prodotto"}


def test_ordinary_slides_inherit_the_most_recent_chapter():
    slides = _context(CHAPTER_DECK)["slides"]
    assert [s["chapter"] for s in slides[2:4]] == [{"n": 1, "title": "Mercato"}] * 2
    assert slides[5]["chapter"] == {"n": 2, "title": "Prodotto"}


def test_chapter_slides_carry_their_position_and_the_chapter_count():
    chapters = [s for s in _context(CHAPTER_DECK)["slides"] if s.get("type") == "chapter"]
    assert [(c["chapter_n"], c["chapter_total"]) for c in chapters] == [(1, 2), (2, 2)]


def test_deck_without_chapters_has_no_chapter_on_any_slide():
    slides = _context("# Deck\n\n---\n\n## A\n\n---\n\n## B\n")["slides"]
    assert [s["chapter"] for s in slides] == [None, None]
    assert [s["number"] for s in slides] == [2, 3]


# --- eyebrow ------------------------------------------------------------------

def _single_slide(slide_text):
    return _context(f"# Deck\n\n---\n\n{slide_text}")["slides"][0]


def test_eyebrow_line_above_h2_becomes_slide_eyebrow():
    slide = _single_slide("^ 04 · Mercato\n## Dimensione\n\nCorpo della slide.")
    assert slide["eyebrow"] == "04 · Mercato"
    assert slide["title"] == "Dimensione"


def test_eyebrow_line_is_removed_from_the_content():
    slide = _single_slide("^ 04 · Mercato\n## Dimensione\n\nCorpo della slide.")
    assert "^" not in slide["content"]
    assert "04 · Mercato" not in slide["content"]
    assert "Corpo della slide." in slide["content"]


def test_eyebrow_is_html_escaped():
    slide = _single_slide("^ R&D <lab>\n## Titolo\n\nx")
    assert slide["eyebrow"] == "R&amp;D &lt;lab&gt;"


def test_slide_without_eyebrow_gets_empty_string():
    slide = _single_slide("## Titolo\n\nx")
    assert slide["eyebrow"] == ""


def test_chapter_slide_gets_empty_eyebrow():
    slides = _context(CHAPTER_DECK)["slides"]
    assert slides[1]["eyebrow"] == ""


def test_orphan_caret_line_without_following_h2_stays_text():
    slide = _single_slide("^ solo testo\nAltra riga.")
    assert slide["eyebrow"] == ""
    assert slide["title"] == "Slide 1"
    assert "^ solo testo" in slide["content"]


def test_caret_line_separated_from_h2_by_blank_line_stays_text():
    slide = _single_slide("^ staccato\n\n## Titolo\n\nx")
    assert slide["eyebrow"] == ""
    assert "^ staccato" in slide["content"]


def test_caret_line_after_the_title_stays_text():
    slide = _single_slide("## Titolo\n^ dentro la slide\n\nx")
    assert slide["eyebrow"] == ""
    assert slide["title"] == "Titolo"
    assert "^ dentro la slide" in slide["content"]


# --- render through a throwaway template (Done when) --------------------------

PROBE_TEMPLATE = (
    "CLIENT={{ meta.client }}\n"
    "{% for slide in slides %}"
    "[{{ slide.number }}/{{ total_pages }}|{{ slide.chapter.title }}"
    "|{{ slide.eyebrow }}|{{ slide.title }}]\n"
    "{% endfor %}"
)

PROBE_DECK = """+++
title = "Deck"
client = "Acme & Co"
+++

# Deck

Cover.

---

^ Premessa
## Intro

Testo.

---

:::chapter
# Mercato
:::

---

^ 01 · Mercato
## Dimensione

x

---

## Concorrenti

y
"""


@pytest.fixture
def probe_template(tmp_path):
    template_dir = tmp_path / "probe"
    template_dir.mkdir()
    (template_dir / "base.html").write_text(PROBE_TEMPLATE, encoding="utf-8")
    return template_dir


def test_probe_template_prints_meta_number_chapter_and_eyebrow(probe_template):
    out = render_html(PROBE_DECK, template_dir=probe_template)
    assert out.splitlines() == [
        "CLIENT=Acme &amp; Co",
        "[2/5||Premessa|Intro]",
        "[3/5|Mercato||Mercato]",
        "[4/5|Mercato|01 · Mercato|Dimensione]",
        "[5/5|Mercato||Concorrenti]",
    ]


# --- default template: print page counter -------------------------------------

PRINT_PAGE_NUMBER_BLOCK = """
/* Print: one slide = one page, and every content page carries its number bottom-right.
   The cover is excluded from the count, so the number a reader sees matches the number a
   cross-reference in the text points at. Mirrors the forestvalley and guidance templates. */
@media print {
    .slide { position: relative; counter-increment: pagenum; }
    #main { counter-reset: pagenum; }
    .cover { counter-increment: none; }
    .slide::after {
        content: counter(pagenum);
        position: absolute; right: 0; bottom: 6mm;
        font-size: 9pt; color: #6a7282;
    }
    .cover::after { content: none; }
    .slide.chapter { counter-increment: none; }
    .slide.chapter::after { content: none; }
}
"""


def test_default_style_css_carries_the_print_page_number_block():
    css = (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")
    assert PRINT_PAGE_NUMBER_BLOCK in css


def test_default_markup_matches_the_print_counter_selectors():
    html_out = render_html(CHAPTER_DECK, template_dir=BUNDLED_TEMPLATES_DIR)
    assert '<div id="main">' in html_out
    assert '<div class="slide cover" id="cover">' in html_out
    assert html_out.count('<div class="slide chapter"') == 2
    assert html_out.count('<div class="slide" id="slide-') == 4
