"""Tests for M112: :::columns up to four columns, `cards` style, `highlight` column."""
import os
import subprocess
import sys

import tinycss2

from md2.core import BUNDLED_TEMPLATES_DIR, preprocess_columns, process_markdown


def _columns(*cols, opening=":::columns"):
    """Build a :::columns block; each col is (marker_suffix, body)."""
    parts = [opening, ""]
    for suffix, body in cols:
        parts += [f":::col{suffix}", body, ""]
    parts.append(":::")
    return "\n".join(parts)


def _plain(*bodies, opening=":::columns"):
    return _columns(*[("", b) for b in bodies], opening=opening)


# --- column count ---

def test_bare_two_columns_markup_is_unchanged():
    result = preprocess_columns(_plain("Left", "Right"))
    assert result == (
        '<div class="md2-columns">'
        '<div class="md2-col"><p>Left</p></div>'
        '<div class="md2-col"><p>Right</p></div>'
        '</div>'
    )


def test_three_columns_are_all_kept_with_count_class():
    result = preprocess_columns(_plain("A1", "B2", "C3"))
    assert '<div class="md2-columns md2-cols-3">' in result
    assert result.count('class="md2-col"') == 3
    assert "C3" in result


def test_four_columns_are_all_kept_with_count_class():
    result = preprocess_columns(_plain("A1", "B2", "C3", "D4"))
    assert '<div class="md2-columns md2-cols-4">' in result
    assert result.count('class="md2-col"') == 4
    assert "D4" in result


def test_fifth_column_is_dropped():
    result = preprocess_columns(_plain("A1", "B2", "C3", "D4", "E5"))
    assert '<div class="md2-columns md2-cols-4">' in result
    assert result.count('class="md2-col"') == 4
    assert "E5" not in result


# --- modifiers on the opening line ---

def test_cards_modifier_adds_cards_class():
    result = preprocess_columns(_plain("A1", "B2", "C3", opening=":::columns cards"))
    assert '<div class="md2-columns md2-cols-3 cards">' in result
    assert ":::columns" not in result


def test_cards_on_two_columns_has_no_count_class():
    result = preprocess_columns(_plain("A1", "B2", opening=":::columns cards"))
    assert '<div class="md2-columns cards">' in result


def test_unknown_columns_modifier_is_ignored():
    result = preprocess_columns(_plain("A1", "B2", "C3", opening=":::columns bogus cards"))
    assert '<div class="md2-columns md2-cols-3 cards">' in result
    assert "bogus" not in result


def test_only_unknown_columns_modifier_emits_no_class():
    result = preprocess_columns(_plain("A1", "B2", opening=":::columns bogus"))
    assert '<div class="md2-columns">' in result
    assert "bogus" not in result


# --- modifiers on :::col ---

def test_highlight_modifier_marks_its_own_column():
    md = _columns(("", "A1"), (" highlight", "B2"), ("", "C3"))
    result = preprocess_columns(md)
    assert result.count('class="md2-col"') == 2
    assert result.count('class="md2-col highlight"') == 1
    assert '<div class="md2-col highlight"><p>B2</p></div>' in result


def test_unknown_col_modifier_is_ignored():
    md = _columns(("", "A1"), (" sparkle", "B2"), (" highlight glow", "C3"))
    result = preprocess_columns(md)
    assert '<div class="md2-col"><p>B2</p></div>' in result
    assert '<div class="md2-col highlight"><p>C3</p></div>' in result
    assert "sparkle" not in result
    assert "glow" not in result


def test_h1_inside_a_column_stays_h1():
    md = _plain("# 42\n\nclienti", "B2", "C3", opening=":::columns cards")
    result = preprocess_columns(md)
    assert '<div class="md2-col"><h1>42</h1>' in result


def test_cards_and_highlight_survive_the_full_pipeline():
    md = _columns(("", "**A1**"), (" highlight", "B2"), ("", "C3"), opening=":::columns cards")
    html, _ = process_markdown(md)
    assert '<div class="md2-columns md2-cols-3 cards">' in html
    assert html.count('class="md2-col highlight"') == 1
    assert html.count('class="md2-col"') == 2
    assert "<strong>A1</strong>" in html


# --- default template CSS ---

def _css_rules(rules, media=None):
    """Yield (media_prelude, selectors, declarations) for every style rule."""
    for rule in rules:
        if rule.type == "qualified-rule":
            selectors = [" ".join(s.split()) for s in tinycss2.serialize(rule.prelude).split(",")]
            decls = {
                d.lower_name: tinycss2.serialize(d.value).strip()
                for d in tinycss2.parse_declaration_list(rule.content, skip_comments=True, skip_whitespace=True)
                if d.type == "declaration"
            }
            yield media, selectors, decls
        elif rule.type == "at-rule" and rule.lower_at_keyword == "media":
            prelude = " ".join(tinycss2.serialize(rule.prelude).split())
            inner = tinycss2.parse_rule_list(rule.content, skip_comments=True, skip_whitespace=True)
            yield from _css_rules(inner, prelude)


def _default_css_rules():
    css = (BUNDLED_TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")
    return list(_css_rules(tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)))


def _top_level_decls(selector):
    return [d for media, sels, d in _default_css_rules() if media is None and selector in sels]


def test_css_has_rules_for_three_and_four_columns():
    selectors = {s for media, sels, _ in _default_css_rules() if media is None for s in sels}
    assert any("md2-cols-3" in s for s in selectors)
    assert any("md2-cols-4" in s for s in selectors)


def test_css_cards_have_background_border_and_radius():
    decls = {}
    for d in _top_level_decls(".md2-columns.cards > .md2-col"):
        decls.update(d)
    assert "background" in decls or "background-color" in decls
    assert "border" in decls
    assert "border-radius" in decls


def test_css_highlight_card_differs_from_plain_card():
    decls = {}
    for d in _top_level_decls(".md2-columns.cards > .md2-col.highlight"):
        decls.update(d)
    assert {"background", "background-color", "border-color", "border"} & decls.keys()


def test_css_cards_print_with_a_background_and_exact_colors():
    print_decls = {}
    for media, sels, d in _default_css_rules():
        if media == "print" and ".md2-columns.cards > .md2-col" in sels:
            print_decls.update(d)
    assert "background" in print_decls or "background-color" in print_decls
    assert print_decls.get("print-color-adjust", "").startswith("exact")


def test_css_every_media_query_is_print_or_screen_scoped():
    preludes = {media for media, _, _ in _default_css_rules() if media is not None}
    assert preludes
    for prelude in preludes:
        assert prelude == "print" or prelude.startswith("screen"), prelude


# --- end to end ---

def test_cli_renders_cards_with_highlight(tmp_path):
    md = tmp_path / "deck.md"
    md.write_text(
        "# Deck\n\n---\n\n## Agenda\n\n"
        + _columns(("", "Uno"), (" highlight", "Due"), ("", "Tre"), opening=":::columns cards")
        + "\n",
        encoding="utf-8",
    )
    r = subprocess.run(
        [sys.executable, "-m", "md2", str(md)],
        capture_output=True, text=True, env={**os.environ, "HOME": str(tmp_path)},
    )
    assert r.returncode == 0, r.stderr
    html = md.with_suffix(".html").read_text(encoding="utf-8")
    assert '<div class="md2-columns md2-cols-3 cards">' in html
    assert html.count('class="md2-col highlight"') == 1
    assert ".md2-columns.cards > .md2-col" in html
