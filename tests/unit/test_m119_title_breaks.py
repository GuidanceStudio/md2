"""M119: `<br>` in cover and chapter titles.

The cover h1 and a chapter slide's own h1 keep the line break; `<title>`,
og:title, og:description and the chapter title every later slide carries
for its eyebrow get plain text, with each `<br>` turned into one space.
"""
import re

import pytest

from md2.cli import render_html
from md2.core import parse_frontmatter, prepare_context


def _deck(title_line, body="---\n\n## Uno\n"):
    return f"{title_line}\n\n{body}"


def _front_matter_deck(title):
    return f'+++\ntitle = "{title}"\n+++\n\n# Ignorato\n\n---\n\n## Uno\n'


def _cover_h1(html):
    return re.search(r'<div class="slide cover" id="cover">\s*<h1>(.*?)</h1>', html, re.DOTALL).group(1)


def _head_title(html):
    return re.search(r"<title>(.*?)</title>", html, re.DOTALL).group(1)


def _og(html, prop):
    return re.search(rf'<meta property="og:{prop}" content="([^"]*)">', html).group(1)


def _context(markdown_text):
    metadata, body = parse_frontmatter(markdown_text)
    return prepare_context(body, metadata=metadata)


# --- cover title ---------------------------------------------------------------

def test_front_matter_title_breaks_on_the_cover_and_is_plain_in_the_head():
    html = render_html(_front_matter_deck("Analisi di mercato<br>Nord Italia"))
    assert _cover_h1(html) == "Analisi di mercato<br>Nord Italia"
    assert _head_title(html) == "Analisi di mercato Nord Italia"
    assert _og(html, "title") == "Analisi di mercato Nord Italia"


def test_cover_h1_title_breaks_on_the_cover_and_is_plain_in_the_head():
    html = render_html(_deck("# Analisi di mercato<br>Nord Italia"))
    assert _cover_h1(html) == "Analisi di mercato<br>Nord Italia"
    assert _head_title(html) == "Analisi di mercato Nord Italia"


@pytest.mark.parametrize("spelling", ["<br/>", "<br />", "<BR>", '<br class="x">'])
def test_every_br_spelling_becomes_one_br_on_the_cover_and_one_space_in_the_head(spelling):
    html = render_html(_deck(f"# Analisi{spelling}Nord"))
    assert _cover_h1(html) == "Analisi<br>Nord"
    assert _head_title(html) == "Analisi Nord"


def test_spaces_around_br_collapse_to_one_space_in_the_head():
    html = render_html(_deck("# Analisi  <br>  Nord"))
    assert _head_title(html) == "Analisi Nord"
    assert _og(html, "title") == "Analisi Nord"


def test_tags_other_than_br_are_removed_from_cover_and_head():
    html = render_html(_front_matter_deck("<em>Analisi</em><br><b>Nord</b>"))
    assert _cover_h1(html) == "Analisi<br>Nord"
    assert _head_title(html) == "Analisi Nord"


def test_script_tag_in_the_title_reaches_neither_cover_nor_head():
    html = render_html(_deck('# Analisi<script>alert(1)</script><img src=x onerror="y()">'))
    for value in (_cover_h1(html), _head_title(html), _og(html, "title")):
        assert "script" not in value
        assert "img" not in value
        assert "onerror" not in value


def test_cover_title_escapes_markup_characters_and_head_escapes_quotes():
    html = render_html(_deck('# R&D "Nord" <br> 5 > 3'))
    assert _cover_h1(html) == 'R&amp;D "Nord" <br> 5 &gt; 3'
    assert _head_title(html) == "R&amp;D &quot;Nord&quot; 5 &gt; 3"
    assert _og(html, "title") == "R&amp;D &quot;Nord&quot; 5 &gt; 3"


def test_title_without_br_is_unchanged():
    html = render_html(_deck("# Report Q1"))
    assert _cover_h1(html) == "Report Q1"
    assert _head_title(html) == "Report Q1"


# --- og:description --------------------------------------------------------------

def test_og_description_falling_back_on_the_title_has_no_br():
    html = render_html(_front_matter_deck("Analisi di mercato<br>Nord Italia"))
    assert _og(html, "description") == "Analisi di mercato Nord Italia"


def test_og_description_from_cover_text_has_no_br():
    html = render_html(_deck("# Titolo\n\nPrima riga<br>seconda riga"))
    assert _og(html, "description") == "Prima riga seconda riga"


# --- chapter titles ----------------------------------------------------------------

CHAPTER_DECK = """# Copertina

---

:::chapter
# Il mercato<br>oggi
Dove siamo
:::

---

## Dimensione
"""


def test_chapter_slide_keeps_the_break_in_its_own_title():
    chapter_slide = _context(CHAPTER_DECK)["slides"][0]
    assert chapter_slide["title"] == "Il mercato<br>oggi"
    html = render_html(CHAPTER_DECK)
    assert '<h1 class="chapter-title">Il mercato<br>oggi</h1>' in html


def test_chapter_title_carried_by_slides_is_plain_text():
    slides = _context(CHAPTER_DECK)["slides"]
    assert [s["chapter"]["title"] for s in slides] == ["Il mercato oggi", "Il mercato oggi"]


def test_chapter_titles_drop_other_tags_and_escape_text():
    deck = "# C\n\n---\n\n:::chapter\n# <b>R&D</b> <br/> <script>x</script>oggi\n:::\n\n---\n\n## Uno\n"
    chapter_slide, plain = _context(deck)["slides"]
    assert chapter_slide["title"] == "R&amp;D <br> xoggi"
    assert plain["chapter"]["title"] == "R&amp;D xoggi"


EYEBROW_TEMPLATE = (
    "{% for slide in slides %}{% if slide.chapter %}"
    '{{ "%02d"|format(slide.chapter.n) }} · {{ slide.chapter.title }}\n'
    "{% endif %}{% endfor %}"
)


def test_eyebrow_built_from_the_chapter_title_reads_on_one_line(tmp_path):
    template_dir = tmp_path / "eyebrow"
    template_dir.mkdir()
    (template_dir / "base.html").write_text(EYEBROW_TEMPLATE, encoding="utf-8")
    out = render_html(CHAPTER_DECK, template_dir=template_dir)
    assert out.splitlines() == ["01 · Il mercato oggi", "01 · Il mercato oggi"]
