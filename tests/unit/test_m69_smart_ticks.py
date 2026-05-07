"""M69: Smart Y-axis parametrization — nice numbers + clustering detection."""
import re

from md2.core import process_markdown, _nice_ticks


# --- Nice numbers ---

def test_nice_ticks_10000_exact_fit():
    """10000 produces [0, 2500, 5000, 7500, 10000] — exact fit thanks to 2.5 in nice numbers."""
    ticks = _nice_ticks(0, 10000)
    assert ticks == [0, 2500, 5000, 7500, 10000]


def test_nice_ticks_25000_minimal_headroom():
    """25000 produces [0, 7500, 15000, 22500, 30000] — 20% headroom."""
    ticks = _nice_ticks(0, 25000)
    assert ticks == [0, 7500, 15000, 22500, 30000]


def test_nice_ticks_100_exact():
    """100 produces [0, 25, 50, 75, 100]."""
    ticks = _nice_ticks(0, 100)
    assert ticks == [0, 25, 50, 75, 100]


def test_nice_ticks_80_exact():
    """80 produces [0, 20, 40, 60, 80]."""
    ticks = _nice_ticks(0, 80)
    assert ticks == [0, 20, 40, 60, 80]


# --- Clustering detection ---

def test_nice_ticks_clustered_data_not_from_zero():
    """Clustered data [50000, 60000] does NOT start from 0."""
    ticks = _nice_ticks(50000, 60000)
    # Should start somewhere below 50000 (not 0)
    assert ticks[0] > 0
    assert ticks[0] <= 50000
    # Last tick should be >= 60000
    assert ticks[-1] >= 60000
    # The range should be narrow (not 0-80000)
    assert ticks[-1] - ticks[0] <= 30000


def test_nice_ticks_clustered_90_100():
    """[90, 100] is clustered — axis sits up near the data, not at 0.

    M102 added 3 to the nice-step list, which can produce a tighter
    axis that starts exactly at data_min. The invariant that matters
    is that the axis is clearly clustered (not [0..N]) and that it
    covers the data."""
    ticks = _nice_ticks(90, 100)
    assert ticks[0] >= 80, f"clustered axis should start near data, got {ticks[0]}"
    assert ticks[-1] >= 100


def test_nice_ticks_not_clustered_starts_from_zero():
    """[500, 10000] is NOT clustered — starts from 0."""
    ticks = _nice_ticks(500, 10000)
    assert ticks[0] == 0


def test_nice_ticks_borderline_half():
    """min/max exactly 0.5 is borderline (strict >) — starts from 0."""
    ticks = _nice_ticks(40, 80)
    assert ticks[0] == 0


# --- Integration: line chart uses smart normalization ---

def test_line_chart_uses_tick_range_normalization():
    """Line chart with data [500..10000] has Y-axis starting at 0."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 500 |\n"
        "| 2 | 10000 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Y-axis first label should be "0"
    yaxis_match = re.search(r'<div class="md2-chart-yaxis">(.+?)</div>', html, re.DOTALL)
    assert yaxis_match
    tick_texts = re.findall(r'<span[^>]*>([^<]*)</span>', yaxis_match.group(1))
    # yaxis shows high-to-low, so last = 0
    assert tick_texts[-1] == "0"
    # First (top) should be 10000 (data max exactly matches)
    assert tick_texts[0] == "10000"


def test_line_chart_clustered_data_yaxis_non_zero_start():
    """Line chart with clustered data has Y-axis NOT starting at 0."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 50000 |\n"
        "| 2 | 60000 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    yaxis_match = re.search(r'<div class="md2-chart-yaxis">(.+?)</div>', html, re.DOTALL)
    tick_texts = re.findall(r'<span[^>]*>([^<]*)</span>', yaxis_match.group(1))
    # Bottom tick should NOT be "0"
    assert tick_texts[-1] != "0"
    # Bottom tick should be less than 50000 (data min)
    assert int(tick_texts[-1]) < 50000
    # Top tick should be >= 60000
    assert int(tick_texts[0]) >= 60000


# --- CSS flex body height fix ---

def test_chart_body_has_explicit_height():
    """The flex body has explicit height so it matches the chart table."""
    from md2.core import BUNDLED_TEMPLATES_DIR
    css = (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")
    assert ".md2-chart-body" in css
    body_idx = css.index(".md2-chart-body")
    block = css[body_idx:css.index("}", body_idx) + 1]
    assert "height" in block
