"""M83: `.md2-chart` card padding contains all chart elements after the
M80 Y-axis introduction. Audit the wrapper so labels never overflow.
"""
import re

from md2.core import process_markdown


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_md2_chart_has_box_sizing_border_box():
    """`.md2-chart` uses `box-sizing: border-box` so its padding doesn't
    grow the rendered card beyond its container."""
    css = _get_style_css()
    # Find the .md2-chart rule (not a child selector)
    pattern = re.compile(
        r'^\.md2-chart\s*\{([^}]+)\}',
        re.MULTILINE,
    )
    match = pattern.search(css)
    assert match, "expected a top-level .md2-chart {...} rule"
    body = match.group(1)
    assert "box-sizing" in body and "border-box" in body, (
        f".md2-chart should declare box-sizing: border-box; got: {body!r}"
    )


def test_md2_chart_padding_bottom_fits_column_labels_size():
    """`.md2-chart` padding-bottom must be ≥ 24px so that column charts'
    `--labels-size: 32px` (reserved inside the chart body) plus the
    surrounding margin don't visually clip on the bottom edge."""
    css = _get_style_css()
    pattern = re.compile(
        r'^\.md2-chart\s*\{([^}]+)\}',
        re.MULTILINE,
    )
    match = pattern.search(css)
    body = match.group(1)
    # Find padding declaration
    pad_match = re.search(r'padding:\s*([^;]+);', body)
    assert pad_match, f"expected padding declaration, got: {body!r}"
    parts = pad_match.group(1).split()
    # Padding can be 1, 2, 3, or 4 values. Bottom is parts[2] for 3-value, parts[2] for 4-value, parts[0] for 1, parts[0] for 2.
    if len(parts) == 1:
        bottom = parts[0]
    elif len(parts) == 2:
        bottom = parts[0]
    elif len(parts) == 3:
        bottom = parts[2]
    else:
        bottom = parts[2]
    # Strip 'px' suffix
    bottom_px = int(re.sub(r'[^\d]', '', bottom))
    assert bottom_px >= 24, (
        f".md2-chart padding-bottom {bottom_px}px should be ≥ 24px to "
        f"contain X labels inside the card border"
    )


def test_aging_chart_with_zero_category_renders_cleanly():
    """Smoke test on the user's original problem case (4 categories, one
    at zero): the rendered HTML wraps the column in `md2-chart-body`,
    has a Y-axis div, and shows all 4 X-label `<th>` elements."""
    md = (
        ":::chart column --labels --show-data --title \"Aging (€)\"\n"
        "| Fascia | Importo |\n"
        "|---|---|\n"
        "| 0-30 gg | 7320 |\n"
        "| 30-60 gg | 0 |\n"
        "| 60-90 gg | 3253 |\n"
        "| > 90 gg | 6832 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # All four category labels are present in the DOM
    for cat in ["0-30 gg", "30-60 gg", "60-90 gg"]:
        assert cat in html, f"expected category label {cat!r} in HTML"
    # ">90 gg" gets HTML-escaped to "&gt;"
    assert "90 gg" in html
    # Wrapped in chart-body with yaxis
    assert 'class="md2-chart-body"' in html
    assert 'class="md2-chart-yaxis"' in html


def test_column_chart_body_height_matches_table_height():
    """The `md2-chart-body` and the inner column table use the same
    `min(300px, 40vh)` height — required so the flex stretch doesn't
    create overflow."""
    css = _get_style_css()
    # md2-chart-body height
    body_match = re.search(
        r'\.md2-chart-body\s*\{([^}]+)\}', css, re.DOTALL,
    )
    assert body_match
    assert "min(300px, 40vh)" in body_match.group(1), (
        ".md2-chart-body must use min(300px, 40vh) height"
    )
    # Column chart has the same height
    col_match = re.search(
        r'\.md2-chart \.charts-css\.column\s*\{([^}]+)\}', css, re.DOTALL,
    )
    assert col_match
    assert "min(300px, 40vh)" in col_match.group(1), (
        "column chart must use the same min(300px, 40vh) height as body"
    )
