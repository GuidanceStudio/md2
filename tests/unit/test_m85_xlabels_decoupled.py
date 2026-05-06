"""M85: X-axis labels for column/bar are decoupled into a sibling
`<div class="md2-chart-xlabels">`, like line/area in M70.

This guarantees X labels are at the visual bottom of the chart card —
not interleaved with negative bars or occluded by the legend.
"""
import re

from md2.core import process_markdown


def test_column_chart_emits_xlabels_div():
    """Column chart HTML contains a `<div class="md2-chart-xlabels">`."""
    md = (
        ":::chart column\n"
        "| M | V |\n"
        "|---|---|\n"
        "| Mag | 100 |\n"
        "| Giu | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-chart-xlabels"' in html


def test_column_xlabels_div_contains_one_span_per_category():
    """Each category label appears as a `<span>` inside the xlabels div."""
    md = (
        ":::chart column\n"
        "| M | V |\n"
        "|---|---|\n"
        "| Mag | 100 |\n"
        "| Giu | 50 |\n"
        "| Lug | 75 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    match = re.search(r'<div class="md2-chart-xlabels">(.+?)</div>', html, re.DOTALL)
    assert match
    spans = re.findall(r'<span[^>]*>([^<]*)</span>', match.group(1))
    assert spans == ["Mag", "Giu", "Lug"]


def test_column_css_sets_labels_size_zero():
    """When X labels are decoupled (M85), the CSS sets `--labels-size: 0`
    on `.charts-css.column` so Charts.css doesn't reserve internal space."""
    from md2.core import BUNDLED_TEMPLATES_DIR
    css = (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")
    # Find the .md2-chart .charts-css.column rule
    match = re.search(
        r'\.md2-chart \.charts-css\.column\s*\{([^}]+)\}', css, re.DOTALL,
    )
    assert match, "expected .md2-chart .charts-css.column rule"
    body = match.group(1)
    assert "--labels-size: 0" in body, (
        f"expected --labels-size: 0 in column CSS rule, got: {body!r}"
    )


def test_column_th_scope_row_removed():
    """The decoupled X labels mean rows no longer carry `<th scope="row">`
    text content — the categorical label text lives in the xlabels div."""
    md = (
        ":::chart column\n"
        "| M | V |\n"
        "|---|---|\n"
        "| Mag | 100 |\n"
        "| Giu | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # The <th scope="row"> still exists structurally (for a11y) but its
    # text content is empty (mirrors line/area pattern from M70).
    th_matches = re.findall(r'<th scope="row">([^<]*)</th>', html)
    # All scope=row should be empty (or absent)
    for content in th_matches:
        assert content.strip() == "", (
            f"<th scope=\"row\"> should be empty after decoupling, "
            f"got {content!r}"
        )


def test_bar_chart_also_decoupled():
    """Bar chart (horizontal) gets the same xlabels decoupling."""
    md = (
        ":::chart bar\n"
        "| C | V |\n"
        "|---|---|\n"
        "| A | 10 |\n"
        "| B | 20 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-chart-xlabels"' in html


def test_line_area_xlabels_unchanged():
    """Backward compat: line/area xlabels (already decoupled in M70) keep
    their behavior — span per data point with category label."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        "| 2 | 200 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-chart-xlabels"' in html
    match = re.search(r'<div class="md2-chart-xlabels">(.+?)</div>', html, re.DOTALL)
    spans = re.findall(r'<span[^>]*>([^<]*)</span>', match.group(1))
    assert spans == ["1", "2"]


def test_pie_chart_no_xlabels():
    """Pie charts must NOT get xlabels — their categories are in the
    legend, not on an axis."""
    md = (
        ":::chart pie\n"
        "| C | V |\n"
        "|---|---|\n"
        "| A | 30 |\n"
        "| B | 70 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-chart-xlabels"' not in html
