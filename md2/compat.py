"""Backward-compatible wrappers for the old API (generate_css, render_presentation)."""

from .core import prepare_context, get_jinja_env, BUNDLED_TEMPLATES_DIR


def generate_css(theme_config=None):
    """Read the bundled CSS file. theme_config is accepted for API compat but ignored
    (theme customization now happens at the template level)."""
    css_path = BUNDLED_TEMPLATES_DIR / "style.css"
    return css_path.read_text(encoding="utf-8")


def render_presentation(markdown_text, theme_config=None):
    """Backward-compatible wrapper: returns dict with 'title', 'body_html', 'css'."""
    context = prepare_context(markdown_text)

    env = get_jinja_env()

    sidebar_template = env.get_template("components/sidebar.html")
    sidebar_html = sidebar_template.render(context)

    cover_template = env.get_template("components/cover.html")
    cover_html = cover_template.render(context)

    slide_template = env.get_template("components/slide.html")
    slides_html = ''.join(slide_template.render(slide=s) for s in context["slides"])

    main_html = f"""
    <div id="main">
{cover_html}
        {slides_html}
    </div>
    """

    return {
        "title": context["title"],
        "body_html": sidebar_html + main_html,
        "css": generate_css(theme_config)
    }
