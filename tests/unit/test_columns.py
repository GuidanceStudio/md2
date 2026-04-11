"""Tests for M29: :::columns — two-column layout directive."""
import subprocess
import sys

from md2.core import preprocess_columns, process_markdown


# --- preprocess_columns ---

def test_columns_directive_parsed():
    """:::columns ... ::: is recognized and produces column divs."""
    md = ":::columns\nLeft content\n\n---\n\nRight content\n:::"
    result = preprocess_columns(md)
    assert 'class="md2-columns"' in result
    assert 'class="md2-col"' in result


def test_columns_two_columns():
    """The --- separator produces exactly two .md2-col divs."""
    md = ":::columns\nLeft\n\n---\n\nRight\n:::"
    result = preprocess_columns(md)
    assert result.count('class="md2-col"') == 2


def test_columns_no_separator_fallback():
    """Without --- inside, no column effect — content passes through."""
    md = ":::columns\nJust some content without separator\n:::"
    result = preprocess_columns(md)
    # Should not create columns without a separator
    assert 'class="md2-columns"' not in result


def test_columns_markdown_preserved():
    """Markdown inside columns is parsed (bold, lists, etc.)."""
    md = ":::columns\n**bold** text\n\n---\n\n- item one\n- item two\n:::"
    result = preprocess_columns(md)
    assert "<strong>bold</strong>" in result
    assert "<li>" in result


def test_columns_with_chart_inside():
    """:::chart inside :::columns works correctly."""
    md = (
        ":::columns\nSome text\n\n---\n\n"
        ":::chart bar --labels\n"
        "| A | B |\n|---|---|\n| x | 50 |\n"
        ":::\n\n:::"
    )
    # Charts are preprocessed first, then columns
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
        ":::columns\nA\n\n---\n\nB\n:::\n\n"
        "Some text between\n\n"
        ":::columns\nC\n\n---\n\nD\n:::"
    )
    result = preprocess_columns(md)
    assert result.count('class="md2-columns"') == 2
    assert result.count('class="md2-col"') == 4


# --- Full pipeline ---

def test_columns_in_process_markdown():
    """Columns go through the full process_markdown pipeline."""
    md = ":::columns\n**Left**\n\n---\n\nRight side\n:::"
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
    # Should have flex-direction: column in a media query
    assert "flex-direction: column" in css or "flex-direction:column" in css


# --- E2E ---

def test_columns_in_slide_e2e(tmp_path):
    """Columns render correctly in a full presentation."""
    md_content = (
        "# Test\n\n---\n\n## Layout\n\n"
        ":::columns\n"
        "**Left column** with text.\n\n"
        "---\n\n"
        "**Right column** with more.\n"
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
