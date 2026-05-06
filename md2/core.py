import html
import math
import re
import sys
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


def _nice_step(raw_step):
    """Round a raw step to a 'nice' value: 1, 2, 2.5, 5, 7.5, 10 × 10^n."""
    if raw_step <= 0:
        return 1
    power = 10 ** math.floor(math.log10(raw_step))
    normalized = raw_step / power
    if normalized <= 1:
        nice = 1
    elif normalized <= 2:
        nice = 2
    elif normalized <= 2.5:
        nice = 2.5
    elif normalized <= 5:
        nice = 5
    elif normalized <= 7.5:
        nice = 7.5
    else:
        nice = 10
    return nice * power


def _fmt_tick(v):
    """Format a tick value as int if integer, else rounded."""
    if v == int(v):
        return int(v)
    return round(v, 2)


def _nice_ticks(data_min, data_max):
    """Return 5 'nice' Y-axis tick values covering [data_min, data_max].

    Three regimes:
    - All non-positive (data_max <= 0): ticks span [data_min, 0].
    - Clustered above zero (data_min > data_max/2): nice floor below
      data_min with a small padding.
    - Otherwise (spans zero, or all-positive starting at 0): start at
      data_min (typically 0) and step up to data_max.
    """
    # All non-positive: mirror the all-positive case around zero.
    if data_max <= 0:
        if data_min >= 0:
            return [0, 1, 2, 3, 4]
        step = _nice_step(-data_min / 4)
        # Top tick at 0, step downward
        ticks = [_fmt_tick(0 - step * (4 - i)) for i in range(5)]
        # Ensure first tick <= data_min
        while ticks[0] > data_min:
            ticks = [_fmt_tick(t - step) for t in ticks]
        return ticks

    # Clustering detection: if the min is close to the max, don't start at 0
    clustered = data_min > 0 and data_min > data_max * 0.5

    if clustered:
        range_val = data_max - data_min
        # Pad 10% on each side of the range for a bit of breathing room
        padding = range_val * 0.1
        raw_step = (data_max + padding - (data_min - padding)) / 4
        step = _nice_step(raw_step)
        # axis start = nice floor of (data_min - padding)
        axis_start = math.floor((data_min - padding) / step) * step
    elif data_min < 0:
        # Mixed range spanning zero: domain [data_min, data_max] with 0 inside.
        total_range = data_max - data_min
        step = _nice_step(total_range / 4)
        # axis start = nice floor of data_min
        axis_start = math.floor(data_min / step) * step
    else:
        axis_start = 0
        step = _nice_step(data_max / 4)

    ticks = [_fmt_tick(axis_start + step * i) for i in range(5)]
    # Ensure last tick >= data_max
    while ticks[-1] < data_max:
        ticks = [_fmt_tick(t + step) for t in ticks]
    return ticks


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
        options_str = match.group(2).strip()
        content = match.group(3)

        # M84: parse options and `--title "..."` directive properly. The
        # parser preserves the title's original casing and unicode chars.
        options, directive_title = _parse_chart_options(options_str)

        # M75: `:::chart line filled` is a friendlier alias for `:::chart area`.
        # The `filled` keyword has no leading `--`, so check the raw tokens too.
        raw_tokens = options_str.lower().split()
        if chart_type == "line" and ("filled" in options or "filled" in raw_tokens):
            chart_type = "area"

        if chart_type not in _VALID_CHART_TYPES:
            return content

        has_charts = True

        # Title resolution: `--title "..."` directive wins over `# heading`
        # inside the block (M84 — explicit beats implicit).
        title = directive_title
        title_match = _CHART_TITLE_RE.search(content)
        if title_match:
            heading_title = title_match.group(1).strip()
            content = _CHART_TITLE_RE.sub('', content, count=1)
            if not title:
                title = heading_title

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

        # M82: stacked column/bar with negatives is semantically ambiguous
        # and Charts.css can't render it. Degrade to grouped + warn on stderr.
        if is_stacked and any(v < 0 for v in all_values):
            print(
                f"md2 warning: chart type '{raw_type}' contains negative "
                f"values; stacking is not supported with negatives, "
                f"rendering as grouped (non-stacked).",
                file=sys.stderr,
            )
            is_stacked = False

        # Graduated Y-axis is shown for line/area (M67-M69) and, since M80,
        # also for column/bar. Segment-style rendering (`is_connected`) stays
        # exclusive to line/area. Column/bar use the floating-bar pattern
        # (M81) — `--start` + `--size` to allow negative values below the
        # baseline.
        is_connected = chart_type in ("line", "area")
        has_yaxis = chart_type in ("line", "area", "column", "bar")
        domain_min = domain_max = domain_range = zero_frac = None
        if is_connected:
            positive_values = [v for v in all_values if v > 0]
            data_min = min(positive_values) if positive_values else 0
            ticks = _nice_ticks(data_min, max_val)
            norm_min = ticks[0]
            norm_max = ticks[-1]
            norm_range = norm_max - norm_min if norm_max > norm_min else 1
        elif has_yaxis:
            # Column/bar: domain always includes zero so the baseline tick is
            # visible and the floating-bar formula gives a stable zero_frac.
            domain_min = min(min(all_values), 0) if all_values else 0
            domain_max = max(max(all_values), 0) if all_values else 0
            domain_range = domain_max - domain_min if domain_max > domain_min else 1
            zero_frac = -domain_min / domain_range  # 0..1
            ticks = _nice_ticks(domain_min, domain_max)
            norm_min = 0
            norm_max = max_val
            norm_range = max_val
        else:
            ticks = None
            norm_min = 0
            norm_max = max_val
            norm_range = max_val

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

        # Line/area: use graduated Y-axis pattern (Charts.css official examples)
        if chart_type in ("line", "area"):
            classes.append("show-primary-axis")
            classes.append("show-4-secondary-axes")
            classes.append("hide-data")
        class_str = " ".join(classes)
        # Whether to show .data spans: auto per type
        show_data = raw_type in _CHART_TYPES_SHOW_DATA
        # Line/area always hide data (graduated Y-axis shows scale)
        if chart_type in ("line", "area"):
            show_data = False

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
        # - line/area: --start = previous value (to connect segments),
        #   normalized against tick_max for Y-axis alignment
        # - bar/column: --size normalized against data max
        is_pie = chart_type == "pie"
        parts.append('<tbody>')
        cumulative = 0.0
        total = sum(all_values) if is_pie and sum(all_values) > 0 else 1

        def _fmt(x):
            return f"{x:g}" if x != int(x) else str(int(x))

        def _norm_connected(num):
            n = (num - norm_min) / norm_range
            return 0 if n < 0 else n

        if is_connected:
            # M74: segment model. N data points → N-1 <tr> segments.
            # Each segment[i] draws the line from point[i] to point[i+1].
            for seg_idx in range(len(data_rows) - 1):
                parts.append('<tr>')
                parts.append('<th scope="row"></th>')
                for col_idx in range(len(data_rows[seg_idx][1])):
                    v0 = parsed_values[seg_idx][col_idx]
                    v1 = parsed_values[seg_idx + 1][col_idx]
                    start = _norm_connected(v0)
                    size = _norm_connected(v1)
                    # A11y: segment[0] carries both endpoint values; later
                    # segments carry only the end value (start = previous
                    # segment's end, already emitted).
                    v0_str = data_rows[seg_idx][1][col_idx].strip()
                    v1_str = data_rows[seg_idx + 1][1][col_idx].strip()
                    if seg_idx == 0:
                        data_span = (
                            f'<span class="data">{v0_str}</span>'
                            f'<span class="data">{v1_str}</span>'
                        )
                    else:
                        data_span = f'<span class="data">{v1_str}</span>'
                    parts.append(
                        f'<td style="--start: {_fmt(start)}; '
                        f'--size: {_fmt(size)}">{data_span}</td>'
                    )
                parts.append('</tr>')
        else:
            for row_idx, (label, values) in enumerate(data_rows):
                parts.append('<tr>')
                parts.append(f'<th scope="row">{label}</th>')
                for col_idx, v in enumerate(values):
                    num_val = parsed_values[row_idx][col_idx]
                    if show_data:
                        data_span = f'<span class="data">{v.strip()}</span>'
                    else:
                        data_span = ""
                    if is_pie:
                        flat_idx = row_idx * len(values) + col_idx
                        start = cumulative
                        proportion = all_values[flat_idx] / total
                        cumulative += proportion
                        end = cumulative
                        parts.append(
                            f'<td style="--start: {_fmt(start)}; '
                            f'--end: {_fmt(end)}">{data_span}</td>'
                        )
                    elif has_yaxis and domain_range is not None:
                        # M81 floating-bar: anchor each bar to the zero
                        # baseline within [domain_min, domain_max].
                        if num_val >= 0:
                            start = zero_frac
                            size = num_val / domain_range
                        else:
                            size = -num_val / domain_range
                            start = zero_frac - size
                        parts.append(
                            f'<td style="--start: {_fmt(start)}; '
                            f'--size: {_fmt(size)}">{data_span}</td>'
                        )
                    else:
                        norm = num_val / norm_max
                        parts.append(
                            f'<td style="--size: {_fmt(norm)}">{data_span}</td>'
                        )
                parts.append('</tr>')
        parts.append('</tbody>')
        parts.append('</table>')

        table_html = "\n".join(parts)
        legend_html = ""

        # Auto-add legend for multi-dataset charts
        if is_multiple and dataset_headers:
            legend_items = "".join(f'<li>{h}</li>' for h in dataset_headers)
            legend_html = f'\n<ul class="charts-css legend legend-inline">{legend_items}</ul>'
        # Pie chart: inline labels inside big slices; legend shows (value)
        # only for small slices (< 6%).
        elif is_pie:
            pie_inline_labels = []
            legend_items_parts = []
            cum = 0.0
            total_pie = sum(all_values) if sum(all_values) > 0 else 1
            for idx, (label, values) in enumerate(data_rows):
                val = all_values[idx]
                proportion = val / total_pie
                mid = cum + proportion / 2
                cum += proportion
                theta = 2 * math.pi * mid  # 0 = 12 o'clock, clockwise
                r = 30  # percent from center
                left = 50 + r * math.sin(theta)
                top = 50 - r * math.cos(theta)
                if proportion >= 0.06:
                    pie_inline_labels.append(
                        f'<span class="md2-pie-label" '
                        f'style="left: {left:.2f}%; top: {top:.2f}%">'
                        f'{values[0].strip()}</span>'
                    )
                    legend_items_parts.append(f'<li>{label}</li>')
                else:
                    legend_items_parts.append(
                        f'<li>{label} ({values[0].strip()})</li>'
                    )
            legend_items = "".join(legend_items_parts)
            legend_html = (
                f'\n<ul class="charts-css legend legend-inline">'
                f'{legend_items}</ul>'
            )
            inline_labels_html = "".join(pie_inline_labels)
            table_html = (
                f'<div class="md2-pie-wrapper">{table_html}'
                f'{inline_labels_html}</div>'
            )

        result = table_html + legend_html

        # Prepend title if present
        title_html = ""
        if chart_title:
            title_html = f'<div class="md2-chart-title">{chart_title}</div>'

        # Generate graduated Y-axis (M67-M69 for line/area, M80 for
        # column/bar). Wrap the chart table (not the legend) in a flex row
        # with the Y-axis on the left.
        if has_yaxis and ticks:
            tick_spans = "".join(
                f'<span>{t}</span>' for t in reversed(ticks)
            )
            yaxis_html = f'<div class="md2-chart-yaxis">{tick_spans}</div>'
            body_html = f'<div class="md2-chart-body">{yaxis_html}{table_html}</div>'
            if is_connected:
                # Line/area emit X labels via a sibling div (M70 decoupling).
                xlabel_spans = "".join(
                    f'<span>{label}</span>' for label, _ in data_rows
                )
                xlabels_html = f'<div class="md2-chart-xlabels">{xlabel_spans}</div>'
                result = body_html + xlabels_html + legend_html
            else:
                # Column/bar keep their X labels inside Charts.css `<th>`s.
                result = body_html + legend_html

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
