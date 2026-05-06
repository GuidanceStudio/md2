"""M56-M58: Final chart polish — labels-size, top padding, multi-line collision."""
import re

from md2.core import process_markdown


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


# --- M56: Column labels-size reduced ---

def test_column_labels_size_zero_after_decoupling():
    """M85: column chart `--labels-size` is `0` because labels are now in
    the sibling `.md2-chart-xlabels` div. The original M56 rationale
    (small label height inside the chart) became obsolete when M85
    moved the labels out entirely."""
    css = _get_style_css()
    match = re.search(r'\.charts-css\.column\s*\{([^}]+)\}', css, re.DOTALL)
    assert match, "Column should have a CSS rule"
    assert "--labels-size: 0" in match.group(1)


def test_bar_labels_size_zero_after_decoupling():
    """M85: bar chart `--labels-size: 0` (decoupled). The previous M56
    contract (>= 100px width for left labels) was specific to in-chart
    label rendering, which M85 replaced."""
    css = _get_style_css()
    match = re.search(r'\.charts-css\.bar\s*\{([^}]+)\}', css, re.DOTALL)
    assert match
    assert "--labels-size: 0" in match.group(1)


# --- M57: Line/area top padding ---

def test_line_chart_body_flex_layout():
    """Line chart body uses flex layout (M67+M68 graduated Y-axis approach)."""
    css = _get_style_css()
    assert ".md2-chart-body" in css
    assert "display: flex" in css


def test_yaxis_stretch_alignment():
    """Y-axis stretches with chart via flex align-items (M68 alignment fix)."""
    css = _get_style_css()
    assert "align-items: stretch" in css or ".md2-chart-yaxis" in css


# --- M58: Multi-line/area no data labels ---

def test_line_multi_dataset_has_hide_data_and_legend():
    """M67: line multi has hide-data + graduated Y-axis + classic legend."""
    md = (
        ":::chart line\n"
        "| Q | A | B | C |\n"
        "|---|---|---|---|\n"
        "| 1 | 100 | 200 | 300 |\n"
        "| 2 | 150 | 250 | 350 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "hide-data" in html
    assert "md2-chart-yaxis" in html
    assert "charts-css legend" in html


def test_line_single_dataset_has_data_spans():
    """Line single-dataset still shows data values."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        "| 2 | 200 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<span class="data">' in html


def test_area_multi_dataset_has_hide_data_and_yaxis():
    """M67: area multi has hide-data + graduated Y-axis + legend."""
    md = (
        ":::chart area\n"
        "| T | A | B |\n"
        "|---|---|---|\n"
        "| 1 | 50 | 80 |\n"
        "| 2 | 70 | 90 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "hide-data" in html
    assert "md2-chart-yaxis" in html
    assert "charts-css legend" in html


def test_area_single_dataset_has_data_spans():
    """Area single-dataset still shows data values."""
    md = (
        ":::chart area\n"
        "| T | V |\n"
        "|---|---|\n"
        "| 1 | 50 |\n"
        "| 2 | 70 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<span class="data">' in html


def test_bar_multi_still_has_data_spans():
    """Bar multi-dataset still shows data spans (no collision issue)."""
    md = (
        ":::chart bar\n"
        "| M | A | B |\n"
        "|---|---|---|\n"
        "| x | 50 | 80 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<span class="data">' in html
