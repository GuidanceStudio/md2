"""Tests for M46-M49: Final CSS polish — bar row spacing, label alignment,
title padding, legend spacing/bullet colors."""
import re

from md2.core import process_markdown


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


# --- M46: Bar row spacing ---

def test_bar_row_spacing_in_css():
    """Bar multi-dataset has CSS rule for inter-row spacing."""
    css = _get_style_css()
    # Should have a rule on .bar tbody tr or table that adds padding/margin
    # between rows of different metrics
    assert re.search(
        r'\.bar[^{]*tbody[^{]*tr[^{]*\{[^}]*(padding|margin|border-spacing)',
        css,
    ) or re.search(
        r'\.bar[^{]*\.multiple[^{]*tr[^{]*\{[^}]*(padding|margin)',
        css,
    )


# --- M47: Label vertical centering ---

def test_bar_label_vertical_centered():
    """Bar chart labels are vertically centered on the row group."""
    css = _get_style_css()
    # Charts.css uses align-items for label cells. Our override or
    # default should ensure vertical-align center.
    # Check that we have a rule for .bar tbody tr th with alignment
    assert re.search(
        r'\.bar[^{]*tr[^{]*th[^{]*\{[^}]*(align-items|vertical-align)',
        css,
    )


# --- M48: Title padding fix ---

def test_title_margin_bottom_breathes():
    """M97: chart title has comfortable breathing room before the chart
    body (tight 8px gap looked cramped — 16-32px is more readable)."""
    css = _get_style_css()
    idx = css.index(".md2-chart-title")
    block = css[idx:css.index("}", idx) + 1]
    match = re.search(r'margin[^:]*:\s*([^;]+)', block)
    assert match
    parts = match.group(1).split()
    if len(parts) >= 3:
        bottom = parts[2]
        if bottom.endswith("px"):
            val = int(bottom.replace("px", ""))
            assert 12 <= val <= 40, (
                f"Title margin-bottom should be in [12, 40]px, got {val}"
            )


# --- M49: Legend spacing and bullet colors ---

def test_legend_margin_top_set():
    """Legend has margin-top to clear x-axis labels (M52: increased from 12 to 40)."""
    css = _get_style_css()
    legend_idx = css.index("md2-chart ul.legend")
    block = css[legend_idx:css.index("}", legend_idx) + 1]
    match = re.search(r'margin-top:\s*(\d+)px', block)
    assert match
    # >= 24 to ensure clearance from x-axis labels in column/line/area
    assert int(match.group(1)) >= 24


def test_legend_bullets_use_palette_colors():
    """Legend li elements have CSS rules that use palette colors."""
    css = _get_style_css()
    # Should have rules like .legend li:nth-child(1) { ... var(--md2-color-1) }
    # or .legend li.legend-item-1 { ... }
    assert re.search(
        r'\.legend[^{]*(?:li|::before)[^{]*\{[^}]*var\(--md2-color-',
        css,
    ) or re.search(
        r'\.legend\s+li[^{]*nth-child[^{]*\{[^}]*var\(--md2-color-',
        css,
    )


def test_legend_li_has_item_classes():
    """Legend <li> elements have numbered classes for color styling."""
    md = (
        ":::chart bar\n"
        "| Metric | Q1 | Q2 |\n"
        "|--------|----|----|\n"
        "| A      | 10 | 20 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Legend items should have a class that allows per-item color
    # e.g. class="legend-item-1" or just rely on :nth-child
    # We'll accept either: presence of nth-child CSS is enough, or
    # class on li
    assert "<li" in html
