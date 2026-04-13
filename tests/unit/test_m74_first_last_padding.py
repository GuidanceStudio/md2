"""M74: Line/area use a segment model (N-1 <tr>s for N data points),
so the line is drawn exactly between consecutive points — no phantom
flat segment at the first/last point.

Each segment <tr> contains one <td> per dataset; that td has
--start = value[i] and --size = value[i+1]. The tr fills 1/(N-1) of
the chart width, so the line goes from point i to point i+1 exactly.

X-labels are rendered as N spans with justify-content: space-between,
so first label aligns to x=0 and last to x=100%.
"""
import re

from md2.core import process_markdown, BUNDLED_TEMPLATES_DIR


def _css():
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def _count_segment_rows(html):
    """Count <tr> elements inside tbody of the first chart table."""
    m = re.search(r"<tbody>(.*?)</tbody>", html, re.DOTALL)
    assert m
    return len(re.findall(r"<tr\b", m.group(1)))


# --- segment count ---

def test_line_chart_emits_n_minus_1_segments():
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        "| 2 | 200 |\n"
        "| 3 | 300 |\n"
        "| 4 | 400 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert _count_segment_rows(html) == 3


def test_area_chart_emits_n_minus_1_segments():
    md = (
        ":::chart area\n"
        "| T | V |\n"
        "|---|---|\n"
        "| A | 10 |\n"
        "| B | 20 |\n"
        "| C | 30 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert _count_segment_rows(html) == 2


def test_bar_chart_still_emits_n_rows():
    """Bar chart is unchanged: 1 row per data row."""
    md = (
        ":::chart bar\n"
        "| L | V |\n"
        "|---|---|\n"
        "| a | 10 |\n"
        "| b | 20 |\n"
        "| c | 30 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert _count_segment_rows(html) == 3


# --- segment values ---

def test_line_segment_start_equals_prev_value():
    """First segment: --start = norm(value[0]), --size = norm(value[1])."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 25 |\n"
        "| 2 | 100 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # positive values: [25, 100]. data_min=25, max=100. 25 > 50? No → not
    # clustered → ticks start at 0. _nice_ticks(25, 100) = [0,25,50,75,100].
    # value 25 norm = 0.25, value 100 norm = 1.
    tds = re.findall(r'<td style="([^"]+)">', html)
    assert len(tds) == 1
    assert "--start: 0.25" in tds[0]
    assert "--size: 1" in tds[0]


def test_multiline_segments_multiple_tds_per_row():
    """Multi-dataset: each segment row has M tds (one per series)."""
    md = (
        ":::chart line\n"
        "| Q | A | B |\n"
        "|---|---|---|\n"
        "| 1 | 100 | 200 |\n"
        "| 2 | 300 | 400 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # 1 segment row, 2 tds (one per series)
    assert _count_segment_rows(html) == 1
    m = re.search(r"<tbody>(.*?)</tbody>", html, re.DOTALL)
    tds = re.findall(r"<td\b", m.group(1))
    assert len(tds) == 2


# --- xlabels still N ---

def test_xlabels_span_count_matches_data_points_not_segments():
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| Q1 | 100 |\n"
        "| Q2 | 200 |\n"
        "| Q3 | 300 |\n"
        "| Q4 | 400 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    m = re.search(
        r'<div class="md2-chart-xlabels">(.*?)</div>', html, re.DOTALL
    )
    assert m
    spans = re.findall(r"<span[^>]*>([^<]*)</span>", m.group(1))
    assert spans == ["Q1", "Q2", "Q3", "Q4"]


# --- CSS: xlabels use space-between so first/last align to chart edges ---

def test_css_xlabels_justify_space_between():
    css = _css()
    m = re.search(r"\.md2-chart-xlabels\s*\{([^}]*)\}", css)
    assert m
    block = m.group(1)
    assert "justify-content: space-between" in block
