"""M106: a `---` inside a fenced code block must not split the slide.

Found on a real deck: a slide showing the anatomy of a SKILL.md file contains
a code sample with YAML frontmatter, whose `---` delimiters were read as slide
separators. One slide became four, two of them untitled.
"""

from md2.core import prepare_context, _split_slides


FRONTMATTER_SAMPLE = """# Cover

intro

---

## Anatomia di SKILL.md

```markdown
---
name: bandonet
description: Compila le risposte a un bando.
---

# Bandonet
```

Testo dopo il blocco.
"""


def test_frontmatter_in_fence_does_not_split():
    ctx = prepare_context(FRONTMATTER_SAMPLE)
    assert len(ctx["slides"]) == 1, (
        f"expected 1 slide, got {len(ctx['slides'])} — "
        "the fenced `---` split the slide again"
    )
    assert ctx["slides"][0]["title"] == "Anatomia di SKILL.md"


def test_no_untitled_slides_generated():
    ctx = prepare_context(FRONTMATTER_SAMPLE)
    for slide in ctx["slides"]:
        assert not slide["title"].startswith("Slide "), (
            "a phantom untitled slide was produced"
        )


def test_tilde_fence_also_protects():
    text = "# C\n\nx\n\n---\n\n## T\n\n~~~markdown\n---\na: 1\n---\n~~~\n"
    assert len(prepare_context(text)["slides"]) == 1


def test_real_separators_still_split():
    text = "# C\n\nx\n\n---\n\n## A\n\na\n\n---\n\n## B\n\nb\n"
    ctx = prepare_context(text)
    assert [s["title"] for s in ctx["slides"]] == ["A", "B"]


def test_indented_separator_still_splits_outside_fence():
    """The old regex allowed leading whitespace; keep that behaviour."""
    text = "# C\n\nx\n\n  ---  \n\n## A\n\na\n"
    assert len(prepare_context(text)["slides"]) == 1


def test_info_string_does_not_close_a_fence():
    """```python opens a fence; it must never be treated as a closer."""
    segments = _split_slides("```python\n---\nx = 1\n```\n---\nafter\n")
    assert len(segments) == 2
    assert "x = 1" in segments[0]
    assert segments[1].strip() == "after"


def test_longer_closing_fence_closes():
    """A closer may be longer than the opener, but not shorter."""
    segments = _split_slides("````\n---\n````\n---\nafter\n")
    assert len(segments) == 2


def test_shorter_fence_inside_longer_does_not_close():
    segments = _split_slides("````\n```\n---\n````\n---\nafter\n")
    assert len(segments) == 2
    assert "---" in segments[0]


def test_unclosed_fence_swallows_rest():
    """An unterminated fence means everything after it is code — no split.

    This mirrors CommonMark, where an unclosed fence runs to end of document.
    """
    segments = _split_slides("```\n---\nstill code\n")
    assert len(segments) == 1


def test_chapter_directive_still_parses_after_change():
    """:::chapter (M105) sits between separators — guard against regression."""
    text = "# C\n\nx\n\n---\n\n:::chapter\n# Atto 1\nSottotitolo.\n:::\n"
    ctx = prepare_context(text)
    assert len(ctx["slides"]) == 1
    assert ctx["slides"][0]["type"] == "chapter"
    assert ctx["slides"][0]["title"] == "Atto 1"
