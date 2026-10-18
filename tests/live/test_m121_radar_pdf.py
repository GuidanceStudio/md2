"""M121: a radar beside a second chart prints on one A4 landscape page per slide.

Renders with the bundled template and prints with a headless Chromium-family
browser, injecting the same @page block the deck renderer adds before printing.
"""
import re
import shutil
import subprocess

import pytest

from md2.cli import render_html

pytestmark = pytest.mark.live

# The deck renderer's browser search order, Chromium family only: Firefox lays out
# print differently and is not the path decks are printed with.
BROWSERS = ["chromium", "google-chrome", "chromium-browser", "chrome", "brave-browser", "brave"]
PAGE_CSS = "<style>@page { size: A4 landscape; margin: 12mm; }</style>"
A4_LANDSCAPE_PT = (841.89, 595.28)

DECK = """# Monitoring report

Second half compared with the first

---

## Profile and volume side by side

:::columns
:::col
:::chart radar --title "Score by dimension"
| Dimension | H1 | H2 |
|---|---|---|
| Price and fees | 3.8 | 4.2 |
| Customer support | 3.1 | 3.9 |
| Ease of use | 4.4 | 4.5 |
| Security | 4.0 | 3.7 |
| Integrations | 2.9 | 3.6 |
| Reporting and exports | 3.5 | 4.1 |
:::
:::col
:::chart bar --title "Answers per dimension"
| Dimension | Answers |
|---|---|
| Price and fees | 120 |
| Customer support | 95 |
| Ease of use | 140 |
| Security | 80 |
| Integrations | 60 |
| Reporting and exports | 75 |
:::
:::

---

## Full-width profile

:::chart radar
| Dimension | H1 | H2 |
|---|---|---|
| Price | 3.8 | 4.2 |
| Support | 3.1 | 3.9 |
| Ease | 4.4 | 4.5 |
| Security | 4.0 | 3.7 |
| Integrations | 2.9 | 3.6 |
:::
"""


def _browser():
    return next((b for b in BROWSERS if shutil.which(b)), None)


def _print_pdf(html_path, pdf_path, browser):
    subprocess.run(
        [browser, "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf_path}", f"file://{html_path}"],
        capture_output=True, timeout=120, check=False,
    )
    assert pdf_path.exists(), f"{browser} wrote no PDF"
    return pdf_path.read_bytes()


def test_radar_beside_a_bar_chart_prints_one_a4_landscape_page_per_slide(tmp_path):
    browser = _browser()
    if browser is None:
        pytest.skip("no Chromium-family browser on PATH to print the PDF")

    html = render_html(DECK).replace("</head>", PAGE_CSS + "</head>", 1)
    assert html.count('<svg class="md2-radar"') == 2
    html_path = tmp_path / "deck.html"
    html_path.write_text(html, encoding="utf-8")

    pdf = _print_pdf(html_path, tmp_path / "deck.pdf", browser)

    pages = re.findall(rb"/Type\s*/Page(?![a-zA-Z])", pdf)
    assert len(pages) == 3  # cover + two slides
    boxes = {tuple(round(float(v), 1) for v in box.split()[2:])
             for box in re.findall(rb"/MediaBox\s*\[([^\]]+)\]", pdf)}
    assert boxes and all(w == pytest.approx(A4_LANDSCAPE_PT[0], abs=1)
                         and h == pytest.approx(A4_LANDSCAPE_PT[1], abs=1) for w, h in boxes)
