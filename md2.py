import argparse
import html
import os
import re
import sys

# Attempt to import required libraries
try:
    import markdown
    import bleach
except ImportError as e:
    print(f"Error: Missing required library: {e.name}")
    print("Please install them using: pip install markdown bleach")
    sys.exit(1)

# --- CONFIGURATION: Security & Sanitization ---
# We allow standard tags plus iframes for embeds
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

DEFAULT_THEME = {
    "bg_color": "#f9f9f9",
    "text_color": "#333",
    "sidebar_bg": "#ffffff",
    "h2_color": "#333",
    "font_family": '"Ubuntu", sans-serif'
}

def sanitize_html(html_content):
    """
    Cleans HTML to prevent XSS while allowing safe tags (like iframes for embeds).
    """
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

_AUTOLINK_RE = re.compile(r'(?<!["\x27=])(https?://[^\s<>\x27"]+)')


def autolink(html_content):
    """
    Converts bare URLs in HTML text into clickable <a> links.
    Skips URLs already inside href/src attributes (preceded by = or quotes).
    """
    return _AUTOLINK_RE.sub(
        r'<a href="\1" target="_blank" rel="noopener">\1</a>',
        html_content
    )

def process_markdown(text):
    """Converts markdown text to sanitized, autolinked HTML."""
    raw_html = markdown.markdown(text, extensions=MD_EXTENSIONS)
    return autolink(sanitize_html(raw_html))


def generate_css(theme_config=None):
    """
    Generates the CSS string based on the provided theme configuration.
    """
    theme = DEFAULT_THEME.copy()
    if theme_config:
        theme.update(theme_config)

    return f"""
        :root {{
            --bg-color: {theme['bg_color']};
            --text-color: {theme['text_color']};
            --sidebar-bg: {theme['sidebar_bg']};
            --h2-color: {theme['h2_color']};
            --font-family: {theme['font_family']};
            
            /* Static Variables */
            --sidebar-border: #e0e0e0;
            --sidebar-hover: #f0f0f0;
            --sidebar-text: #333;
            --slide-border: #ccc;
            --h2-border: #333;
            --code-bg: #f4f4f4;
            --table-border: #ddd;
            --table-header-bg: #f2f2f2;
            --cover-title-color: #222;
            --cover-text-color: #444;
            --blockquote-accent: #3498db;
        }}

        body.dark-mode {{
            --bg-color: #0d1117;
            --text-color: #c9d1d9;
            --sidebar-bg: #161b22;
            --sidebar-border: #3e3e42;
            --sidebar-hover: #2a2d2e;
            --sidebar-text: #cccccc;
            --slide-border: #444;
            --h2-color: #ffffff;
            --h2-border: #ffffff;
            --code-bg: #1c2128;
            --table-border: #555;
            --table-header-bg: #333;
            --cover-title-color: #ffffff;
            --cover-text-color: #cccccc;
            --blockquote-accent: #5dade2;
        }}

        body {{
            margin: 0;
            padding: 0;
            font-family: var(--font-family);
            display: flex;
            height: 100vh;
            overflow: hidden;
            background-color: var(--bg-color);
            color: var(--text-color);
            transition: background-color 0.3s, color 0.3s;
        }}

        /* Sidebar Styles */
        #sidebar {{
            width: 280px;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--sidebar-border);
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            flex-shrink: 0;
            transition: background-color 0.3s, border-color 0.3s;
            box-shadow: 2px 0 8px rgba(0,0,0,0.06);
        }}

        #sidebar ul {{ list-style: none; padding: 0; margin: 0; }}
        #sidebar li {{ border-bottom: 1px solid var(--sidebar-border); }}
        #sidebar a {{
            display: block; padding: 15px 20px; text-decoration: none;
            color: var(--sidebar-text); font-size: 0.95rem; transition: background 0.2s;
        }}
        #sidebar a:hover {{ background-color: var(--sidebar-hover); color: var(--text-color); }}
        #sidebar a.active {{
            border-left: 3px solid #3498db; background: var(--sidebar-hover);
            font-weight: 600;
        }}

        /* Main Content Styles */
        #main {{
            flex: 1;
            overflow-y: auto;
            padding: 40px 60px;
            scroll-behavior: smooth;
            scroll-snap-type: y mandatory;
        }}

        .slide {{
            min-height: 100vh;
            padding: 60px 0 40px 0;
            border-bottom: 1px solid var(--slide-border);
            box-sizing: border-box;
            scroll-margin-top: 40px;
            max-width: 960px;
            margin: 0 auto;
            scroll-snap-align: start;
        }}
        .slide:last-child {{ border-bottom: none; }}

        .slide h2 {{
            margin-top: 40px; padding-bottom: 10px;
            border-bottom: 2px solid var(--h2-border);
            color: var(--h2-color); font-size: clamp(1.4rem, 3vh, 2.2rem);
            font-weight: 700;
        }}
        .slide h3 {{
            margin-top: 35px; margin-bottom: 10px; font-size: clamp(1.15rem, 2.2vh, 1.6rem);
            color: var(--h2-color); border-bottom: 1px solid var(--slide-border);
            padding-bottom: 5px; letter-spacing: 0.5px; font-weight: 600;
        }}
        .slide h4 {{
            margin-top: 20px; margin-bottom: 5px; font-size: clamp(1rem, 1.8vh, 1.3rem);
            color: var(--text-color); font-weight: 500;
        }}
        .slide blockquote {{
            border-left: 4px solid var(--blockquote-accent); margin: 1em 0;
            padding: 0.5em 1.5em; background-color: var(--code-bg);
            color: var(--text-color); font-style: italic;
        }}

        /* Cover Slide */
        .cover {{
            height: 100vh; display: flex; flex-direction: column;
            justify-content: center; align-items: center; text-align: center;
        }}
        .cover h1 {{ font-size: clamp(1.8rem, 5vw, 3.5rem); margin-bottom: 0; color: var(--cover-title-color); }}
        .cover hr {{
            width: 80px; height: 3px; background: #3498db;
            border: none; margin: 20px auto 30px;
        }}
        .cover p {{ line-height: 1.6; font-size: 1.1rem; color: var(--cover-text-color); }}

        /* General Content */
        .slide p, .slide li, .slide td {{ line-height: 1.6; font-size: clamp(0.95rem, 2vh, 1.25rem); color: var(--text-color); }}
        .slide p {{ margin-bottom: 1em; }}
        .slide ul, .slide ol {{ padding-left: 40px; margin-bottom: 1em; }}
        .slide ul {{ list-style-type: disc; }}
        .slide ol {{ list-style-type: decimal; }}
        .slide pre {{
            background: var(--code-bg); padding: 15px; border-radius: 5px;
            overflow-x: auto; font-size: clamp(0.8rem, 1.5vh, 1rem);
            margin: 1.2em 0; line-height: 1.5;
            border: 1px solid var(--table-border);
        }}
        .slide code {{ font-family: "Fira Code", "JetBrains Mono", "Cascadia Code", "Consolas", monospace; background: var(--code-bg); padding: 2px 4px; border-radius: 3px; }}
        .slide pre code {{ background: none; padding: 0; }}

        /* Tables */
        .slide table {{
            border-collapse: collapse; width: 100%; margin: 30px auto;
            box-shadow: 0 2px 15px rgba(0,0,0,0.05);
            border-radius: 8px; overflow: hidden;
        }}
        .slide th, .slide td {{ border: 1px solid var(--table-border); padding: 8px; text-align: left; }}
        .slide th {{ background-color: var(--table-header-bg); font-weight: bold; }}

        /* Images */
        .slide img {{
            max-width: 100%; height: auto; display: block;
            margin: 20px auto; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .slide img:hover {{
            transform: scale(1.02); box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }}
        .content {{ max-width: 900px; margin: 0 auto; }}
        .slide a {{
            color: #3498db; text-decoration: none; border-bottom: 1px dotted #3498db; transition: color 0.2s;
        }}
        .slide a:hover {{ color: #2980b9; border-bottom-style: solid; }}

        /* Sidebar collapse toggle — fixed on sidebar edge */
        #sidebar-toggle {{
            position: fixed; top: 12px; left: 280px; z-index: 1002;
            padding: 6px 4px;
            cursor: pointer; border: 1px solid var(--sidebar-border);
            border-left: none; background: var(--sidebar-bg);
            color: var(--sidebar-text); font-size: 0.85rem;
            border-radius: 0 6px 6px 0;
            box-shadow: 2px 0 4px rgba(0,0,0,0.06);
            transition: left 0.3s ease, background 0.2s;
        }}
        #sidebar-toggle:hover {{ background: var(--sidebar-hover); }}
        #sidebar.collapsed {{ width: 0; overflow: hidden; padding: 0; border: none; }}
        #sidebar.collapsed ~ #sidebar-toggle {{ left: 0; }}

        /* Sidebar shortcuts guide */
        #sidebar-shortcuts {{
            margin-top: auto; padding: 15px 20px;
            border-top: 1px solid var(--sidebar-border);
            font-size: 0.75rem; color: var(--sidebar-text); opacity: 0.5;
            line-height: 1.8;
        }}
        #sidebar-shortcuts kbd {{
            display: inline-block; background: var(--sidebar-hover);
            border: 1px solid var(--sidebar-border); border-radius: 3px;
            padding: 0 4px; font-family: inherit; font-size: 0.7rem;
        }}

        /* Slide indicator */
        #slide-indicator {{
            position: fixed; bottom: 20px; right: 70px; z-index: 1000;
            font-size: 0.8rem; color: var(--text-color); opacity: 0.6;
            background: var(--sidebar-bg); padding: 4px 10px;
            border-radius: 12px; border: 1px solid var(--sidebar-border);
            pointer-events: none;
        }}

        /* Footnotes */
        .footnote {{
            font-size: clamp(0.75rem, 1.3vh, 0.9rem);
            color: var(--text-color); opacity: 0.8;
        }}
        .footnote hr {{
            border: none; border-top: 1px solid var(--slide-border);
            margin: 2em 0 1em;
        }}
        .footnote ol {{ padding-left: 20px; }}

        /* Mobile & UI Elements */
        #theme-toggle {{
            position: fixed; top: 20px; right: 20px; z-index: 1000;
            width: 40px; height: 40px; border-radius: 50%;
            background-color: var(--sidebar-bg); border: 1px solid var(--sidebar-border);
            color: var(--text-color); cursor: pointer; display: flex;
            align-items: center; justify-content: center; font-size: 1.2rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2); transition: transform 0.2s, background-color 0.3s;
        }}
        #theme-toggle:hover {{ transform: scale(1.1); background-color: var(--sidebar-hover); }}

        #progress-bar {{
            height: 3px; background: #3498db; position: fixed;
            top: 0; left: 0; z-index: 1100; width: 0;
            transition: width 0.2s;
        }}

        #menu-toggle {{
            display: none; position: fixed; top: 20px; right: 20px; z-index: 1001;
            background-color: var(--sidebar-bg); border: 1px solid var(--sidebar-border);
            color: var(--text-color); cursor: pointer; padding: 10px;
            border-radius: 5px; font-size: 1.2rem; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}

        /* Fade-in animation */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .slide .content.visible {{
            animation: fadeIn 0.4s ease forwards;
        }}

        /* Print stylesheet */
        @media print {{
            #sidebar, #theme-toggle, #menu-toggle, #progress-bar,
            #slide-indicator, #sidebar-toggle {{ display: none !important; }}
            body {{ display: block; height: auto; overflow: visible; }}
            #main {{
                overflow: visible; padding: 0;
                scroll-snap-type: none;
            }}
            .slide {{
                min-height: auto; page-break-after: always;
                scroll-snap-align: none; border-bottom: none;
                padding: 20px 0; max-width: 100%;
            }}
            .slide:last-child {{ page-break-after: avoid; }}
            .cover {{ height: auto; page-break-after: always; }}
            * {{ color: #000 !important; background: #fff !important;
                 box-shadow: none !important; }}
        }}

        @media (max-width: 1024px) {{
            #sidebar {{ width: 220px; }}
            #sidebar-toggle {{ left: 220px; }}
            #sidebar.collapsed ~ #sidebar-toggle {{ left: 0; }}
            #main {{ padding: 30px 40px; }}
        }}

        @media (max-width: 768px) {{
            #menu-toggle {{ display: block; }}
            #sidebar-toggle {{ display: none; }}
            #sidebar-shortcuts {{ display: none; }}
            #slide-indicator {{ display: none; }}
            #sidebar {{
                position: fixed; left: -100%; top: 0; height: 100%; width: 80%;
                max-width: 300px; z-index: 1000; transition: left 0.3s ease;
                box-shadow: 2px 0 5px rgba(0,0,0,0.5);
            }}
            #sidebar.active {{ left: 0; }}
            #main {{ padding: 20px; }}
            #theme-toggle {{ display: flex; top: auto; bottom: 20px; right: 20px; }}
            .cover h1 {{ font-size: clamp(1.5rem, 6vw, 2rem); }}
            .slide h2 {{ font-size: 1.5rem; }}
            .slide h3 {{ font-size: 1.2rem; }}
            .slide p, .slide li, .slide td {{ font-size: 1rem; line-height: 1.7; }}
            .slide pre {{ font-size: 0.9rem; }}
            .slide table {{
                display: block; overflow-x: auto; white-space: nowrap;
                margin: 30px 0; width: 100%;
            }}
        }}
    """

def render_presentation(markdown_text, theme_config=None):
    """
    Core logic: Converts Markdown to HTML structure (Slides + Sidebar).
    Returns a dictionary containing the HTML body and the CSS.
    """
    # Split by '---' surrounded by newlines
    raw_slides = _SLIDE_SPLIT_RE.split(markdown_text)

    slides_data = []
    cover_title = "Presentation"
    cover_content = ""

    # Process Cover
    if raw_slides:
        first_slide_text = raw_slides[0].strip()
        lines = first_slide_text.split('\n')
        if lines and lines[0].startswith('# '):
            cover_title = lines[0][2:].strip()
            cover_content = '\n'.join(lines[1:])
        else:
            cover_content = first_slide_text

    # Process Slides
    for i, slide_text in enumerate(raw_slides[1:]):
        slide_text = slide_text.strip()
        lines = slide_text.split('\n')
        slide_title = f"Slide {i + 1}"
        slide_body = slide_text

        if lines and lines[0].startswith('## '):
            slide_title = lines[0][3:].strip()
            slide_body = '\n'.join(lines[1:])

        clean_html = process_markdown(slide_body)

        slides_data.append({
            "id": f"slide-{i}",
            "title": slide_title,
            "content": clean_html
        })

    cover_clean = process_markdown(cover_content)

    # Build Sidebar HTML
    sidebar_items = ''.join([f'<li><a href="#{s["id"]}">{s["title"]}</a></li>' for s in slides_data])
    sidebar_html = f"""
    <div id="sidebar">
        <ul>
            <li><a href="#cover">{cover_title}</a></li>
            {sidebar_items}
        </ul>
        <div id="sidebar-shortcuts">
            <kbd>&#8595;</kbd> <kbd>&#8594;</kbd> Next<br>
            <kbd>&#8593;</kbd> <kbd>&#8592;</kbd> Prev<br>
            <kbd>Home</kbd> / <kbd>End</kbd><br>
            <kbd>S</kbd> Toggle Sidebar
        </div>
    </div>
    <button id="sidebar-toggle" onclick="toggleSidebar()" title="Toggle Sidebar">&#171;</button>
    """

    # Build Main Content HTML
    slides_html = ''.join([
        f'<div class="slide" id="{s["id"]}"><h2>{s["title"]}</h2><div class="content">{s["content"]}</div></div>' 
        for s in slides_data
    ])
    
    main_html = f"""
    <div id="main">
        <div class="slide cover" id="cover">
            <h1>{cover_title}</h1>
            <hr>
            <div>{cover_clean}</div>
        </div>
        {slides_html}
    </div>
    """

    return {
        "title": cover_title,
        "body_html": sidebar_html + main_html,
        "css": generate_css(theme_config)
    }

def main():
    """
    CLI Wrapper: Generates a full standalone HTML file.
    """
    parser = argparse.ArgumentParser(description="Convert a Markdown file to an HTML presentation.")
    parser.add_argument("filename", help="The input Markdown file")
    parser.add_argument("--lang", default="it", help="HTML lang attribute (default: it)")
    parser.add_argument("--dark", action="store_true", help="Use dark theme as default")
    args = parser.parse_args()

    if not os.path.exists(args.filename):
        print(f"Error: File '{args.filename}' not found.")
        sys.exit(1)

    base_name = os.path.splitext(args.filename)[0]
    output_filename = f"{base_name}.html"

    with open(args.filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Call the core engine
    result = render_presentation(content)

    # Extract OG description from first non-empty lines of cover
    og_desc_lines = []
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('#') or line == '---':
            if line == '---':
                break
            continue
        if line:
            og_desc_lines.append(line)
        if len(og_desc_lines) >= 2:
            break
    og_description = html.escape(' '.join(og_desc_lines)[:200] if og_desc_lines else result['title'])
    safe_title = html.escape(result['title'])

    # Wrap in full HTML shell (with inline JS for local testing)
    body_class = ' class="dark-mode"' if args.dark else ''
    sun_display = 'block' if args.dark else 'none'
    moon_display = 'none' if args.dark else 'block'
    full_html = f"""<!DOCTYPE html>
<html lang="{args.lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_title}</title>
    <meta name="description" content="{og_description}">
    <meta property="og:title" content="{safe_title}">
    <meta property="og:type" content="website">
    <meta property="og:description" content="{og_description}">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='15' fill='%233498db'/><text x='50' y='68' font-size='60' font-family='Arial' fill='white' text-anchor='middle' font-weight='bold'>M</text></svg>">
    <style>{result['css']}</style>
</head>
<body{body_class}>
    <!-- Progress Bar -->
    <div id="progress-bar"></div>

    <!-- Hamburger Button (Mobile Only) -->
    <button id="menu-toggle" onclick="toggleMenu()" aria-label="Toggle Menu">
        <svg id="hamburger-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
    </button>

    {result['body_html']}

    <!-- Slide Indicator -->
    <div id="slide-indicator"></div>

    <!-- Theme Toggle -->
    <button id="theme-toggle" onclick="toggleTheme()" title="Toggle Theme">
        <svg id="theme-icon-sun" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="display:{sun_display};">
            <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
        <svg id="theme-icon-moon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="display:{moon_display};">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
    </button>

    <script>
        function toggleTheme() {{
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            document.getElementById('theme-icon-sun').style.display = isDark ? 'block' : 'none';
            document.getElementById('theme-icon-moon').style.display = isDark ? 'none' : 'block';
        }}
        function toggleMenu() {{
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('active');
        }}

        // Progress bar
        const mainEl = document.getElementById('main');
        const progressBar = document.getElementById('progress-bar');
        mainEl.addEventListener('scroll', function() {{
            const scrollTop = mainEl.scrollTop;
            const scrollHeight = mainEl.scrollHeight - mainEl.clientHeight;
            const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
            progressBar.style.width = progress + '%';
        }});

        // Slide tracking state
        const slides = document.querySelectorAll('.slide');
        const slidesArray = Array.from(slides);
        const sidebarLinks = document.querySelectorAll('#sidebar a');
        const slideIndicator = document.getElementById('slide-indicator');
        const totalSlides = slides.length;
        let currentSlideIndex = 0;

        function updateIndicator(index) {{
            currentSlideIndex = index;
            slideIndicator.textContent = (index + 1) + ' / ' + totalSlides;
        }}
        updateIndicator(0);

        // Single IntersectionObserver for sidebar active link + slide indicator
        const slideObserver = new IntersectionObserver(function(entries) {{
            entries.forEach(function(entry) {{
                if (entry.isIntersecting) {{
                    const id = entry.target.id;
                    sidebarLinks.forEach(function(link) {{
                        link.classList.remove('active');
                        if (link.getAttribute('href') === '#' + id) {{
                            link.classList.add('active');
                        }}
                    }});
                    const idx = slidesArray.indexOf(entry.target);
                    if (idx >= 0) updateIndicator(idx);
                }}
            }});
        }}, {{ root: mainEl, threshold: 0.3 }});
        slides.forEach(function(slide) {{ slideObserver.observe(slide); }});

        // Fade-in animation for slide content
        const fadeObserver = new IntersectionObserver(function(entries) {{
            entries.forEach(function(entry) {{
                if (entry.isIntersecting) entry.target.classList.add('visible');
            }});
        }}, {{ root: mainEl, threshold: 0.1 }});
        document.querySelectorAll('.slide .content').forEach(function(el) {{ fadeObserver.observe(el); }});

        // Sidebar collapse (always open by default)
        function toggleSidebar() {{
            const sidebar = document.getElementById('sidebar');
            const btn = document.getElementById('sidebar-toggle');
            sidebar.classList.toggle('collapsed');
            btn.innerHTML = sidebar.classList.contains('collapsed') ? '&#187;' : '&#171;';
        }}

        // Keyboard navigation
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === 'PageDown') {{
                e.preventDefault();
                slidesArray[Math.min(currentSlideIndex + 1, slidesArray.length - 1)].scrollIntoView({{ behavior: 'smooth' }});
            }} else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft' || e.key === 'PageUp') {{
                e.preventDefault();
                slidesArray[Math.max(currentSlideIndex - 1, 0)].scrollIntoView({{ behavior: 'smooth' }});
            }} else if (e.key === 'Home') {{
                e.preventDefault();
                slidesArray[0].scrollIntoView({{ behavior: 'smooth' }});
            }} else if (e.key === 'End') {{
                e.preventDefault();
                slidesArray[slidesArray.length - 1].scrollIntoView({{ behavior: 'smooth' }});
            }} else if (e.key === 's' || e.key === 'S') {{
                e.preventDefault();
                toggleSidebar();
            }}
        }});
    </script>
</body>
</html>"""

    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"Success! Generated '{output_filename}'")

if __name__ == "__main__":
    main()
