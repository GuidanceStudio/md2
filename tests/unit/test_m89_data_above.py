"""M89: large negative bars place their data label ABOVE the bar (near
the zero baseline) instead of BELOW, avoiding collision with the
xlabels div."""
import re

from md2.core import process_markdown


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_large_negative_bar_label_above():
    """A negative bar with `--size > 0.50` carries `data outside above`."""
    md = (
        ":::chart column\n"
        "| C | V |\n"
        "|---|---|\n"
        "| big_pos | 10 |\n"
        "| big_neg | -20 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    spans = re.findall(
        r'<span class="(data[^"]*)">([^<]+)</span>', html
    )
    classes_by_value = {v: c for c, v in spans}
    assert "above" in classes_by_value.get("-20", ""), (
        f"large negative bar (-20) should carry 'above' class; got "
        f"{classes_by_value!r}"
    )


def test_small_negative_bar_label_no_above():
    """A negative bar with `--size <= 0.50` keeps the label below
    (just `data outside`, no `above`)."""
    md = (
        ":::chart column\n"
        "| C | V |\n"
        "|---|---|\n"
        "| big_pos | 30 |\n"
        "| small_neg | -5 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    spans = re.findall(
        r'<span class="(data[^"]*)">([^<]+)</span>', html
    )
    classes_by_value = {v: c for c, v in spans}
    assert "outside" in classes_by_value.get("-5", "")
    assert "above" not in classes_by_value.get("-5", "")


def test_positive_bar_never_above():
    """Positive bars (small or large) never get the `above` class."""
    md = (
        ":::chart column\n"
        "| C | V |\n"
        "|---|---|\n"
        "| big | 100 |\n"
        "| small | 5 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    spans = re.findall(
        r'<span class="(data[^"]*)">([^<]+)</span>', html
    )
    classes_by_value = {v: c for c, v in spans}
    for v, c in classes_by_value.items():
        assert "above" not in c, (
            f"positive bar {v} should not carry 'above', got class={c!r}"
        )


def test_above_css_positions_label_at_top():
    """CSS rule for `.data.outside.above` aligns the label to the top
    of its `<td>` (near the zero baseline for negative bars)."""
    css = _get_style_css()
    pattern = re.compile(
        r'\.md2-chart [^{]*\.data\.outside\.above[^{]*\{([^}]+)\}',
        re.DOTALL,
    )
    match = pattern.search(css)
    assert match, "expected a .data.outside.above CSS rule"
    body = match.group(1)
    # One of these is enough: top:0, vertical-align: top, align-self: flex-start
    has_top_position = (
        re.search(r'\btop:\s*0', body)
        or "vertical-align: top" in body
        or "align-self: flex-start" in body
    )
    assert has_top_position, (
        f".data.outside.above should top-align the label, got: {body!r}"
    )
