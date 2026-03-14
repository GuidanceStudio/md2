"""Tests for the template system (Milestone 22)."""

import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from md2.cli import (
    _ensure_default_template,
    _init_templates,
    _resolve_template_dir,
    render_html,
    USER_TEMPLATES_DIR,
)
from md2.core import BUNDLED_TEMPLATES_DIR


SAMPLE_MD = "# Test\n\nCover.\n\n---\n\n## Slide 1\nContent."


@pytest.fixture
def tmp_templates(tmp_path):
    """Provide a temporary templates directory, patching USER_TEMPLATES_DIR."""
    fake_dir = tmp_path / "templates"
    fake_dir.mkdir()
    with patch("md2.cli.USER_TEMPLATES_DIR", fake_dir):
        yield fake_dir


def test_ensure_default_template_creates_dir(tmp_templates):
    """First call creates the default template dir."""
    result = _ensure_default_template()
    assert result is True
    assert (tmp_templates / "default" / "base.html").exists()
    assert (tmp_templates / "default" / "style.css").exists()
    assert (tmp_templates / "default" / "components" / "sidebar.html").exists()


def test_ensure_default_template_noop_if_exists(tmp_templates):
    """Second call does nothing if dir already exists."""
    _ensure_default_template()
    result = _ensure_default_template()
    assert result is False


def test_init_templates_overwrites(tmp_templates):
    """--init-templates overwrites existing default template."""
    _ensure_default_template()
    # Modify a file
    marker = tmp_templates / "default" / "MODIFIED"
    marker.write_text("test")
    assert marker.exists()

    _init_templates()
    # Marker should be gone (dir was recreated)
    assert not marker.exists()
    # Template files should still be there
    assert (tmp_templates / "default" / "base.html").exists()


def test_resolve_template_dir_named(tmp_templates):
    """--template name resolves to ~/.md2/templates/name/."""
    custom = tmp_templates / "corporate"
    custom.mkdir()
    (custom / "base.html").write_text("test")
    result = _resolve_template_dir("corporate")
    assert result == custom


def test_resolve_template_dir_missing_errors(tmp_templates):
    """--template with nonexistent name exits with error."""
    with pytest.raises(SystemExit):
        _resolve_template_dir("nonexistent")


def test_resolve_template_dir_auto_creates_default(tmp_templates):
    """Without --template, auto-creates default if missing."""
    result = _resolve_template_dir(None)
    assert result == tmp_templates / "default"
    assert (tmp_templates / "default" / "base.html").exists()


def test_resolve_template_dir_uses_existing_default(tmp_templates):
    """Without --template, uses existing default dir."""
    _ensure_default_template()
    result = _resolve_template_dir(None)
    assert result == tmp_templates / "default"


def test_render_html_with_default_template(tmp_templates):
    """render_html works with the default template from user dir."""
    _ensure_default_template()
    template_dir = tmp_templates / "default"
    html = render_html(SAMPLE_MD, template_dir=template_dir)
    assert "Test" in html
    assert "Slide 1" in html
    assert "id=\"sidebar\"" in html


def test_render_html_with_custom_template_extending_default(tmp_templates):
    """Custom template that extends default/base.html works."""
    _ensure_default_template()
    custom = tmp_templates / "nosidebar"
    custom.mkdir()
    (custom / "base.html").write_text(
        '{% extends "default/base.html" %}\n{% block sidebar %}{% endblock %}'
    )
    html = render_html(SAMPLE_MD, template_dir=custom)
    assert "Test" in html
    assert "Slide 1" in html
    # Sidebar should be absent
    assert 'id="sidebar"' not in html


def test_render_html_bundled_fallback():
    """render_html works with None template_dir (bundled fallback)."""
    html = render_html(SAMPLE_MD, template_dir=None)
    assert "Test" in html
    assert "Slide 1" in html


def test_bundled_templates_complete():
    """Bundled template directory has all required files."""
    assert BUNDLED_TEMPLATES_DIR.exists()
    assert (BUNDLED_TEMPLATES_DIR / "base.html").exists()
    assert (BUNDLED_TEMPLATES_DIR / "style.css").exists()
    for component in ["head.html", "sidebar.html", "cover.html", "slide.html", "controls.html", "scripts.html"]:
        assert (BUNDLED_TEMPLATES_DIR / "components" / component).exists()
