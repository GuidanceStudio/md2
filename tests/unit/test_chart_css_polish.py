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


def test_xlabels_decoupled_div_styled():
    """M85 made x-labels decoupled to a sibling `.md2-chart-xlabels` div
    instead of relying on Charts.css internal `--labels-size`. The CSS
    must define rules for that div so labels remain readable."""
    css = _get_style_css()
    assert ".md2-chart-xlabels" in css, (
        "expected .md2-chart-xlabels CSS rules — labels are now in a "
        "sibling div (M70 for line/area, M85 for column/bar)"
    )


def test_data_spacing_set():
    """Data spacing is configured to prevent value overlap."""
    css = _get_style_css()
    assert "--data-spacing" in css
