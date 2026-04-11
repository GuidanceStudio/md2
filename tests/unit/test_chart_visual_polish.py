"""Tests for M37: Chart visual polish — frame, padding, data text color."""


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_chart_wrapper_has_box_shadow():
    """Chart wrapper has box-shadow like tables."""
    css = _get_style_css()
    # .md2-chart should have box-shadow
    assert "md2-chart" in css
    assert "box-shadow" in css.split(".md2-chart")[1].split("}")[0]


def test_chart_wrapper_has_border_radius():
    """Chart wrapper has border-radius like tables."""
    css = _get_style_css()
    chunk = css.split(".md2-chart")[1].split("}")[0]
    assert "border-radius" in chunk


def test_chart_wrapper_has_padding():
    """Chart wrapper has padding for internal breathing room."""
    css = _get_style_css()
    chunk = css.split(".md2-chart")[1].split("}")[0]
    assert "padding" in chunk


def test_data_text_is_white():
    """Data text (.data) inside charts is white for contrast on colored bars."""
    css = _get_style_css()
    assert ".data" in css
    # Find the .data rule inside chart context
    data_idx = css.index(".md2-chart")
    chart_css = css[data_idx:]
    assert "color:" in chart_css
    assert "#fff" in chart_css or "white" in chart_css


def test_data_text_has_shadow():
    """Data text has text-shadow for readability on any background."""
    css = _get_style_css()
    assert "text-shadow" in css
