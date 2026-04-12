"""M55: X-axis labels not clipped by wrapper overflow."""


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_chart_wrapper_no_overflow_hidden():
    """Chart wrapper does not use overflow: hidden (would clip x-axis labels)."""
    css = _get_style_css()
    idx = css.index(".md2-chart {")
    block = css[idx:css.index("}", idx) + 1]
    assert "overflow: hidden" not in block


def test_chart_title_has_border_radius_top():
    """Chart title has border-radius top to match wrapper rounded corners.

    Without wrapper overflow:hidden, the title needs its own top border-radius.
    """
    css = _get_style_css()
    idx = css.index(".md2-chart-title")
    block = css[idx:css.index("}", idx) + 1]
    assert "border-radius" in block
