"""M104: Bar chart category labels overlapped by the adjacent bar.

Charts.css renders a bar chart's `<th>` category label as a fixed-width
(`--labels-size: 130px`) flex row via `position: absolute`. Without an
explicit wrap, long labels ("Trazione integrale / AWD") don't break
onto a second line — they overflow sideways past the 130px column and
get visually covered by the adjacent bar's colored fill.
"""
import re
from pathlib import Path


def _style_css_path():
    return Path(__file__).resolve().parents[2] / "md2" / "templates" / "default" / "style.css"


def test_bar_th_label_allows_wrapping():
    """`.md2-chart .charts-css.bar tbody tr th` must allow long labels to
    wrap within their fixed-width column instead of overflowing it."""
    css = _style_css_path().read_text()
    match = re.search(
        r'\.md2-chart \.charts-css\.bar tbody tr th\s*\{([^}]+)\}', css
    )
    assert match, "expected .md2-chart .charts-css.bar tbody tr th rule in style.css"
    rule_body = match.group(1)
    assert "white-space: normal" in rule_body, (
        "bar label text must wrap (white-space: normal) instead of "
        "overflowing past the fixed --labels-size column"
    )
    assert "flex-wrap: wrap" in rule_body, (
        "the label is a flex row (Charts.css) — flex-wrap: wrap lets "
        "its text content break onto a second line"
    )
