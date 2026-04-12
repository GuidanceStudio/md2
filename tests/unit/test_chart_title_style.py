"""Tests for M40: Chart title styling as card header."""


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_chart_title_class_has_style():
    """md2-chart-title class has CSS styling."""
    css = _get_style_css()
    assert ".md2-chart-title" in css


def test_chart_title_has_header_background():
    """Chart title has the same background as table headers."""
    css = _get_style_css()
    idx = css.index(".md2-chart-title")
    block = css[idx:css.index("}", idx) + 1]
    assert "--table-header-bg" in block or "background" in block


def test_chart_title_is_bold():
    """Chart title has bold font weight."""
    css = _get_style_css()
    idx = css.index(".md2-chart-title")
    block = css[idx:css.index("}", idx) + 1]
    assert "font-weight" in block or "bold" in block


def test_chart_title_has_padding():
    """Chart title has padding for breathing room."""
    css = _get_style_css()
    idx = css.index(".md2-chart-title")
    block = css[idx:css.index("}", idx) + 1]
    assert "padding" in block
