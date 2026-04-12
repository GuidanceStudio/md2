"""M62-M63: Data pill z-index + multi-line/area legend spacing."""
import re


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


# --- M62 ---

def test_line_data_has_z_index():
    """Line chart .data has z-index so pill is above sibling td colors."""
    css = _get_style_css()
    # Find a rule for .line .data with z-index
    assert re.search(
        r'\.line \.data[^{]*\{[^}]*z-index',
        css,
    )


def test_area_data_has_z_index():
    """Area chart .data has z-index."""
    css = _get_style_css()
    assert re.search(
        r'\.area \.data[^{]*\{[^}]*z-index',
        css,
    )


def test_line_area_data_position_relative():
    """Line/area .data uses position relative for z-index to take effect."""
    css = _get_style_css()
    # There must be a rule applying position: relative to .line/.area .data
    # (z-index requires a positioned element)
    match = re.search(
        r'\.(line|area) \.data[^{]*\{([^}]+)\}',
        css,
    )
    assert match
    block = match.group(2)
    assert "position" in block and "relative" in block


# --- M63 ---

def test_multi_line_legend_has_large_margin():
    """Multi-dataset line/area legend has large margin-top to clear x-labels."""
    css = _get_style_css()
    # Should have a selector for .md2-chart:has(.line.multiple/.area.multiple) ul.legend
    # with margin-top >= 60px
    assert re.search(
        r':has\([^)]*\.(line|area)\.multiple[^)]*\)[^{]*ul\.legend[^{]*\{[^}]*margin-top:\s*(\d+)px',
        css,
    ) or re.search(
        r':has\([^)]*\.multiple\.(line|area)[^)]*\)[^{]*ul\.legend[^{]*\{[^}]*margin-top:\s*(\d+)px',
        css,
    ), "Multi-line/area legend needs large margin-top to clear x-axis labels"
