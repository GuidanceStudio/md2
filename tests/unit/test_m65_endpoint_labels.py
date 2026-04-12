"""M65: Endpoint labels for multi-line/area + robust .data override."""
import re

from md2.core import process_markdown


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


# --- Single-dataset: all values shown ---

def test_single_line_shows_all_values():
    """Single-dataset line chart shows data span for every point."""
    md = (
        ":::chart line\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| 1 | 100 |\n"
        "| 2 | 200 |\n"
        "| 3 | 300 |\n"
        "| 4 | 400 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Should have 4 data spans, one per point
    assert html.count('<span class="data">') == 4
    # No "Name: Value" format for single (no series name)
    assert ":" not in re.findall(r'<span class="data">([^<]+)</span>', html)[0]


def test_single_area_shows_all_values():
    """Single-dataset area chart shows data span for every point."""
    md = (
        ":::chart area\n"
        "| T | V |\n"
        "|---|---|\n"
        "| 1 | 50 |\n"
        "| 2 | 80 |\n"
        "| 3 | 30 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert html.count('<span class="data">') == 3


# --- Multi-dataset: only endpoint labels with Name: Value format ---

def test_multi_line_only_endpoint_labels():
    """Multi-dataset line chart shows data span ONLY at last data point per series."""
    md = (
        ":::chart line\n"
        "| Q | A | B | C |\n"
        "|---|---|---|---|\n"
        "| 1 | 100 | 200 | 300 |\n"
        "| 2 | 150 | 250 | 350 |\n"
        "| 3 | 200 | 300 | 400 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # 3 series, only endpoint = 3 data spans total
    assert html.count('<span class="data">') == 3


def test_multi_line_label_has_header_prefix():
    """Multi-line endpoint labels contain the dataset header as prefix."""
    md = (
        ":::chart line\n"
        "| Q | Enterprise | SMB |\n"
        "|---|-----------|-----|\n"
        "| 1 | 500       | 1200 |\n"
        "| 2 | 6000      | 9000 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Endpoint labels should include series name
    assert "Enterprise" in html
    assert "SMB" in html
    # Format "Name: Value" (both series and value in same span)
    spans = re.findall(r'<span class="data">([^<]+)</span>', html)
    assert len(spans) == 2
    assert any("Enterprise" in s and "6000" in s for s in spans)
    assert any("SMB" in s and "9000" in s for s in spans)


def test_multi_area_only_endpoint_labels():
    """Multi-area chart also uses endpoint-only labels."""
    md = (
        ":::chart area\n"
        "| T | X | Y |\n"
        "|---|---|---|\n"
        "| 1 | 10 | 20 |\n"
        "| 2 | 30 | 40 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert html.count('<span class="data">') == 2
    spans = re.findall(r'<span class="data">([^<]+)</span>', html)
    assert any("X" in s and "30" in s for s in spans)
    assert any("Y" in s and "40" in s for s in spans)


# --- No legend for multi-line/area (label IS the legend) ---

def test_multi_line_no_legend():
    """Multi-line chart has no separate legend (endpoint labels include names)."""
    md = (
        ":::chart line\n"
        "| Q | A | B |\n"
        "|---|---|---|\n"
        "| 1 | 100 | 200 |\n"
        "| 2 | 150 | 250 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "charts-css legend" not in html


def test_multi_area_no_legend():
    """Multi-area chart has no legend."""
    md = (
        ":::chart area\n"
        "| T | X | Y |\n"
        "|---|---|---|\n"
        "| 1 | 10 | 20 |\n"
        "| 2 | 30 | 40 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "charts-css legend" not in html


def test_bar_multi_still_has_legend():
    """Bar multi still has legend (only line/area drop it)."""
    md = (
        ":::chart bar\n"
        "| M | A | B |\n"
        "|---|---|---|\n"
        "| x | 50 | 80 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    assert "charts-css legend" in html


# --- CSS override presence ---

def test_line_data_has_transform_override():
    """Line/area .data has transform override to position labels safely."""
    css = _get_style_css()
    assert re.search(
        r'\.(?:line|area) \.data[^{]*\{[^}]*transform',
        css,
    )


def test_line_data_high_z_index():
    """Line/area .data has high z-index (10+) to clear sibling td colors."""
    css = _get_style_css()
    match = re.search(
        r'\.(?:line|area) \.data[^{]*\{[^}]*z-index:\s*(\d+)',
        css,
    )
    assert match
    assert int(match.group(1)) >= 10


# --- Obsolete rules removed ---

def test_no_padding_block_start_on_line_area():
    """M57 padding-block-start removed from .line and .area."""
    css = _get_style_css()
    line_match = re.search(r'\.charts-css\.line\s*\{([^}]*)\}', css)
    if line_match:
        assert "padding-block-start" not in line_match.group(1)
    area_match = re.search(r'\.charts-css\.area\s*\{([^}]*)\}', css)
    if area_match:
        assert "padding-block-start" not in area_match.group(1)


def test_no_multi_line_legend_margin_override():
    """M63 obsolete: no margin override for multi-line legend."""
    css = _get_style_css()
    # Should not have a rule targeting .line.multiple ul.legend with margin-top
    assert not re.search(
        r':has\([^)]*\.line\.multiple[^)]*\)[^{]*ul\.legend[^{]*\{[^}]*margin-top',
        css,
    )
