"""M118: a :::chart table with an alignment row renders the same chart.

The `tables` extension puts `style="text-align: …"` on every cell of an
aligned column; the chart must read those cells like attribute-free ones.
"""
import re

import pytest

from md2.core import process_markdown

CHART_TYPES = [
    "bar", "column", "line", "line filled", "area", "pie",
    "stacked-bar", "stacked-column",
]

# Multi-series for every type except pie, which is single series by design.
SERIES = {
    "pie": ("| Fonte | Quota |", ["| Web | 50 |", "| Agenti | 30 |", "| Negozi | 20 |"]),
    "other": (
        "| Trimestre | Entrate | Uscite |",
        ["| Q1 | 50 | 40 |", "| Q2 | 100 | 70 |", "| Q3 | 80 | 90 |"],
    ),
}

ALIGNMENTS = ["---:", ":---:", ":---"]


def _chart(chart_type, separator_cells):
    header, rows = SERIES["pie" if chart_type == "pie" else "other"]
    n_cols = header.count("|") - 1
    separator = "|" + "|".join(separator_cells(n_cols)) + "|"
    return "\n".join([f":::chart {chart_type}", header, separator, *rows, ":::"])


def _render(chart_type, separator_cells):
    html, has_charts = process_markdown(_chart(chart_type, separator_cells))
    assert has_charts
    return html


def _plain(n):
    return ["---"] * n


@pytest.mark.parametrize("alignment", ALIGNMENTS)
@pytest.mark.parametrize("chart_type", CHART_TYPES)
def test_every_column_aligned_renders_the_unaligned_chart(chart_type, alignment):
    plain = _render(chart_type, _plain)
    aligned = _render(chart_type, lambda n: [alignment] * n)
    assert aligned == plain


@pytest.mark.parametrize("alignment", ALIGNMENTS)
@pytest.mark.parametrize("chart_type", CHART_TYPES)
def test_only_data_columns_aligned_renders_the_unaligned_chart(chart_type, alignment):
    plain = _render(chart_type, _plain)
    aligned = _render(chart_type, lambda n: ["---"] + [alignment] * (n - 1))
    assert aligned == plain


@pytest.mark.parametrize("chart_type", CHART_TYPES)
def test_unaligned_reference_chart_carries_its_values(chart_type):
    # Guards the equality tests above: two empty charts would also be equal.
    html = _render(chart_type, _plain)
    cells = re.findall(r"<td style=\"--(?:size|start)", html)
    # line/area draw N-1 segments per series; the others one cell per value.
    expected = {"pie": 3, "line": 4, "line filled": 4, "area": 4}.get(chart_type, 6)
    assert len(cells) == expected


def test_right_aligned_bar_keeps_sizes_labels_and_header():
    md = (
        ":::chart bar\n"
        "| Prodotto | Vendite |\n"
        "|---|---:|\n"
        "| Widget A | 50 |\n"
        "| Widget B | 100 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert re.findall(r"--size: [\d.]+", html) == ["--size: 0.5", "--size: 1"]
    assert '<th scope="row">Widget A</th>' in html
    assert '<th scope="col">Vendite</th>' in html
    assert "text-align" not in html


def test_aligned_multi_series_keeps_the_legend():
    md = (
        ":::chart column\n"
        "| Trimestre | Entrate | Uscite |\n"
        "|:---|---:|---:|\n"
        "| Q1 | 100 | 80 |\n"
        "| Q2 | 150 | 90 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    legend = re.search(r'<ul class="charts-css legend[^"]*">(.*?)</ul>', html, re.DOTALL)
    assert legend is not None
    assert re.findall(r"<li>(.*?)</li>", legend.group(1)) == ["Entrate", "Uscite"]
