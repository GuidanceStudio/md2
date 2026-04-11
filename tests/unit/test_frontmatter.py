"""Tests for M24: TOML frontmatter parsing."""
import subprocess
import sys

from md2.core import parse_frontmatter, prepare_context


# --- parse_frontmatter unit tests ---

def test_no_frontmatter_backward_compat():
    """Without frontmatter, returns empty dict and full text."""
    md = "# Title\n\nSome content\n\n---\n\n## Slide"
    meta, body = parse_frontmatter(md)
    assert meta == {}
    assert body == md


def test_frontmatter_parsed():
    """TOML frontmatter between +++ delimiters is extracted."""
    md = '+++\ntitle = "Hello"\npalette = "warm"\n+++\n\n# Hello\n\nContent'
    meta, body = parse_frontmatter(md)
    assert meta["title"] == "Hello"
    assert meta["palette"] == "warm"


def test_frontmatter_stripped_from_content():
    """Frontmatter block does not appear in the body."""
    md = '+++\ntitle = "Hello"\n+++\n\n# Hello\n\nContent'
    meta, body = parse_frontmatter(md)
    assert "+++" not in body
    assert 'title = "Hello"' not in body
    assert "Content" in body


def test_frontmatter_with_all_fields():
    """All supported fields are parsed correctly."""
    md = (
        '+++\n'
        'title = "Report Q1"\n'
        'palette = "cool"\n'
        'colors = ["#ff0000", "#00ff00", "#0000ff"]\n'
        'lang = "en"\n'
        'dark = true\n'
        '+++\n\n'
        '# Report Q1\n\nContent'
    )
    meta, body = parse_frontmatter(md)
    assert meta["title"] == "Report Q1"
    assert meta["palette"] == "cool"
    assert meta["colors"] == ["#ff0000", "#00ff00", "#0000ff"]
    assert meta["lang"] == "en"
    assert meta["dark"] is True


def test_frontmatter_preserves_body_whitespace():
    """Body starts cleanly after frontmatter, without leading blank explosion."""
    md = '+++\ntitle = "T"\n+++\n\n# Title\n\nParagraph'
    _, body = parse_frontmatter(md)
    # Body should start with "# Title" (possibly with leading newlines, but no +++ remnants)
    stripped = body.lstrip("\n")
    assert stripped.startswith("# Title")


def test_frontmatter_empty_block():
    """Empty frontmatter block returns empty dict."""
    md = "+++\n+++\n\n# Title"
    meta, body = parse_frontmatter(md)
    assert meta == {}
    assert "# Title" in body


def test_frontmatter_malformed_toml():
    """Invalid TOML in frontmatter raises a clear error."""
    md = '+++\ntitle = [unclosed\n+++\n\n# Title'
    try:
        parse_frontmatter(md)
        assert False, "Should have raised an error"
    except ValueError as e:
        assert "frontmatter" in str(e).lower()


def test_frontmatter_only_at_start():
    """+++ in the middle of the document is NOT treated as frontmatter."""
    md = "# Title\n\nSome text\n\n+++\ntitle = \"X\"\n+++\n\nMore text"
    meta, body = parse_frontmatter(md)
    assert meta == {}
    assert "+++" in body


def test_frontmatter_with_leading_whitespace():
    """Leading blank lines before +++ — frontmatter still detected."""
    md = '\n\n+++\ntitle = "T"\n+++\n\n# Title'
    meta, body = parse_frontmatter(md)
    assert meta["title"] == "T"


# --- Integration with prepare_context ---

def test_frontmatter_title_override():
    """title in frontmatter overrides # H1 for the presentation title."""
    md = '+++\ntitle = "Custom Title"\n+++\n\n# Markdown Title\n\nContent'
    meta, body = parse_frontmatter(md)
    ctx = prepare_context(body, metadata=meta)
    assert ctx["title"] == "Custom Title"


def test_frontmatter_title_does_not_override_without():
    """Without frontmatter title, # H1 is used as before."""
    md = "# Original Title\n\nContent"
    meta, body = parse_frontmatter(md)
    ctx = prepare_context(body, metadata=meta)
    assert ctx["title"] == "Original Title"


def test_frontmatter_palette_in_context():
    """palette field is available in the context."""
    md = '+++\npalette = "warm"\n+++\n\n# Title'
    meta, body = parse_frontmatter(md)
    ctx = prepare_context(body, metadata=meta)
    assert ctx["palette"] == "warm"


def test_frontmatter_colors_in_context():
    """colors field is available in the context."""
    md = '+++\ncolors = ["#ff0000", "#00ff00"]\n+++\n\n# Title'
    meta, body = parse_frontmatter(md)
    ctx = prepare_context(body, metadata=meta)
    assert ctx["colors"] == ["#ff0000", "#00ff00"]


def test_frontmatter_lang_dark_parsed():
    """lang and dark from frontmatter are available in metadata."""
    md = '+++\nlang = "en"\ndark = true\n+++\n\n# Title'
    meta, body = parse_frontmatter(md)
    assert meta["lang"] == "en"
    assert meta["dark"] is True


def test_prepare_context_defaults_without_frontmatter():
    """Without frontmatter, context has default palette/colors."""
    md = "# Title\n\nContent"
    ctx = prepare_context(md)
    assert ctx.get("palette") == "default"
    assert ctx.get("colors") is None


# --- CLI integration ---

def _run_md2(tmp_path, md_content, extra_args=None):
    """Helper to run md2 CLI on a temp file and return generated HTML."""
    md_file = tmp_path / "test.md"
    md_file.write_text(md_content, encoding="utf-8")
    args = f"['md2', '{md_file}'"
    if extra_args:
        for a in extra_args:
            args += f", '{a}'"
    args += "]"
    result = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = {args}; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path),
    )
    assert result.returncode == 0, f"md2 failed: {result.stdout}{result.stderr}"
    return (tmp_path / "test.html").read_text(encoding="utf-8")


def test_cli_overrides_frontmatter_lang(tmp_path):
    """--lang CLI flag overrides lang in frontmatter."""
    html = _run_md2(
        tmp_path,
        '+++\nlang = "de"\n+++\n\n# Test\n\n---\n\n## Slide\nContent',
        extra_args=["--lang", "en"],
    )
    assert 'lang="en"' in html


def test_cli_frontmatter_lang_used_when_no_flag(tmp_path):
    """Frontmatter lang is used when CLI does not specify --lang."""
    html = _run_md2(
        tmp_path,
        '+++\nlang = "fr"\n+++\n\n# Test\n\n---\n\n## Slide\nContent',
    )
    assert 'lang="fr"' in html


def test_cli_frontmatter_dark(tmp_path):
    """dark = true in frontmatter applies dark mode."""
    html = _run_md2(
        tmp_path,
        '+++\ndark = true\n+++\n\n# Test\n\n---\n\n## Slide\nContent',
    )
    assert 'class="dark-mode"' in html


def test_cli_frontmatter_title_in_html(tmp_path):
    """Frontmatter title appears in the HTML <title>."""
    html = _run_md2(
        tmp_path,
        '+++\ntitle = "Custom Title"\n+++\n\n# Markdown Title\n\n---\n\n## Slide\nContent',
    )
    assert "<title>Custom Title</title>" in html
