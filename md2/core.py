import html
import re
from pathlib import Path

import markdown
import bleach
from bleach.css_sanitizer import CSSSanitizer
from jinja2 import Environment, FileSystemLoader

# Bundled templates directory (inside the package)
BUNDLED_TEMPLATES_DIR = Path(__file__).parent / "templates" / "default"

# --- CONFIGURATION: Security & Sanitization ---
ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span', 'br', 'hr',
    'ul', 'ol', 'li', 'blockquote', 'pre', 'code',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'img', 'iframe'
]

ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id', 'style', 'title'],
    'a': ['href', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
    'iframe': ['src', 'width', 'height', 'allowfullscreen', 'frameborder', 'allow']
}

MD_EXTENSIONS = ['tables', 'sane_lists', 'nl2br', 'fenced_code', 'footnotes']

_SLIDE_SPLIT_RE = re.compile(r'\n+[ \t]*---[ \t]*\n+')
_AUTOLINK_RE = re.compile(r'(?<!["\x27=])(https?://[^\s<>\x27"]+)')

DEFAULT_THEME = {
    "bg_color": "#f9f9f9",
    "text_color": "#333",
    "sidebar_bg": "#ffffff",
    "h2_color": "#333",
    "font_family": '"Ubuntu", sans-serif'
}


def sanitize_html(html_content):
    """Cleans HTML to prevent XSS while allowing safe tags."""
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        css_sanitizer=CSSSanitizer(),
        strip=True
    )


def autolink(html_content):
    """Converts bare URLs in HTML text into clickable <a> links."""
    return _AUTOLINK_RE.sub(
        r'<a href="\1" target="_blank" rel="noopener">\1</a>',
        html_content
    )


def process_markdown(text):
    """Converts markdown text to sanitized, autolinked HTML."""
    raw_html = markdown.markdown(text, extensions=MD_EXTENSIONS)
    return autolink(sanitize_html(raw_html))


def prepare_context(markdown_text):
    """
    Parses markdown into a context dict for template rendering.
    Returns a dict with 'title', 'cover', and 'slides'.
    """
    raw_slides = _SLIDE_SPLIT_RE.split(markdown_text)

    cover_title = "Presentation"
    cover_content = ""

    if raw_slides:
        first_slide_text = raw_slides[0].strip()
        lines = first_slide_text.split('\n')
        if lines and lines[0].startswith('# '):
            cover_title = lines[0][2:].strip()
            cover_content = '\n'.join(lines[1:])
        else:
            cover_content = first_slide_text

    slides_data = []
    for i, slide_text in enumerate(raw_slides[1:]):
        slide_text = slide_text.strip()
        lines = slide_text.split('\n')
        slide_title = f"Slide {i + 1}"
        slide_body = slide_text

        if lines and lines[0].startswith('## '):
            slide_title = lines[0][3:].strip()
            slide_body = '\n'.join(lines[1:])

        slides_data.append({
            "id": f"slide-{i}",
            "title": slide_title,
            "content": process_markdown(slide_body)
        })

    cover_clean = process_markdown(cover_content)

    return {
        "title": cover_title,
        "cover": {
            "title": cover_title,
            "content": cover_clean
        },
        "slides": slides_data,
    }


def extract_og_description(markdown_text, fallback_title):
    """Extract OG description from cover section of markdown."""
    og_desc_lines = []
    for line in markdown_text.split('\n'):
        line = line.strip()
        if line.startswith('#') or line == '---':
            if line == '---':
                break
            continue
        if line:
            og_desc_lines.append(line)
        if len(og_desc_lines) >= 2:
            break
    return html.escape(' '.join(og_desc_lines)[:200] if og_desc_lines else fallback_title)


def get_jinja_env(template_dir=None):
    """Create a Jinja2 Environment for the given template directory (or bundled default)."""
    if template_dir is None:
        template_dir = BUNDLED_TEMPLATES_DIR
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
    )
