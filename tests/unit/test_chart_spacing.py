"""Tests for M41: Chart spacing — gap label/bars, row/group spacing, legend."""


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_bar_label_gap_increased():
    """Bar chart labels have enough gap from bars (>= 110px)."""
    import re
    css = _get_style_css()
    # Find the .bar --labels-size rule
    match = re.search(r'\.charts-css\.bar[^{]*\{[^}]*--labels-size:\s*(\d+)', css)
    assert match, "Bar chart should have --labels-size"
    assert int(match.group(1)) >= 110


def test_chart_data_spacing_set():
    """--data-spacing is set for row/group separation."""
    css = _get_style_css()
    assert "--data-spacing" in css


def test_legend_has_margin_top():
    """Legend has margin-top to avoid overlap with axis labels."""
    css = _get_style_css()
    legend_idx = css.index("md2-chart ul.legend") if "md2-chart ul.legend" in css else css.index(".legend")
    block = css[legend_idx:css.index("}", legend_idx) + 1]
    assert "margin-top" in block
    # Should be at least 20px
    import re
    match = re.search(r'margin-top:\s*(\d+)px', block)
    if match:
        assert int(match.group(1)) >= 20
