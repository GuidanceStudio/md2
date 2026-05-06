"""M90: chart-body height reduced to fit a single A4 landscape page.

Goes from `min(300px, 40vh)` to `min(260px, 36vh)`, making room for
title + xlabels + legend + surrounding slide content.
"""
import re


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_chart_body_height_compact():
    """`.md2-chart-body` height uses 260px max (was 300px)."""
    css = _get_style_css()
    match = re.search(
        r'\.md2-chart-body\s*\{([^}]+)\}', css, re.DOTALL,
    )
    body = match.group(1)
    h_match = re.search(r'height:\s*min\((\d+)px', body)
    assert h_match, f"chart-body should have a height: min(...px,...) rule, got: {body!r}"
    assert int(h_match.group(1)) <= 270, (
        f"chart-body height should be <= 270px (compact), got {h_match.group(1)}px"
    )


def test_column_chart_height_matches_body():
    """`.charts-css.column` height matches the new compact body height."""
    css = _get_style_css()
    match = re.search(
        r'\.md2-chart \.charts-css\.column\s*\{([^}]+)\}', css, re.DOTALL,
    )
    body = match.group(1)
    h_match = re.search(r'height:\s*min\((\d+)px', body)
    assert h_match, f"column chart should have height rule, got: {body!r}"
    assert int(h_match.group(1)) <= 270


def test_line_area_height_also_compacted():
    """Line/area chart heights should match the same compact target so
    they're consistent in mixed decks."""
    css = _get_style_css()
    line_match = re.search(
        r'\.md2-chart \.charts-css\.line\s*\{([^}]+)\}', css, re.DOTALL,
    )
    body = line_match.group(1)
    h_match = re.search(r'height:\s*min\((\d+)px', body)
    assert h_match
    assert int(h_match.group(1)) <= 270, (
        f"line chart height should be <= 270px, got {h_match.group(1)}px"
    )
