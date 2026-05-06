"""M70: Decouple x-labels from Charts.css tbody for line/area baseline alignment."""
import re

from md2.core import process_markdown, BUNDLED_TEMPLATES_DIR


def _css():
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


# --- HTML structure ---

def test_line_chart_emits_xlabels_div():
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| Q1 | 100 |\n"
        "| Q2 | 200 |\n"
        "| Q3 | 300 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-chart-xlabels"' in html


def test_area_chart_emits_xlabels_div():
    md = (
        ":::chart area\n"
        "| T | V |\n"
        "|---|---|\n"
        "| A | 10 |\n"
        "| B | 20 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-chart-xlabels"' in html


def test_bar_chart_now_has_xlabels_div():
    """M85: bar chart now uses the decoupled xlabels pattern (was
    line/area only in M70). Reverses the original M70 assertion."""
    md = (
        ":::chart bar\n"
        "| L | V |\n"
        "|---|---|\n"
        "| x | 1 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "md2-chart-xlabels" in html


def test_column_chart_now_has_xlabels_div():
    """M85: column chart also adopts decoupled xlabels."""
    md = (
        ":::chart column\n"
        "| L | V |\n"
        "|---|---|\n"
        "| x | 1 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "md2-chart-xlabels" in html


def test_xlabels_span_count_matches_rows():
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| Q1 | 100 |\n"
        "| Q2 | 200 |\n"
        "| Q3 | 300 |\n"
        "| Q4 | 400 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    m = re.search(
        r'<div class="md2-chart-xlabels">(.*?)</div>', html, re.DOTALL
    )
    assert m
    spans = re.findall(r"<span[^>]*>([^<]*)</span>", m.group(1))
    assert spans == ["Q1", "Q2", "Q3", "Q4"]


def test_xlabels_outside_chart_body():
    """xlabels div is sibling of md2-chart-body, inside md2-chart."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| Q1 | 100 |\n"
        "| Q2 | 200 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    body_idx = html.index("md2-chart-body")
    body_end = html.index("</div>", html.index("</table>", body_idx)) + len(
        "</div>"
    )
    xlabels_idx = html.index("md2-chart-xlabels")
    assert xlabels_idx > body_end


# --- CSS rules ---

def test_css_labels_size_zero_for_line_area():
    css = _css()
    # Should set --labels-size: 0 for line/area
    assert re.search(
        r"\.charts-css\.line[^{]*\{[^}]*--labels-size:\s*0",
        css,
    ) or re.search(
        r"line[^{}]*,[^{}]*area[^{}]*\{[^}]*--labels-size:\s*0",
        css,
    )


def test_css_hides_row_th_for_line_area():
    css = _css()
    assert "th[scope" in css and "display: none" in css


def test_css_xlabels_class_defined():
    css = _css()
    assert ".md2-chart-xlabels" in css


def test_css_yaxis_no_more_padding_bottom_24():
    """Yaxis must no longer use the fragile padding-bottom: 24px hack."""
    css = _css()
    m = re.search(r"\.md2-chart-yaxis\s*\{([^}]*)\}", css)
    assert m
    block = m.group(1)
    assert "padding-bottom: 24px" not in block
