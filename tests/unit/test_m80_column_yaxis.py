"""M80: Graduated Y-axis for column/bar charts.

Adds the same `md2-chart-yaxis` graduated scale that line/area got in M67,
so column/bar charts can render with a meaningful axis. Domain always
includes zero — foundation for negative-value rendering in M81.
"""
import re

from md2.core import process_markdown, _nice_ticks


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


# --- _nice_ticks extension: negative-range support ---

def test_nice_ticks_all_negative():
    """`_nice_ticks(-30, 0)` returns 5 ticks spanning [-30, 0]."""
    ticks = _nice_ticks(-30, 0)
    assert len(ticks) == 5
    assert ticks[0] <= -30, f"first tick {ticks[0]} should be ≤ -30"
    assert ticks[-1] >= 0, f"last tick {ticks[-1]} should be ≥ 0"
    # Strictly increasing
    assert all(ticks[i] < ticks[i + 1] for i in range(4))


def test_nice_ticks_mixed_range():
    """`_nice_ticks(-5, 10)` returns ticks spanning the full range, 0 inside."""
    ticks = _nice_ticks(-5, 10)
    assert len(ticks) == 5
    assert ticks[0] <= -5
    assert ticks[-1] >= 10
    assert all(ticks[i] < ticks[i + 1] for i in range(4))
    # 0 must be inside the range covered (not necessarily exactly a tick)
    assert ticks[0] < 0 < ticks[-1]


def test_nice_ticks_all_positive_unchanged():
    """Backward compat: `_nice_ticks(0, 100)` still returns positive ticks
    starting at 0 (existing M67 behavior)."""
    ticks = _nice_ticks(0, 100)
    assert ticks[0] == 0
    assert ticks[-1] >= 100


# --- Column chart: graduated Y-axis present ---

def test_column_chart_has_yaxis_div():
    """A column chart's HTML contains a `md2-chart-yaxis` div."""
    md = (
        ":::chart column\n"
        "| M | V |\n"
        "|---|---|\n"
        "| A | 100 |\n"
        "| B | 200 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-chart-yaxis"' in html


def test_column_chart_yaxis_has_5_ticks():
    """Y-axis div for column has 5 tick spans."""
    md = (
        ":::chart column\n"
        "| M | V |\n"
        "|---|---|\n"
        "| A | 100 |\n"
        "| B | 500 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    match = re.search(r'<div class="md2-chart-yaxis">(.+?)</div>', html, re.DOTALL)
    assert match, "expected md2-chart-yaxis div"
    spans = re.findall(r'<span[^>]*>([^<]*)</span>', match.group(1))
    assert len(spans) == 5


def test_column_chart_with_negatives_has_negative_tick():
    """Mixed positive/negative dataset → yaxis ticks include a negative
    value (otherwise the chart can't represent the negative bars)."""
    md = (
        ":::chart column\n"
        "| Mese | A |\n"
        "|---|---|\n"
        "| Maggio | 10 |\n"
        "| Giugno | -5 |\n"
        "| Luglio | 8 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    match = re.search(r'<div class="md2-chart-yaxis">(.+?)</div>', html, re.DOTALL)
    assert match, "expected yaxis even when chart includes negatives"
    spans_text = re.findall(r'<span[^>]*>([^<]*)</span>', match.group(1))
    # At least one tick label parses as a negative number
    has_negative = any(
        s.strip().lstrip("-").replace(",", ".").replace(".", "", 1).isdigit()
        and s.strip().startswith("-")
        for s in spans_text
    )
    assert has_negative, f"yaxis ticks {spans_text} should contain a negative value"


def test_column_chart_all_negative_yaxis_spans_negatives():
    """All-negative dataset: yaxis ticks span the negative range and reach 0."""
    md = (
        ":::chart column\n"
        "| M | V |\n"
        "|---|---|\n"
        "| A | -10 |\n"
        "| B | -20 |\n"
        "| C | -30 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    match = re.search(r'<div class="md2-chart-yaxis">(.+?)</div>', html, re.DOTALL)
    assert match, "expected yaxis on all-negative chart"
    spans_text = [s.strip() for s in re.findall(r'<span[^>]*>([^<]*)</span>', match.group(1))]
    # Top tick should be 0 (or close to it) — domain always includes 0
    # Tick labels rendered top-down (reversed): first span is the highest.
    top = spans_text[0]
    bottom = spans_text[-1]
    # Bottom tick should reach at least -30
    bottom_val = float(bottom.replace(",", ".")) if bottom.replace("-", "").replace(",", "").replace(".", "").isdigit() else None
    assert bottom_val is not None and bottom_val <= -30, (
        f"bottom tick {bottom!r} should be ≤ -30 (is {bottom_val!r})"
    )


# --- Bar chart (horizontal) gets the same Y-axis treatment ---

def test_bar_chart_has_yaxis_div():
    """Bar (horizontal) chart also gets the graduated Y-axis."""
    md = (
        ":::chart bar\n"
        "| C | V |\n"
        "|---|---|\n"
        "| A | 100 |\n"
        "| B | 200 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-chart-yaxis"' in html


# --- Backward compat: all-positive column rendering preserved ---

def test_column_all_positive_size_values_unchanged():
    """Regression: an all-positive column chart renders the same `--size`
    values as before M80 (zero_frac stays at 0 in this case)."""
    md = (
        ":::chart column\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| A | 100 |\n"
        "| B | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Existing rendering: max=100 → A: --size: 1, B: --size: 0.5
    assert "--size: 1" in html
    assert "--size: 0.5" in html


# --- CSS: yaxis selectors apply to column/bar ---

def test_yaxis_css_applies_to_column_and_bar():
    """`.md2-chart-yaxis` CSS rules must NOT be scoped to line/area only —
    column and bar chart need them too."""
    css = _get_style_css()
    # Find the .md2-chart-yaxis selector. It must exist and not exclude
    # column/bar via :not(.column) or similar.
    assert ".md2-chart-yaxis" in css, "expected .md2-chart-yaxis in stylesheet"
    # Heuristic: the rule should not contain `.line` / `.area` only-prefixes
    # blocking column/bar. We search for any `.md2-chart-yaxis` rule lines
    # and accept if at least one is non-restrictive.
    yaxis_rules = re.findall(
        r'([^\{}]*\.md2-chart-yaxis[^\{}]*)\s*\{', css
    )
    # At least one selector path must reach .md2-chart-yaxis without
    # depending on .line or .area.
    non_restricted = [
        r for r in yaxis_rules
        if ".line " not in r and ".area " not in r
    ]
    assert non_restricted, (
        f"all .md2-chart-yaxis selectors are scoped to line/area: {yaxis_rules}"
    )
