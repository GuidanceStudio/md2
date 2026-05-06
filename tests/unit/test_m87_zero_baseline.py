"""M87: zero-value bars render their `0` label as ghost text on the
baseline, not as a tiny pill.

The `<span class="data zero">0</span>` gets its own CSS rule that drops
the white text + text-shadow styling and uses a neutral muted color.
"""
import re

from md2.core import process_markdown


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_zero_value_gets_zero_class():
    """A `0` value emits `<span class="data zero">0</span>`."""
    md = (
        ":::chart column\n"
        "| C | V |\n"
        "|---|---|\n"
        "| A | 10 |\n"
        "| B | 0 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    spans = re.findall(
        r'<span class="(data[^"]*)">([^<]+)</span>', html
    )
    classes_by_value = {v: c for c, v in spans}
    assert classes_by_value.get("0") == "data zero", (
        f"zero-value span should have class 'data zero', got "
        f"{classes_by_value!r}"
    )


def test_nonzero_no_zero_class():
    """Non-zero values do not get the `zero` class even if they are
    small (those get `outside` instead, M86)."""
    md = (
        ":::chart column\n"
        "| C | V |\n"
        "|---|---|\n"
        "| A | 10 |\n"
        "| B | 1 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    spans = re.findall(
        r'<span class="(data[^"]*)">([^<]+)</span>', html
    )
    classes_by_value = {v: c for c, v in spans}
    assert "zero" not in classes_by_value.get("10", "")
    # 1 is small (10% of range) → 'outside', not 'zero'
    assert "zero" not in classes_by_value.get("1", "")


def test_zero_class_css_styling():
    """CSS rule for `.data.zero` removes the white-on-bar styling and
    uses a muted text color (ghost effect)."""
    css = _get_style_css()
    pattern = re.compile(
        r'\.md2-chart [^{]*\.data\.zero[^{]*\{([^}]+)\}',
        re.DOTALL,
    )
    match = pattern.search(css)
    assert match, "expected a .data.zero CSS rule"
    body = match.group(1)
    has_text_color = (
        "var(--text-color)" in body
        or "var(--text)" in body
        or "currentColor" in body
        or "inherit" in body
    )
    assert has_text_color, f".data.zero should use text-color token, got: {body!r}"
    assert "text-shadow: none" in body or "text-shadow:none" in body, (
        f".data.zero should clear text-shadow, got: {body!r}"
    )
    # Muted via opacity (ghost effect)
    assert re.search(r'opacity:\s*0\.[0-7]', body), (
        f".data.zero should set opacity < 0.7 for ghost effect, got: {body!r}"
    )
