"""M73: Chart wrapper has a border matching the table style."""
import re

from md2.core import BUNDLED_TEMPLATES_DIR


def _css():
    return (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")


def test_md2_chart_has_border():
    css = _css()
    m = re.search(r"\.md2-chart\s*\{([^}]*)\}", css)
    assert m
    block = m.group(1)
    assert "border:" in block
    assert "var(--table-border)" in block
