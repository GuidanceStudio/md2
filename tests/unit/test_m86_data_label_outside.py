"""M86: data labels render readably for small bars and negative bars.

When a bar's `--size < 0.20` (less than 20% of the chart range) or its
value is negative, the value label gets a `data outside` class and
renders in default text color instead of white-on-white.
"""
import re

from md2.core import process_markdown


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_small_positive_bar_gets_outside_class():
    """A bar with `--size < 0.20` carries a `data outside` span class."""
    md = (
        ":::chart column\n"
        "| C | V |\n"
        "|---|---|\n"
        "| big | 100 |\n"
        "| small | 5 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    # Find the small bar's data span (the second one)
    spans = re.findall(
        r'<span class="(data[^"]*)">([^<]+)</span>', html
    )
    # Match by value
    classes_by_value = {v: c for c, v in spans}
    assert "outside" in classes_by_value.get("5", ""), (
        f"small bar (value=5) should have 'outside' class; got "
        f"{classes_by_value!r}"
    )
    # Big bar stays plain "data"
    assert classes_by_value.get("100", "") == "data", (
        f"big bar (value=100) should have plain 'data' class; got "
        f"{classes_by_value!r}"
    )


def test_negative_bar_gets_outside_class():
    """A negative-value bar carries a `data outside` class."""
    md = (
        ":::chart column\n"
        "| C | V |\n"
        "|---|---|\n"
        "| pos | 10 |\n"
        "| neg | -8 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    spans = re.findall(
        r'<span class="(data[^"]*)">([^<]+)</span>', html
    )
    classes_by_value = {v: c for c, v in spans}
    assert "outside" in classes_by_value.get("-8", ""), (
        f"negative bar (value=-8) should have 'outside' class; got "
        f"{classes_by_value!r}"
    )


def test_large_positive_bar_no_outside_class():
    """A bar at `--size >= 0.20` keeps the plain `data` class."""
    md = (
        ":::chart column\n"
        "| C | V |\n"
        "|---|---|\n"
        "| big | 100 |\n"
        "| medium | 50 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    spans = re.findall(
        r'<span class="(data[^"]*)">([^<]+)</span>', html
    )
    classes_by_value = {v: c for c, v in spans}
    assert classes_by_value.get("100") == "data"
    assert classes_by_value.get("50") == "data"


def test_outside_data_css_uses_text_color():
    """CSS rule for `.data.outside` uses default text color (not the
    hardcoded `#fff` used for in-bar labels) and no text-shadow."""
    css = _get_style_css()
    # Find a rule that targets .data.outside
    pattern = re.compile(
        r'\.md2-chart [^{]*\.data\.outside[^{]*\{([^}]+)\}',
        re.DOTALL,
    )
    match = pattern.search(css)
    assert match, "expected a .data.outside CSS rule"
    body = match.group(1)
    # Must use a token that is not literally "#fff"
    has_text_color = (
        "var(--text-color)" in body
        or "var(--text)" in body
        or "currentColor" in body
        or "inherit" in body
    )
    assert has_text_color, (
        f".data.outside should use a text-color token, got: {body!r}"
    )
    # text-shadow should be removed (or empty)
    assert "text-shadow: none" in body or "text-shadow:none" in body, (
        f".data.outside should clear text-shadow, got: {body!r}"
    )


def test_multi_series_mixed_signs():
    """Multi-series cashflow case: bars with mix of large/small/negative
    each get the right class."""
    md = (
        ":::chart column\n"
        "| Mese | A | B | C |\n"
        "|---|---|---|---|\n"
        "| Mag | 50000 | 21000 | 2000 |\n"
        "| Giu | 50000 | 10000 | -8000 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    spans = re.findall(
        r'<span class="(data[^"]*)">([^<]+)</span>', html
    )
    classes_by_value = {v: c for c, v in spans}
    # 50000 is the max → --size=1 → plain data
    assert classes_by_value.get("50000") == "data"
    # 2000 is small (4% of range) → outside
    assert "outside" in classes_by_value.get("2000", "")
    # -8000 is negative → outside
    assert "outside" in classes_by_value.get("-8000", "")
