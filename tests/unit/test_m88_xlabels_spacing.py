"""M88: separazione visiva netta tra chart-body e xlabels.

Aumenta margin-top dei xlabels e aggiunge un border-bottom al chart-body
per fungere da baseline.
"""
import re


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_xlabels_margin_top_calc_with_zero_frac():
    """M88 introduced margin-top to separate xlabels from bars; M95
    extended it to a calc() that lifts xlabels up to the zero baseline
    when `--zero-frac > 0` (mixed positive/negative data). Default
    base margin is 12px (~14px target), reduced by zero_frac × body
    height for charts that cross zero."""
    css = _get_style_css()
    match = re.search(
        r'\.md2-chart-xlabels\s*\{([^}]+)\}', css, re.DOTALL,
    )
    assert match
    body = match.group(1)
    mt_match = re.search(r'margin-top:\s*([^;]+);', body)
    assert mt_match
    decl = mt_match.group(1)
    # Either a static >= 12px, or a calc() that includes 12px and zero-frac
    if "calc(" in decl:
        assert "12px" in decl
        assert "--zero-frac" in decl
    else:
        px = int(re.search(r'(\d+)\s*px', decl).group(1))
        assert px >= 12


def test_chart_body_has_visual_baseline():
    """M88 + M95: `.md2-chart-body` has a visible baseline. M95 made it
    a `::after` pseudo-element positioned at the zero line (so for
    mixed-sign charts the X-axis line sits between positive and negative
    bars), instead of a static border-bottom."""
    css = _get_style_css()
    match = re.search(
        r'\.md2-chart-body::after\s*\{([^}]+)\}', css, re.DOTALL,
    )
    assert match, (
        "expected a `.md2-chart-body::after` rule that draws the zero "
        "baseline; not found"
    )
    body = match.group(1)
    assert "background" in body or "border" in body, (
        "::after must paint a visible baseline (background or border)"
    )


def test_chart_body_baseline_uses_theme_token():
    """The baseline uses a CSS variable so dark mode + theming work."""
    css = _get_style_css()
    match = re.search(
        r'\.md2-chart-body::after\s*\{([^}]+)\}', css, re.DOTALL,
    )
    body = match.group(1)
    assert "var(--" in body, (
        f"baseline pseudo-element should use a CSS variable for color, "
        f"got: {body!r}"
    )
