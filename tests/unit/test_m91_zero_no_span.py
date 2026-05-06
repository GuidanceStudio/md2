"""M91: when a column/bar cell has value 0, do not emit a data span.

Charts.css can't position the span when `--size: 0` (the cell has zero
height), so the span ends up in random positions outside the chart area.
The category remains visible via the X-axis label — the empty bar +
X label is enough to communicate "this category is zero".
"""
import re

from md2.core import process_markdown


def test_zero_cell_has_no_data_span():
    """A cell with `--size: 0` must NOT contain `<span class="data">`."""
    md = (
        ":::chart column\n"
        "| C | V |\n"
        "|---|---|\n"
        "| A | 10 |\n"
        "| B | 0 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Find all td rows in the rendered chart
    tds = re.findall(r'<td style="[^"]+">(.*?)</td>', html, re.DOTALL)
    # Identify the zero cell (--size: 0 and --start: 0)
    zero_cells = [
        td for td, style in zip(
            tds, re.findall(r'<td style="([^"]+)">', html)
        ) if "--size: 0" in style and "--start: 0" in style
        and "--size: 0." not in style  # exact 0, not 0.444
    ]
    # Match the cell with --size: 0
    match = re.search(
        r'<td style="--start: 0; --size: 0">(.*?)</td>', html, re.DOTALL,
    )
    assert match, "expected a td with --size: 0"
    inner = match.group(1).strip()
    assert inner == "", (
        f"zero-value cell should have empty inner content (no data span); "
        f"got: {inner!r}"
    )


def test_nonzero_cell_still_has_data_span():
    """A cell with `--size > 0` still has its data span."""
    md = (
        ":::chart column\n"
        "| C | V |\n"
        "|---|---|\n"
        "| A | 10 |\n"
        "| B | 5 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    spans = re.findall(r'<span class="data[^"]*">([^<]+)</span>', html)
    assert "10" in spans
    assert "5" in spans


def test_pie_chart_renders_normally():
    """Pie charts use a different rendering path (md2-pie-label spans
    plus legend) — the M91 zero-skip in column/bar must not affect them."""
    md = (
        ":::chart pie\n"
        "| C | V |\n"
        "|---|---|\n"
        "| A | 30 |\n"
        "| B | 70 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Pie emits md2-pie-label spans for slice labels
    assert "md2-pie-label" in html or "<li>" in html


def test_zero_in_multi_series_handled():
    """Multi-series cashflow with a zero value: only that cell loses
    its data span; the others keep theirs."""
    md = (
        ":::chart column\n"
        "| Mese | A | B |\n"
        "|---|---|---|\n"
        "| Mag | 10 | 0 |\n"
        "| Giu | 5 | 8 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    spans = re.findall(r'<span class="data[^"]*">([^<]+)</span>', html)
    # Non-zero cells keep their spans
    assert "10" in spans
    assert "5" in spans
    assert "8" in spans
    # Zero cell does not emit a span
    assert "0" not in spans
