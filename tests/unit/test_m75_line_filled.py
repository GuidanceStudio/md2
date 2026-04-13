"""M75: `:::chart line filled` is a friendlier alias for `:::chart area`.
Both produce the same internal markup."""
import re

from md2.core import process_markdown


def _strip_chart_type_attr(html):
    """Remove data-chart-type attr so we can compare the rest of the markup."""
    return re.sub(r' data-chart-type="[^"]*"', "", html)


def test_line_filled_uses_area_class():
    md = (
        ":::chart line filled\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 10 |\n"
        "| 2 | 20 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert re.search(r'class="charts-css area\b', html)


def test_plain_line_no_area_class():
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 10 |\n"
        "| 2 | 20 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert re.search(r'class="charts-css line\b', html)
    assert "charts-css area" not in html


def test_line_filled_and_area_produce_same_chart_markup():
    md_filled = (
        ":::chart line filled\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 10 |\n"
        "| 2 | 20 |\n"
        "| 3 | 15 |\n"
        ":::"
    )
    md_area = md_filled.replace("line filled", "area")
    html_filled, _ = process_markdown(md_filled)
    html_area, _ = process_markdown(md_area)
    assert _strip_chart_type_attr(html_filled) == _strip_chart_type_attr(
        html_area
    )


def test_line_filled_is_connected_has_yaxis():
    md = (
        ":::chart line filled\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 10 |\n"
        "| 2 | 20 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-chart-yaxis"' in html
    assert 'class="md2-chart-xlabels"' in html


def test_area_still_works_as_before():
    """Backward compat: `:::chart area` keeps producing a valid chart."""
    md = (
        ":::chart area\n"
        "| T | V |\n"
        "|---|---|\n"
        "| A | 5 |\n"
        "| B | 15 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "charts-css area" in html
