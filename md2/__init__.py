"""md2 — Markdown to HTML Presentation Converter."""

from .core import (
    sanitize_html,
    autolink,
    process_markdown,
    preprocess_chart_directives,
    transform_charts,
    prepare_context,
    parse_frontmatter,
    extract_og_description,
    get_jinja_env,
    DEFAULT_THEME,
    ALLOWED_TAGS,
    ALLOWED_ATTRIBUTES,
    MD_EXTENSIONS,
)
from .cli import main, render_html

# Backward compatibility: generate_css and render_presentation
from .compat import generate_css, render_presentation

__all__ = [
    "sanitize_html",
    "autolink",
    "process_markdown",
    "prepare_context",
    "parse_frontmatter",
    "extract_og_description",
    "get_jinja_env",
    "generate_css",
    "render_presentation",
    "render_html",
    "main",
    "DEFAULT_THEME",
]
