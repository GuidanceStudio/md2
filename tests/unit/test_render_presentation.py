from md2 import render_presentation, process_markdown, autolink, prepare_context


SAMPLE_MD = """# My Presentation

Cover text here.

---

## Introduction
First slide content.

---

## Details
Second slide content.

---

## Conclusion
Final slide.
"""


def _render(md=SAMPLE_MD, **kwargs):
    return render_presentation(md, **kwargs)


# --- Cover ---

def test_cover_title_extraction():
    result = _render()
    assert result["title"] == "My Presentation"


def test_cover_default_title():
    result = _render("Some text without H1\n\n---\n\n## Slide")
    assert result["title"] == "Presentation"


def test_cover_content():
    result = _render()
    assert "Cover text here" in result["body_html"]


# --- Slides ---

def test_slide_splitting():
    result = _render()
    assert 'id="slide-0"' in result["body_html"]
    assert 'id="slide-1"' in result["body_html"]
    assert 'id="slide-2"' in result["body_html"]


def test_slide_titles():
    result = _render()
    assert "Introduction" in result["body_html"]
    assert "Details" in result["body_html"]
    assert "Conclusion" in result["body_html"]


def test_slide_default_title():
    md = "# Cover\n\n---\n\nContent without H2"
    result = _render(md)
    assert "Slide 1" in result["body_html"]


# --- Sidebar ---

def test_sidebar_contains_all_titles():
    result = _render()
    html = result["body_html"]
    assert "Introduction" in html
    assert "Details" in html
    assert "Conclusion" in html


def test_sidebar_contains_cover_link():
    result = _render()
    assert 'href="#cover"' in result["body_html"]


# --- Markdown rendering ---

def test_markdown_tables_rendered():
    md = "# T\n\n---\n\n## S\n\n| A | B |\n|---|---|\n| 1 | 2 |"
    result = _render(md)
    assert "<table>" in result["body_html"]


def test_markdown_code_blocks_rendered():
    md = "# T\n\n---\n\n## S\n\n    indented code block"
    result = _render(md)
    assert "<code>" in result["body_html"]


def test_markdown_lists_rendered():
    md = "# T\n\n---\n\n## S\n\n- item1\n- item2"
    result = _render(md)
    assert "<ul>" in result["body_html"]
    assert "<li>" in result["body_html"]


def test_markdown_links_rendered():
    md = "# T\n\n---\n\n## S\n\n[click](https://example.com)"
    result = _render(md)
    assert '<a href="https://example.com">' in result["body_html"]


def test_markdown_images_rendered():
    md = "# T\n\n---\n\n## S\n\n![alt](img.png)"
    result = _render(md)
    assert "<img" in result["body_html"]
    assert 'src="img.png"' in result["body_html"]


def test_markdown_blockquote_rendered():
    md = "# T\n\n---\n\n## S\n\n> quoted text"
    result = _render(md)
    assert "<blockquote>" in result["body_html"]


def test_markdown_inline_code_rendered():
    md = "# T\n\n---\n\n## S\n\nUse `variable` here"
    result = _render(md)
    assert "<code>" in result["body_html"]
    assert "variable" in result["body_html"]


# --- Structure ---

def test_empty_input():
    result = _render("")
    assert "title" in result
    assert "body_html" in result
    assert "css" in result


def test_single_slide_no_separator():
    result = _render("# Only Cover\n\nSome content")
    assert result["title"] == "Only Cover"
    assert "slide-0" not in result["body_html"]


def test_result_structure():
    result = _render()
    assert "title" in result
    assert "body_html" in result
    assert "css" in result


def test_result_title_type():
    result = _render()
    assert isinstance(result["title"], str)


def test_result_css_type():
    result = _render()
    assert isinstance(result["css"], str)
    assert len(result["css"]) > 0


def test_slide_ids_sequential():
    result = _render()
    html = result["body_html"]
    assert 'id="slide-0"' in html
    assert 'id="slide-1"' in html
    assert 'id="slide-2"' in html


def test_cover_has_correct_classes():
    result = _render()
    assert 'class="slide cover"' in result["body_html"]
    assert 'id="cover"' in result["body_html"]


def test_multiple_slides():
    md = "# T\n" + "\n---\n\n## S{}\ncontent\n".format("") * 5
    # Build 5 slides
    slides = "\n".join([f"\n---\n\n## Slide {i}\ncontent" for i in range(5)])
    md = "# T\n" + slides
    result = _render(md)
    for i in range(5):
        assert f'id="slide-{i}"' in result["body_html"]


def test_html_sanitized_in_slides():
    md = "# T\n\n---\n\n## S\n\n<script>alert(1)</script>Safe text"
    result = _render(md)
    assert "<script>" not in result["body_html"]
    assert "Safe text" in result["body_html"]


def test_css_contains_default_values():
    result = _render()
    assert "#f9f9f9" in result["css"]  # default bg_color


# --- Milestone 9: Parser extensions ---

def test_fenced_code_blocks():
    md = "# T\n\n---\n\n## S\n\n```\nsome code\n```"
    result = _render(md)
    assert "<pre>" in result["body_html"]
    assert "<code>" in result["body_html"]


def test_fenced_code_with_language():
    md = "# T\n\n---\n\n## S\n\n```python\nprint(1)\n```"
    result = _render(md)
    assert "<pre>" in result["body_html"]
    assert "<code" in result["body_html"]


def test_autolink_url():
    md = "# T\n\n---\n\n## S\n\nhttps://example.com here"
    result = _render(md)
    assert 'href="https://example.com"' in result["body_html"]


def test_autolink_no_double_wrap():
    md = "# T\n\n---\n\n## S\n\n[click](https://example.com)"
    result = _render(md)
    assert result["body_html"].count('href="https://example.com"') == 1


def test_footnotes_rendered():
    md = "# T\n\n---\n\n## S\n\nText[^1]\n\n[^1]: Footnote text"
    result = _render(md)
    assert "Footnote text" in result["body_html"]


# --- Milestone 10: Cover typography ---

def test_cover_text_centered():
    css = _render()["css"]
    assert "text-align: center" in css


# --- Milestone 11: Sidebar toggle ---

def test_sidebar_has_toggle_button():
    result = _render()
    assert "sidebar-toggle" in result["body_html"]


# --- Simplify: process_markdown helper ---

def test_process_markdown_basic():
    html = process_markdown("Hello **world**")
    assert "<strong>world</strong>" in html


def test_process_markdown_autolinks():
    html = process_markdown("Visit https://example.com today")
    assert 'href="https://example.com"' in html


def test_process_markdown_sanitizes():
    html = process_markdown("<script>alert(1)</script>Safe")
    assert "<script>" not in html
    assert "Safe" in html


# --- Simplify: autolink lookbehind ---

def test_autolink_skips_href():
    assert autolink('<a href="https://x.com">').count("https://x.com") == 1


def test_autolink_skips_src():
    assert autolink('<img src="https://x.com/i.png">').count("https://x.com") == 1


def test_autolink_wraps_bare_url():
    result = autolink("<p>https://x.com here</p>")
    assert '<a href="https://x.com"' in result


def test_autolink_skips_equals():
    result = autolink('data=https://x.com/path')
    assert "<a " not in result


def test_process_markdown_fenced_code():
    html = process_markdown("```python\nprint(1)\n```")
    assert "<pre>" in html
    assert "<code" in html


def test_process_markdown_footnotes():
    html = process_markdown("Text[^1]\n\n[^1]: My footnote")
    assert "My footnote" in html


def test_process_markdown_table():
    html = process_markdown("| A | B |\n|---|---|\n| 1 | 2 |")
    assert "<table>" in html


# --- Milestone 15: Sidebar UX ---

def test_sidebar_has_shortcuts_guide():
    result = _render()
    assert 'id="sidebar-shortcuts"' in result["body_html"]


def test_sidebar_shortcuts_content():
    result = _render()
    html = result["body_html"]
    assert "Next" in html
    assert "Prev" in html
    assert "Home" in html
    assert "End" in html


# --- Milestone 16: Sidebar toggle shortcut ---

def test_sidebar_shortcuts_shows_toggle_key():
    result = _render()
    html = result["body_html"]
    assert "Toggle Sidebar" in html
    assert "<kbd>S</kbd>" in html


# --- Milestone 18: Theme toggle shortcut ---

def test_sidebar_shortcuts_shows_theme_toggle_key():
    result = _render()
    html = result["body_html"]
    assert "Toggle Theme" in html
    assert "<kbd>D</kbd>" in html


# --- Milestone 21: prepare_context ---

def test_prepare_context_structure():
    ctx = prepare_context(SAMPLE_MD)
    assert "title" in ctx
    assert "cover" in ctx
    assert "slides" in ctx
    assert ctx["title"] == "My Presentation"
    assert ctx["cover"]["title"] == "My Presentation"
    assert "<p>" in ctx["cover"]["content"]


def test_prepare_context_slides():
    ctx = prepare_context(SAMPLE_MD)
    assert len(ctx["slides"]) == 3
    assert ctx["slides"][0]["id"] == "slide-0"
    assert ctx["slides"][0]["title"] == "Introduction"
    assert ctx["slides"][1]["id"] == "slide-1"
    assert ctx["slides"][1]["title"] == "Details"
    assert ctx["slides"][2]["id"] == "slide-2"
    assert ctx["slides"][2]["title"] == "Conclusion"


def test_prepare_context_default_title():
    ctx = prepare_context("Just some text\n\n---\n\n## Slide 1")
    assert ctx["title"] == "Presentation"


def test_prepare_context_empty():
    ctx = prepare_context("")
    assert ctx["title"] == "Presentation"
    assert ctx["slides"] == []
