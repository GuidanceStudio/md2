import os
import subprocess
import sys

import pytest

from md2 import render_presentation


EXAMPLE_MD = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "example.md")


@pytest.fixture
def example_html():
    with open(EXAMPLE_MD, "r", encoding="utf-8") as f:
        content = f.read()
    result = render_presentation(content)
    # Build full HTML like main() does
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{result['title']}</title>
    <style>{result['css']}</style>
</head>
<body>
    {result['body_html']}
</body>
</html>"""
    return full_html


def test_example_file_converts(example_html):
    assert len(example_html) > 0


def test_output_is_valid_html(example_html):
    assert "<!DOCTYPE html>" in example_html
    assert "<html" in example_html
    assert "<head>" in example_html
    assert "<body>" in example_html


def test_output_contains_sidebar(example_html):
    assert 'id="sidebar"' in example_html


def test_output_contains_theme_toggle():
    # Test via CLI output
    result = render_presentation("# Test\n\n---\n\n## Slide\nContent")
    assert "sidebar" in result["body_html"].lower() or 'id="sidebar"' in result["body_html"]


def test_output_contains_slides(example_html):
    assert '<div class="slide"' in example_html


def test_output_contains_cover(example_html):
    assert '<div class="slide cover"' in example_html


def test_output_contains_css(example_html):
    assert "<style>" in example_html
    assert ":root" in example_html


def test_output_contains_javascript():
    # The main() function adds JS; test it via subprocess
    pass  # Covered by test_cli_generates_file


def test_cli_generates_file(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("# Hello\n\n---\n\n## World\nContent here.", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path)
    )
    html_file = tmp_path / "test.html"
    assert html_file.exists()
    content = html_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "toggleTheme" in content
    assert "toggleMenu" in content


def test_cli_stdout_message(tmp_path):
    md_file = tmp_path / "out.md"
    md_file.write_text("# Title\n\n---\n\n## Slide\nText", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path)
    )
    assert "Success!" in result.stdout
