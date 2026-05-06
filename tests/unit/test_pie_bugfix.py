"""Tests for M32: Bugfix — pie chart colors and responsive sizing."""
import re

from md2.core import process_markdown, BUNDLED_TEMPLATES_DIR


# --- Pie chart uses --start/--end, not --size ---

def test_pie_uses_start_end():
    """Pie chart slices use --start and --end CSS properties."""
    md = (
        ":::chart pie --labels\n"
        "| Area | Budget |\n"
        "|------|--------|\n"
        "| R&D  | 48     |\n"
        "| Sales| 28     |\n"
        "| AI   | 24     |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "--start:" in html
    assert "--end:" in html


def test_pie_no_size_property():
    """Pie chart should NOT use --size (that's for bar/column/line/area)."""
    md = (
        ":::chart pie --labels\n"
        "| Area | Budget |\n"
        "|------|--------|\n"
        "| R&D  | 48     |\n"
        "| Sales| 28     |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "--size:" not in html


def test_pie_slices_sum_to_one():
    """Pie slice --end values are cumulative and the last one reaches ~1.0."""
    md = (
        ":::chart pie\n"
        "| A | V |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        "| y | 30 |\n"
        "| z | 20 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Find all --end values
    ends = re.findall(r'--end:\s*([\d.]+)', html)
    assert len(ends) == 3
    # Last slice should end at 1.0
    assert float(ends[-1]) == 1.0


def test_pie_first_slice_starts_at_zero():
    """First pie slice starts at 0."""
    md = (
        ":::chart pie\n"
        "| A | V |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        "| y | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    starts = re.findall(r'--start:\s*([\d.]+)', html)
    assert len(starts) == 2
    assert float(starts[0]) == 0


def test_pie_cumulative_positions():
    """Pie slices have correct cumulative start/end positions."""
    md = (
        ":::chart pie\n"
        "| A | V |\n"
        "|---|---|\n"
        "| x | 25 |\n"
        "| y | 25 |\n"
        "| z | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    starts = [float(s) for s in re.findall(r'--start:\s*([\d.]+)', html)]
    ends = [float(e) for e in re.findall(r'--end:\s*([\d.]+)', html)]
    assert starts == [0, 0.25, 0.5]
    assert ends == [0.25, 0.5, 1.0]


# --- Non-pie charts still use --size ---

def test_bar_uses_size_and_start():
    """M81: bar charts use both --size and --start (floating-bar pattern).
    They never use --end (which is reserved for pie's cumulative angles)."""
    md = (
        ":::chart bar\n"
        "| A | V |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "--size:" in html
    assert "--start:" in html
    assert "--end:" not in html


# --- Responsive sizing ---

def test_pie_responsive_uses_viewport_units():
    """Pie CSS uses viewport units (vh/vw) for responsive sizing."""
    css = (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")
    pie_idx = css.index(".charts-css.pie")
    pie_block = css[pie_idx:css.index("}", pie_idx) + 1]
    assert "vh" in pie_block or "vw" in pie_block


def test_pie_uses_aspect_ratio():
    """Pie CSS uses aspect-ratio to stay square."""
    css = (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")
    pie_idx = css.index(".charts-css.pie")
    pie_block = css[pie_idx:css.index("}", pie_idx) + 1]
    assert "aspect-ratio" in pie_block
