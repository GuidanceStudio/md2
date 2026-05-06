"""M82: Stacked column/bar charts degrade gracefully when data contains
negatives.

Stacking with negatives is semantically ambiguous (Charts.css can't
honor it). M82 detects the case, emits a warning to stderr, and forces
the rendering to grouped (non-stacked) so the user sees something
correct instead of silently broken HTML.
"""
import re

from md2.core import process_markdown


def test_stacked_column_with_negatives_drops_stacked_class(capsys):
    """A stacked-column chart with any negative value renders WITHOUT
    the `stacked` CSS class, and a warning is emitted on stderr."""
    md = (
        ":::chart stacked-column\n"
        "| Q | A | B |\n"
        "|---|---|---|\n"
        "| 1 | 10 | -5 |\n"
        "| 2 | 8 | 3 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    captured = capsys.readouterr()

    # The output table should be column (multiple), NOT stacked.
    table_match = re.search(r'<table class="([^"]+)">', html)
    assert table_match, "expected a chart <table>"
    classes = table_match.group(1).split()
    assert "column" in classes
    assert "stacked" not in classes, (
        f"stacked class must be dropped when data has negatives, got {classes}"
    )
    # Warning emitted to stderr
    assert (
        "stacked" in captured.err.lower()
        and ("negative" in captured.err.lower() or "negativ" in captured.err.lower())
    ), f"expected warning on stderr about stacked + negatives, got {captured.err!r}"


def test_stacked_bar_with_negatives_drops_stacked_class(capsys):
    """Same behavior for the horizontal stacked-bar variant."""
    md = (
        ":::chart stacked-bar\n"
        "| Q | A | B |\n"
        "|---|---|---|\n"
        "| 1 | 10 | -3 |\n"
        "| 2 | 5 | 7 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    captured = capsys.readouterr()

    table_match = re.search(r'<table class="([^"]+)">', html)
    classes = table_match.group(1).split()
    assert "bar" in classes
    assert "stacked" not in classes
    assert "stacked" in captured.err.lower()


def test_stacked_column_all_positive_keeps_stacked_class(capsys):
    """Backward compat: stacked-column WITHOUT negatives still renders
    with the `stacked` class and no warning is emitted."""
    md = (
        ":::chart stacked-column\n"
        "| Q | A | B |\n"
        "|---|---|---|\n"
        "| 1 | 10 | 5 |\n"
        "| 2 | 8 | 3 |\n"
        ":::"
    )
    html, _ = process_markdown(md)
    captured = capsys.readouterr()

    table_match = re.search(r'<table class="([^"]+)">', html)
    classes = table_match.group(1).split()
    assert "column" in classes
    assert "stacked" in classes
    assert "stacked" not in captured.err.lower(), (
        f"no warning expected for all-positive stacked, got {captured.err!r}"
    )


def test_non_stacked_column_with_negatives_no_warning(capsys):
    """A regular (non-stacked) column with negatives must NOT emit the
    M82 warning — that's M81 territory and works fine."""
    md = (
        ":::chart column\n"
        "| Q | V |\n"
        "|---|---|\n"
        "| A | 10 |\n"
        "| B | -5 |\n"
        ":::"
    )
    process_markdown(md)
    captured = capsys.readouterr()
    assert "stacked" not in captured.err.lower()
