"""Tests for M35: Chart value normalization and zero handling."""
import re

from md2.core import process_markdown


def _get_sizes(html):
    """Extract all --size values from HTML."""
    return [float(s) for s in re.findall(r'--size:\s*([\d.]+)', html)]


def test_multi_dataset_global_normalization():
    """Multi-dataset normalizes to a single global max across all values.

    All bars share the same scale so they're truly comparable.
    With values [2, 12, 62, 87, 99, 100], max = 100, so:
    - Deploy/week Q3=2 → 0.02
    - Deploy/week Q1=12 → 0.12
    - Test Coverage Q3=62 → 0.62
    - Uptime Q1=100 → 1.0
    """
    md = (
        ":::chart bar\n"
        "| Metric        | Q3 2025 | Q1 2026 |\n"
        "|---------------|---------|----------|\n"
        "| Deploy/week   | 2       | 12       |\n"
        "| Test Coverage | 62      | 87       |\n"
        "| Uptime %      | 99      | 100      |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    sizes = _get_sizes(html)
    # Global max = 100, so values are normalized to their ratio of 100
    assert 0.02 in sizes  # Deploy/week Q3 = 2/100
    assert 0.12 in sizes  # Deploy/week Q1 = 12/100
    assert 0.62 in sizes  # Test Coverage Q3 = 62/100
    assert 1.0 in sizes  # Uptime Q1 = 100/100


def test_single_dataset_normalization_unchanged():
    """Single dataset still normalizes to global max (unchanged behavior)."""
    md = (
        ":::chart bar --labels\n"
        "| Item | Value |\n"
        "|------|-------|\n"
        "| A    | 50    |\n"
        "| B    | 100   |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    sizes = _get_sizes(html)
    assert sizes == [0.5, 1.0]


def test_zero_value_renders_data_span():
    """M81 enabled the zero data span; M87 added the `zero` class so the
    label renders as muted ghost text. The span is present either way —
    accept both class forms for backward compat."""
    md = (
        ":::chart column --labels --legend\n"
        "| Pillar       | Engineers | ML Specialists |\n"
        "|--------------|-----------|----------------|\n"
        "| Core         | 8         | 0              |\n"
        "| Intelligence | 5         | 2              |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Accept either `data` or `data zero` (M87) class on the zero label
    assert (
        '<span class="data">0</span>' in html
        or '<span class="data zero">0</span>' in html
    )
    # The td with --size: 0 still exists for chart structure
    assert "--size: 0" in html


def test_zero_value_still_has_td():
    """Zero values still produce a <td> element (for chart structure)."""
    md = (
        ":::chart bar\n"
        "| A | V |\n"
        "|---|---|\n"
        "| x | 0 |\n"
        "| y | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Both rows should have td elements
    assert html.count("<td ") == 2


def test_multi_dataset_all_zeros_column():
    """A column that's all zeros doesn't cause division by zero."""
    md = (
        ":::chart column --legend\n"
        "| A | Real | Empty |\n"
        "|---|------|-------|\n"
        "| x | 50   | 0     |\n"
        "| y | 100  | 0     |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Should not crash, zeros produce --size: 0
    assert "--size: 0" in html
    assert "--size: 1" in html
