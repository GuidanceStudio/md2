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
    """First line cell's --start equals its own value (no previous point)."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 50 |\n"
        "| 2 | 100 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # First cell: --start should equal --size (0.5)
    first_td = re.search(r'<td style="([^"]+)"[^>]*>.*?<th scope="row">2', html, re.DOTALL)
    # Actually check the first td in order
    tds = re.findall(r'<td style="([^"]+)">', html)
    assert len(tds) >= 2
    # First td has --start and --end/--size with same normalized value (0.5 in this case)
    assert "--start: 0.5" in tds[0]


def test_line_chart_connects_points():
    """Subsequent line cells have --start = previous value, --end/--size = current."""
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
    # Td 0: start=0.5 (itself), size=0.5
    # Td 1: start=0.5 (prev), size=1.0 (current = 100/100)
    # Td 2: start=1.0 (prev), size=0.25 (current = 25/100)
    assert "--start: 0.5" in tds[1]
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
