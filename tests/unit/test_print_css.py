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


# --- M76: bulletproof hiding of UI controls in print ---

UI_ELEMENTS_HIDDEN_IN_PRINT = [
    "#sidebar",
    "#sidebar-toggle",
    "#menu-toggle",
    "#theme-toggle",
    "#progress-bar",
    "#slide-indicator",
]


def _rule_blocks_for_selector(print_css, selector):
    """Return all declaration blocks where `selector` appears in the selector list."""
    # Strip CSS comments so they don't contaminate selector parsing.
    cleaned = re.sub(r'/\*.*?\*/', '', print_css, flags=re.DOTALL)
    blocks = []
    for match in re.finditer(r'([^{}]+)\{([^{}]*)\}', cleaned):
        selectors = match.group(1)
        body = match.group(2)
        sel_list = [s.strip() for s in selectors.split(',')]
        if selector in sel_list:
            blocks.append(body)
    return blocks


def test_m76_all_ui_controls_listed_in_print():
    """Every UI control selector must appear in the print block."""
    print_css = _get_print_block()
    for selector in UI_ELEMENTS_HIDDEN_IN_PRINT:
        assert selector in print_css, f"{selector} missing from @media print"


def test_m76_ui_controls_have_bulletproof_hiding():
    """Each hidden UI control must use the bulletproof combo:
    display:none + visibility:hidden + position:absolute + offscreen + zero-size,
    all !important. Resilient to renderers that ignore one of the properties.
    """
    print_css = _get_print_block()
    required_props = [
        ("display", "none"),
        ("visibility", "hidden"),
        ("position", "absolute"),
        ("left", "-9999px"),
        ("width", "0"),
        ("height", "0"),
    ]
    for selector in UI_ELEMENTS_HIDDEN_IN_PRINT:
        blocks = _rule_blocks_for_selector(print_css, selector)
        assert blocks, f"No rule block found targeting {selector} alone in print"
        # Combine all blocks where this selector appears
        combined = "\n".join(blocks)
        for prop, value in required_props:
            pattern = rf'{prop}\s*:\s*{re.escape(value)}[^;]*!important'
            assert re.search(pattern, combined), (
                f"{selector} missing `{prop}: {value} !important` in print block"
            )
