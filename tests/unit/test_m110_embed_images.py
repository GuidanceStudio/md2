"""M110 — `--embed-images` inlines local images and refuses to ship broken ones."""

import base64
import subprocess
import sys
from pathlib import Path

import pytest

from md2.core import EmbedError, embed_local_images

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFAAH/q842iQAAAABJRU5ErkJggg=="
)


@pytest.fixture
def img(tmp_path):
    p = tmp_path / "logo.png"
    p.write_bytes(PNG)
    return p


def test_embeds_absolute_file_uri(tmp_path, img):
    html = f'<img src="file://{img}" alt="">'
    out, warnings = embed_local_images(html, tmp_path)
    assert "data:image/png;base64," in out
    assert "file://" not in out
    assert warnings == []


def test_embeds_relative_reference_against_base_dir(tmp_path, img):
    out, _ = embed_local_images('<img src="logo.png">', tmp_path)
    assert "data:image/png;base64," in out


def test_embeds_css_url(tmp_path, img):
    out, _ = embed_local_images(f'<style>a {{ background: url("file://{img}"); }}</style>', tmp_path)
    assert "data:image/png;base64," in out


def test_leaves_remote_and_data_uris_alone(tmp_path):
    html = '<img src="https://example.com/a.png"><img src="data:image/png;base64,AAAA">'
    out, _ = embed_local_images(html, tmp_path)
    assert out == html


def test_missing_file_raises_and_names_it(tmp_path):
    with pytest.raises(EmbedError) as exc:
        embed_local_images('<img src="nope.png">', tmp_path)
    assert "nope.png" in str(exc.value)


def test_warns_when_payload_is_large(tmp_path):
    big = tmp_path / "big.png"
    big.write_bytes(PNG + b"\x00" * (200 * 1024))
    html = f'<img src="file://{big}"><img src="file://{big}">'
    _, warnings = embed_local_images(html, tmp_path)
    assert warnings and "appears 2 time(s)" in warnings[0]


def test_warning_names_the_pixel_dimensions(tmp_path):
    """The dimensions are what make an oversized asset recognisable: "5001x5001"
    says it is wrong, "303 KB" does not."""
    from md2.core import _image_pixel_size

    big = tmp_path / "big.png"
    # 1x1 PNG padded to trip the warning threshold; dimensions come from the header.
    big.write_bytes(PNG + b"\x00" * (200 * 1024))
    _, warnings = embed_local_images(f'<img src="file://{big}">', tmp_path)
    assert "1x1" in warnings[0]
    assert "1000px" in warnings[0]
    assert _image_pixel_size(PNG, ".png") == (1, 1)


def test_pixel_size_reads_gif_and_ignores_unknown(tmp_path):
    from md2.core import _image_pixel_size

    gif = b"GIF89a" + (7).to_bytes(2, "little") + (5).to_bytes(2, "little") + b"\x00" * 10
    assert _image_pixel_size(gif, ".gif") == (7, 5)
    assert _image_pixel_size(b"<svg/>", ".svg") is None
    assert _image_pixel_size(b"nonsense", ".png") is None


def test_cli_off_by_default_keeps_the_reference(tmp_path, img):
    md = tmp_path / "d.md"
    md.write_text("# T\n\n![](logo.png)\n", encoding="utf-8")
    subprocess.run([sys.executable, "-m", "md2", str(md)], check=True, capture_output=True)
    html = md.with_suffix(".html").read_text()
    assert 'src="logo.png"' in html
    assert "data:image/png;base64," not in html


def test_cli_embeds_a_relative_markdown_image(tmp_path, img):
    md = tmp_path / "d.md"
    md.write_text("# T\n\n![](logo.png)\n", encoding="utf-8")
    subprocess.run(
        [sys.executable, "-m", "md2", "--embed-images", str(md)], check=True, capture_output=True
    )
    html = md.with_suffix(".html").read_text()
    assert "data:image/png;base64," in html
    assert 'src="logo.png"' not in html


def test_cli_embeds_a_template_asset(tmp_path, img):
    """The real case: the absolute file:// reference lives in the template, not in
    the markdown — bleach strips the file: protocol from author-written images, so a
    template is the only way one reaches the output."""
    tpl = tmp_path / ".md2" / "templates" / "withlogo"
    tpl.mkdir(parents=True)
    (tpl / "base.html").write_text(
        f'<!DOCTYPE html><html><head></head><body>'
        f'<img class="logo" src="file://{img}" alt="">{{{{ slides_html }}}}</body></html>',
        encoding="utf-8",
    )
    md = tmp_path / "d.md"
    md.write_text("# T\n\ntesto\n", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, "-m", "md2", "--template", "withlogo", "--embed-images", str(md)],
        capture_output=True, text=True, env={**__import__("os").environ, "HOME": str(tmp_path)},
    )
    assert r.returncode == 0, r.stderr
    html = md.with_suffix(".html").read_text()
    assert "data:image/png;base64," in html
    assert "file://" not in html


def test_cli_fails_without_writing_when_an_image_is_missing(tmp_path):
    md = tmp_path / "d.md"
    md.write_text("# T\n\n![](assente.png)\n", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, "-m", "md2", "--embed-images", str(md)], capture_output=True, text=True
    )
    assert r.returncode == 1
    assert "assente.png" in r.stderr
    assert not md.with_suffix(".html").exists()
