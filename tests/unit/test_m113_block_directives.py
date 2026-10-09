"""M113: block directives `:::take`, `:::source`, `:::timeline` and `:::statement` slides.

A block directive wraps its rendered inner markdown in `<div class="md2-<name>">`,
with `<div class="md2-label">` first when the opening line carries a label. A
`:::statement` fence covering a whole slide makes a slide of type "statement".
"""
import pytest

from md2.cli import render_html
from md2.core import BUNDLED_TEMPLATES_DIR, prepare_context, process_markdown
from tests.unit.test_m112_columns_cards import _default_css_rules


def _html(markdown_text):
    return process_markdown(markdown_text)[0]


# --- block containers ---------------------------------------------------------

def test_take_without_label_wraps_the_rendered_markdown():
    html = _html(":::take\n**Tre** mercati su cinque\n:::")
    assert '<div class="md2-take"><p><strong>Tre</strong> mercati su cinque</p></div>' in html
    assert "md2-label" not in html
    assert ":::" not in html


def test_take_with_label_puts_the_label_first():
    html = _html(":::take Il punto\nTesto del box\n:::")
    assert (
        '<div class="md2-take"><div class="md2-label">Il punto</div>'
        '<p>Testo del box</p></div>'
    ) in html


def test_label_is_html_escaped():
    html = _html(":::take R&D <b>bold</b>\nTesto\n:::")
    assert '<div class="md2-label">R&amp;D &lt;b&gt;bold&lt;/b&gt;</div>' in html
    assert "<b>" not in html


@pytest.mark.parametrize("name", ["take", "source", "timeline"])
def test_each_block_name_accepts_a_label(name):
    html = _html(f":::{name} Etichetta\n- uno\n:::")
    assert f'<div class="md2-{name}"><div class="md2-label">Etichetta</div><ul>' in html


def test_source_block():
    html = _html(":::source\nFonte: ISTAT, 2025\n:::")
    assert '<div class="md2-source"><p>Fonte: ISTAT, 2025</p></div>' in html


def test_timeline_renders_its_ordered_list():
    html = _html(":::timeline\n1. Analisi\n2. Pilota\n3. Rollout\n:::")
    assert '<div class="md2-timeline"><ol>' in html
    assert html.count("<li>") == 3
    assert "<li>Rollout</li>" in html


def test_bullet_list_inside_a_take_is_rendered():
    html = _html(":::take\n- primo\n- secondo\n:::")
    assert '<div class="md2-take"><ul>' in html
    assert html.count("<li>") == 2


def test_unknown_directive_name_stays_text():
    html = _html(":::sidebar\nciao\n:::")
    assert "md2-sidebar" not in html
    assert ":::sidebar" in html


def test_name_with_a_whitelisted_prefix_is_not_a_directive():
    html = _html(":::takeaway\nciao\n:::")
    assert "md2-take" not in html
    assert ":::takeaway" in html


def test_unclosed_block_stays_text():
    html = _html(":::take\nnessuna chiusura")
    assert "md2-take" not in html
    assert ":::take" in html


def test_empty_block_renders_an_empty_div():
    html = _html("prima\n\n:::take\n:::\n\ndopo")
    assert '<div class="md2-take"></div>' in html
    assert "<p>dopo</p>" in html


def test_block_directly_under_a_paragraph_line_is_still_a_block():
    html = _html("Testo introduttivo\n:::take\nIl punto\n:::")
    assert '<div class="md2-take"><p>Il punto</p></div>' in html
    assert "<p>Testo introduttivo" in html
    assert "<p><div" not in html


def test_several_blocks_in_one_slide_close_independently():
    md = (
        ":::take Il punto\nPrimo box\n:::\n\n"
        "Tra i blocchi\n\n"
        ":::timeline\n1. Uno\n2. Due\n:::\n\n"
        ":::source\nFonte: interna\n:::"
    )
    html = _html(md)
    assert html.count('class="md2-take"') == 1
    assert html.count('class="md2-timeline"') == 1
    assert html.count('class="md2-source"') == 1
    assert "<p>Tra i blocchi</p>" in html
    take_end = html.index("Primo box</p></div>")
    assert take_end < html.index("Tra i blocchi") < html.index('class="md2-timeline"')
    assert ":::" not in html


def test_block_inside_a_col_keeps_all_three_columns():
    md = (
        ":::columns cards\n\n"
        ":::col\n:::take Il punto\n**A1** nel box\n:::\n\ndopo il box\n\n"
        ":::col\nB2\n\n"
        ":::col\nC3\n\n"
        ":::"
    )
    html = _html(md)
    assert '<div class="md2-columns md2-cols-3 cards">' in html
    assert html.count('class="md2-col"') == 3
    take = html.index('<div class="md2-take"><div class="md2-label">Il punto</div>')
    second_col = html.index('<div class="md2-col"><p>B2</p></div>')
    assert take < html.index("<p>dopo il box</p>") < second_col
    assert "<strong>A1</strong>" in html
    assert "C3" in html
    assert ":::" not in html


def test_charts_still_render_next_to_a_block():
    md = ":::take\nNota\n:::\n\n:::chart bar\n| A | B |\n|---|---|\n| x | 5 |\n:::"
    html, has_charts = process_markdown(md)
    assert has_charts is True
    assert 'class="md2-take"' in html
    assert "charts-css" in html


# --- :::statement slides --------------------------------------------------------

def _slides(markdown_text):
    return prepare_context(markdown_text)["slides"]


STATEMENT_DECK = """# Deck

---

:::statement
Il **70%** dei clienti arriva dal web.
Il resto dal passaparola.
:::
"""


def test_statement_fence_makes_a_statement_slide():
    slide = _slides(STATEMENT_DECK)[0]
    assert slide["type"] == "statement"
    assert "<strong>70%</strong>" in slide["content"]
    assert ":::" not in slide["content"]


def test_statement_sidebar_title_is_the_first_line_as_plain_text():
    assert _slides(STATEMENT_DECK)[0]["title"] == "Il 70% dei clienti arriva dal web."


@pytest.mark.parametrize("inner, title", [
    ("# 70%\ndei clienti", "70%"),
    ("1. Primo punto\n2. Secondo", "Primo punto"),
    ("Vedi [il report](https://example.com) completo", "Vedi il report completo"),
])
def test_statement_title_drops_markdown_markers(inner, title):
    deck = f"# Deck\n\n---\n\n:::statement\n{inner}\n:::"
    assert _slides(deck)[0]["title"] == title


def test_statement_title_stops_at_the_end_of_a_block_label():
    deck = "# Deck\n\n---\n\n:::statement\n:::take Il punto\nTesto del box\n:::\n:::"
    assert _slides(deck)[0]["title"] == "Il punto"


def test_statement_title_is_html_escaped():
    deck = "# Deck\n\n---\n\n:::statement\nR&D vale 5 > 3\n:::"
    assert _slides(deck)[0]["title"] == "R&amp;D vale 5 &gt; 3"


def test_statement_without_text_falls_back_to_slide_n():
    deck = "# Deck\n\n---\n\n## Uno\n\n---\n\n:::statement\n![](grafico.png)\n:::"
    slide = _slides(deck)[1]
    assert slide["type"] == "statement"
    assert slide["title"] == "Slide 2"


def test_statement_can_hold_a_source_block():
    deck = "# Deck\n\n---\n\n:::statement\nFrase forte.\n\n:::source\nFonte: ISTAT\n:::\n:::"
    slide = _slides(deck)[0]
    assert slide["type"] == "statement"
    assert '<div class="md2-source"><p>Fonte: ISTAT</p></div>' in slide["content"]
    assert slide["title"] == "Frase forte."


def test_statement_fence_inside_an_ordinary_slide_is_not_a_statement():
    slide = _slides("# Deck\n\n---\n\n## Titolo\n\n:::statement\nx\n:::")[0]
    assert "type" not in slide
    assert slide["title"] == "Titolo"


CHAPTER_AND_STATEMENT_DECK = """# Deck

---

:::chapter
# Mercato
:::

---

:::statement
Il mercato cresce.
:::

---

## Dettaglio
"""


def test_statement_slide_keeps_the_common_template_fields():
    context = prepare_context(CHAPTER_AND_STATEMENT_DECK)
    chapter, statement, detail = context["slides"]
    assert statement["type"] == "statement"
    assert statement["id"] == "slide-1"
    assert statement["number"] == 3
    assert statement["eyebrow"] == ""
    assert statement["chapter"] == {"n": 1, "title": "Mercato"}
    assert detail["number"] == 4
    assert detail["chapter"] is chapter["chapter"]
    assert context["total_pages"] == 4
    assert chapter["chapter_total"] == 1


# --- default template -----------------------------------------------------------

def test_default_template_renders_a_statement_slide_without_h2():
    out = render_html(CHAPTER_AND_STATEMENT_DECK, template_dir=BUNDLED_TEMPLATES_DIR)
    start = out.index('<div class="slide statement" id="slide-1">')
    end = out.index('id="slide-2"')
    statement_markup = out[start:end]
    assert "<h2>" not in statement_markup
    assert "<p>Il mercato cresce.</p>" in statement_markup
    assert '<a href="#slide-1">Il mercato cresce.</a>' in out


def test_default_template_renders_the_four_constructs():
    deck = (
        "# Deck\n\n---\n\n## Sintesi\n\n"
        ":::take Il punto\nTre **mercati**\n:::\n\n"
        ":::timeline\n1. Analisi\n2. Pilota\n:::\n\n"
        ":::source\nFonte: interna\n:::\n\n---\n\n"
        ":::statement\nUna frase.\n:::\n"
    )
    out = render_html(deck, template_dir=BUNDLED_TEMPLATES_DIR)
    assert '<div class="md2-take"><div class="md2-label">Il punto</div><p>Tre <strong>mercati</strong></p></div>' in out
    assert '<div class="md2-timeline"><ol>' in out
    assert '<div class="md2-source"><p>Fonte: interna</p></div>' in out
    assert '<div class="slide statement" id="slide-1">' in out
    assert ":::" not in out.split("<body", 1)[1]


# --- default template CSS -------------------------------------------------------

def _decls(selector, media=None):
    merged = {}
    for rule_media, sels, decls in _default_css_rules():
        if rule_media == media and selector in sels:
            merged.update(decls)
    return merged


def test_css_take_is_a_tinted_box_with_a_left_accent():
    decls = _decls(".md2-take")
    assert {"background", "background-color"} & decls.keys()
    assert "border-left" in decls


def test_css_label_is_small_uppercase():
    decls = _decls(".md2-label")
    assert decls.get("text-transform") == "uppercase"
    assert "font-size" in decls


def test_css_source_is_a_small_secondary_line():
    decls = _decls(".slide .md2-source p")
    assert "font-size" in decls
    assert {"opacity", "color"} & decls.keys()


def test_css_timeline_lays_its_list_out_in_a_row():
    decls = _decls(".md2-timeline > ol")
    assert decls.get("display") == "flex"
    assert decls.get("list-style") == "none"


def test_css_statement_slide_has_its_own_rule():
    assert _decls(".slide.statement")
    assert "font-size" in _decls(".slide.statement .content > p")


def test_css_take_prints_on_white():
    decls = _decls(".md2-take", media="print")
    assert decls.get("background", "").startswith("#fff")


def test_css_narrow_screen_stacks_the_timeline():
    decls = _decls(".md2-timeline > ol", media="screen and (max-width: 768px)")
    assert decls.get("flex-direction") == "column"
