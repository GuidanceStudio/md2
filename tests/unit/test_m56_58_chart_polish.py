"""M56-M58: Final chart polish — labels-size, top padding, multi-line collision."""
import re

from md2.core import process_markdown


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


# --- M56: Column labels-size reduced ---

def test_column_labels_size_reduced():
    """Column chart --labels-size is small (close to text height, not 100px)."""
    css = _get_style_css()
    # Find .charts-css.column rule
    match = re.search(r'\.charts-css\.column\s*\{[^}]*--labels-size:\s*(\d+)px', css)
    assert match, "Column should have --labels-size set"
    val = int(match.group(1))
    assert val <= 40, f"Column --labels-size should be <= 40px, got {val}px"


def test_bar_labels_size_unchanged():
    """Bar chart --labels-size stays large (it's the WIDTH for left labels)."""
    css = _get_style_css()
    match = re.search(r'\.charts-css\.bar\s*\{[^}]*--labels-size:\s*(\d+)px', css)
    assert match
    val = int(match.group(1))
    assert val >= 100, f"Bar --labels-size should be >= 100px (label width), got {val}px"


# --- M57: Line/area top padding ---

def test_line_has_top_padding():
    """Line chart has padding-block-start to prevent max-value label clipping."""
    css = _get_style_css()
    # Find .charts-css.line rule
    match = re.search(r'\.charts-css\.line\s*\{[^}]*padding-block-start', css)
    assert match, "Line chart should have padding-block-start"


def test_area_has_top_padding():
    """Area chart has padding-block-start to prevent max-value label clipping."""
    css = _get_style_css()
    match = re.search(r'\.charts-css\.area\s*\{[^}]*padding-block-start', css)
    assert match, "Area chart should have padding-block-start"


# --- M58: Multi-line/area no data labels ---

def test_line_multi_dataset_no_data_spans():
    """Line multi-dataset does NOT show data spans (anti-collision)."""
    md = (
        ":::chart line\n"
        "| Q | A | B | C |\n"
        "|---|---|---|---|\n"
        "| 1 | 100 | 200 | 300 |\n"
        "| 2 | 150 | 250 | 350 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<span class="data">' not in html


def test_line_single_dataset_has_data_spans():
    """Line single-dataset still shows data values."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        "| 2 | 200 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<span class="data">' in html


def test_area_multi_dataset_no_data_spans():
    """Area multi-dataset does NOT show data spans."""
    md = (
        ":::chart area\n"
        "| T | A | B |\n"
        "|---|---|---|\n"
        "| 1 | 50 | 80 |\n"
        "| 2 | 70 | 90 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<span class="data">' not in html


def test_area_single_dataset_has_data_spans():
    """Area single-dataset still shows data values."""
    md = (
        ":::chart area\n"
        "| T | V |\n"
        "|---|---|\n"
        "| 1 | 50 |\n"
        "| 2 | 70 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<span class="data">' in html


def test_bar_multi_still_has_data_spans():
    """Bar multi-dataset still shows data spans (no collision issue)."""
    md = (
        ":::chart bar\n"
        "| M | A | B |\n"
        "|---|---|---|\n"
        "| x | 50 | 80 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert '<span class="data">' in html
