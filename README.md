# Markdown to HTML Presentation Converter

Uno script Python per convertire file Markdown in presentazioni HTML con navigazione laterale.

## Requisiti

- Python 3.9+
- [`uv`](https://docs.astral.sh/uv/) (gestore pacchetti Python)

Per installare `uv`:

    curl -LsSf https://astral.sh/uv/install.sh | sh

## Installazione

### Veloce (Script)
Per installare tutto automaticamente (dipendenze incluse) e rendere disponibile il comando `md2` globalmente, esegui:

    chmod +x install.sh
    ./install.sh

Lo script installerà `uv` (se non presente) e il tool `md2` globalmente tramite `uv tool install`.

**Nota importante:** Se dopo l'installazione il comando `md2` non viene trovato, potresti dover aggiungere `~/.local/bin` al tuo PATH eseguendo:

    export PATH="$HOME/.local/bin:$PATH"

### Manuale (Globale)
Se preferisci usare `uv` direttamente:

    uv tool install .

### Sviluppo (Locale)
Per configurare l'ambiente di lavoro in modo isolato e pulito:

    make install

Questo creerà un ambiente virtuale `.venv` e installerà le dipendenze con `uv sync`.


## Come usarlo

### Globale
Se hai installato lo script globalmente, puoi generare la presentazione HTML direttamente:

    md2 nomefile.md

### Opzioni

    md2 nomefile.md --lang en

| Flag     | Default | Descrizione                        |
|----------|---------|------------------------------------|
| `--lang` | `it`    | Attributo `lang` dell'HTML generato |

### Sviluppo (Locale)
In alternativa, usa il target `run` di `make` specificando il file Markdown:

    make run FILE=nomefile.md

Il comando genererà un file `nomefile.html` nella stessa directory.

### Navigazione da tastiera

L'HTML generato supporta le seguenti scorciatoie:

| Tasto                      | Azione                     |
|----------------------------|----------------------------|
| `↓` / `→` / `PgDn`        | Slide successiva           |
| `↑` / `←` / `PgUp`        | Slide precedente           |
| `Home`                     | Torna alla cover           |
| `End`                      | Vai all'ultima slide       |

## Test

I test usano `pytest` e sono divisi in **unit** (funzioni pure, senza I/O) e **live** (end-to-end con file su disco).

    tests/
    ├── unit/
    │   ├── test_sanitize_html.py      # sanitizzazione HTML e prevenzione XSS
    │   ├── test_generate_css.py       # generazione CSS, temi, dark mode, responsive
    │   ├── test_render_presentation.py # parsing markdown, slide, sidebar, struttura HTML
    │   └── test_main_cli.py           # parsing argomenti CLI
    └── live/
        ├── test_conversion_e2e.py     # conversione completa file → HTML
        ├── test_edge_cases_e2e.py     # file vuoti, unicode, XSS, casi limite
        └── test_ui_improvements_e2e.py # verifica migliorie grafiche nell'output

### Tutti i test

    make test

oppure direttamente:

    uv run pytest

### Solo unit test

    make test-unit

### Solo live test (end-to-end)

    make test-live

### Test con output verboso

    uv run pytest -v

### Singolo file di test

    uv run pytest tests/unit/test_sanitize_html.py

### Singolo test per nome

    uv run pytest -k "test_strips_script_tags"

## Pulizia

Per rimuovere l'ambiente virtuale e i file generati:

    make clean

## Funzionalità

### Markdown supportato

Oltre alla sintassi base (heading, bold, italic, link, immagini, liste), md2 supporta:

- **Fenced code blocks** — ` ```python ... ``` ` con attributo di linguaggio
- **Tabelle** — sintassi standard con `|` e `---`
- **Footnotes** — `[^1]` nel testo e `[^1]: nota` in fondo alla slide
- **Autolink** — URL nudi (`https://...`) vengono automaticamente convertiti in link cliccabili

### Interfaccia generata

- **Sidebar navigabile** con link a ogni slide e indicatore slide attiva
- **Sidebar collassabile** (bottone `«` in alto nella sidebar, bottone `»` fisso per riaprirla)
- **Guida shortcut** nella sidebar — mostra le scorciatoie da tastiera in fondo al menu
- **Indicatore slide** — mostra "2 / 5" in basso a destra
- **Barra di progresso** — linea blu in cima alla pagina
- **Dark mode** — toggle sole/luna in alto a destra
- **Scroll-snap** — ogni slide occupa l'intero viewport
- **Fade-in** — il contenuto delle slide appare con animazione
- **Print** — `Ctrl+P` produce un layout pulito senza UI, una slide per pagina
- **Meta tag Open Graph** — titolo e descrizione per la condivisione
- **Favicon inline** — nessun 404 nel browser
- **Responsive** — breakpoint a 1024px (tablet) e 768px (mobile) con menu hamburger

## Struttura del file Markdown

Lo script interpreta il file Markdown secondo le seguenti regole:

1.  **Copertina:** La prima sezione del file (prima del primo separatore) rappresenta la copertina. Il primo titolo `# H1` trovato qui viene utilizzato come titolo principale della presentazione.
2.  **Separatori:** Usa `---` (su una riga separata) per dividere le diverse slide.
3.  **Titoli delle Slide:** In ogni sezione successiva, il primo titolo `## H2` viene utilizzato come intestazione della slide e come voce nel menu di navigazione laterale.

### Esempio

    # Titolo della Presentazione

    Questo testo appare sulla copertina.

    ---

    ## Introduzione
    Contenuto della prima slide.

    ---

    ## Sviluppo
    Contenuto della seconda slide.
