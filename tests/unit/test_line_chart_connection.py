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
    """M69: First line cell --start = own normalized value.

    _nice_ticks(50, 100): 50 > 50 is false → NOT clustered → axis_start=0
    → ticks [0, 25, 50, 75, 100]. Value 50 → (50-0)/100 = 0.5.
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
    assert "--start: 0.5" in tds[0]


def test_line_chart_connects_points():
    """M69: line cells --start = prev normalized value.

    _nice_ticks(25, 100): not clustered → ticks [0,25,50,75,100].
    Values 50→0.5, 100→1, 25→0.25.
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
    # Td 1: --start = prev = 0.5
    assert "--start: 0.5" in tds[1]
    # Td 2: --start = prev = 1 (100 at norm_max)
    assert "--start: 1" in tds[2]


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
