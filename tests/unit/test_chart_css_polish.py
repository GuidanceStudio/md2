"""Tests for M36: Chart CSS polish — bar height, line visibility, label spacing."""
import re


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_bar_has_min_height():
    """Bar chart rows have a minimum height for visibility."""
    css = _get_style_css()
    # Should have a rule for bar tr or bar td with min-height
    assert re.search(r'\.bar.*?min-height', css, re.DOTALL)


def test_line_has_line_size():
    """Line chart has --line-size set for visible lines."""
    css = _get_style_css()
    assert "--line-size" in css


def test_labels_size_adequate():
    """Labels have enough space (>= 100px) for longer text."""
    css = _get_style_css()
    # Find --labels-size values
    sizes = re.findall(r'--labels-size:\s*(\d+)px', css)
    assert any(int(s) >= 100 for s in sizes), \
        f"--labels-size should be >= 100px, found {sizes}"


def test_data_spacing_set():
    """Data spacing is configured to prevent value overlap."""
    css = _get_style_css()
    assert "--data-spacing" in css
