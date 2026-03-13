import subprocess
import sys

from md2 import render_presentation, generate_css


def _cli_html(tmp_path, md_text="# Test\n\n---\n\n## Slide\nContent"):
    md_file = tmp_path / "ui_test.md"
    md_file.write_text(md_text, encoding="utf-8")
    subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path)
    )
    html_file = tmp_path / "ui_test.html"
    return html_file.read_text(encoding="utf-8")


def test_output_has_progress_bar(tmp_path):
    html = _cli_html(tmp_path)
    assert 'id="progress-bar"' in html


def test_output_has_svg_icons(tmp_path):
    html = _cli_html(tmp_path)
    assert "<svg" in html
    assert "theme-icon-moon" in html
    assert "theme-icon-sun" in html
    assert "hamburger-icon" in html


def test_output_has_intersection_observer(tmp_path):
    html = _cli_html(tmp_path)
    assert "IntersectionObserver" in html


def test_css_has_clamp(tmp_path):
    html = _cli_html(tmp_path)
    assert "clamp(" in html


def test_css_has_scroll_snap(tmp_path):
    html = _cli_html(tmp_path)
    assert "scroll-snap-type" in html


def test_css_has_tablet_breakpoint(tmp_path):
    html = _cli_html(tmp_path)
    assert "max-width: 1024px" in html


# --- Milestone 9-13 live tests ---

def test_output_has_keyboard_navigation(tmp_path):
    html = _cli_html(tmp_path)
    assert "ArrowDown" in html
    assert "ArrowUp" in html


def test_output_has_slide_indicator(tmp_path):
    html = _cli_html(tmp_path)
    assert 'id="slide-indicator"' in html


def test_output_has_print_styles(tmp_path):
    html = _cli_html(tmp_path)
    assert "@media print" in html


def test_output_has_favicon(tmp_path):
    html = _cli_html(tmp_path)
    assert '<link rel="icon"' in html


def test_output_has_og_tags(tmp_path):
    html = _cli_html(tmp_path)
    assert 'og:title' in html
    assert 'og:description' in html


def test_output_has_lang_attribute(tmp_path):
    html = _cli_html(tmp_path)
    assert 'lang="it"' in html


def test_fenced_code_e2e(tmp_path):
    md = "# T\n\n---\n\n## S\n\n```python\nprint('hello')\n```"
    html = _cli_html(tmp_path, md)
    assert "<pre>" in html
    assert "<code" in html


def test_autolink_e2e(tmp_path):
    md = "# T\n\n---\n\n## S\n\nhttps://example.com here"
    html = _cli_html(tmp_path, md)
    assert 'href="https://example.com"' in html
