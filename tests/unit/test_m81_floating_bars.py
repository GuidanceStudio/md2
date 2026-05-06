"""M81: Column/bar charts use the floating-bar pattern for negatives.

Each `<td>` carries `--start` (where the bar begins, 0–1 of the chart
height) and `--size` (its length, 0–1). Positives sit on the zero
baseline and grow up; negatives hang from the baseline and grow down.
Zero values render an empty bar but keep the data label and the X-axis
category visible.
"""
import re

from md2.core import process_markdown


# --- All-positive: backward compat ---

def test_column_all_positive_uses_zero_start():
    """All-positive column charts emit `--start: 0` (or no `--start` if
    legacy form is preserved). Bars on the baseline grow up."""
    md = (
        ":::chart column\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| A | 100 |\n"
        "| B | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Each value's <td> must carry a --size and --start such that
    # start + size == value/range. For all-positive, range = max,
    # zero_frac = 0, so start = 0 and size = v/max.
    tds = re.findall(r'<td style="([^"]+)">', html)
    assert len(tds) == 2, f"expected 2 column <td>, got {tds}"
    # Both should have --start: 0 and --size proportional to value.
    assert "--start: 0" in tds[0] and "--size: 1" in tds[0]
    assert "--start: 0" in tds[1] and "--size: 0.5" in tds[1]


# --- Mixed positives and negatives ---

def test_column_mixed_positive_negative_floating_bars():
    """Mixed dataset: positives float above baseline, negatives hang below.
    Bars are normalized against the TICK domain (after _nice_ticks rounds
    the extremes), so the bar positions align with the visible Y-axis
    ticks. For [10, -5, 8] data, ticks span [-5..10] (or wider). The
    invariants checked here are sign-based, not exact fractions."""
    md = (
        ":::chart column\n"
        "| M | V |\n"
        "|---|---|\n"
        "| Mag | 10 |\n"
        "| Giu | -5 |\n"
        "| Lug | 8 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    tds = re.findall(r'<td style="([^"]+)">', html)
    assert len(tds) == 3, f"expected 3 <td>, got {tds}"

    def _extract(style, prop):
        match = re.search(rf'--{prop}:\s*([0-9.\-]+)', style)
        return float(match.group(1)) if match else None

    starts = [_extract(td, "start") for td in tds]
    sizes = [_extract(td, "size") for td in tds]

    # All sizes must be non-negative — Charts.css can't render negative size.
    for s in sizes:
        assert s is not None and s >= 0, f"size must be ≥ 0, got {s}"

    # Positive bars (10 and 8) share the same start = zero_frac, since
    # both anchor at the zero baseline.
    assert starts[0] == starts[2], (
        f"both positive bars should share zero_frac as start; "
        f"got {starts[0]} and {starts[2]}"
    )
    # Negative bar's start is below the zero baseline (start < zero_frac).
    assert starts[1] < starts[0], (
        f"negative bar start {starts[1]} should be < positive start {starts[0]}"
    )
    # The negative bar reaches the zero line: start + size == zero_frac.
    assert abs((starts[1] + sizes[1]) - starts[0]) < 0.001, (
        f"negative bar's top ({starts[1]} + {sizes[1]}) should hit the "
        f"zero baseline ({starts[0]})"
    )


# --- All-negative ---

def test_column_all_negative_bars_visible():
    """All-negative dataset: every bar has size > 0 (visible) and start < 1."""
    md = (
        ":::chart column\n"
        "| C | V |\n"
        "|---|---|\n"
        "| A | -10 |\n"
        "| B | -20 |\n"
        "| C | -30 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    tds = re.findall(r'<td style="([^"]+)">', html)
    assert len(tds) == 3

    sizes = [float(re.search(r'--size:\s*([0-9.\-]+)', td).group(1)) for td in tds]
    starts = [float(re.search(r'--start:\s*([0-9.\-]+)', td).group(1)) for td in tds]

    # All sizes must be > 0 (bars visible)
    for i, s in enumerate(sizes):
        assert s > 0, f"bar {i} should have visible size, got {s}"
    # All sizes must be ≤ 1
    for i, s in enumerate(sizes):
        assert s <= 1.0001, f"bar {i} size {s} should be ≤ 1"
    # All starts must be in [0, 1]
    for i, st in enumerate(starts):
        assert 0 <= st <= 1, f"bar {i} start {st} should be in [0, 1]"


# --- Zero values: bar empty but category visible ---

def test_column_zero_value_keeps_category_label():
    """A category with value 0 still emits its `<th>` row label."""
    md = (
        ":::chart column\n"
        "| Cat | V |\n"
        "|---|---|\n"
        "| Alpha | 10 |\n"
        "| Beta | 0 |\n"
        "| Gamma | 5 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # All three labels appear in the rendered HTML
    assert ">Alpha<" in html
    assert ">Beta<" in html
    assert ">Gamma<" in html


def test_column_zero_value_no_data_label():
    """M91 superseded M87: a zero-value cell no longer emits a data
    span at all (the span couldn't be positioned by Charts.css with
    `--size: 0`). The category remains visible via the X-axis label."""
    md = (
        ":::chart column\n"
        "| C | V |\n"
        "|---|---|\n"
        "| A | 10 |\n"
        "| B | 0 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    data_spans = re.findall(r'<span class="data[^"]*">([^<]*)</span>', html)
    # "10" is still rendered; "0" is not
    assert "10" in data_spans
    assert "0" not in data_spans


# --- Bar (horizontal) chart: same treatment ---

def test_bar_chart_negatives_floating():
    """Bar (horizontal) chart with negatives: same floating-bar pattern."""
    md = (
        ":::chart bar\n"
        "| C | V |\n"
        "|---|---|\n"
        "| A | 10 |\n"
        "| B | -5 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    tds = re.findall(r'<td style="([^"]+)">', html)
    assert len(tds) == 2
    sizes = [float(re.search(r'--size:\s*([0-9.\-]+)', td).group(1)) for td in tds]
    # Both sizes positive (no negative `--size` leaking through)
    for s in sizes:
        assert s > 0, f"size {s} should be positive"


# --- Multi-series with negatives ---

def test_column_multi_series_with_negatives():
    """Multi-series column: each `<td>` independently floats."""
    md = (
        ":::chart column\n"
        "| Q | A | B |\n"
        "|---|---|---|\n"
        "| 1 | 10 | -3 |\n"
        "| 2 | -5 | 8 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    tds = re.findall(r'<td style="([^"]+)">', html)
    assert len(tds) == 4
    for td in tds:
        size = float(re.search(r'--size:\s*([0-9.\-]+)', td).group(1))
        assert size > 0, f"all sizes must be positive, got {size} in {td}"
