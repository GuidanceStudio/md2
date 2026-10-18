"""M121: `:::chart radar` — md2 draws the profile itself as an inline SVG.

The SVG is checked geometrically: a series vertex must sit on its axis spoke at
value / scale-end of the spoke's length, wherever md2 puts the centre.
"""
import itertools
import math
import re
import xml.etree.ElementTree as ET

import pytest

from md2.core import BUNDLED_TEMPLATES_DIR, process_markdown

AXES = ["Price", "Support", "Speed", "Safety", "Ease"]
PERIOD_A = [4.2, 3, 5, 1.5, 0]
PERIOD_B = [3.5, 4, 2.5, 4.5, 2]


def _table(axes, *series, names=None):
    names = names or [f"S{i + 1}" for i in range(len(series))]
    lines = ["| Dimension | " + " | ".join(names) + " |"]
    lines.append("|" + "---|" * (len(series) + 1))
    for i, axis in enumerate(axes):
        lines.append(f"| {axis} | " + " | ".join(str(s[i]) for s in series) + " |")
    return "\n".join(lines)


def _render(md):
    html, has_charts = process_markdown(md)
    assert has_charts
    return html


def _radar(axes, *series, names=None, title=None):
    head = f':::chart radar --title "{title}"' if title else ":::chart radar"
    return _render(f"{head}\n{_table(axes, *series, names=names)}\n:::")


def _svg(html):
    match = re.search(r"<svg\b.*?</svg>", html, re.DOTALL)
    assert match, "expected an inline <svg>"
    return ET.fromstring(match.group(0))


def _by_class(root, cls):
    return [el for el in root.iter() if cls in (el.get("class") or "").split()]


def _points(polygon):
    return [tuple(float(c) for c in p.split(",")) for p in polygon.get("points").split()]


def _spokes(root):
    return [
        ((float(s.get("x1")), float(s.get("y1"))), (float(s.get("x2")), float(s.get("y2"))))
        for s in _by_class(root, "md2-radar-spoke")
    ]


def _text(el):
    return " ".join("".join(el.itertext()).split())


def _ticks(root):
    return [_text(t) for t in _by_class(root, "md2-radar-tick")]


# --- the chart -----------------------------------------------------------------

def test_radar_renders_an_svg_inside_the_chart_card():
    html = _radar(AXES, PERIOD_A)
    assert html.startswith('<div class="md2-chart">')
    assert '<svg class="md2-radar"' in html
    assert ":::" not in html


def test_svg_has_five_grid_rings_with_one_vertex_per_axis():
    rings = _by_class(_svg(_radar(AXES, PERIOD_A)), "md2-radar-ring")
    assert len(rings) == 5
    assert all(len(_points(r)) == len(AXES) for r in rings)


def test_svg_has_one_spoke_and_one_label_per_axis_in_order():
    root = _svg(_radar(AXES, PERIOD_A))
    assert len(_spokes(root)) == len(AXES)
    assert [_text(t) for t in _by_class(root, "md2-radar-label")] == AXES


def test_first_axis_points_up_and_the_next_one_clockwise():
    (c, first), (_, second) = _spokes(_svg(_radar(AXES, PERIOD_A)))[:2]
    assert first[0] == pytest.approx(c[0]) and first[1] < c[1]
    assert second[0] > c[0]


def test_outer_ring_runs_through_the_spoke_ends():
    root = _svg(_radar(AXES, PERIOD_A))
    outer = _points(_by_class(root, "md2-radar-ring")[-1])
    for vertex, (_, end) in zip(outer, _spokes(root)):
        assert vertex == pytest.approx(end, abs=0.01)


@pytest.mark.parametrize("n_series", [1, 2, 3])
def test_one_series_polygon_per_data_column(n_series):
    series = [PERIOD_A, PERIOD_B, PERIOD_A][:n_series]
    polygons = _by_class(_svg(_radar(AXES, *series)), "md2-radar-series")
    assert len(polygons) == n_series
    assert all(len(_points(p)) == len(AXES) for p in polygons)


def test_series_vertices_sit_on_their_spokes_at_value_over_scale_end():
    root = _svg(_radar(AXES, PERIOD_A, PERIOD_B))
    end = 5  # the largest value is 5
    spokes = _spokes(root)
    polygons = _by_class(root, "md2-radar-series")
    for polygon, values in zip(polygons, [PERIOD_A, PERIOD_B]):
        for (x, y), ((cx, cy), (ex, ey)), v in zip(_points(polygon), spokes, values):
            assert x == pytest.approx(cx + (ex - cx) * v / end, abs=0.01)
            assert y == pytest.approx(cy + (ey - cy) * v / end, abs=0.01)


@pytest.mark.parametrize(
    "largest, ticks",
    [
        (4.0, ["1", "2", "3", "4", "5"]),
        (4.2, ["1", "2", "3", "4", "5"]),
        (3.3, ["1", "2", "3", "4", "5"]),
        (5, ["1", "2", "3", "4", "5"]),
        (37, ["10", "20", "30", "40", "50"]),
        (100, ["20", "40", "60", "80", "100"]),
        (2.0, ["0.5", "1", "1.5", "2", "2.5"]),
        (12, ["2.5", "5", "7.5", "10", "12.5"]),
    ],
)
def test_five_rings_step_by_the_smallest_nice_number_covering_the_largest(largest, ticks):
    # Nice steps are 1, 2, 2.5 and 5 x 10^k; the step is the smallest at or above largest / 5.
    root = _svg(_radar(AXES, [largest * f for f in (0.5, 1, 0.25, 0.75, 0)]))
    assert _ticks(root) == ticks


def test_series_colours_come_from_the_palette_variables_only():
    html = _radar(AXES, PERIOD_A, PERIOD_B)
    svg = re.search(r"<svg\b.*?</svg>", html, re.DOTALL).group(0)
    polygons = _by_class(_svg(html), "md2-radar-series")
    assert [p.get("style") for p in polygons] == [
        "color: var(--md2-color-1)",
        "color: var(--md2-color-2)",
    ]
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(", svg)


def test_axis_labels_are_html_escaped_text():
    html = _radar(["R&D", "A < B", "<script>alert(1)</script>Ops", "Q", "Z"], PERIOD_A)
    labels = re.findall(r'<text class="md2-radar-label".*?</text>', html, re.DOTALL)
    assert "R&amp;D" in labels[0]
    assert "A &lt; B" in labels[1]
    assert "<script" not in html
    assert [_text(t) for t in _by_class(_svg(html), "md2-radar-label")][:2] == ["R&D", "A < B"]


def test_single_series_has_no_legend():
    assert "legend" not in _radar(AXES, PERIOD_A)


def test_two_series_get_the_legend_the_other_charts_use():
    html = _radar(AXES, PERIOD_A, PERIOD_B, names=["2025", "2026"])
    legend = re.search(r'<ul class="charts-css legend legend-inline">(.*?)</ul>', html)
    assert legend is not None
    assert re.findall(r"<li>(.*?)</li>", legend.group(1)) == ["2025", "2026"]


def test_source_table_stays_for_screen_readers_and_is_visually_hidden():
    html = _radar(AXES, PERIOD_A, PERIOD_B, title="Profile")
    # A table treats width/height as minimums, so a wrapping div does the hiding.
    hidden = re.search(r'<div class="md2-radar-data" style="([^"]*)"><table>(.*?)</table></div>',
                       html, re.DOTALL)
    assert hidden is not None
    style, body = hidden.groups()
    assert "position: absolute" in style and "overflow: hidden" in style
    assert "clip-path: inset(50%)" in style
    assert "<caption>Profile</caption>" in body
    assert re.findall(r"<td[^>]*>(.*?)</td>", body)[:3] == ["Price", "4.2", "3.5"]
    assert re.search(r'<svg class="md2-radar"[^>]*aria-hidden="true"', html)


def test_title_goes_in_the_chart_title_bar():
    html = _radar(AXES, PERIOD_A, title="Profile")
    assert '<div class="md2-chart-title">Profile</div>' in html


def test_well_formed_radar_writes_no_warning(capsys):
    _radar(AXES, PERIOD_A, PERIOD_B)
    assert capsys.readouterr().err == ""


def test_default_template_sizes_the_radar_like_a_line_chart():
    css = (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")
    rule = re.search(r"\.md2-radar\s*\{([^}]*)\}", css)
    assert rule is not None
    assert re.search(r"height:\s*min\(260px,\s*36vh\)", rule.group(1))


# --- fallbacks -----------------------------------------------------------------

def test_fewer_than_three_axes_renders_as_bar_with_a_warning(capsys):
    table = _table(["Price", "Support"], [3, 4], [2, 5])
    radar = _render(f":::chart radar\n{table}\n:::")
    err = capsys.readouterr().err
    assert radar == _render(f":::chart bar\n{table}\n:::")
    assert "radar" in err and "three" in err and "bar" in err


def test_negative_value_is_drawn_at_the_centre_with_a_warning(capsys):
    root = _svg(_radar(AXES, [3, -2, 5, 1, 2]))
    err = capsys.readouterr().err
    (cx, cy), _ = _spokes(root)[1]
    vertex = _points(_by_class(root, "md2-radar-series")[0])[1]
    assert vertex == pytest.approx((cx, cy), abs=0.01)
    assert "radar" in err and "negative" in err


def test_more_than_four_series_keeps_the_first_four_with_a_warning(capsys):
    names = ["A", "B", "C", "D", "E"]
    html = _radar(AXES, *([PERIOD_A] * 5), names=names)
    err = capsys.readouterr().err
    assert len(_by_class(_svg(html), "md2-radar-series")) == 4
    legend = re.search(r'<ul class="charts-css legend legend-inline">(.*?)</ul>', html)
    assert re.findall(r"<li>(.*?)</li>", legend.group(1)) == names[:4]
    assert "radar" in err and "four" in err


def test_more_than_twelve_axes_keeps_the_first_twelve_with_a_warning(capsys):
    axes = [f"D{i}" for i in range(1, 15)]
    root = _svg(_radar(axes, list(range(1, 15))))
    err = capsys.readouterr().err
    assert [_text(t) for t in _by_class(root, "md2-radar-label")] == axes[:12]
    assert len(_spokes(root)) == 12
    assert "radar" in err and "twelve" in err


def test_scale_end_covers_the_drawn_series_only():
    html = _radar(AXES, *([[1, 2, 3, 4, 4.2]] * 4), [90, 90, 90, 90, 90])
    assert _ticks(_svg(html)) == ["1", "2", "3", "4", "5"]


def test_label_math_stays_finite_for_an_all_zero_series():
    root = _svg(_radar(AXES, [0, 0, 0, 0, 0]))
    assert all(math.isfinite(c) for p in _by_class(root, "md2-radar-series") for xy in _points(p) for c in xy)
    assert len(_ticks(root)) == 5


def test_table_without_a_data_column_draws_the_grid_alone():
    html = _render(":::chart radar\n| Dimension |\n|---|\n| A |\n| B |\n| C |\n:::")
    root = _svg(html)
    assert len(_by_class(root, "md2-radar-ring")) == 5
    assert _by_class(root, "md2-radar-series") == []
    assert "legend" not in html


# --- review: label layout, label text, angles, short rows ---------------------

LONG_LABELS = [
    "Prezzo e commissioni base", "Assistenza clienti online", "Customer support response",
    "Sicurezza dei dati utenti", "Integrazioni con software", "Reporting and data export",
    "Ease of use for new users", "Reliability of the system", "Mobile app and web portal",
    "Expense policy compliance", "Multi-currency management", "Onboarding and activation",
]


def _label_boxes(root):
    """Label boxes as md2 estimates them: 0.6 em per character, 0.8 em above the
    first baseline and 0.3 em below the last."""
    fs = float(root.get("font-size"))
    boxes = []
    for label in _by_class(root, "md2-radar-label"):
        spans = label.findall("tspan")
        spread = sum(float(s.get("dy")) for s in spans[1:])
        width = max(len(s.text or "") for s in spans) * 0.6 * fs
        x, y = float(label.get("x")), float(label.get("y"))
        x0 = {"start": x, "middle": x - width / 2, "end": x - width}[label.get("text-anchor")]
        boxes.append((_text(label), x0, x0 + width, y - 0.8 * fs, y + spread + 0.3 * fs))
    return boxes


@pytest.mark.parametrize("n", range(3, 13))
def test_25_character_labels_never_overlap(n):
    assert all(len(label) == 25 for label in LONG_LABELS)
    boxes = _label_boxes(_svg(_radar(LONG_LABELS[:n], [3] * n)))
    for a, b in itertools.combinations(boxes, 2):
        overlap = a[1] < b[2] and b[1] < a[2] and a[3] < b[4] and b[3] < a[4]
        assert not overlap, f"{a[0]!r} overlaps {b[0]!r}"


@pytest.mark.parametrize("n", [3, 12])
def test_spoke_i_points_at_2pi_i_over_n_clockwise_from_the_top(n):
    spokes = _spokes(_svg(_radar([f"A{i}" for i in range(n)], [1] * n)))
    assert len(spokes) == n
    for i, ((cx, cy), (ex, ey)) in enumerate(spokes):
        angle = math.atan2(ex - cx, cy - ey)
        off = (angle - 2 * math.pi * i / n + math.pi) % (2 * math.pi) - math.pi
        assert abs(off) < 1e-3


def test_label_markup_becomes_plain_text_with_no_element_inside_the_label():
    label = _by_class(_svg(_radar(["**Bold** & x", "B", "C"], [1, 2, 3])), "md2-radar-label")[0]
    assert _text(label) == "Bold & x"
    assert all(child.tag == "tspan" and len(child) == 0 for child in label)


def test_four_axes_anchor_top_middle_right_start_bottom_middle_left_end():
    labels = _by_class(_svg(_radar(["N", "E", "S", "W"], [1, 2, 3, 4])), "md2-radar-label")
    assert [t.get("text-anchor") for t in labels] == ["middle", "start", "middle", "end"]


def test_a_long_side_label_wraps_onto_several_lines():
    labels = _by_class(_svg(_radar(["N", "Customer support quality", "S", "W"], [1, 2, 3, 4])),
                       "md2-radar-label")
    assert len(labels[1].findall("tspan")) > 1


def test_br_in_a_label_starts_a_new_line():
    label = _by_class(_svg(_radar(["Customer<br>support", "B", "C"], [1, 2, 3])), "md2-radar-label")[0]
    assert [s.text for s in label.findall("tspan")] == ["Customer", "support"]


def test_hand_written_table_with_a_short_row_reads_the_missing_cell_as_zero():
    table = (
        "<table><tr><th>D</th><th>A</th><th>B</th></tr>"
        "<tr><td>x</td><td>1</td><td>2</td></tr>"
        "<tr><td>y</td><td>3</td></tr>"
        "<tr><td>z</td><td>4</td><td>5</td></tr></table>"
    )
    root = _svg(_render(f":::chart radar\n{table}\n:::"))
    (cx, cy), _ = _spokes(root)[1]
    assert _points(_by_class(root, "md2-radar-series")[1])[1] == pytest.approx((cx, cy), abs=0.01)


@pytest.mark.parametrize("n", range(3, 13))
def test_a_long_single_word_on_the_vertical_axis_clears_its_neighbours(n):
    labels = list(LONG_LABELS[:n])
    labels[0] = "Internazionalizzazione"
    labels[1] = labels[-1] = "Customer support response time"
    if n % 2 == 0:
        labels[n // 2] = "Internazionalizzazione"
        labels[n // 2 - 1] = labels[n // 2 + 1] = "Customer support response time"
    boxes = _label_boxes(_svg(_radar(labels, [3] * n)))
    for a, b in itertools.combinations(boxes, 2):
        overlap = a[1] < b[2] and b[1] < a[2] and a[3] < b[4] and b[3] < a[4]
        assert not overlap, f"{a[0]!r} overlaps {b[0]!r}"


def test_short_first_row_of_a_hand_written_table_warns_that_later_series_are_dropped(capsys):
    table = (
        "<table><tr><th>D</th><th>A</th><th>B</th></tr>"
        "<tr><td>x</td><td>1</td></tr>"
        "<tr><td>y</td><td>3</td><td>4</td></tr>"
        "<tr><td>z</td><td>4</td><td>5</td></tr></table>"
    )
    root = _svg(_render(f":::chart radar\n{table}\n:::"))
    err = capsys.readouterr().err
    assert len(_by_class(root, "md2-radar-series")) == 1
    assert "radar" in err and "first row" in err


def test_table_without_a_header_row_has_no_empty_legend():
    table = (
        "<table><tr><td>x</td><td>1</td><td>2</td></tr>"
        "<tr><td>y</td><td>3</td><td>4</td></tr>"
        "<tr><td>z</td><td>4</td><td>5</td></tr></table>"
    )
    html = _render(f":::chart radar\n{table}\n:::")
    assert len(_by_class(_svg(html), "md2-radar-series")) == 2
    assert "legend" not in html
