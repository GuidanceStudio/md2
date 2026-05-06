"""Tests for M41: Chart spacing — gap label/bars, row/group spacing, legend."""


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_bar_chart_uses_decoupled_xlabels():
    """M85: bar chart x-labels are now in a sibling `.md2-chart-xlabels`
    div, so the table's internal `--labels-size` is 0. The previous
    `>= 110px` requirement is obsolete — the gap from bars is provided
    by the sibling div's margin-top instead."""
    import re
    css = _get_style_css()
    match = re.search(
        r'\.md2-chart \.charts-css\.bar\s*\{([^}]+)\}', css, re.DOTALL,
    )
    assert match, "expected .md2-chart .charts-css.bar rule"
    assert "--labels-size: 0" in match.group(1)


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
    # Should be at least 8px for separation
    import re
    match = re.search(r'margin-top:\s*(\d+)px', block)
    if match:
        assert int(match.group(1)) >= 8
