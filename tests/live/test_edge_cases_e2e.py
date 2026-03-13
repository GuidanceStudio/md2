import subprocess
import sys

import pytest

from md2 import render_presentation


def _full_html(md_text):
    result = render_presentation(md_text)
    return f"""<!DOCTYPE html>
<html lang="en">
<head><title>{result['title']}</title><style>{result['css']}</style></head>
<body>{result['body_html']}</body>
</html>"""


def test_empty_file():
    html = _full_html("")
    assert "<!DOCTYPE html>" in html
    assert "<body>" in html


def test_only_cover():
    html = _full_html("# Just a Cover\n\nNo slides here.")
    assert "Just a Cover" in html
    assert "slide-0" not in html


def test_unicode_content():
    md = "# 日本語タイトル 🎉\n\n---\n\n## Slide 🚀\nEmoji content: 🎊✨"
    html = _full_html(md)
    assert "日本語タイトル" in html
    assert "🎉" in html
    assert "🚀" in html


def test_large_file():
    slides = "\n".join([f"\n---\n\n## Slide {i}\nContent for slide {i}" for i in range(50)])
    md = "# Large Presentation\n" + slides
    html = _full_html(md)
    assert 'id="slide-49"' in html


def test_special_characters_in_title():
    md = "# Title with <angle> & \"quotes\"\n\n---\n\n## Slide\nContent"
    result = render_presentation(md)
    # Title should be extracted (the raw text, rendering handles escaping)
    assert "angle" in result["title"] or "<angle>" in result["title"]


def test_output_overwrites_existing(tmp_path):
    md_file = tmp_path / "overwrite.md"
    html_file = tmp_path / "overwrite.html"
    html_file.write_text("OLD CONTENT", encoding="utf-8")
    md_file.write_text("# New\n\n---\n\n## Fresh\nContent", encoding="utf-8")
    subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path)
    )
    content = html_file.read_text(encoding="utf-8")
    assert "OLD CONTENT" not in content
    assert "New" in content


def test_nested_markdown():
    md = "# T\n\n---\n\n## S\n\n> - item in blockquote\n> - another item"
    html = _full_html(md)
    assert "<blockquote>" in html


def test_multiple_separators_consecutive():
    md = "# T\n\n---\n\n---\n\n---\n\n## Final\nContent"
    result = render_presentation(md)
    # Should not crash
    assert result["title"] == "T"


def test_only_separators():
    md = "---\n\n---\n\n---"
    result = render_presentation(md)
    assert "title" in result
    assert "body_html" in result


def test_title_html_escaped(tmp_path):
    md = '# Title with "quotes" & <angles>\n\n---\n\n## Slide\nContent'
    md_file = tmp_path / "esc.md"
    md_file.write_text(md, encoding="utf-8")
    subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path)
    )
    html = (tmp_path / "esc.html").read_text(encoding="utf-8")
    # OG meta content should have escaped quotes/angles
    assert '&quot;' in html or '&#x27;' in html or '&amp;' in html


def test_xss_in_markdown():
    md = "# T\n\n---\n\n## S\n\n<script>document.cookie</script>\n\nSafe text"
    html = _full_html(md)
    assert "<script>" not in html.split("<script>")[0] if "<script>" in html else True
    # More precise: the slide content should not contain script
    result = render_presentation(md)
    assert "<script>" not in result["body_html"]
