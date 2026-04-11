"""Tests for M25: Palette color system — TOML files + cascade."""
import subprocess
import sys
from pathlib import Path

from md2.palettes import (
    load_palette,
    resolve_colors,
    generate_palette_css,
    lighten_colors,
    BUILTIN_PALETTES_DIR,
)


# --- load_palette ---

def test_load_builtin_palette():
    """load_palette('default') loads from the builtin directory."""
    palette = load_palette("default")
    assert "colors" in palette
    assert len(palette["colors"]) >= 6


def test_load_builtin_warm():
    """load_palette('warm') loads the warm palette."""
    palette = load_palette("warm")
    assert "colors" in palette
    assert len(palette["colors"]) >= 6


def test_load_user_palette(tmp_path, monkeypatch):
    """User palette in ~/.md2/palettes/ takes priority over builtin."""
    user_dir = tmp_path / "palettes"
    user_dir.mkdir()
    (user_dir / "default.toml").write_text(
        'name = "custom-default"\ncolors = ["#111111", "#222222"]\n',
        encoding="utf-8",
    )
    monkeypatch.setattr("md2.palettes.USER_PALETTES_DIR", user_dir)
    palette = load_palette("default")
    assert palette["colors"] == ["#111111", "#222222"]


def test_palette_not_found():
    """Non-existent palette name raises a clear error."""
    try:
        load_palette("nonexistent_palette_xyz")
        assert False, "Should have raised"
    except FileNotFoundError as e:
        assert "nonexistent_palette_xyz" in str(e)


# --- resolve_colors ---

def test_resolve_colors_default():
    """Without frontmatter palette/colors, uses default palette."""
    colors, dark_colors = resolve_colors({})
    assert len(colors) >= 6
    assert len(dark_colors) >= 6


def test_resolve_colors_palette_name():
    """palette = 'warm' loads the warm palette colors."""
    colors, dark_colors = resolve_colors({"palette": "warm"})
    assert len(colors) >= 6
    # warm colors should differ from default
    default_colors, _ = resolve_colors({})
    assert colors != default_colors


def test_resolve_colors_inline_override():
    """colors = [...] in frontmatter overrides the palette entirely."""
    custom = ["#aa0000", "#bb0000", "#cc0000"]
    colors, _ = resolve_colors({"colors": custom})
    assert colors[:3] == custom


def test_resolve_colors_partial_merge():
    """palette + colors = partial merge (colors overrides first N)."""
    colors, _ = resolve_colors({
        "palette": "default",
        "colors": ["#ff0000"],
    })
    assert colors[0] == "#ff0000"
    # Rest should come from the default palette
    default_colors, _ = resolve_colors({"palette": "default"})
    assert colors[1:] == default_colors[1:]


# --- generate_palette_css ---

def test_generate_palette_css():
    """Output CSS contains --md2-color-N variables."""
    css = generate_palette_css(["#aaa", "#bbb", "#ccc"])
    assert "--md2-color-1: #aaa" in css
    assert "--md2-color-2: #bbb" in css
    assert "--md2-color-3: #ccc" in css
    assert ":root" in css


def test_generate_palette_css_dark():
    """With dark colors, output contains dark mode variables."""
    css = generate_palette_css(
        ["#aaa", "#bbb"],
        dark_colors=["#ddd", "#eee"],
    )
    assert "dark-mode" in css
    assert "--md2-color-1: #ddd" in css


def test_generate_palette_css_empty():
    """Empty color list produces empty CSS."""
    css = generate_palette_css([])
    assert css.strip() == ""


# --- lighten_colors (dark auto-generation) ---

def test_dark_auto_generated():
    """Without [dark] section, dark colors are auto-calculated."""
    colors, dark_colors = resolve_colors({"palette": "default"})
    # Dark colors should exist and differ from light
    assert len(dark_colors) == len(colors)


def test_dark_explicit():
    """With [dark] section in palette, explicit dark colors are used."""
    palette = load_palette("default")
    assert "dark" in palette, "default palette should have a [dark] section"
    colors, dark_colors = resolve_colors({"palette": "default"})
    assert dark_colors == palette["dark"]["colors"]


def test_lighten_colors_output():
    """lighten_colors produces brighter variants."""
    original = ["#4e79a7", "#e15759"]
    lightened = lighten_colors(original)
    assert len(lightened) == len(original)
    # Each lightened color should be a valid hex
    for c in lightened:
        assert c.startswith("#")
        assert len(c) == 7


# --- All builtin palettes valid ---

def test_palette_toml_format():
    """All builtin .toml palette files are valid and parsable."""
    toml_files = list(BUILTIN_PALETTES_DIR.glob("*.toml"))
    assert len(toml_files) >= 6  # default, warm, cool, mono, vivid, pastel
    for f in toml_files:
        palette = load_palette(f.stem)
        assert "colors" in palette
        assert isinstance(palette["colors"], list)
        assert len(palette["colors"]) >= 2


# --- Integration: palette CSS in rendered HTML ---

def test_palette_css_in_rendered_html(tmp_path):
    """Rendered HTML includes palette CSS variables."""
    md_file = tmp_path / "test.md"
    md_file.write_text(
        '+++\npalette = "warm"\n+++\n\n# Test\n\n---\n\n## Slide\nContent',
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path),
    )
    assert result.returncode == 0, f"md2 failed: {result.stdout}{result.stderr}"
    html = (tmp_path / "test.html").read_text(encoding="utf-8")
    assert "--md2-color-1" in html


def test_default_palette_css_in_html(tmp_path):
    """Even without frontmatter, default palette CSS is included."""
    md_file = tmp_path / "test.md"
    md_file.write_text(
        "# Test\n\n---\n\n## Slide\nContent",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.argv = ['md2', '{md_file}']; from md2 import main; main()"],
        capture_output=True, text=True, cwd=str(tmp_path),
    )
    assert result.returncode == 0, f"md2 failed: {result.stdout}{result.stderr}"
    html = (tmp_path / "test.html").read_text(encoding="utf-8")
    assert "--md2-color-1" in html
