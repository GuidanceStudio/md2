import argparse
import html
import sys
from pathlib import Path

from .core import prepare_context, extract_og_description, get_jinja_env


def render_html(markdown_text, lang="it", dark_mode=False, template_dir=None):
    """Render markdown to a full HTML string using Jinja2 templates."""
    context = prepare_context(markdown_text)

    og_description = extract_og_description(markdown_text, context["title"])
    safe_title = html.escape(context["title"])

    context.update({
        "title": safe_title,
        "og_description": og_description,
        "lang": lang,
        "dark_mode": dark_mode,
    })
    # Escape cover title consistently
    context["cover"]["title"] = safe_title

    env = get_jinja_env(template_dir)
    template = env.get_template("base.html")
    return template.render(context)


def main():
    """CLI entry point: converts a Markdown file to an HTML presentation."""
    parser = argparse.ArgumentParser(description="Convert a Markdown file to an HTML presentation.")
    parser.add_argument("filename", help="The input Markdown file")
    parser.add_argument("--lang", default="it", help="HTML lang attribute (default: it)")
    parser.add_argument("--dark", action="store_true", help="Use dark theme as default")
    args = parser.parse_args()

    filepath = Path(args.filename)
    if not filepath.exists():
        print(f"Error: File '{args.filename}' not found.")
        sys.exit(1)

    output_filename = filepath.with_suffix(".html")

    content = filepath.read_text(encoding="utf-8")
    full_html = render_html(content, lang=args.lang, dark_mode=args.dark)
    output_filename.write_text(full_html, encoding="utf-8")

    print(f"Success! Generated '{output_filename}'")


if __name__ == "__main__":
    main()
