"""M51: Column chart gap between categories."""
import re


def _get_style_css():
    from md2.core import BUNDLED_TEMPLATES_DIR
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_column_tr_has_padding_inline():
    """Column chart tr has padding-inline to create gap between categories."""
    css = _get_style_css()
    # Should have a rule on .column tbody tr with padding-inline or margin-inline
    assert re.search(
        r'\.column\s+tbody\s+tr[^{]*\{[^}]*(padding-inline|margin-inline)',
        css,
    )
