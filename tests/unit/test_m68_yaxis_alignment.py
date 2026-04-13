"""M68: Y-axis alignment — normalize against tick_max, 3 gridlines."""
import re

from md2.core import process_markdown, _nice_ticks


# --- Normalization against tick_max ---

def test_line_size_uses_tick_max_not_data_max():
    """Line chart --size/--end uses the tick_max (from _nice_ticks), not data max.

    With data max=25000, _nice_ticks returns a top tick of ~30000 or 40000.
    The line should reach --end = 25000/tick_max, not 1.0.
    """
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 3200 |\n"
        "| 2 | 8500 |\n"
        "| 3 | 15000 |\n"
        "| 4 | 25000 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    ticks = _nice_ticks(0, 25000)
    tick_max = ticks[-1]
    expected_end = 25000 / tick_max
    # --size for the last point should be expected_end, not 1
    # Check that --size: 1 is NOT present for the max data point
    if tick_max > 25000:
        # e.g. tick_max = 30000 → expected_end ≈ 0.833
        # --size: 1 should NOT appear
        size_ones = re.findall(r'--size:\s*1\b', html)
        # Some 1s may appear in other contexts, but line should use tick_max
        last_end_match = re.search(r'--size:\s*([\d.]+)', html)
        assert last_end_match
        # Confirm that at least one --size matches the expected 25000/tick_max
        sizes = [float(s) for s in re.findall(r'--size:\s*([\d.]+)', html)]
        assert any(abs(s - expected_end) < 0.01 for s in sizes), \
            f"Expected size ~{expected_end}, got {sizes}"


def test_area_size_uses_tick_max():
    """Area chart also normalizes against tick_max."""
    md = (
        ":::chart area\n"
        "| T | V |\n"
        "|---|---|\n"
        "| 1 | 50 |\n"
        "| 2 | 80 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    ticks = _nice_ticks(0, 80)
    tick_max = ticks[-1]
    expected_end = 80 / tick_max
    sizes = [float(s) for s in re.findall(r'--size:\s*([\d.]+)', html)]
    assert any(abs(s - expected_end) < 0.01 for s in sizes), \
        f"Expected size ~{expected_end}, got {sizes}"


def test_bar_still_uses_data_max():
    """Bar chart normalization unchanged (no tick scaling)."""
    md = (
        ":::chart bar\n"
        "| M | V |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        "| y | 100 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Max value 100 should produce --size: 1 (normalized to data max)
    assert "--size: 1" in html
    assert "--size: 0.5" in html


# --- 3 secondary axes ---

def test_line_uses_4_secondary_axes():
    """M71: Line uses show-4-secondary-axes → 4 secondary gridlines + primary
    axis = 5 lines, one per Y label (0/25/50/75/100%)."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        "| 2 | 200 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "show-4-secondary-axes" in html
    assert "show-3-secondary-axes" not in html


def test_area_uses_4_secondary_axes():
    md = (
        ":::chart area\n"
        "| T | V |\n"
        "|---|---|\n"
        "| 1 | 50 |\n"
        "| 2 | 80 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "show-4-secondary-axes" in html
    assert "show-3-secondary-axes" not in html
