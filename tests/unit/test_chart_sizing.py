"""Tests for M28: Chart sizing — sensible default dimensions per chart type."""
import subprocess
import sys
import re

from md2.core import process_markdown


def _render_chart(chart_type, extra_opts=""):
    """Helper: render a chart of given type through the full pipeline."""
    md = (
        f":::chart {chart_type} {extra_opts}\n"
        "| Label | Value |\n"
        "|-------|-------|\n"
        "| A     | 50    |\n"
        "| B     | 80    |\n"
        "| C     | 30    |\n"
        ":::"
    )
    html, has_charts = process_markdown(md)
    assert has_charts
    return html


def _get_style_css():
    """Read the bundled style.css content."""
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


# --- CSS rules exist for each chart type ---

def test_pie_has_constrained_size():
    """Pie charts have viewport-relative responsive sizing."""
    css = _get_style_css()
    assert ".charts-css.pie" in css
    pie_section = css[css.index(".charts-css.pie"):]
    pie_block = pie_section[:pie_section.index("}") + 1]
    assert "aspect-ratio" in pie_block
    # Uses viewport units, not fixed px
    assert "vh" in pie_block or "vw" in pie_block


def test_column_has_viewport_height():
    """Column charts use viewport-relative height."""
    css = _get_style_css()
    assert re.search(r'\.charts-css\.column\b.*?height', css, re.DOTALL)
    # Should contain vh unit for responsive sizing
    col_idx = css.index(".charts-css.column")
    col_block = css[col_idx:css.index("}", col_idx) + 1]
    assert "vh" in col_block


def test_line_has_height():
    """Line charts have a fixed height in CSS."""
    css = _get_style_css()
    assert re.search(r'\.charts-css\.line\b.*?height', css, re.DOTALL)


def test_area_has_height():
    """Area charts have a fixed height in CSS."""
    css = _get_style_css()
    assert re.search(r'\.charts-css\.area\b.*?height', css, re.DOTALL)


def test_bar_no_fixed_height():
    """The top-level `.charts-css.bar` rule does NOT have a fixed height.
    Tbody inner rules may set `height: 100%` (M70/M85 aspect-ratio
    override) — that's a child constraint, not a fixed bar-chart height."""
    css = _get_style_css()
    # Find rules that target ONLY .charts-css.bar at the top level (not
    # `.charts-css.bar tbody` or `.charts-css.bar tr`).
    bar_matches = [
        m.start() for m in re.finditer(r'\.md2-chart \.charts-css\.bar\s*\{', css)
    ]
    for start in bar_matches:
        block = css[start:css.index("}", start) + 1]
        height_matches = re.findall(r'(?<!-)(?<!min-)\bheight\s*:', block)
        assert len(height_matches) == 0, f"Bar chart should not have fixed height: {block}"


# --- E2E: sizing shows up in rendered HTML ---

def test_chart_sizing_in_rendered_html(tmp_path):
    """Generated HTML includes the chart sizing CSS rules."""
    md_content = (
        "# Test\n\n---\n\n## Charts\n\n"
        ":::chart pie --labels\n"
        "| A | B |\n|---|---|\n| x | 50 |\n:::\n\n"
        ":::chart column --labels\n"
        "| A | B |\n|---|---|\n| x | 50 |\n:::\n"
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
    # CSS should contain pie sizing rules
    assert ".charts-css.pie" in html
    assert "height" in html
