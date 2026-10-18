"""M121 review: chart cells that are not numbers, and the line/area axis floor.

Cells hold sanitised HTML, so `**4**` arrives as `<strong>4</strong>`.
"""
import re

import pytest

from md2.core import process_markdown

CHART_TYPES = [
    "bar", "column", "line", "line filled", "area", "pie",
    "stacked-bar", "stacked-column", "radar",
]


def _chart(chart_type, cells):
    rows = [f"| r{i} | {cell} |" for i, cell in enumerate(cells)]
    return "\n".join([f":::chart {chart_type}", "| K | V |", "|---|---|", *rows, ":::"])


def _warnings(err):
    return [line for line in err.splitlines() if "not a number" in line]


@pytest.mark.parametrize("chart_type", CHART_TYPES)
def test_each_non_empty_cell_that_is_not_a_number_warns(chart_type, capsys):
    html, _ = process_markdown(_chart(chart_type, ["3,8", "n/a", "**4**", "", "2", "5"]))
    warnings = _warnings(capsys.readouterr().err)
    assert len(warnings) == 3
    for value, row in [("3,8", "r0"), ("n/a", "r1"), ("<strong>4</strong>", "r2")]:
        assert any(f"'{value}'" in w and f"'{row}'" in w for w in warnings)
    assert html.startswith('<div class="md2-chart"')


@pytest.mark.parametrize("chart_type", CHART_TYPES)
def test_non_finite_cells_count_as_zero_with_the_same_warning(chart_type, capsys):
    html, _ = process_markdown(_chart(chart_type, ["nan", "inf", "1e400", "-inf", "2", "5"]))
    warnings = _warnings(capsys.readouterr().err)
    assert len(warnings) == 4
    assert html.startswith('<div class="md2-chart"')


@pytest.mark.parametrize("chart_type", CHART_TYPES)
def test_numeric_table_writes_no_warning(chart_type, capsys):
    process_markdown(_chart(chart_type, ["1", "2.5", "-0", "+3", "4"]))
    assert _warnings(capsys.readouterr().err) == []


def _yaxis(html):
    axis = re.search(r'<div class="md2-chart-yaxis">(.*?)</div>', html)
    return re.findall(r"<span>(.*?)</span>", axis.group(1))[::-1]


def _segments(html):
    return [tuple(float(x) for x in m) for m in
            re.findall(r"--start: ([\d.]+); --size: ([\d.]+)", html)]


@pytest.mark.parametrize("chart_type", ["line", "line filled", "area"])
def test_line_with_zeros_starts_its_axis_at_zero(chart_type):
    html, _ = process_markdown(_chart(chart_type, ["0", "0", "100", "100"]))
    assert _yaxis(html) == ["0", "25", "50", "75", "100"]
    assert _segments(html) == [(0, 0), (0, 1), (1, 1)]


def test_line_of_zeros_then_one_value_keeps_the_zeros_on_the_baseline():
    html, _ = process_markdown(_chart("line", ["0"] * 14 + ["50"]))
    ticks = _yaxis(html)
    assert ticks[0] == "0" and float(ticks[-1]) >= 50
    assert _segments(html)[:13] == [(0, 0)] * 13


def test_line_without_zeros_keeps_its_clustered_axis():
    html, _ = process_markdown(_chart("line", ["90", "95", "100"]))
    assert _yaxis(html)[0] != "0"


@pytest.mark.parametrize("chart_type", ["line", "column"])
def test_all_zero_chart_gets_a_zero_to_four_integer_axis(chart_type):
    html, _ = process_markdown(_chart(chart_type, ["0", "0", "0"]))
    assert _yaxis(html) == ["0", "1", "2", "3", "4"]


@pytest.mark.parametrize("chart_type", CHART_TYPES)
def test_values_too_large_to_draw_count_as_zero_with_the_warning(chart_type, capsys):
    html, _ = process_markdown(_chart(chart_type, ["1e308", "1.7e308", "-1e308", "2", "5"]))
    assert len(_warnings(capsys.readouterr().err)) == 3
    assert html.startswith('<div class="md2-chart"')


@pytest.mark.parametrize("chart_type", ["line", "area"])
def test_line_of_negative_values_runs_its_axis_from_the_lowest_up_to_zero(chart_type):
    html, _ = process_markdown(_chart(chart_type, ["-10", "-20", "-5"]))
    assert _yaxis(html) == ["-20", "-15", "-10", "-5", "0"]
    assert _segments(html) == [(0.5, 0), (0, 0.75)]
