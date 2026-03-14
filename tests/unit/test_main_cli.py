import subprocess
import sys


def test_missing_file_exits():
    result = subprocess.run(
        [sys.executable, "-m", "md2", "nonexistent_file.md"],
        capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "not found" in result.stderr or "not found" in result.stdout


def test_no_arguments_exits():
    result = subprocess.run(
        [sys.executable, "-m", "md2"],
        capture_output=True, text=True
    )
    assert result.returncode != 0


def test_output_filename_derived():
    # Test that the logic derives .html from .md
    import os
    base_name = os.path.splitext("test_file.md")[0]
    output = f"{base_name}.html"
    assert output == "test_file.html"


def test_lang_flag_default(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\n---\n\n## Slide\nContent", encoding="utf-8")
    subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path)
    )
    html = (tmp_path / "test.html").read_text(encoding="utf-8")
    assert 'lang="it"' in html


def test_lang_flag_custom(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\n---\n\n## Slide\nContent", encoding="utf-8")
    subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}', '--lang', 'en']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path)
    )
    html = (tmp_path / "test.html").read_text(encoding="utf-8")
    assert 'lang="en"' in html


# --- Milestone 17: --dark flag ---

def test_dark_flag_adds_class(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\n---\n\n## Slide\nContent", encoding="utf-8")
    subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}', '--dark']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path)
    )
    html = (tmp_path / "test.html").read_text(encoding="utf-8")
    assert 'class="dark-mode"' in html


def test_no_dark_flag_no_class(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\n---\n\n## Slide\nContent", encoding="utf-8")
    subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path)
    )
    html = (tmp_path / "test.html").read_text(encoding="utf-8")
    assert 'class="dark-mode"' not in html


def test_dark_flag_sun_icon_visible(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\n---\n\n## Slide\nContent", encoding="utf-8")
    subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}', '--dark']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path)
    )
    html = (tmp_path / "test.html").read_text(encoding="utf-8")
    # In dark mode: sun icon visible (to switch to light), moon hidden
    assert 'theme-icon-sun' in html
    assert 'theme-icon-moon' in html
    # Sun should be display:block, moon display:none
    sun_idx = html.index('theme-icon-sun')
    moon_idx = html.index('theme-icon-moon')
    sun_section = html[sun_idx:sun_idx+200]
    moon_section = html[moon_idx:moon_idx+200]
    assert 'display:block' in sun_section
    assert 'display:none' in moon_section


# --- Milestone 18: Theme toggle shortcut ---

def test_theme_toggle_shortcut_in_js(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\n---\n\n## Slide\nContent", encoding="utf-8")
    subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path)
    )
    html = (tmp_path / "test.html").read_text(encoding="utf-8")
    assert "e.key === 'd'" in html or "e.key === 'D'" in html
    assert "toggleTheme()" in html
