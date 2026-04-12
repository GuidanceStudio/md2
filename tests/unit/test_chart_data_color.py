"""Tests for M42: .data color per chart type."""
import re


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_bar_data_is_white():
    """Bar chart .data has white color (text inside bars)."""
    css = _get_style_css()
    # Find a rule .bar .data or .md2-chart .charts-css.bar .data
    assert re.search(r'\.bar[^{]*\.data[^{]*\{[^}]*#fff', css) \
        or re.search(r'\.bar\s+\.data[^{]*\{[^}]*#fff', css)


def test_pie_data_is_white():
    """Pie chart .data has white color."""
    css = _get_style_css()
    assert re.search(r'\.pie[^{]*\.data[^{]*\{[^}]*#fff', css) \
        or re.search(r'\.pie\s+\.data[^{]*\{[^}]*#fff', css)


def test_line_area_hidden_data_via_class():
    """Line/area use Charts.css .hide-data class (M67 graduated Y-axis replaces inline labels)."""
    from md2.core import process_markdown
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "hide-data" in html


def test_no_generic_data_color_rule():
    """There's no generic .md2-chart .data rule — it's per type."""
    css = _get_style_css()
    # The rule `.md2-chart .data` applied to all chart types is removed
    generic_match = re.search(r'\.md2-chart\s+\.data\s*\{', css)
    assert generic_match is None, \
        "Generic .md2-chart .data rule should not exist (must be per-type)"
