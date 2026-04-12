"""Tests for M39: Simplified chart API — no options, auto-defaults."""
from md2.core import process_markdown, preprocess_chart_directives


# --- No-options syntax ---

def test_chart_bar_no_options():
    """:::chart bar with just a table works."""
    md = (
        ":::chart bar\n"
        "| Metric | Value |\n"
        "|--------|-------|\n"
        "| A      | 50    |\n"
        "| B      | 80    |\n"
        ":::"
    )
    html, has_charts = process_markdown(md)
    assert has_charts
    assert "charts-css" in html
    assert " bar" in html


def test_chart_auto_labels_always_on():
    """Labels class is always applied regardless of options."""
    md = (
        ":::chart bar\n"
        "| A | B |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "show-labels" in html


def test_chart_auto_legend_for_multi_dataset():
    """Legend is auto-added for multi-dataset charts."""
    md = (
        ":::chart bar\n"
        "| Label | Q1 | Q2 |\n"
        "|-------|----|----|\n"
        "| A     | 10 | 20 |\n"
        "| B     | 30 | 40 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "charts-css legend" in html


def test_chart_no_legend_for_single_dataset():
    """Legend is NOT added for single dataset charts."""
    md = (
        ":::chart bar\n"
        "| Label | Value |\n"
        "|-------|-------|\n"
        "| A     | 50    |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "charts-css legend" not in html


def test_chart_show_data_for_bar():
    """show-data is auto-applied for bar charts."""
    md = (
        ":::chart bar\n"
        "| A | B |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "show-data-on-hover" in html or "<span class=\"data\">" in html


def test_chart_show_data_for_column():
    """show-data is auto-applied for column charts."""
    md = (
        ":::chart column\n"
        "| A | B |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "<span class=\"data\">" in html


def test_chart_pie_has_legend_with_values():
    """Pie chart auto-generates a legend with label + value (M53)."""
    md = (
        ":::chart pie\n"
        "| A | B |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        "| y | 30 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Pie no longer shows data inside slices (illegible rotated labels).
    # Instead it has a legend with label + value.
    assert "charts-css legend" in html
    assert "50" in html
    assert "30" in html


def test_chart_show_data_for_line():
    """Line charts show data values for readability (M54)."""
    md = (
        ":::chart line\n"
        "| A | B |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        "| y | 30 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "<span class=\"data\">" in html


def test_chart_show_data_for_area():
    """Area charts show data values for readability (M54)."""
    md = (
        ":::chart area\n"
        "| A | B |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        "| y | 30 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "<span class=\"data\">" in html


# --- Stacked types ---

def test_chart_stacked_bar_type():
    """stacked-bar produces bar + stacked classes."""
    md = (
        ":::chart stacked-bar\n"
        "| Label | Q1 | Q2 |\n"
        "|-------|----|----|\n"
        "| A     | 10 | 20 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert " bar" in html
    assert "stacked" in html


def test_chart_stacked_column_type():
    """stacked-column produces column + stacked classes."""
    md = (
        ":::chart stacked-column\n"
        "| Label | Q1 | Q2 |\n"
        "|-------|----|----|\n"
        "| A     | 10 | 20 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert " column" in html
    assert "stacked" in html


# --- Title from heading ---

def test_chart_title_from_h3():
    """### Title inside chart block is extracted as the chart title."""
    md = (
        ":::chart bar\n"
        "### Platform Metrics\n"
        "| A | B |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Title should appear in the chart somehow (as heading or caption)
    assert "Platform Metrics" in html
    # And NOT as a separate H3 outside the chart
    assert "<h3>Platform Metrics</h3>" not in html


def test_chart_title_from_h2():
    """## Title inside chart block is also extracted."""
    md = (
        ":::chart bar\n"
        "## Metrics\n"
        "| A | B |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "Metrics" in html


def test_chart_no_title():
    """Chart without heading has no title element."""
    md = (
        ":::chart bar\n"
        "| A | B |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "md2-chart-title" not in html


def test_chart_title_rendered_in_chart():
    """Title when present is rendered inside the chart wrapper."""
    md = (
        ":::chart bar\n"
        "### My Title\n"
        "| A | B |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Title should be inside the md2-chart div
    chart_start = html.index("md2-chart")
    chart_end = html.index("</div>", chart_start)
    chart_html = html[chart_start:chart_end]
    assert "My Title" in chart_html


# --- Backward compat: old options are silently ignored ---

def test_chart_old_options_ignored():
    """Old options like --labels are silently ignored (backward compat)."""
    md = (
        ":::chart bar --labels --legend\n"
        "| A | B |\n"
        "|---|---|\n"
        "| x | 50 |\n"
        ":::"
    )
    # Should not crash, still produces a valid chart
    html, has_charts = process_markdown(md)
    assert has_charts
    assert "charts-css" in html
