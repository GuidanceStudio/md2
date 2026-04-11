"""Palette color system — load TOML palette files, resolve cascade, generate CSS."""
import colorsys
from pathlib import Path

from ._compat import tomllib

BUILTIN_PALETTES_DIR = Path(__file__).parent / "palettes"
USER_PALETTES_DIR = Path.home() / ".md2" / "palettes"


def load_palette(name="default"):
    """Load a palette by name. User dir takes priority over builtin.

    Returns a dict with at least 'colors' (list of hex strings).
    May also contain 'dark' with its own 'colors'.
    Raises FileNotFoundError if the palette is not found.
    """
    user_file = USER_PALETTES_DIR / f"{name}.toml"
    builtin_file = BUILTIN_PALETTES_DIR / f"{name}.toml"

    if user_file.exists():
        path = user_file
    elif builtin_file.exists():
        path = builtin_file
    else:
        raise FileNotFoundError(
            f"Palette '{name}' not found in {USER_PALETTES_DIR} or {BUILTIN_PALETTES_DIR}"
        )

    with open(path, "rb") as f:
        return tomllib.load(f)


def lighten_colors(colors, amount=0.2):
    """Generate lighter variants of hex colors for dark mode.

    Increases lightness by `amount` in HSL space.
    """
    result = []
    for hex_color in colors:
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        l = min(1.0, l + amount)
        r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
        result.append(f"#{int(r2*255):02x}{int(g2*255):02x}{int(b2*255):02x}")
    return result


def resolve_colors(metadata):
    """Given frontmatter metadata, return (colors, dark_colors).

    Cascade: palette file -> frontmatter colors override.
    """
    palette_name = metadata.get("palette", "default")
    palette = load_palette(palette_name)
    if "colors" not in palette:
        raise ValueError(f"Palette '{palette_name}' is missing required 'colors' key")
    colors = list(palette["colors"])

    # Frontmatter colors override (partial merge)
    fm_colors = metadata.get("colors")
    if fm_colors:
        for i, c in enumerate(fm_colors):
            if i < len(colors):
                colors[i] = c
            else:
                colors.append(c)

    # Dark colors: explicit from palette or auto-generated
    if "dark" in palette and "colors" in palette["dark"]:
        dark_colors = list(palette["dark"]["colors"])
        # Apply same frontmatter overrides to dark if needed
        if fm_colors:
            for i, c in enumerate(fm_colors):
                lightened = lighten_colors([c])[0]
                if i < len(dark_colors):
                    dark_colors[i] = lightened
                else:
                    dark_colors.append(lightened)
    else:
        dark_colors = lighten_colors(colors)

    return colors, dark_colors


def generate_palette_css(colors, dark_colors=None):
    """Generate CSS custom properties from color lists.

    Returns a string with :root and body.dark-mode blocks.
    """
    if not colors:
        return ""

    lines = [":root {"]
    for i, c in enumerate(colors, 1):
        lines.append(f"    --md2-color-{i}: {c};")
    lines.append("}")

    if dark_colors:
        lines.append("body.dark-mode {")
        for i, c in enumerate(dark_colors, 1):
            lines.append(f"    --md2-color-{i}: {c};")
        lines.append("}")

    return "\n".join(lines)
