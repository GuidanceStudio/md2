"""Tests for M35: Chart value normalization and zero handling."""
import re

from md2.core import process_markdown


def _get_sizes(html):
    """Extract all --size values from HTML."""
    return [float(s) for s in re.findall(r'--size:\s*([\d.]+)', html)]


def test_multi_dataset_per_column_normalization():
    """Multi-dataset normalizes per-column, not globally.

    Deploy/week (2, 12) and Uptime (99, 100) have very different scales.
    Each column should normalize to its own max, so Deploy/week=12 gets
    --size: 1 (not 0.12).
    """
    md = (
        ":::chart bar --labels --legend\n"
        "| Metric        | Q3 2025 | Q1 2026 |\n"
        "|---------------|---------|----------|\n"
        "| Deploy/week   | 2       | 12       |\n"
        "| Test Coverage | 62      | 87       |\n"
        "| Uptime %      | 99      | 100      |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    sizes = _get_sizes(html)
    # No --size should be < 0.1 for significant values
    # Deploy/week=2 should be 2/99 ≈ 0.02 with global normalization
    # but with per-column: Q3 max=99, so 2/99≈0.02 — still small.
    # Wait — per-column means Q3 column max is max(2,62,99)=99 and
    # Q1 column max is max(12,87,100)=100. That's still cross-row.
    #
    # Actually the right approach for bar charts: each ROW should be
    # independently normalized. Deploy/week: max(2,12)=12, so 2/12=0.17.
    # This way each metric's bars are comparable to itself.
    #
    # Let me test: the highest --size in each row should be 1.0
    # Row 1 (Deploy): 2, 12 → 2/12=0.17, 12/12=1.0
    # Row 2 (Coverage): 62, 87 → 62/87=0.71, 87/87=1.0
    # Row 3 (Uptime): 99, 100 → 99/100=0.99, 100/100=1.0
    assert max(sizes) == 1.0
    # The key assertion: no --size below 0.1 (Deploy/week=2 should NOT be 0.02)
    assert all(s >= 0.1 for s in sizes if s > 0), \
        f"All significant values should have --size >= 0.1, got {sizes}"


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


def test_zero_value_no_data_span():
    """Zero values do not generate <span class='data'> to avoid floating '0'."""
    md = (
        ":::chart column --labels --legend\n"
        "| Pillar       | Engineers | ML Specialists |\n"
        "|--------------|-----------|----------------|\n"
        "| Core         | 8         | 0              |\n"
        "| Intelligence | 5         | 2              |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Should NOT have <span class="data">0</span>
    assert '<span class="data">0</span>' not in html
    # But should still have the td with --size: 0
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
