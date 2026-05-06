"""M88: separazione visiva netta tra chart-body e xlabels.

Aumenta margin-top dei xlabels e aggiunge un border-bottom al chart-body
per fungere da baseline.
"""
import re


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_xlabels_margin_top_increased():
    """`.md2-chart-xlabels` has margin-top >= 14px (was 6px)."""
    css = _get_style_css()
    match = re.search(
        r'\.md2-chart-xlabels\s*\{([^}]+)\}', css, re.DOTALL,
    )
    assert match
    body = match.group(1)
    mt_match = re.search(r'margin-top:\s*(\d+)\s*px', body)
    assert mt_match, f"expected margin-top declaration in xlabels rule, got: {body!r}"
    assert int(mt_match.group(1)) >= 14, (
        f"xlabels margin-top should be >= 14px, got {mt_match.group(1)}px"
    )


def test_chart_body_has_border_bottom():
    """`.md2-chart-body` has a `border-bottom` (visual baseline)."""
    css = _get_style_css()
    match = re.search(
        r'\.md2-chart-body\s*\{([^}]+)\}', css, re.DOTALL,
    )
    assert match
    body = match.group(1)
    assert "border-bottom" in body, (
        f"chart-body should declare border-bottom, got: {body!r}"
    )
    # The value must not be `none` or `0`
    bb_match = re.search(r'border-bottom:\s*([^;]+);', body)
    assert bb_match
    value = bb_match.group(1).strip()
    assert value.lower() != "none" and value != "0", (
        f"border-bottom should be visible, got: {value!r}"
    )


def test_chart_body_border_uses_theme_token():
    """The border-bottom uses a CSS variable (theme-aware) rather than a
    hardcoded color, so dark mode works."""
    css = _get_style_css()
    match = re.search(
        r'\.md2-chart-body\s*\{([^}]+)\}', css, re.DOTALL,
    )
    body = match.group(1)
    bb_match = re.search(r'border-bottom:\s*([^;]+);', body)
    value = bb_match.group(1)
    assert "var(--" in value, (
        f"border-bottom color should use a CSS variable, got: {value!r}"
    )
