"""M54: Line/area chart values shown on points for readability."""
from md2.core import process_markdown


def test_line_chart_shows_data_values():
    """Line chart now shows .data spans on points."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        "| 2 | 250 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<span class="data">' in html
    assert "100" in html
    assert "250" in html


def test_area_chart_shows_data_values():
    """Area chart now shows .data spans on points."""
    md = (
        ":::chart area\n"
        "| T | V |\n"
        "|---|---|\n"
        "| 1 | 30 |\n"
        "| 2 | 70 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<span class="data">' in html
    assert "30" in html
    assert "70" in html
