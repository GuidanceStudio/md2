"""M50: Bar row gap via margin (not border-spacing)."""
import re


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_bar_no_border_spacing():
    """Bar chart does not rely on border-spacing (which doesn't work with flex tr)."""
    css = _get_style_css()
    # Find .charts-css.bar rule
    idx = css.index(".charts-css.bar ")
    block = css[idx:css.index("}", idx) + 1]
    assert "border-spacing" not in block


def test_bar_tr_has_margin_top():
    """Bar chart has margin-top on tr:not(:first-child) for gap."""
    css = _get_style_css()
    # Should have a rule like .bar tbody tr:not(:first-child) { margin-top: ... }
    assert re.search(
        r'\.bar\s+tbody\s+tr:not\(:first-child\)[^{]*\{[^}]*margin-top:\s*\d+px',
        css,
    )
