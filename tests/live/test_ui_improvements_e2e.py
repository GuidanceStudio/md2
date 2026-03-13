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
