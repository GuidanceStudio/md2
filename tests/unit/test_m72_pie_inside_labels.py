"""M72: Pie charts display values inside slices (≥6% slices) with
horizontal text, small slices fall back to the external legend."""
import re

from md2.core import process_markdown, BUNDLED_TEMPLATES_DIR


def _css():
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


# --- wrapper + labels ---

def test_pie_has_wrapper():
    md = (
        ":::chart pie\n"
        "| L | V |\n"
        "|---|---|\n"
        "| A | 25 |\n"
        "| B | 25 |\n"
        "| C | 25 |\n"
        "| D | 25 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert 'class="md2-pie-wrapper"' in html


def test_pie_equal_slices_all_have_inline_labels():
    md = (
        ":::chart pie\n"
        "| L | V |\n"
        "|---|---|\n"
        "| A | 25 |\n"
        "| B | 25 |\n"
        "| C | 25 |\n"
        "| D | 25 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    labels = re.findall(r'class="md2-pie-label"[^>]*>([^<]+)<', html)
    assert labels == ["25", "25", "25", "25"]


def test_pie_small_slice_no_inline_label():
    """A slice < 6% does NOT get an inline label."""
    md = (
        ":::chart pie\n"
        "| L | V |\n"
        "|---|---|\n"
        "| A | 50 |\n"
        "| B | 45 |\n"
        "| C | 5  |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    labels = re.findall(r'class="md2-pie-label"[^>]*>([^<]+)<', html)
    assert "50" in labels
    assert "45" in labels
    assert "5" not in labels


def test_pie_legend_small_slices_show_value():
    """Small slices keep (value) in the legend; big slices show only name."""
    md = (
        ":::chart pie\n"
        "| L | V |\n"
        "|---|---|\n"
        "| Big | 95 |\n"
        "| Tiny | 5 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Find legend items
    legend_match = re.search(
        r'<ul class="charts-css legend[^"]*">(.*?)</ul>', html, re.DOTALL
    )
    assert legend_match
    items = re.findall(r"<li[^>]*>([^<]+)</li>", legend_match.group(1))
    # Big slice (>= 6%): no parens
    big = [i for i in items if "Big" in i][0]
    assert "(" not in big
    # Tiny slice (< 6%): has (5)
    tiny = [i for i in items if "Tiny" in i][0]
    assert "(5)" in tiny


# --- position calculation ---

def test_pie_label_positioned_with_left_top():
    md = (
        ":::chart pie\n"
        "| L | V |\n"
        "|---|---|\n"
        "| A | 50 |\n"
        "| B | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    labels = re.findall(r'class="md2-pie-label" style="([^"]+)"', html)
    assert len(labels) == 2
    for s in labels:
        assert "left:" in s
        assert "top:" in s


def test_pie_single_full_slice_centered_horizontally():
    """A 100% slice has its midpoint at 1/2 cycle = 180° (6 o'clock),
    so position is left=50%, top=50% + r (below center)."""
    md = (
        ":::chart pie\n"
        "| L | V |\n"
        "|---|---|\n"
        "| Only | 100 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    m = re.search(r'md2-pie-label" style="([^"]+)"', html)
    assert m
    # left must be exactly 50% (sin(pi) = 0)
    assert re.search(r"left:\s*50(?:\.0+)?%", m.group(1))


# --- CSS ---

def test_css_pie_wrapper_class():
    css = _css()
    assert ".md2-pie-wrapper" in css
    assert ".md2-pie-label" in css


def test_css_pie_label_transform_centers_text():
    css = _css()
    idx = css.index(".md2-pie-label")
    block = css[idx:css.index("}", idx)]
    assert "position: absolute" in block
    assert "translate(-50%, -50%)" in block
