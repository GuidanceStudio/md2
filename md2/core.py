import html
import re
from pathlib import Path

from ._compat import tomllib

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
    'table', 'thead', 'tbody', 'tr', 'th', 'td', 'caption',
    'img', 'iframe'
]

ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id', 'style', 'title'],
    'a': ['href', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
    'iframe': ['src', 'width', 'height', 'allowfullscreen', 'frameborder', 'allow'],
    'div': ['class', 'id', 'style', 'data-chart-type', 'data-chart-options', 'data-chart-title'],
    'th': ['class', 'scope'],
}

MD_EXTENSIONS = ['tables', 'sane_lists', 'nl2br', 'fenced_code', 'footnotes']

_SLIDE_SPLIT_RE = re.compile(r'\n+[ \t]*---[ \t]*\n+')
_AUTOLINK_RE = re.compile(r'(?<!["\x27=])(https?://[^\s<>\x27"]+)')
_FRONTMATTER_RE = re.compile(r'\A\s*\+\+\+\n(.*?)\n\+\+\+\n?', re.DOTALL)
_CHART_DIRECTIVE_RE = re.compile(
    r'^:::chart\s+(\S+)(.*?)\n(.*?)\n:::',
    re.MULTILINE | re.DOTALL
)
_VALID_CHART_TYPES = {
    'bar', 'column', 'line', 'area', 'pie',
    'stacked-bar', 'stacked-column',
}
# Chart types that show data values directly on the chart
# (pie uses a legend with values instead, since slice labels would be rotated)
_CHART_TYPES_SHOW_DATA = {
    'bar', 'column', 'stacked-bar', 'stacked-column',
    'line', 'area',
}
_CHART_TITLE_RE = re.compile(r'^#{1,6}\s+(.+?)$', re.MULTILINE)
_COLUMNS_DIRECTIVE_RE = re.compile(
    r'^:::columns\n(.*?)\n:::[ \t]*$',
    re.MULTILINE | re.DOTALL
)
_CHART_DIV_RE = re.compile(
    r'<div class="md2-chart" data-chart-type="([\w-]+)"'
    r'(?:\s+data-chart-title="([^"]*)")?\s*'
    r'>(.*?)</div>',
    re.DOTALL
)

DEFAULT_THEME = {
    "bg_color": "#f9f9f9",
    "text_color": "#333",
    "sidebar_bg": "#ffffff",
    "h2_color": "#333",
    "font_family": '"Ubuntu", sans-serif'
}


def parse_frontmatter(markdown_text):
    """Extract TOML frontmatter delimited by +++ and return (metadata, body).

    If no frontmatter is found, returns ({}, original_text).
    Raises ValueError on malformed TOML.
    """
    match = _FRONTMATTER_RE.match(markdown_text)
    if not match:
        return {}, markdown_text

    toml_str = match.group(1)
    body = markdown_text[match.end():]

    if not toml_str.strip():
        return {}, body

    try:
        metadata = tomllib.loads(toml_str)
    except Exception as e:
        raise ValueError(f"Invalid TOML in frontmatter: {e}") from e

    return metadata, body


def _parse_chart_options(options_str):
    """Parse chart option flags and title from the directive line."""
    options = []
    title = ""
    parts = options_str.split()
    i = 0
    while i < len(parts):
        part = parts[i]
        if part == '--title' and i + 1 < len(parts):
            # Collect title: may be quoted ("multi word") or a single token
            i += 1
            if parts[i].startswith('"'):
                title_tokens = [parts[i]]
                while i < len(parts) and not parts[i].endswith('"'):
                    i += 1
                    if i < len(parts):
                        title_tokens.append(parts[i])
                title = " ".join(title_tokens).strip('"')
            else:
                title = parts[i]
        elif part.startswith('--'):
            options.append(part[2:])
        i += 1
    return options, title


def preprocess_chart_directives(markdown_text):
    """Find :::chart ... ::: blocks, parse tables, and produce chart HTML.

    Returns (modified_markdown, has_charts).
    The chart type is the only user input. All rendering decisions
    (labels, legend, show-data, stacked) are automatic based on type
    and data structure. An optional heading (# ... ######) inside the
    block is used as the chart title.
    """
    has_charts = False

    def _replace_chart(match):
        nonlocal has_charts
        chart_type = match.group(1).strip().lower()
        # Old options are silently ignored (backward compat)
        content = match.group(3)

        if chart_type not in _VALID_CHART_TYPES:
            return content

        has_charts = True

        # Extract optional heading as title
        title = ""
        title_match = _CHART_TITLE_RE.search(content)
        if title_match:
            title = title_match.group(1).strip()
            content = _CHART_TITLE_RE.sub('', content, count=1)

        title_attr = f' data-chart-title="{html.escape(title)}"' if title else ""

        # Parse table markdown independently
        table_html = markdown.markdown(content.strip(), extensions=['tables'])

        return (
            f'<div class="md2-chart" data-chart-type="{chart_type}"'
            f'{title_attr}>'
            f'{table_html}'
            f'</div>'
        )

    result = _CHART_DIRECTIVE_RE.sub(_replace_chart, markdown_text)
    return result, has_charts


def preprocess_columns(markdown_text):
    """Find :::columns ... ::: blocks and convert to two-column HTML layout.

    Columns are delimited by :::col markers inside the block. Content in
    each column is parsed as markdown independently. If no :::col marker
    is found, the block is left unchanged (no column effect).
    """
    def _replace_columns(match):
        content = match.group(1)

        # Split on :::col markers
        parts = re.split(r'\n*:::col\n', content)

        # First part (before any :::col) is discarded if empty
        col_contents = [p for p in parts if p.strip()]

        if len(col_contents) < 2:
            # Not enough columns — no column effect
            return content

        # Take first two columns only (max 2)
        cols_html = []
        for part in col_contents[:2]:
            col_md = part.strip()
            col_html = markdown.markdown(col_md, extensions=MD_EXTENSIONS)
            cols_html.append(f'<div class="md2-col">{col_html}</div>')

        return f'<div class="md2-columns">{"".join(cols_html)}</div>'

    return _COLUMNS_DIRECTIVE_RE.sub(_replace_columns, markdown_text)


def transform_charts(html_content):
    """Post-process HTML to convert marked chart divs into Charts.css structure.

    Finds <div class="md2-chart"> wrappers and transforms the <table> inside
    into the structure Charts.css expects.

    Note: the table HTML inside chart divs is generated by markdown.markdown()
    in preprocess_chart_directives, then passes through sanitize_html(). The
    regex extraction here assumes clean markdown-generated table tags without
    extra attributes. This is safe because the input is controlled.
    """
    def _transform_chart(match):
        raw_type = match.group(1)
        chart_title = match.group(2) or ""
        inner_html = match.group(3)

        # Resolve stacked-bar → bar + stacked class, stacked-column → column + stacked
        if raw_type == "stacked-bar":
            chart_type = "bar"
            is_stacked = True
        elif raw_type == "stacked-column":
            chart_type = "column"
            is_stacked = True
        else:
            chart_type = raw_type
            is_stacked = False

        # Parse the HTML table
        headers = re.findall(r'<th>(.*?)</th>', inner_html)
        rows = re.findall(r'<tr>(.*?)</tr>', inner_html, re.DOTALL)

        # Skip header row(s) — find data rows (those with <td>)
        data_rows = []
        for row_html in rows:
            cells = re.findall(r'<td>(.*?)</td>', row_html)
            if cells:
                # First cell is label, rest are data
                row_th = re.findall(r'<th>(.*?)</th>', row_html)
                label = row_th[0] if row_th else cells[0]
                values = cells if not row_th else cells
                if row_th:
                    data_rows.append((label, values))
                else:
                    data_rows.append((cells[0], cells[1:]))

        if not data_rows:
            return match.group(0)  # No data, return unchanged

        # Determine if multi-dataset
        num_datasets = len(data_rows[0][1]) if data_rows else 0
        is_multiple = num_datasets > 1

        # Parse numeric values into a 2D grid (rows x columns)
        parsed_values = []
        for _, values in data_rows:
            row_vals = []
            for v in values:
                try:
                    row_vals.append(float(v.strip()))
                except (ValueError, TypeError):
                    row_vals.append(0)
            parsed_values.append(row_vals)

        # Flat list and global max for normalization
        all_values = [v for row in parsed_values for v in row]
        max_val = max(all_values) if all_values and max(all_values) > 0 else 1

        # Dataset headers (for legend)
        dataset_headers = headers[1:] if len(headers) > 1 else []

        # Build CSS classes — all visual options are auto-applied
        classes = ["charts-css", chart_type]
        if is_multiple:
            classes.append("multiple")
        # Labels always on
        classes.append("show-labels")
        # Stacked when type is stacked-bar or stacked-column
        if is_stacked:
            classes.append("stacked")

        class_str = " ".join(classes)
        # Whether to show .data spans: auto per type
        show_data = raw_type in _CHART_TYPES_SHOW_DATA
        # Multi-line/area: endpoint-only labels (series name + value)
        # to avoid inline collision
        is_multi_connected = is_multiple and chart_type in ("line", "area")

        # Build new table HTML
        parts = [f'<table class="{class_str}">']

        if chart_title:
            parts.append(f'<caption>{chart_title}</caption>')

        # Thead
        parts.append('<thead><tr>')
        parts.append(f'<th scope="col">{headers[0] if headers else "Label"}</th>')
        for h in dataset_headers:
            parts.append(f'<th scope="col">{h}</th>')
        parts.append('</tr></thead>')

        # Tbody — rendering differs by type:
        # - pie: --start/--end cumulative
        # - line/area: --start = previous value (to connect segments)
        # - bar/column: --size only
        is_pie = chart_type == "pie"
        is_connected = chart_type in ("line", "area")
        parts.append('<tbody>')
        cumulative = 0.0
        total = sum(all_values) if is_pie and sum(all_values) > 0 else 1

        # For connected charts: precompute normalized values per column
        # so each column's line connects its points (single dataset only here)
        prev_norm_by_col = {}

        # Multi-line/area endpoint labels: stagger by rank of final value.
        # Charts.css positions .data in line charts unpredictably — compute-from-
        # value y doesn't match actual rendered position. Instead, we stagger
        # ALL labels by their value rank (highest at top, each below by 28px).
        # This guarantees no overlap regardless of native positioning.
        endpoint_offsets = {}  # col_idx -> pixel offset from default position
        if is_multi_connected and data_rows:
            last_row_vals = parsed_values[-1]
            # Sort cols by value descending (highest first → visually at top)
            ranked = sorted(
                range(len(last_row_vals)),
                key=lambda c: -last_row_vals[c],
            )
            # Assign offset: rank 0 → 0px, rank 1 → +28px, rank 2 → +56px
            for rank, col_idx in enumerate(ranked):
                endpoint_offsets[col_idx] = rank * 28

        for row_idx, (label, values) in enumerate(data_rows):
            parts.append('<tr>')
            parts.append(f'<th scope="row">{label}</th>')
            is_last_row = row_idx == len(data_rows) - 1
            for col_idx, v in enumerate(values):
                num_val = parsed_values[row_idx][col_idx]
                # Multi-line/area: emit data span ONLY at the endpoint (last row)
                # with format "SeriesName: Value"
                if is_multi_connected:
                    if is_last_row and num_val != 0 and col_idx < len(dataset_headers):
                        series_name = dataset_headers[col_idx]
                        offset = endpoint_offsets.get(col_idx, 0)
                        if offset != 0:
                            data_span = (
                                f'<span class="data" style="--label-offset: {offset}px">'
                                f'{series_name}: {v.strip()}</span>'
                            )
                        else:
                            data_span = f'<span class="data">{series_name}: {v.strip()}</span>'
                    else:
                        data_span = ""
                elif show_data and num_val != 0:
                    data_span = f'<span class="data">{v.strip()}</span>'
                else:
                    data_span = ""
                if is_pie:
                    flat_idx = row_idx * len(values) + col_idx
                    start = cumulative
                    proportion = all_values[flat_idx] / total
                    cumulative += proportion
                    end = cumulative
                    s_str = f"{start:g}"
                    e_str = f"{end:g}"
                    parts.append(f'<td style="--start: {s_str}; --end: {e_str}">{data_span}</td>')
                else:
                    norm = num_val / max_val
                    size_str = f"{norm:g}" if norm != int(norm) else str(int(norm))
                    if is_connected:
                        # Line/area: --start is the previous point's value for this column
                        prev = prev_norm_by_col.get(col_idx, norm)
                        start_str = f"{prev:g}" if prev != int(prev) else str(int(prev))
                        prev_norm_by_col[col_idx] = norm
                        parts.append(
                            f'<td style="--start: {start_str}; --size: {size_str}">{data_span}</td>'
                        )
                    else:
                        parts.append(f'<td style="--size: {size_str}">{data_span}</td>')
            parts.append('</tr>')
        parts.append('</tbody>')
        parts.append('</table>')

        result = "\n".join(parts)

        # Auto-add legend for multi-dataset charts — EXCEPT line/area which use
        # endpoint labels (Name: Value) that serve as legend
        if is_multiple and dataset_headers and not is_multi_connected:
            legend_items = "".join(f'<li>{h}</li>' for h in dataset_headers)
            result += f'\n<ul class="charts-css legend legend-inline">{legend_items}</ul>'
        # Pie chart: always generate a legend with label + value (since values
        # can't be shown inside slices due to rotation)
        elif is_pie:
            legend_items = "".join(
                f'<li>{label} ({values[0].strip()})</li>'
                for label, values in data_rows
            )
            result += f'\n<ul class="charts-css legend legend-inline">{legend_items}</ul>'

        # Prepend title if present
        title_html = ""
        if chart_title:
            title_html = f'<div class="md2-chart-title">{chart_title}</div>'

        return f'<div class="md2-chart">{title_html}{result}</div>'

    return _CHART_DIV_RE.sub(_transform_chart, html_content)


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
    """Converts markdown text to sanitized, autolinked HTML.

    Returns (html_string, has_charts) tuple.
    """
    text, has_charts = preprocess_chart_directives(text)
    text = preprocess_columns(text)
    raw_html = markdown.markdown(text, extensions=MD_EXTENSIONS)
    sanitized = sanitize_html(raw_html)
    result = autolink(sanitized)
    if has_charts:
        result = transform_charts(result)
    return result, has_charts


def prepare_context(markdown_text, metadata=None):
    """
    Parses markdown into a context dict for template rendering.
    Returns a dict with 'title', 'cover', 'slides', and frontmatter fields.
    """
    if metadata is None:
        metadata = {}

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

    # Frontmatter title overrides H1 for the presentation title
    if "title" in metadata:
        cover_title = metadata["title"]

    has_charts = False
    slides_data = []
    for i, slide_text in enumerate(raw_slides[1:]):
        slide_text = slide_text.strip()
        lines = slide_text.split('\n')
        slide_title = f"Slide {i + 1}"
        slide_body = slide_text

        if lines and lines[0].startswith('## '):
            slide_title = lines[0][3:].strip()
            slide_body = '\n'.join(lines[1:])

        content, slide_has_charts = process_markdown(slide_body)
        if slide_has_charts:
            has_charts = True
        slides_data.append({
            "id": f"slide-{i}",
            "title": slide_title,
            "content": content
        })

    cover_clean, cover_has_charts = process_markdown(cover_content)
    if cover_has_charts:
        has_charts = True

    return {
        "title": cover_title,
        "cover": {
            "title": cover_title,
            "content": cover_clean
        },
        "slides": slides_data,
        "palette": metadata.get("palette", "default"),
        "colors": metadata.get("colors"),
        "has_charts": has_charts,
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
