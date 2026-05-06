"""M84: chart `--title "..."` directive must populate the chart title.

Today the directive is silently ignored — only a `# heading` inside the
chart block sets the title. M84 wires `--title` through `_parse_chart_options`
so users can use either form.
"""
from md2.core import process_markdown


def test_title_directive_renders_chart_title():
    """A `:::chart column --title "Hello (€)"` directive produces a
    `<div class="md2-chart-title">Hello (€)</div>` in the rendered HTML."""
    md = (
        ':::chart column --title "Hello (€)"\n'
        "| A | V |\n"
        "|---|---|\n"
        "| x | 10 |\n"
        "| y | 20 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<div class="md2-chart-title">Hello (€)</div>' in html, (
        f"expected chart title in output, got:\n{html}"
    )


def test_title_directive_preserves_unicode_and_case():
    """The title preserves original casing and unicode chars; the
    pre-M84 behavior `.lower()` destroyed both."""
    md = (
        ':::chart column --title "Crediti 2026 — fascia (€)"\n'
        "| A | V |\n"
        "|---|---|\n"
        "| x | 10 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "Crediti 2026 — fascia (€)" in html, (
        f"title should preserve casing and unicode, got:\n{html}"
    )


def test_heading_inside_block_still_works():
    """Backward compat: `# heading` inside the chart block continues to
    set the title."""
    md = (
        ":::chart column\n"
        "# Heading title\n"
        "| A | V |\n"
        "|---|---|\n"
        "| x | 10 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<div class="md2-chart-title">Heading title</div>' in html


def test_directive_title_wins_over_heading():
    """If both `--title "X"` and `# Y` are present, the directive wins
    (more explicit)."""
    md = (
        ':::chart column --title "Directive wins"\n'
        "# Heading should be ignored\n"
        "| A | V |\n"
        "|---|---|\n"
        "| x | 10 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<div class="md2-chart-title">Directive wins</div>' in html
    assert "Heading should be ignored" not in html


def test_no_title_no_title_div():
    """Backward compat: a chart without title and without heading does
    NOT emit a chart-title div."""
    md = (
        ":::chart column\n"
        "| A | V |\n"
        "|---|---|\n"
        "| x | 10 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-chart-title"' not in html
