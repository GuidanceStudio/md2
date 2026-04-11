"""Tests for M26: Charts.css — embedding and :::chart directive."""
import subprocess
import sys

from md2.core import preprocess_chart_directives, transform_charts, process_markdown


# --- preprocess_chart_directives ---

def test_chart_directive_parsed():
    """:::chart bar ... ::: is recognized and produces a marker div with parsed table."""
    md = ":::chart bar\n| A | B |\n|---|---|\n| x | 10 |\n:::"
    result, has_charts = preprocess_chart_directives(md)
    assert has_charts is True
    assert 'data-chart-type="bar"' in result
    assert "<table>" in result  # table markdown was parsed to HTML


def test_no_chart_directive():
    """Text without :::chart returns unchanged with has_charts=False."""
    md = "# Title\n\nJust text"
    result, has_charts = preprocess_chart_directives(md)
    assert has_charts is False
    assert result == md


def test_chart_type_bar():
    """type 'bar' is extracted."""
    md = ":::chart bar\n| A | B |\n|---|---|\n| x | 10 |\n:::"
    result, _ = preprocess_chart_directives(md)
    assert 'data-chart-type="bar"' in result


def test_chart_type_column():
    """type 'column' is extracted."""
    md = ":::chart column\n| A | B |\n|---|---|\n| x | 10 |\n:::"
    result, _ = preprocess_chart_directives(md)
    assert 'data-chart-type="column"' in result


def test_chart_type_line():
    """type 'line' is extracted."""
    md = ":::chart line\n| A | B |\n|---|---|\n| x | 10 |\n:::"
    result, _ = preprocess_chart_directives(md)
    assert 'data-chart-type="line"' in result


def test_chart_type_area():
    """type 'area' is extracted."""
    md = ":::chart area\n| A | B |\n|---|---|\n| x | 10 |\n:::"
    result, _ = preprocess_chart_directives(md)
    assert 'data-chart-type="area"' in result


def test_chart_type_pie():
    """type 'pie' is extracted."""
    md = ":::chart pie\n| A | B |\n|---|---|\n| x | 10 |\n:::"
    result, _ = preprocess_chart_directives(md)
    assert 'data-chart-type="pie"' in result


def test_chart_options_labels():
    """--labels is captured in data-chart-options."""
    md = ":::chart bar --labels\n| A | B |\n|---|---|\n| x | 10 |\n:::"
    result, _ = preprocess_chart_directives(md)
    assert "labels" in result


def test_chart_options_stacked():
    """--stacked is captured."""
    md = ":::chart bar --stacked\n| A | B |\n|---|---|\n| x | 10 |\n:::"
    result, _ = preprocess_chart_directives(md)
    assert "stacked" in result


def test_chart_options_legend():
    """--legend is captured."""
    md = ":::chart bar --legend\n| A | B |\n|---|---|\n| x | 10 |\n:::"
    result, _ = preprocess_chart_directives(md)
    assert "legend" in result


def test_chart_options_show_data():
    """--show-data is captured."""
    md = ":::chart bar --show-data\n| A | B |\n|---|---|\n| x | 10 |\n:::"
    result, _ = preprocess_chart_directives(md)
    assert "show-data" in result


def test_chart_title():
    """--title 'My Title' is captured."""
    md = ':::chart bar --title "Sales Report"\n| A | B |\n|---|---|\n| x | 10 |\n:::'
    result, _ = preprocess_chart_directives(md)
    assert "Sales Report" in result


def test_chart_multiple_options():
    """Multiple options on one line."""
    md = ":::chart column --labels --legend --stacked\n| A | B |\n|---|---|\n| x | 10 |\n:::"
    result, _ = preprocess_chart_directives(md)
    assert "labels" in result
    assert "legend" in result
    assert "stacked" in result


# --- transform_charts (post-processing HTML) ---

def test_transform_adds_charts_css_class():
    """Transformed table gets .charts-css class."""
    html = (
        '<div class="md2-chart" data-chart-type="bar" data-chart-options="">'
        '<table><thead><tr><th>Label</th><th>Value</th></tr></thead>'
        '<tbody><tr><td>A</td><td>50</td></tr></tbody></table></div>'
    )
    result = transform_charts(html)
    assert "charts-css" in result
    assert " bar" in result


def test_chart_size_normalization():
    """Numeric values are normalized to 0-1 range with --size."""
    html = (
        '<div class="md2-chart" data-chart-type="bar" data-chart-options="">'
        '<table><thead><tr><th>Label</th><th>Value</th></tr></thead>'
        '<tbody><tr><td>A</td><td>50</td></tr>'
        '<tr><td>B</td><td>100</td></tr></tbody></table></div>'
    )
    result = transform_charts(html)
    assert "--size: 0.5" in result  # 50/100
    assert "--size: 1" in result    # 100/100


def test_chart_multi_dataset():
    """Table with multiple value columns produces .multiple class."""
    html = (
        '<div class="md2-chart" data-chart-type="bar" data-chart-options="">'
        '<table><thead><tr><th>Label</th><th>Q1</th><th>Q2</th></tr></thead>'
        '<tbody><tr><td>A</td><td>50</td><td>80</td></tr></tbody></table></div>'
    )
    result = transform_charts(html)
    assert "multiple" in result


def test_chart_labels_class():
    """--labels option adds .show-labels class."""
    html = (
        '<div class="md2-chart" data-chart-type="bar" data-chart-options="labels">'
        '<table><thead><tr><th>Label</th><th>Value</th></tr></thead>'
        '<tbody><tr><td>A</td><td>50</td></tr></tbody></table></div>'
    )
    result = transform_charts(html)
    assert "show-labels" in result


def test_chart_stacked_class():
    """--stacked option adds .stacked class."""
    html = (
        '<div class="md2-chart" data-chart-type="bar" data-chart-options="stacked">'
        '<table><thead><tr><th>Label</th><th>Q1</th><th>Q2</th></tr></thead>'
        '<tbody><tr><td>A</td><td>50</td><td>80</td></tr></tbody></table></div>'
    )
    result = transform_charts(html)
    assert "stacked" in result


def test_chart_show_data_class():
    """--show-data adds .show-data-on-hover class."""
    html = (
        '<div class="md2-chart" data-chart-type="bar" data-chart-options="show-data">'
        '<table><thead><tr><th>Label</th><th>Value</th></tr></thead>'
        '<tbody><tr><td>A</td><td>50</td></tr></tbody></table></div>'
    )
    result = transform_charts(html)
    assert "show-data-on-hover" in result


def test_chart_legend_html():
    """--legend option produces a legend list."""
    html = (
        '<div class="md2-chart" data-chart-type="bar" data-chart-options="legend">'
        '<table><thead><tr><th>Label</th><th>Q1</th><th>Q2</th></tr></thead>'
        '<tbody><tr><td>A</td><td>50</td><td>80</td></tr></tbody></table></div>'
    )
    result = transform_charts(html)
    assert "charts-css legend" in result
    assert "Q1" in result
    assert "Q2" in result


def test_chart_caption():
    """--title produces a <caption> element."""
    html = (
        '<div class="md2-chart" data-chart-type="bar" data-chart-options="" '
        'data-chart-title="Sales Report">'
        '<table><thead><tr><th>Label</th><th>Value</th></tr></thead>'
        '<tbody><tr><td>A</td><td>50</td></tr></tbody></table></div>'
    )
    result = transform_charts(html)
    assert "<caption>" in result
    assert "Sales Report" in result


def test_chart_has_charts_flag():
    """has_charts is True only when there are chart directives."""
    _, has = preprocess_chart_directives(":::chart bar\n| A | B |\n|---|---|\n| x | 10 |\n:::")
    assert has is True
    _, has = preprocess_chart_directives("Just normal text")
    assert has is False


def test_chart_invalid_type():
    """Invalid chart type falls back to plain table."""
    md = ":::chart invalid_type\n| A | B |\n|---|---|\n| x | 10 |\n:::"
    result, has_charts = preprocess_chart_directives(md)
    assert has_charts is False
    # Content is preserved but not wrapped as chart
    assert "| A | B |" in result


def test_chart_non_numeric_values():
    """Non-numeric values in data cells are handled gracefully."""
    html = (
        '<div class="md2-chart" data-chart-type="bar" data-chart-options="">'
        '<table><thead><tr><th>Label</th><th>Value</th></tr></thead>'
        '<tbody><tr><td>A</td><td>not_a_number</td></tr>'
        '<tr><td>B</td><td>100</td></tr></tbody></table></div>'
    )
    result = transform_charts(html)
    # Should not crash; non-numeric treated as 0
    assert "--size: 0" in result
    assert "--size: 1" in result


def test_multiple_charts_in_same_document():
    """Multiple :::chart blocks in the same text all get processed."""
    md = (
        ":::chart bar\n| A | B |\n|---|---|\n| x | 10 |\n:::\n\n"
        "Some text\n\n"
        ":::chart column\n| C | D |\n|---|---|\n| y | 20 |\n:::"
    )
    result, has_charts = preprocess_chart_directives(md)
    assert has_charts is True
    assert 'data-chart-type="bar"' in result
    assert 'data-chart-type="column"' in result


# --- Full pipeline: process_markdown with charts ---

def test_chart_in_process_markdown():
    """Chart directive goes through the full process_markdown pipeline."""
    md = ":::chart bar --labels\n| Item | Value |\n|------|-------|\n| A | 50 |\n| B | 100 |\n:::"
    html, has_charts = process_markdown(md)
    assert has_charts is True
    assert "charts-css" in html
    assert "bar" in html
    assert "--size:" in html


def test_no_chart_process_markdown():
    """Without charts, process_markdown returns has_charts=False."""
    html, has_charts = process_markdown("Just **bold** text")
    assert has_charts is False
    assert "<strong>" in html


# --- E2E: Charts.css inclusion ---

def test_no_charts_no_chartscss(tmp_path):
    """Without charts, Charts.css library is NOT included in output."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\n---\n\n## Slide\nContent", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path),
    )
    assert result.returncode == 0
    html = (tmp_path / "test.html").read_text(encoding="utf-8")
    # Charts.css library defines @property --color-1; our integration CSS doesn't
    assert "@property --color-1" not in html


def test_chart_in_slide_e2e(tmp_path):
    """Chart in a slide renders with Charts.css included."""
    md_content = (
        "# Test\n\n---\n\n## Data\n\n"
        ":::chart bar --labels\n"
        "| Item | Value |\n"
        "|------|-------|\n"
        "| A    | 50    |\n"
        "| B    | 100   |\n"
        ":::\n"
    )
    md_file = tmp_path / "test.md"
    md_file.write_text(md_content, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path),
    )
    assert result.returncode == 0, f"md2 failed: {result.stdout}{result.stderr}"
    html = (tmp_path / "test.html").read_text(encoding="utf-8")
    assert "charts-css" in html
    assert "--size:" in html
