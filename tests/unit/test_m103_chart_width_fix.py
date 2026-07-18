"""M103: Bar chart domain padding wasted width; column x-labels overlapped.

Bug A: bar charts normalized `--size` against a `_nice_ticks`-padded
domain (same mechanism as column's visible Y-axis), but bar shows no
axis at all — so the padding silently shrank every bar. Fix: bar's
domain is the exact data extremes, not a rounded tick domain.

Bug B: `.md2-chart-xlabels span` used `white-space: nowrap` +
`overflow: visible`, so labels wider than their flex slice visually
overlapped the neighboring label. Fix: allow wrapping.
"""
import re

from md2.core import process_markdown


def _style_css_path():
    from pathlib import Path
    return Path(__file__).resolve().parents[2] / "md2" / "templates" / "default" / "style.css"


def test_bar_chart_largest_bar_fills_full_width():
    """Non-round max value (4.7) must not be padded to a wider tick
    domain (e.g. 8) — the largest bar should render --size: 1."""
    md = (
        ":::chart bar\n"
        "| Attributo | Score |\n"
        "|-----------|-------|\n"
        "| Trazione integrale / AWD | 4.7 |\n"
        "| Outdoor / montagna | 4.3 |\n"
        "| Comfort di marcia | 3.2 |\n"
        "| Consumi | 1.0 |\n"
        "| Prezzo | 1.4 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    sizes = [
        float(m.group(1))
        for m in re.finditer(r'--size:\s*([\d.]+)', html)
    ]
    assert sizes, "expected --size values in bar chart output"
    assert max(sizes) == 1.0, (
        f"largest bar (max value in dataset) should fill --size: 1, "
        f"got sizes {sizes} (padded domain would shrink it, e.g. 4.7/8=0.5875)"
    )


def test_bar_chart_negative_values_still_render_correctly():
    """Removing the nice-tick padding must not break negative floating-bar
    positioning: sizes stay non-negative and start+size hits the zero line."""
    md = (
        ":::chart bar\n"
        "| M | V |\n"
        "|---|---|\n"
        "| A | 10 |\n"
        "| B | -5 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    tds = re.findall(r'<td style="([^"]+)">', html)
    assert len(tds) == 2

    def _extract(style, prop):
        m = re.search(rf'--{prop}:\s*([0-9.\-]+)', style)
        return float(m.group(1)) if m else None

    starts = [_extract(td, "start") for td in tds]
    sizes = [_extract(td, "size") for td in tds]
    for s in sizes:
        assert s is not None and s >= 0
    # Domain spans the exact data extremes [-5, 10] (range 15), unpadded.
    assert abs(sizes[0] - 10 / 15) < 0.001
    assert abs(sizes[1] - 5 / 15) < 0.001
    # Negative bar's top reaches the zero baseline.
    assert abs((starts[1] + sizes[1]) - starts[0]) < 0.001


def test_xlabels_css_allows_wrapping_instead_of_overlap():
    """`.md2-chart-xlabels span` must not use nowrap+overflow:visible,
    which lets long labels visually overlap their neighbor."""
    css = _style_css_path().read_text()
    match = re.search(r'\.md2-chart-xlabels span\s*\{([^}]+)\}', css)
    assert match, "expected .md2-chart-xlabels span rule in style.css"
    rule_body = match.group(1)
    assert "white-space: normal" in rule_body, (
        "long labels must wrap (white-space: normal), not overflow "
        "sideways into the neighboring label (white-space: nowrap)"
    )
