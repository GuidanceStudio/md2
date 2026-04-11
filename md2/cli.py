import argparse
import html
import shutil
import sys
from pathlib import Path

from .core import (
    parse_frontmatter,
    prepare_context,
    extract_og_description,
    get_jinja_env,
    BUNDLED_TEMPLATES_DIR,
)
from .palettes import resolve_colors, generate_palette_css

USER_TEMPLATES_DIR = Path.home() / ".md2" / "templates"


def _ensure_default_template():
    """Copy bundled default template to ~/.md2/templates/default/ if not present."""
    dest = USER_TEMPLATES_DIR / "default"
    if dest.exists():
        return False
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(BUNDLED_TEMPLATES_DIR, dest, dirs_exist_ok=True)
    print(f"Initialized default template in {dest}")
    return True


def _init_templates():
    """(Re)copy bundled default template to ~/.md2/templates/default/."""
    dest = USER_TEMPLATES_DIR / "default"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(BUNDLED_TEMPLATES_DIR, dest, dirs_exist_ok=True)
    print(f"Default template (re)initialized in {dest}")


def _resolve_template_dir(template_name=None):
    """Resolve template directory. Returns Path or None for bundled default."""
    if template_name:
        template_dir = USER_TEMPLATES_DIR / template_name
        if not template_dir.exists():
            print(f"Error: Template '{template_name}' not found in {template_dir}")
            sys.exit(1)
        return template_dir

    # Check if user has a default template installed
    user_default = USER_TEMPLATES_DIR / "default"
    if user_default.exists():
        return user_default

    # Auto-install default template, then use it
    _ensure_default_template()
    return user_default


def render_html(markdown_text, lang=None, dark_mode=None, template_dir=None):
    """Render markdown to a full HTML string using Jinja2 templates."""
    metadata, body = parse_frontmatter(markdown_text)
    context = prepare_context(body, metadata=metadata)

    og_description = extract_og_description(body, context["title"])
    safe_title = html.escape(context["title"])

    # Resolve lang: caller > frontmatter > default "it"
    resolved_lang = lang if lang is not None else metadata.get("lang", "it")

    # Resolve dark: caller > frontmatter > default False
    resolved_dark = dark_mode if dark_mode is not None else metadata.get("dark", False)

    # Resolve palette colors and generate CSS
    colors, dark_colors = resolve_colors(metadata)
    palette_css = generate_palette_css(colors, dark_colors)

    context.update({
        "title": safe_title,
        "og_description": og_description,
        "lang": resolved_lang,
        "dark_mode": resolved_dark,
        "palette_css": palette_css,
    })
    # Escape cover title consistently
    context["cover"]["title"] = safe_title

    # Multi-path loader for cross-template inheritance:
    # 1. The specific template dir (so its base.html and own includes resolve)
    # 2. The default template dir (so inherited includes like components/head.html resolve)
    # 3. The parent ~/.md2/templates/ (so {% extends "default/base.html" %} works)
    if template_dir and template_dir.parent == USER_TEMPLATES_DIR:
        from jinja2 import FileSystemLoader, Environment
        search_paths = [str(template_dir)]
        default_dir = USER_TEMPLATES_DIR / "default"
        if default_dir.exists() and template_dir != default_dir:
            search_paths.append(str(default_dir))
        search_paths.append(str(USER_TEMPLATES_DIR))
        loader = FileSystemLoader(search_paths)
        env = Environment(loader=loader, autoescape=False)
    else:
        env = get_jinja_env(template_dir)
    template = env.get_template("base.html")

    return template.render(context)


def main():
    """CLI entry point: converts a Markdown file to an HTML presentation."""
    parser = argparse.ArgumentParser(description="Convert a Markdown file to an HTML presentation.")
    parser.add_argument("filename", nargs="?", help="The input Markdown file")
    parser.add_argument("--lang", default=None, help="HTML lang attribute (default: it)")
    parser.add_argument("--dark", action="store_true", default=None, help="Use dark theme as default")
    parser.add_argument("--template", metavar="NAME", help="Template name from ~/.md2/templates/")
    parser.add_argument("--init-templates", action="store_true", help="(Re)initialize default template in ~/.md2/templates/")
    args = parser.parse_args()

    if args.init_templates:
        _init_templates()
        return

    if not args.filename:
        parser.error("the following arguments are required: filename")

    filepath = Path(args.filename)
    if not filepath.exists():
        print(f"Error: File '{args.filename}' not found.")
        sys.exit(1)

    template_dir = _resolve_template_dir(args.template)

    output_filename = filepath.with_suffix(".html")
    content = filepath.read_text(encoding="utf-8")
    full_html = render_html(
        content, lang=args.lang, dark_mode=args.dark, template_dir=template_dir,
    )
    output_filename.write_text(full_html, encoding="utf-8")

    print(f"Success! Generated '{output_filename}'")


if __name__ == "__main__":
    main()
