"""M67: Graduated Y-axis for line/area charts."""
import re

from md2.core import process_markdown, _nice_ticks


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


# --- Nice ticks algorithm ---

def test_nice_ticks_round_number():
    """_nice_ticks(10000) returns 5 values from 0 to ~10000."""
    ticks = _nice_ticks(10000)
    assert len(ticks) == 5
    assert ticks[0] == 0
    assert ticks[-1] >= 10000
    # Ticks should be monotonically increasing
    assert all(ticks[i] < ticks[i+1] for i in range(4))


def test_nice_ticks_25000():
    """_nice_ticks(25000) returns nice round values."""
    ticks = _nice_ticks(25000)
    assert ticks[0] == 0
    assert ticks[-1] >= 25000
    # Step should be a "nice" number (1, 2, 5, 10, 25, 50 × 10^n)
    step = ticks[1] - ticks[0]
    # 25000 / 4 = 6250 → nice step could be 10000 or 7500
    assert step in (5000, 7500, 10000)


def test_nice_ticks_small_value():
    """_nice_ticks(50) handles small values."""
    ticks = _nice_ticks(50)
    assert ticks[0] == 0
    assert ticks[-1] >= 50


def test_nice_ticks_100():
    """_nice_ticks(100) returns [0, 25, 50, 75, 100] or similar."""
    ticks = _nice_ticks(100)
    assert ticks[0] == 0
    assert ticks[-1] >= 100


# --- Y-axis HTML generation ---

def test_line_chart_has_yaxis_div():
    """Line chart HTML contains md2-chart-yaxis div with tick spans."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        "| 2 | 250 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-chart-yaxis"' in html


def test_line_chart_yaxis_has_5_ticks():
    """Y-axis div has 5 span elements for tick labels."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        "| 2 | 500 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Find the yaxis block
    match = re.search(r'<div class="md2-chart-yaxis">(.+?)</div>', html, re.DOTALL)
    assert match
    spans = re.findall(r'<span[^>]*>([^<]*)</span>', match.group(1))
    assert len(spans) == 5


def test_area_chart_has_yaxis_div():
    """Area chart HTML also has Y-axis."""
    md = (
        ":::chart area\n"
        "| T | V |\n"
        "|---|---|\n"
        "| 1 | 30 |\n"
        "| 2 | 60 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-chart-yaxis"' in html


def test_bar_chart_no_yaxis_div():
    """Bar chart does NOT get Y-axis (it has built-in labels on bars)."""
    md = (
        ":::chart bar\n"
        "| M | V |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'md2-chart-yaxis' not in html


# --- Charts.css axis classes applied ---

def test_line_has_axis_classes():
    """Line chart table has show-primary-axis and show-secondary-axes classes."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        "| 2 | 200 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "show-primary-axis" in html
    assert "show-4-secondary-axes" in html


def test_line_hides_inline_data():
    """Line chart uses hide-data class (inline values hidden, Y-axis shows scale)."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        "| 2 | 200 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "hide-data" in html


# --- Multi-dataset gets standard legend back ---

def test_multi_line_has_legend():
    """Multi-line chart has classic legend (M67 restores it after M65 removal)."""
    md = (
        ":::chart line\n"
        "| Q | A | B |\n"
        "|---|---|---|\n"
        "| 1 | 100 | 200 |\n"
        "| 2 | 300 | 400 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "charts-css legend" in html
    # And no more "Name: Value" endpoint format
    assert "A: 300" not in html


# --- CSS cleanup ---

def test_css_has_yaxis_styling():
    """CSS contains .md2-chart-yaxis styling."""
    css = _get_style_css()
    assert ".md2-chart-yaxis" in css


def test_css_no_more_endpoint_translate_hack():
    """CSS no longer has translate(6px, calc(-50% + var(--label-offset))) hack."""
    css = _get_style_css()
    assert "--label-offset" not in css


def test_css_wrapper_no_more_big_padding():
    """Wrapper padding-top no longer 56px for line/area (phantom card fix)."""
    css = _get_style_css()
    # Find :has(line/area) rule
    match = re.search(
        r':has\([^)]*\.(?:line|area)[^)]*\)\s*,?\s*[^{]*\{([^}]*)\}',
        css,
    )
    if match:
        block = match.group(1)
        # Should not have padding-top: 56px anymore
        assert "56px" not in block or "padding-top" not in block
