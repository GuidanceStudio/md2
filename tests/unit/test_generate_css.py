from md2 import generate_css, DEFAULT_THEME


def test_default_theme():
    css = generate_css()
    assert "#f9f9f9" in css
    assert "#333" in css  # text_color


def test_custom_theme_override():
    css = generate_css({"bg_color": "#000000"})
    assert "#000000" in css
    # Other defaults still present
    assert "#333" in css


def test_custom_theme_full():
    custom = {
        "bg_color": "#111",
        "text_color": "#eee",
        "sidebar_bg": "#222",
        "h2_color": "#fff",
        "font_family": '"Arial", sans-serif',
    }
    css = generate_css(custom)
    for val in custom.values():
        assert val in css


def test_contains_dark_mode():
    css = generate_css()
    assert "body.dark-mode" in css


def test_contains_responsive():
    css = generate_css()
    assert "@media (max-width: 768px)" in css


def test_contains_css_variables():
    css = generate_css()
    assert ":root" in css
    for var in ["--bg-color", "--text-color", "--sidebar-bg", "--h2-color", "--font-family"]:
        assert var in css


def test_contains_sidebar_styles():
    css = generate_css()
    assert "#sidebar" in css


def test_contains_slide_styles():
    css = generate_css()
    assert ".slide" in css


def test_contains_cover_styles():
    css = generate_css()
    assert ".cover" in css


def test_contains_theme_toggle():
    css = generate_css()
    assert "#theme-toggle" in css


# --- UI Improvement tests ---

def test_clamp_font_sizes():
    css = generate_css()
    assert "clamp(" in css
    # No bare vh font-sizes (except inside clamp)
    import re
    # Find font-size declarations with bare vh (not inside clamp)
    bare_vh = re.findall(r'font-size:\s*[\d.]+vh', css)
    assert len(bare_vh) == 0, f"Found bare vh font-sizes: {bare_vh}"


def test_font_weight_headings():
    css = generate_css()
    assert "font-weight: 700" in css  # h2
    assert "font-weight: 600" in css  # h3
    assert "font-weight: 500" in css  # h4


def test_monospace_font_stack():
    css = generate_css()
    assert '"Fira Code"' in css
    assert '"JetBrains Mono"' in css
    assert '"Cascadia Code"' in css
    assert '"Consolas"' in css


def test_line_height_body():
    css = generate_css()
    assert "line-height: 1.6" in css


def test_text_color_contrast():
    assert DEFAULT_THEME["text_color"] == "#333"


def test_sidebar_box_shadow():
    css = generate_css()
    assert "box-shadow: 2px 0 8px" in css


def test_blockquote_accent():
    css = generate_css()
    assert "--blockquote-accent" in css
    assert "var(--blockquote-accent)" in css


def test_dark_mode_colors_updated():
    css = generate_css()
    assert "#0d1117" in css
    assert "#c9d1d9" in css
    assert "#161b22" in css
    assert "#1c2128" in css


def test_slide_border_solid():
    css = generate_css()
    # Should have "1px solid" for slide border, not "dashed"
    assert "1px solid var(--slide-border)" in css


def test_table_border_radius():
    css = generate_css()
    assert "border-radius: 8px" in css


def test_code_block_border():
    css = generate_css()
    assert "border: 1px solid var(--table-border)" in css


def test_image_hover():
    css = generate_css()
    assert ".slide img:hover" in css
    assert "scale(1.02)" in css


def test_sidebar_active_style():
    css = generate_css()
    assert "#sidebar a.active" in css


def test_scroll_snap():
    css = generate_css()
    assert "scroll-snap-type: y mandatory" in css
    assert "scroll-snap-align: start" in css


def test_progress_bar_style():
    css = generate_css()
    assert "#progress-bar" in css


def test_tablet_breakpoint():
    css = generate_css()
    assert "@media (max-width: 1024px)" in css


def test_max_width_content():
    css = generate_css()
    assert "max-width: 960px" in css


# --- Milestone 10-13 CSS tests ---

def test_cover_h1_clamp():
    css = generate_css()
    assert "clamp(1.8rem, 5vw, 3.5rem)" in css


def test_print_stylesheet():
    css = generate_css()
    assert "@media print" in css


def test_print_hides_sidebar():
    css = generate_css()
    assert "#sidebar" in css
    # The print block should hide sidebar
    assert "display: none !important" in css


def test_print_page_break():
    css = generate_css()
    assert "page-break-after" in css


def test_slide_indicator_style():
    css = generate_css()
    assert "#slide-indicator" in css


def test_sidebar_collapse_button():
    css = generate_css()
    assert "#sidebar-toggle" in css
    assert "#sidebar.collapsed" in css


def test_fade_in_animation():
    css = generate_css()
    assert "@keyframes fadeIn" in css
    assert ".content.visible" in css


def test_footnote_styles():
    css = generate_css()
    assert ".footnote" in css


def test_sidebar_shortcuts_style():
    css = generate_css()
    assert "#sidebar-shortcuts" in css


def test_sidebar_toggle_fixed_edge():
    css = generate_css()
    assert "left: 280px" in css
    assert "#sidebar.collapsed ~ #sidebar-toggle" in css


# --- Milestone 19: Sidebar scroll tests ---

def test_sidebar_no_overflow_y_auto():
    """Sidebar container must not scroll itself — the ul scrolls instead."""
    css = generate_css()
    # Extract the #sidebar { ... } block (first occurrence)
    import re
    match = re.search(r'#sidebar\s*\{([^}]+)\}', css)
    assert match, "#sidebar rule not found"
    sidebar_css = match.group(1)
    assert "overflow-y: auto" not in sidebar_css
    assert "overflow: hidden" in sidebar_css


def test_sidebar_ul_scrollable():
    """The slide list <ul> must have flex: 1 and overflow-y: auto."""
    css = generate_css()
    import re
    match = re.search(r'#sidebar ul\s*\{([^}]+)\}', css)
    assert match, "#sidebar ul rule not found"
    ul_css = match.group(1)
    assert "flex: 1" in ul_css
    assert "overflow-y: auto" in ul_css


def test_sidebar_shortcuts_no_margin_top_auto():
    """Shortcuts must use flex-shrink: 0 instead of margin-top: auto."""
    css = generate_css()
    import re
    match = re.search(r'#sidebar-shortcuts\s*\{([^}]+)\}', css)
    assert match, "#sidebar-shortcuts rule not found"
    shortcuts_css = match.group(1)
    assert "margin-top: auto" not in shortcuts_css
    assert "flex-shrink: 0" in shortcuts_css
