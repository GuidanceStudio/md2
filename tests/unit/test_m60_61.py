"""M60-M61: Column white labels + line/area overflow fix."""
import re


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


# --- M60: Column .data white ---

def test_column_data_is_white():
    """Column chart .data has white color (text is inside the colored bar)."""
    css = _get_style_css()
    # Find a rule like ".column .data" with #fff
    assert re.search(
        r'\.column\s+\.data[^{]*\{[^}]*(?:#fff|white)',
        css,
    ), "Column .data should be white"


def test_column_data_not_in_text_color_rule():
    """Column .data should NOT be in the text-color rule (was illegible black)."""
    css = _get_style_css()
    # Find any rule that contains both ".column .data" and "var(--text-color)"
    text_color_blocks = re.findall(
        r'[^{]*\{[^}]*var\(--text-color\)[^}]*\}',
        css,
    )
    for block in text_color_blocks:
        if ".column .data" in block:
            assert False, f"Column .data should not use text-color: {block[:200]}"


# --- M61: Line/area overflow ---

def test_line_no_padding_block_start():
    """Line chart has no padding-block-start (was pushing labels out of card)."""
    css = _get_style_css()
    line_match = re.search(r'\.charts-css\.line\s*\{([^}]*)\}', css)
    assert line_match
    assert "padding-block-start" not in line_match.group(1)


def test_area_no_padding_block_start():
    """Area chart has no padding-block-start."""
    css = _get_style_css()
    area_match = re.search(r'\.charts-css\.area\s*\{([^}]*)\}', css)
    assert area_match
    assert "padding-block-start" not in area_match.group(1)


def test_line_area_uses_flex_body():
    """Line/area use flex body with Y-axis (M67 approach replaces padding hack)."""
    css = _get_style_css()
    assert ".md2-chart-body" in css
    assert ".md2-chart-yaxis" in css
