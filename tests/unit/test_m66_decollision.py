"""M66: De-collision endpoint labels + area top clipping fix."""
import re

from md2.core import process_markdown


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


# --- Endpoint label de-collision ---

def test_multi_line_labels_staggered_by_rank():
    """Multi-line endpoint labels are always staggered by rank of value.
    Highest value → offset 0, each next by +28px."""
    md = (
        ":::chart line\n"
        "| Q | A | B | C |\n"
        "|---|---|---|---|\n"
        "| 1 | 100 | 100 | 100 |\n"
        "| 2 | 9000 | 9500 | 10000 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Highest (C=10000) has offset 0 (implicit — no inline style)
    # Next (B=9500) has offset 28px
    # Lowest (A=9000) has offset 56px
    assert "--label-offset: 28px" in html
    assert "--label-offset: 56px" in html


def test_multi_line_top_rank_no_offset():
    """The highest-value series has no --label-offset (0 is implicit)."""
    md = (
        ":::chart line\n"
        "| Q | Low | High |\n"
        "|---|-----|------|\n"
        "| 1 | 5 | 100 |\n"
        "| 2 | 10 | 200 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Rank 1 (Low) gets offset 28px
    assert "--label-offset: 28px" in html
    # Rank 0 (High) has no label-offset inline (0 is default from CSS var fallback)


def test_single_line_no_offset_logic():
    """Single-line chart doesn't need offset (no multi-series collision)."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        "| 2 | 200 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Single-line has labels for all points — no need for collision offset
    assert html.count('<span class="data">') == 2


# --- Area top clipping ---

def test_line_area_wrapper_padding_top_increased():
    """Wrapper padding-top for line/area is sufficient for translateY(-110%)."""
    css = _get_style_css()
    # Find :has(line/area) wrapper padding
    match = re.search(
        r':has\([^)]*\.(?:line|area)[^)]*\)[^{]*\{[^}]*padding-top:\s*(\d+)px',
        css,
    )
    assert match
    val = int(match.group(1))
    assert val >= 48, f"Wrapper padding-top should be >= 48px for line/area, got {val}px"
