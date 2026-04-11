"""Tests for M30: Print-optimized CSS — chart colors preserved in print."""
import re


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def _get_print_block():
    """Extract the @media print { ... } block from style.css."""
    css = _get_style_css()
    match = re.search(r'@media print\s*\{(.+?)^\}', css, re.DOTALL | re.MULTILINE)
    assert match, "No @media print block found in style.css"
    return match.group(1)


def test_print_css_no_global_star_reset():
    """Print CSS does NOT use * { color: #000; background: #fff }."""
    print_css = _get_print_block()
    # Should not have a wildcard * reset for color/background
    assert not re.search(r'\*\s*\{[^}]*color\s*:\s*#000', print_css), \
        "Print CSS should not use * { color: #000 } global reset"


def test_print_css_chart_colors_preserved():
    """Print block includes print-color-adjust for charts."""
    print_css = _get_print_block()
    assert "print-color-adjust" in print_css


def test_print_css_chart_break_avoid():
    """Charts have break-inside: avoid in print."""
    print_css = _get_print_block()
    assert "break-inside" in print_css or "page-break-inside" in print_css


def test_print_css_columns_preserved():
    """Columns layout is preserved (flex) in print."""
    print_css = _get_print_block()
    assert "md2-columns" in print_css


def test_print_css_layout_elements_reset():
    """Layout elements (body, slide, etc.) get color reset in print."""
    print_css = _get_print_block()
    # Should have selective reset for slide text elements
    assert "slide" in print_css
    assert "color" in print_css


def test_print_css_hides_ui_elements():
    """Sidebar, toggles, progress bar are hidden in print."""
    print_css = _get_print_block()
    assert "#sidebar" in print_css
    assert "display: none" in print_css
