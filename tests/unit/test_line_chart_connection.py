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


def test_line_chart_first_segment_uses_two_endpoints():
    """M74: segment model. First segment --start = norm(value[0]),
    --size = norm(value[1]). For [50, 100]: ticks [0,25,50,75,100],
    so start=0.5 and size=1.
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
    assert len(tds) == 1
    assert "--start: 0.5" in tds[0]
    assert "--size: 1" in tds[0]


def test_line_chart_segment_model_n_minus_1_tds():
    """M74: N points → N-1 segment tds."""
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
    assert len(tds) == 2
    # Segment 0: 50→100, start=0.5, size=1
    assert "--start: 0.5" in tds[0]
    assert "--size: 1" in tds[0]
    # Segment 1: 100→25, start=1, size=0.25
    assert "--start: 1" in tds[1]
    assert "--size: 0.25" in tds[1]


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
