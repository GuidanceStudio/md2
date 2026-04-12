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

def test_multi_line_no_legend_at_all():
    """M65 supersedes M63: multi-line/area no longer has any legend at all
    (endpoint labels serve as legend)."""
    from md2.core import process_markdown
    md = (
        ":::chart line\n"
        "| Q | A | B |\n"
        "|---|---|---|\n"
        "| 1 | 100 | 200 |\n"
        "| 2 | 150 | 250 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "charts-css legend" not in html
