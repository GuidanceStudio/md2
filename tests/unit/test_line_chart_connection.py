"""Tests for M43: Line/area charts generate --start for connected segments."""
import re

from md2.core import process_markdown


def test_line_chart_has_start_end():
    """Line chart cells have both --start (previous) and --end (current)."""
    md = (
        ":::chart line\n"
        "| Q | Users |\n"
        "|---|-------|\n"
        "| 1 | 100   |\n"
        "| 2 | 200   |\n"
        "| 3 | 500   |\n"
        "| 4 | 800   |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Should have --start for line segments
    assert "--start" in html
    # Should still have --size or --end (Charts.css supports both)
    assert "--size" in html or "--end" in html


def test_line_chart_first_point_start_equals_end():
    """First line cell's --start equals its own value (no previous point).

    M68: values normalized against tick_max (from _nice_ticks), not data max.
    For max=100, _nice_ticks returns [0,50,100,150,200], tick_max=200.
    Value 50 → 50/200 = 0.25. First cell's --start = --size = 0.25.
    """
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 50 |\n"
        "| 2 | 100 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    tds = re.findall(r'<td style="([^"]+)">', html)
    assert len(tds) >= 2
    # First td has --start = --size normalized against tick_max=200
    # So 50/200 = 0.25
    assert "--start: 0.25" in tds[0]


def test_line_chart_connects_points():
    """Subsequent line cells have --start = previous value, --size = current.

    M68: normalized against tick_max. _nice_ticks(100) = [0,50,100,150,200].
    - 50 → 0.25, 100 → 0.5, 25 → 0.125
    """
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 50  |\n"
        "| 2 | 100 |\n"
        "| 3 | 25  |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    tds = re.findall(r'<td style="([^"]+)">', html)
    assert len(tds) == 3
    # Td 1: --start = prev value (50/200=0.25)
    assert "--start: 0.25" in tds[1]
    # Td 2: --start = prev value (100/200=0.5)
    assert "--start: 0.5" in tds[2]


def test_area_chart_has_start_end():
    """Area chart also uses --start for connected segments."""
    md = (
        ":::chart area\n"
        "| T | V |\n"
        "|---|---|\n"
        "| 1 | 30 |\n"
        "| 2 | 70 |\n"
        "| 3 | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "--start" in html


def test_bar_chart_no_start():
    """Bar chart does NOT have --start (uses plain --size)."""
    md = (
        ":::chart bar\n"
        "| A | V |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        "| y | 100 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # --start should NOT appear for bar chart
    assert "--start" not in html
