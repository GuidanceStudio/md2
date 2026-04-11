"""Tests for M33: :::columns with :::col — two-column layout directive."""
import subprocess
import sys

from md2.core import preprocess_columns, process_markdown


# --- preprocess_columns ---

def test_columns_directive_parsed():
    """:::columns with :::col markers produces column divs."""
    md = ":::columns\n\n:::col\nLeft content\n\n:::col\nRight content\n\n:::"
    result = preprocess_columns(md)
    assert 'class="md2-columns"' in result
    assert 'class="md2-col"' in result


def test_columns_two_columns():
    """Two :::col markers produce exactly two .md2-col divs."""
    md = ":::columns\n\n:::col\nLeft\n\n:::col\nRight\n\n:::"
    result = preprocess_columns(md)
    assert result.count('class="md2-col"') == 2


def test_columns_no_col_marker_fallback():
    """Without :::col inside, no column effect — content passes through."""
    md = ":::columns\nJust some content without col markers\n:::"
    result = preprocess_columns(md)
    assert 'class="md2-columns"' not in result


def test_columns_markdown_preserved():
    """Markdown inside columns is parsed (bold, lists, etc.)."""
    md = ":::columns\n\n:::col\n**bold** text\n\n:::col\n- item one\n- item two\n\n:::"
    result = preprocess_columns(md)
    assert "<strong>bold</strong>" in result
    assert "<li>" in result


def test_columns_with_chart_inside():
    """:::chart inside :::columns works correctly."""
    md = (
        ":::columns\n\n:::col\nSome text\n\n:::col\n"
        ":::chart bar --labels\n"
        "| A | B |\n|---|---|\n| x | 50 |\n"
        ":::\n\n:::"
    )
    from md2.core import preprocess_chart_directives
    preprocessed, has_charts = preprocess_chart_directives(md)
    result = preprocess_columns(preprocessed)
    assert 'class="md2-columns"' in result
    assert 'class="md2-chart"' in result


def test_no_columns_unchanged():
    """Text without :::columns passes through unchanged."""
    md = "Just normal **text**\n\nMore text"
    result = preprocess_columns(md)
    assert result == md


def test_multiple_columns_blocks():
    """Multiple :::columns blocks in the same text all get processed."""
    md = (
        ":::columns\n\n:::col\nA\n\n:::col\nB\n\n:::\n\n"
        "Some text between\n\n"
        ":::columns\n\n:::col\nC\n\n:::col\nD\n\n:::"
    )
    result = preprocess_columns(md)
    assert result.count('class="md2-columns"') == 2
    assert result.count('class="md2-col"') == 4


def test_columns_no_conflict_with_slide_separator():
    """--- inside :::columns is NOT treated as column separator (no conflict)."""
    md = ":::columns\n\n:::col\nText with --- horizontal rule\n\n:::col\nRight\n\n:::"
    result = preprocess_columns(md)
    # Should still produce 2 columns, --- is just markdown content
    assert result.count('class="md2-col"') == 2


# --- Full pipeline ---

def test_columns_in_process_markdown():
    """Columns go through the full process_markdown pipeline."""
    md = ":::columns\n\n:::col\n**Left**\n\n:::col\nRight side\n\n:::"
    html, _ = process_markdown(md)
    assert 'class="md2-columns"' in html
    assert "<strong>Left</strong>" in html
    assert "Right side" in html


# --- CSS ---

def test_columns_css_exists():
    """style.css contains .md2-columns flexbox rules."""
    from md2.core import BUNDLED_TEMPLATES_DIR
    css = (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")
    assert ".md2-columns" in css
    assert "display: flex" in css or "display:flex" in css


def test_columns_responsive_css():
    """CSS has a mobile breakpoint that stacks columns."""
    from md2.core import BUNDLED_TEMPLATES_DIR
    css = (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")
    assert "flex-direction: column" in css or "flex-direction:column" in css


# --- E2E ---

def test_columns_in_slide_e2e(tmp_path):
    """Columns render correctly in a full presentation."""
    md_content = (
        "# Test\n\n---\n\n## Layout\n\n"
        ":::columns\n\n"
        ":::col\n**Left column** with text.\n\n"
        ":::col\n**Right column** with more.\n\n"
        ":::\n"
    )
    md_file = tmp_path / "test.md"
    md_file.write_text(md_content, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path),
    )
    assert result.returncode == 0, f"md2 failed: {result.stdout}{result.stderr}"
    html = (tmp_path / "test.html").read_text(encoding="utf-8")
    assert "md2-columns" in html
    assert "md2-col" in html
