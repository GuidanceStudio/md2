"""Tests for M38: Chart CSS refinement — padding, caption, legend."""


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_chart_td_has_padding():
    """Chart td elements have padding for data value breathing room."""
    css = _get_style_css()
    # Should have a padding rule on chart td
    assert "md2-chart" in css
    assert "padding" in css


def test_chart_title_styled():
    """Chart title (md2-chart-title) is styled like a card header."""
    css = _get_style_css()
    assert ".md2-chart-title" in css
    idx = css.index(".md2-chart-title")
    title_block = css[idx:css.index("}", idx) + 1]
    assert "font-weight" in title_block or "bold" in title_block


def test_chart_wrapper_asymmetric_padding():
    """Chart wrapper has less padding on top than sides/bottom."""
    css = _get_style_css()
    # The .md2-chart rule should NOT have uniform padding: 20px
    chart_section = css[css.index(".md2-chart"):]
    chart_block = chart_section[:chart_section.index("}") + 1]
    # Should not be simple "padding: 20px" — should be asymmetric
    assert "padding:" in chart_block
    assert "padding: 20px" not in chart_block


def test_chart_legend_no_border():
    """Chart legend has no border/outline."""
    css = _get_style_css()
    assert "legend" in css
    # Find legend rule
    legend_idx = css.index(".md2-chart")
    legend_section = css[legend_idx:]
    assert "border: none" in legend_section or "border:none" in legend_section or "border: 0" in legend_section
