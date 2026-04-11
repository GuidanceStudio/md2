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

    md2 nomefile.md --lang en --dark --template corporate

| Flag               | Default | Descrizione                                       |
|--------------------|---------|---------------------------------------------------|
| `--lang`           | `it`    | Attributo `lang` dell'HTML generato                |
| `--dark`           | off     | Usa il tema scuro come default                     |
| `--template NOME`  | —       | Usa un template da `~/.md2/templates/NOME/`        |
| `--init-templates` | —       | (Re)copia il template default in `~/.md2/templates/` |

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
| `S`                        | Toggle sidebar             |
| `D`                        | Toggle dark/light mode     |

## Test

I test usano `pytest` e sono divisi in **unit** (funzioni pure, senza I/O) e **live** (end-to-end con file su disco).

    tests/
    ├── unit/
    │   ├── test_sanitize_html.py      # sanitizzazione HTML e prevenzione XSS
    │   ├── test_generate_css.py       # generazione CSS, temi, dark mode, responsive
    │   ├── test_render_presentation.py # parsing markdown, slide, sidebar, struttura HTML
    │   ├── test_main_cli.py           # parsing argomenti CLI
    │   ├── test_template_system.py    # sistema template, --template, --init-templates
    │   ├── test_frontmatter.py        # parsing frontmatter TOML
    │   ├── test_palettes.py           # sistema palette colori
    │   ├── test_charts.py             # direttiva :::chart e Charts.css
    │   ├── test_chart_sizing.py       # dimensioni default per tipo di chart
    │   ├── test_columns.py            # direttiva :::columns layout
    │   └── test_print_css.py          # CSS stampa ottimizzato per chart
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

## Frontmatter

md2 supporta un blocco frontmatter TOML all'inizio del file markdown, delimitato da `+++`:

```markdown
+++
title = "Report Trimestrale"
palette = "warm"
lang = "en"
dark = true
+++

# Report Trimestrale

Contenuto della presentazione...
```

| Campo     | Tipo            | Default     | Descrizione                          |
|-----------|-----------------|-------------|--------------------------------------|
| `title`   | string          | da `# H1`  | Titolo della presentazione (override)|
| `palette` | string          | `"default"` | Nome palette colori                  |
| `colors`  | array di string | —           | Override colori della palette         |
| `lang`    | string          | `"it"`      | Lingua del documento                 |
| `dark`    | bool            | `false`     | Dark mode come default               |

I flag CLI (`--lang`, `--dark`) hanno priorità sul frontmatter quando specificati esplicitamente.

## Palette colori

md2 include 6 palette predefinite: `default`, `warm`, `cool`, `mono`, `vivid`, `pastel`.

Le palette sono file TOML con questa struttura:

```toml
name = "warm"

colors = [
    "#d45d00",
    "#e8910c",
    "#f5c542",
    "#e15759",
]

[dark]
colors = [
    "#f0a050",
    "#f5b84c",
    "#fce08a",
    "#f28e8e",
]
```

### Palette custom

Crea un file `.toml` in `~/.md2/palettes/`:

```bash
# Nuova palette
~/.md2/palettes/corporate.toml

# Override di una builtin
~/.md2/palettes/warm.toml
```

Le palette utente hanno priorità sulle builtin.

### Cascata colori

```
Palette builtin → Palette utente → Frontmatter (palette=) → Frontmatter (colors=)
```

Se nel frontmatter sono presenti sia `palette` che `colors`, i colori nel frontmatter sovrascrivono i primi N colori della palette selezionata.

Se la sezione `[dark]` è assente nel file palette, le varianti dark vengono calcolate automaticamente.

## Struttura del file Markdown

md2 converte un singolo file `.md` in una presentazione HTML. Il file è diviso in sezioni separate da `---`.

### Copertina

La prima sezione (prima del primo `---`) è la **copertina**. Il primo `# H1` diventa il titolo della presentazione e della pagina HTML. Il testo sotto appare centrato nella slide di copertina. Se non c'è un `# H1`, il titolo di default è "Presentation".

### Separatore slide

Usa `---` su una riga separata, con **righe vuote sopra e sotto**, per separare le slide:

```
Contenuto slide 1

---

Contenuto slide 2
```

### Titolo slide

Il primo `## H2` di ogni sezione diventa il titolo della slide e la voce corrispondente nella sidebar di navigazione. Se una sezione non ha `## H2`, viene chiamata "Slide N".

### Sotto-sezioni

All'interno di ogni slide puoi usare `### H3` e `#### H4` per creare sotto-sezioni.

### Esempio completo

```markdown
# Titolo della Presentazione

Questo testo appare sulla copertina.
**Data:** 14 marzo 2026

---

## Introduzione

Contenuto della prima slide con **bold** e *italic*.

- Punto uno
- Punto due
  - Sotto-punto

> Una citazione importante.

---

## Dati e Codice

### Tabella risultati

| Metrica | Valore | Trend |
|---------|--------|-------|
| CPL     | €29    | +15%  |
| CAC     | €514   | -2%   |

### Esempio di codice

```python
def hello():
    print("Hello, world!")
```

Un link automatico: https://example.com

Una nota a piè di pagina[^1].

[^1]: Questa è la nota.
```

## Markdown supportato

### Testo

| Sintassi                | Risultato          |
|-------------------------|--------------------|
| `**bold**`              | **bold**           |
| `*italic*`              | *italic*           |
| `` `inline code` ``    | `inline code`      |
| `[testo](url)`          | link cliccabile    |
| `![alt](url)`           | immagine centrata  |

### Heading

| Livello    | Uso                                              |
|------------|--------------------------------------------------|
| `# H1`    | Titolo della presentazione (solo nella copertina) |
| `## H2`   | Titolo della slide (uno per slide)                |
| `### H3`  | Sotto-sezione dentro una slide                    |
| `#### H4` | Sotto-sezione di livello inferiore                |

### Liste

Liste puntate (`-` o `*`) e numerate (`1.`), anche annidate con indentazione.

### Tabelle

Sintassi standard con `|` e `---`. L'allineamento colonne è supportato (`:---`, `:---:`, `---:`).

### Grafici (Charts)

Usa la direttiva `:::chart` per trasformare una tabella markdown in un grafico visuale. La sintassi è:

```
:::chart TIPO [--opzioni...]
| Intestazione | Colonna Dati |
|--------------|--------------|
| Etichetta    | Valore       |
:::
```

La prima colonna è sempre l'etichetta (asse delle categorie). Le colonne successive sono i dati. Se ci sono più colonne dati, il grafico diventa automaticamente multi-dataset.

#### Tipi di grafico

| Tipo     | Descrizione                                          |
|----------|------------------------------------------------------|
| `bar`    | Barre orizzontali — ideale per confronti             |
| `column` | Barre verticali — ideale per serie temporali         |
| `line`   | Grafico a linea — trend e andamenti                  |
| `area`   | Grafico ad area — come line ma con riempimento       |
| `pie`    | Grafico a torta — proporzioni (solo singola serie)   |

#### Opzioni

| Opzione       | Effetto                                               |
|---------------|-------------------------------------------------------|
| `--labels`    | Mostra le etichette (prima colonna) sugli assi        |
| `--legend`    | Mostra legenda sotto il grafico (per multi-dataset)   |
| `--stacked`   | Barre/colonne impilate anziché affiancate             |
| `--show-data` | Mostra i valori numerici al passaggio del mouse       |
| `--title "…"` | Aggiunge un titolo/caption sopra il grafico           |

#### Esempio: singola serie

```
:::chart bar --labels --title "Vendite per prodotto"
| Prodotto | Vendite |
|----------|---------|
| Widget A | 50      |
| Widget B | 80      |
| Widget C | 65      |
:::
```

#### Esempio: multi-dataset con legenda

```
:::chart column --labels --legend
| Trimestre | Entrate | Uscite |
|-----------|---------|--------|
| Q1        | 100     | 80     |
| Q2        | 150     | 90     |
| Q3        | 130     | 110    |
:::
```

#### Dimensioni

Ogni tipo di grafico ha dimensioni di default sensate:

| Tipo | Altezza | Larghezza |
|------|---------|-----------|
| `bar` | automatica (cresce con le righe) | 100% |
| `column`, `line`, `area` | `min(300px, 40vh)` | 100% |
| `pie` | proporzionale al viewport | `min(50vh, 50vw)` centrato |

#### Note

- I valori nelle colonne dati devono essere **numerici**. Valori non numerici vengono trattati come 0.
- I grafici usano automaticamente i colori della **palette** del documento (vedi sezione Palette colori).
- **Charts.css** viene incluso nell'HTML solo quando il documento contiene almeno un grafico — le presentazioni senza grafici non hanno overhead aggiuntivo.
- Basato su [Charts.css](https://chartscss.org/), una libreria CSS pura senza JavaScript.
- In **stampa**, i colori dei grafici vengono preservati (`print-color-adjust: exact`). I grafici non vengono spezzati tra pagine.

### Layout a colonne

Usa `:::columns` con `:::col` per affiancare contenuti in due colonne:

```
:::columns

:::col
Testo nella colonna sinistra.

- Punto uno
- Punto due

:::col
:::chart bar --labels
| A | B |
|---|---|
| x | 50 |
:::

:::
```

Ogni `:::col` delimita l'inizio di una colonna (massimo 2). Su mobile (< 768px) le colonne si impilano verticalmente. In stampa restano affiancate.

### Blocchi di codice

Fenced code blocks con ` ```linguaggio ``` `. Il linguaggio viene usato come attributo class per eventuale syntax highlighting.

### Blockquote

`>` produce un blocco citazione con bordino laterale blu.

### Footnotes

`[^1]` nel testo e `[^1]: testo della nota` in fondo alla slide. Le note vengono renderizzate in fondo alla slide con stile ridotto.

### Autolink

URL nudi (`https://...`) vengono automaticamente convertiti in link cliccabili con `target="_blank"`.

### Newline

Un singolo invio nel markdown produce un `<br>` nell'HTML (estensione `nl2br`). Non serve il doppio spazio a fine riga.

### HTML inline

Tag HTML sicuri vengono preservati: `<iframe>` per embed video/mappe, `<img>` con attributi `src`, `alt`, `width`, `height`. Tag pericolosi (`<script>`, `onclick`, `javascript:`) vengono rimossi automaticamente.

## Interfaccia generata

- **Sidebar navigabile** — link a ogni slide, indicatore slide attiva, lista scrollabile con shortcut fissi in fondo
- **Sidebar collassabile** — bottone `«`/`»` o tasto `S`
- **Dark mode** — toggle sole/luna in alto a destra o tasto `D`
- **Indicatore slide** — mostra "2 / 5" in basso a destra
- **Barra di progresso** — linea blu in cima alla pagina
- **Scroll-snap** — ogni slide occupa l'intero viewport
- **Fade-in** — il contenuto delle slide appare con animazione
- **Print** — `Ctrl+P` produce un layout pulito senza UI, una slide per pagina. I grafici mantengono i colori e non vengono spezzati tra pagine
- **Meta tag Open Graph** — titolo e descrizione per la condivisione
- **Favicon inline** — nessun 404 nel browser
- **Responsive** — breakpoint a 1024px (tablet) e 768px (mobile) con menu hamburger

## Template personalizzati

md2 usa un sistema di template basato su [Jinja2](https://jinja.palletsprojects.com/). Al primo avvio, il template default viene copiato in `~/.md2/templates/default/` — puoi modificarlo o crearne di nuovi.

### Struttura di un template

```
~/.md2/templates/
├── default/                    ← template default (copiato automaticamente)
│   ├── base.html               ← template principale con {% block %}
│   ├── style.css               ← CSS completo
│   └── components/
│       ├── head.html           ← <head> con meta, OG, favicon, <style>
│       ├── sidebar.html        ← sidebar con lista slide e shortcut
│       ├── cover.html          ← slide di copertina
│       ├── slide.html          ← singola slide (usata nel for loop)
│       ├── controls.html       ← progress bar, indicator, theme toggle
│       └── scripts.html        ← JavaScript
└── mio-template/               ← template custom
    └── base.html
```

### Creare un template custom

**Metodo 1 — Copia e modifica:**

```bash
cp -r ~/.md2/templates/default ~/.md2/templates/mio-template
# Modifica i file a piacere
md2 presentazione.md --template mio-template
```

**Metodo 2 — Ereditarietà (solo override):**

Crea `~/.md2/templates/mio-template/base.html`:

```jinja2
{% extends "default/base.html" %}

{% block sidebar %}{% endblock %}
{% block controls %}{% endblock %}
```

Questo template eredita tutto dal default e rimuove sidebar e controlli. Puoi sovrascrivere qualsiasi blocco.

### Blocchi disponibili

| Blocco          | Contenuto                                      |
|-----------------|-------------------------------------------------|
| `head`          | Contenuto di `<head>` (meta, title, CSS)        |
| `css`           | Solo il CSS (dentro `<style>`)                   |
| `controls`      | Progress bar, hamburger, indicator, theme toggle |
| `sidebar`       | Sidebar completa con lista slide e shortcut      |
| `main`          | Container principale con cover e slide           |
| `cover`         | Slide di copertina                               |
| `slides`        | Loop delle slide                                 |
| `scripts`       | Blocco `<script>` con tutto il JS                |

### Variabili di contesto

Queste variabili sono disponibili in tutti i template:

| Variabile          | Tipo    | Descrizione                                |
|--------------------|---------|--------------------------------------------|
| `title`            | string  | Titolo della presentazione (HTML-escaped)  |
| `og_description`   | string  | Meta description per Open Graph            |
| `lang`             | string  | Attributo lang (`it`, `en`, ...)            |
| `dark_mode`        | bool    | `true` se `--dark` è attivo                |
| `cover.title`      | string  | Titolo della copertina                     |
| `cover.content`    | string  | HTML del contenuto della copertina         |
| `slides`           | list    | Lista delle slide                          |
| `slides[].id`      | string  | ID HTML della slide (`slide-0`, `slide-1`) |
| `slides[].title`   | string  | Titolo della slide                         |
| `slides[].content` | string  | HTML del contenuto della slide             |
| `palette_css`      | string  | CSS con variabili `--md2-color-N`          |
| `has_charts`       | bool    | `true` se il documento contiene grafici    |

### Aggiornare il template default

Dopo un aggiornamento di md2, puoi rigenerare il template default con:

```bash
md2 --init-templates
```

Questo sovrascrive `~/.md2/templates/default/` con la versione bundled aggiornata. I template custom non vengono toccati.
