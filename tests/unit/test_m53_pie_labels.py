"""M53: Pie chart — no rotated labels inside, use legend with values."""
from md2.core import process_markdown


def test_pie_no_data_span_inside_slices():
    """Pie chart does not generate .data spans inside slices (illegible rotated)."""
    md = (
        ":::chart pie\n"
        "| Area | Budget |\n"
        "|------|--------|\n"
        "| R&D  | 48     |\n"
        "| Sales| 28     |\n"
        "| AI   | 24     |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<span class="data">' not in html


def test_pie_has_legend_with_values():
    """Pie chart auto-generates a legend with label + value for each slice."""
    md = (
        ":::chart pie\n"
        "| Area | Budget |\n"
        "|------|--------|\n"
        "| R&D  | 48     |\n"
        "| Sales| 28     |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "charts-css legend" in html
    # Legend should contain both the label and the value
    assert "R&amp;D" in html or "R&D" in html
    assert "48" in html
    assert "Sales" in html
    assert "28" in html


def test_non_pie_no_auto_legend_single_dataset():
    """Non-pie single-dataset charts still have no auto legend."""
    md = (
        ":::chart bar\n"
        "| Label | Value |\n"
        "|-------|-------|\n"
        "| A     | 50    |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "charts-css legend" not in html
