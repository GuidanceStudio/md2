# DEVPLAN — Test Suite per md2

## Milestone 1: Unit Tests (`tests/unit/`)

Test delle funzioni pure, senza I/O su disco.

### 1.1 `test_sanitize_html.py` — Sanitizzazione HTML

- **test_strips_script_tags**: verifica che `<script>alert('xss')</script>` venga rimosso
- **test_strips_onclick**: verifica che attributi event handler (`onclick`, `onerror`) vengano rimossi
- **test_allows_safe_tags**: verifica che tag consentiti (`p`, `h1`, `ul`, `table`, `code`, `pre`, `img`) passino intatti
- **test_allows_iframe**: verifica che `<iframe src="...">` venga preservato (usato per embed)
- **test_allows_style_attribute**: verifica che l'attributo `style` su elementi consentiti venga mantenuto
- **test_allows_img_attributes**: verifica che `src`, `alt`, `width`, `height` su `<img>` vengano mantenuti
- **test_strips_dangerous_href**: verifica che `href="javascript:..."` venga gestito
- **test_empty_input**: stringa vuota restituisce stringa vuota

### 1.2 `test_generate_css.py` — Generazione CSS

- **test_default_theme**: senza parametri usa i colori di DEFAULT_THEME
- **test_custom_theme_override**: passando un dict parziale, i valori vengono sovrascritti
- **test_custom_theme_full**: passando tutti i valori, nessun default rimane
- **test_contains_dark_mode**: il CSS contiene le regole `body.dark-mode`
- **test_contains_responsive**: il CSS contiene la media query `@media (max-width: 768px)`

### 1.3 `test_render_presentation.py` — Logica di rendering

- **test_cover_title_extraction**: il primo `# Titolo` diventa il titolo della presentazione
- **test_cover_default_title**: senza `# H1`, il titolo di default è "Presentation"
- **test_cover_content**: il testo sotto il titolo di copertina viene incluso nel body
- **test_slide_splitting**: `---` separa correttamente le slide
- **test_slide_titles**: ogni `## H2` diventa il titolo della slide corrispondente
- **test_slide_default_title**: slide senza `## H2` riceve titolo "Slide N"
- **test_sidebar_contains_all_titles**: la sidebar contiene link a tutte le slide
- **test_sidebar_contains_cover_link**: la sidebar include il link alla copertina
- **test_markdown_tables_rendered**: tabelle markdown vengono convertite in `<table>`
- **test_markdown_code_blocks_rendered**: blocchi di codice vengono convertiti in `<pre><code>`
- **test_empty_input**: input vuoto non genera errori
- **test_single_slide_no_separator**: input senza `---` produce solo la copertina
- **test_result_structure**: il risultato contiene le chiavi `title`, `body_html`, `css`

### 1.4 `test_main_cli.py` — Parsing CLI (senza scrivere file)

- **test_missing_file_exits**: file inesistente causa `sys.exit(1)`
- **test_no_arguments_exits**: nessun argomento causa errore argparse
- **test_output_filename**: il file di output ha estensione `.html` al posto di `.md`

---

## Milestone 2: Live Tests (`tests/live/`)

Test end-to-end che leggono/scrivono file su disco.

### 2.1 `test_conversion_e2e.py` — Conversione completa

- **test_example_file_converts**: `examples/example.md` viene convertito senza errori e produce un file `.html`
- **test_output_is_valid_html**: l'output contiene `<!DOCTYPE html>`, `<html`, `<head>`, `<body>`
- **test_output_contains_sidebar**: l'HTML generato contiene `id="sidebar"`
- **test_output_contains_theme_toggle**: l'HTML contiene il bottone `id="theme-toggle"`
- **test_output_contains_slides**: l'HTML contiene almeno un `<div class="slide"`
- **test_output_contains_cover**: l'HTML contiene `<div class="slide cover"`
- **test_cli_generates_file**: eseguire `md2 file.md` da CLI crea effettivamente `file.html` su disco
- **test_cli_stdout_message**: l'output stdout contiene "Success!"

### 2.2 `test_edge_cases_e2e.py` — Casi limite end-to-end

- **test_empty_file**: un file `.md` vuoto produce comunque un HTML valido
- **test_only_cover**: file senza `---` produce HTML con solo la copertina
- **test_unicode_content**: contenuto con emoji e caratteri Unicode viene gestito correttamente
- **test_large_file**: file con molte slide (50+) viene processato senza errori
- **test_special_characters_in_title**: caratteri speciali (`<`, `>`, `&`) nel titolo vengono gestiti
- **test_output_overwrites_existing**: se il file `.html` esiste già, viene sovrascritto

---

## Milestone 16: Shortcut tastiera per toggle sidebar ✅

Aggiungere una scorciatoia da tastiera per nascondere/mostrare la sidebar.

- **Shortcut keyboard**: associare un tasto (es. `S` o `Ctrl+B`) per toggle della sidebar
- **Listener globale**: il listener deve funzionare indipendentemente dal focus corrente
- **Integrazione con guida shortcut**: aggiornare la guida delle scorciatoie nella sidebar per includere il nuovo shortcut
- **Stato persistente**: ricordare lo stato della sidebar (aperta/chiusa) durante la navigazione

---

## Milestone 17: Flag per tema dark di default ✅

Aggiungere un flag CLI per impostare il tema scuro come default alla generazione.

- **Flag CLI `--dark`**: aggiungere un argomento opzionale `--dark` al parser CLI
- **Body class**: quando il flag è attivo, il `<body>` viene generato con `class="dark-mode"` già applicata
- **Compatibilità toggle**: il bottone di toggle tema deve continuare a funzionare normalmente anche quando il dark è il default
- **Test unitario**: verificare che con `--dark` l'HTML generato contenga `class="dark-mode"` sul body
- **Test senza flag**: verificare che senza `--dark` il comportamento resti invariato (tema light di default)

---

## Milestone 18: Shortcut tastiera per toggle tema dark/light ✅

Aggiungere una scorciatoia da tastiera per alternare tra tema chiaro e scuro nella presentazione generata.

- **Shortcut keyboard**: associare un tasto (es. `D`) per toggle del tema dark/light
- **Listener globale**: il listener deve funzionare indipendentemente dal focus corrente (ignorare se si è in un campo input/textarea)
- **Integrazione con guida shortcut**: aggiornare la guida delle scorciatoie nella sidebar per includere il nuovo shortcut
- **Toggle body class**: aggiungere/rimuovere `dark-mode` dal `<body>` al keypress
- **Compatibilità con --dark**: lo shortcut deve funzionare sia quando si parte dal tema light che dal dark
- **Test unitario**: verificare che il JS generato contenga il listener per il toggle tema

---

## Milestone 19: Sidebar scroll — lista slide scrollabile con istruzioni fisse in fondo ✅

Quando le slide sono molte, l'intero sidebar scrolla via portando con sé le istruzioni shortcut. L'utente perde il riferimento ai comandi da tastiera.

**Soluzione**: approccio CSS-only con flexbox. La `<ul>` delle slide prende lo scroll interno, le istruzioni restano ancorate in fondo.

### Modifiche CSS in `md2.py`

1. **`#sidebar`** (~riga 137): rimuovere `overflow-y: auto`, aggiungere `overflow: hidden` — il container non scrolla più
2. **`#sidebar ul`** (~riga 149): aggiungere `flex: 1; overflow-y: auto` — la lista scrolla internamente
3. **`#sidebar-shortcuts`** (~riga 270): sostituire `margin-top: auto` con `flex-shrink: 0` — le istruzioni non si comprimono e restano fisse in fondo

### Verifica
- Generare una presentazione con 20+ slide
- La lista slide scrolla indipendentemente
- Le istruzioni restano sempre visibili in fondo alla sidebar
- Toggle sidebar, tema dark/light, mobile continuano a funzionare

---

## Milestone 20: README — documentazione completa formato Markdown e funzionalità supportate ✅

Il README attuale ha sezioni "Markdown supportato" e "Struttura del file Markdown" ma sono incomplete e frammentate. Servono informazioni chiare e complete su come scrivere il file `.md` per ottenere una buona presentazione, e su cosa esattamente il tool supporta.

### Cosa aggiornare nel README

1. **Sezione "Struttura del file Markdown"** — riscrivere con struttura chiara:
   - **Copertina**: tutto il contenuto prima del primo `---`. Il primo `# H1` diventa il titolo della presentazione e della pagina HTML. Il resto appare centrato nella slide di copertina. Se non c'è `# H1`, il titolo di default è "Presentation"
   - **Separatore slide**: `---` su riga separata (con righe vuote sopra e sotto). Ogni `---` crea una nuova slide
   - **Titolo slide**: il primo `## H2` di ogni sezione diventa il titolo della slide e la voce nella sidebar. Se assente, la slide viene chiamata "Slide N"
   - **Sotto-sezioni**: `### H3` e `#### H4` sono supportati dentro le slide come sotto-titoli

2. **Sezione "Markdown supportato"** — espandere con tutti gli elementi effettivamente supportati:
   - **Testo base**: paragrafi, **bold**, *italic*, ~~strikethrough~~, `inline code`
   - **Heading**: `# H1` (solo cover), `## H2` (titolo slide), `### H3`, `#### H4` (sotto-sezioni)
   - **Liste**: puntate (`-` / `*`) e numerate (`1.`), anche annidate
   - **Link**: `[testo](url)` — aperti in nuova tab con `target="_blank"`
   - **Immagini**: `![alt](url)` — centrate, responsive, con bordi arrotondati e ombra
   - **Tabelle**: sintassi standard con `|` e `---`, con allineamento colonne (`:---`, `:---:`, `---:`)
   - **Blocchi di codice**: fenced con ` ```linguaggio ``` `, con font monospace e syntax highlighting base
   - **Blockquote**: `>` con bordino laterale blu
   - **Footnotes**: `[^1]` nel testo e `[^1]: nota` in fondo alla slide
   - **Autolink**: URL nudi (`https://...`) convertiti automaticamente in link cliccabili
   - **Newline**: a capo singolo (`nl2br`) — un singolo invio nel markdown produce un `<br>` nell'HTML
   - **HTML inline**: tag sicuri vengono preservati (`iframe` per embed, `img` con attributi). Tag pericolosi (`script`, `onclick`, etc.) vengono rimossi per sicurezza

3. **Sezione "Interfaccia generata"** — verificare che sia aggiornata con tutte le feature attuali, in particolare:
   - Aggiungere shortcut `D` per toggle tema nella tabella navigazione tastiera
   - Verificare che la lista delle feature UI sia completa

4. **Esempio completo** — aggiornare l'esempio nella sezione "Struttura del file Markdown" per mostrare più elementi supportati (tabella, code block, blockquote, immagine, footnote, liste annidate)

### Cosa NON fare
- Non tradurre in inglese — il README è in italiano
- Non aggiungere sezioni non necessarie
- Non duplicare informazioni già presenti altrove nel README

---

## Milestone 21: Ristrutturazione a pacchetto + refactoring Jinja2 ✅

Oggi `md2.py` è un singolo file che costruisce HTML/CSS/JS con f-string Python. Questo milestone converte il progetto in un pacchetto Python con template Jinja2, separando dati da presentazione.

### 21.1 Conversione a pacchetto

Il modulo singolo `md2.py` diventa il pacchetto `md2/`:

```
md2/
├── __init__.py              ← re-export pubblici (main, render_presentation, etc.)
├── core.py                  ← logica: parsing markdown, sanitize, prepare context
├── cli.py                   ← main() e argparse
├── templates/
│   └── default/
│       ├── base.html        ← template principale con {% block %}
│       ├── style.css        ← CSS completo (era generate_css())
│       └── components/
│           ├── head.html    ← <head> con meta, OG, favicon, <style>
│           ├── sidebar.html ← sidebar con lista slide e shortcuts
│           ├── cover.html   ← slide copertina
│           ├── slide.html   ← singola slide (usata nel {% for %})
│           ├── controls.html← progress bar, indicator, theme toggle, hamburger
│           └── scripts.html ← tutto il JavaScript
```

Aggiornare `pyproject.toml`:
- `packages = ["md2"]` al posto di `include = ["md2.py"]`
- Aggiungere `jinja2>=3.0` alle dipendenze
- Includere `md2/templates/**` come package data
- L'entry point `md2 = "md2.cli:main"` (o `md2:main` se re-exportato da `__init__`)

Rimuovere il vecchio `md2.py` dalla root.

### 21.2 Refactoring della logica core

**`core.py`** contiene:
- `sanitize_html()`, `autolink()`, `process_markdown()` — invariati
- `prepare_context(markdown_text, theme_config=None)` — nuova funzione che sostituisce `render_presentation()`. Ritorna un dict di contesto per Jinja2:

```python
{
    "title": "Titolo Presentazione",       # testo plain, escaped
    "og_description": "...",                # meta description
    "lang": "it",                           # da CLI
    "dark_mode": False,                     # da CLI --dark
    "cover": {
        "title": "Titolo Presentazione",
        "content": "<p>html copertina...</p>"
    },
    "slides": [
        {"id": "slide-0", "title": "Intro", "content": "<p>html...</p>"},
        {"id": "slide-1", "title": "Dati",  "content": "<p>html...</p>"},
    ],
}
```

**`cli.py`** contiene:
- `main()` — argparse, carica template, chiama `prepare_context()`, rende con Jinja2, scrive file

### 21.3 Template Jinja2 default

Estrarre le f-string attuali nei file template. Il template default replica **esattamente** l'output attuale — nessun cambiamento visivo.

**`base.html`** — struttura principale:
```jinja2
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    {% block head %}{% include "components/head.html" %}{% endblock %}
</head>
<body{% if dark_mode %} class="dark-mode"{% endif %}>
    {% block progress %}<div id="progress-bar"></div>{% endblock %}
    {% block menu_toggle %}{% include "components/controls.html" %}{% endblock %}
    {% block sidebar %}{% include "components/sidebar.html" %}{% endblock %}
    {% block main %}
    <div id="main">
        {% block cover %}{% include "components/cover.html" %}{% endblock %}
        {% block slides %}
        {% for slide in slides %}
            {% include "components/slide.html" %}
        {% endfor %}
        {% endblock %}
    </div>
    {% endblock %}
    {% block indicator %}<div id="slide-indicator"></div>{% endblock %}
    {% block theme_toggle %}...{% endblock %}
    {% block scripts %}<script>{% include "components/scripts.html" %}</script>{% endblock %}
</body>
</html>
```

**`style.css`** — il CSS di `generate_css()` convertito. Le variabili del tema (`--bg-color`, etc.) restano CSS custom properties. Il file CSS viene incluso via `{% include "style.css" %}` dentro un `<style>`.

**`components/sidebar.html`**:
```jinja2
<div id="sidebar">
    <ul>
        <li><a href="#cover">{{ cover.title }}</a></li>
        {% for slide in slides %}
        <li><a href="#{{ slide.id }}">{{ slide.title }}</a></li>
        {% endfor %}
    </ul>
    <div id="sidebar-shortcuts">
        <kbd>&#8595;</kbd> <kbd>&#8594;</kbd> Next<br>
        <kbd>&#8593;</kbd> <kbd>&#8592;</kbd> Prev<br>
        <kbd>Home</kbd> / <kbd>End</kbd><br>
        <kbd>S</kbd> Toggle Sidebar<br>
        <kbd>D</kbd> Toggle Theme
    </div>
</div>
<button id="sidebar-toggle" onclick="toggleSidebar()" title="Toggle Sidebar">&#171;</button>
```

**`components/scripts.html`** — il blocco `<script>` attuale, convertito da f-string a JS puro (non serve Jinja2 nel JS, non ci sono variabili dinamiche).

### 21.4 Rendering con Jinja2

In `cli.py`, il rendering:

```python
from jinja2 import Environment, FileSystemLoader, PackageLoader

def load_template(template_name=None):
    """Carica il template. Se None, usa il default bundled."""
    if template_name:
        # carica da ~/.md2/templates/{template_name}/
        template_dir = Path.home() / ".md2" / "templates" / template_name
        env = Environment(loader=FileSystemLoader(str(template_dir)))
    else:
        # carica il default bundled nel pacchetto
        env = Environment(loader=PackageLoader("md2", "templates/default"))
    return env.get_template("base.html")
```

### 21.5 Aggiornamento build e test

- Aggiornare `pyproject.toml` con nuova struttura pacchetto
- Aggiornare tutti gli import nei test (`from md2 import ...` deve continuare a funzionare via `__init__.py`)
- Verificare che `uv run md2 examples/example.md` produca output **identico** (o equivalente) a prima
- Tutti i 154 test esistenti devono passare
- Aggiungere test per `prepare_context()` che verifichi la struttura del dict ritornato

### Cosa NON fare
- Non cambiare l'output visivo — il template default deve produrre HTML identico
- Non aggiungere feature nuove — solo refactoring
- Non rimuovere `generate_css()` se serve ancora per i test, ma internamente il template usa `style.css`

---

## Milestone 22: Sistema template utente — `--template` e `--init-templates` ✅

### 22.1 Auto-setup `~/.md2/templates/default/`

Al **primo run** di `md2` (o quando `~/.md2/templates/default/` non esiste), copiare automaticamente il template bundled in `~/.md2/templates/default/`. Messaggio informativo:

```
Initialized default template in ~/.md2/templates/default/
```

Da quel momento, `md2` usa il template da `~/.md2/` — l'utente può modificarlo liberamente.

### 22.2 Flag `--template`

```
md2 file.md --template corporate
```

Carica il template da `~/.md2/templates/corporate/base.html`. Se la directory non esiste, errore chiaro:

```
Error: Template 'corporate' not found in ~/.md2/templates/corporate/
```

### 22.3 Comando `--init-templates`

```
md2 --init-templates
```

(Re)copia il template default bundled in `~/.md2/templates/default/`, sovrascrivendo. Utile dopo un aggiornamento di md2 per ottenere il template aggiornato. Avviso se la directory esiste già:

```
Default template (re)initialized in ~/.md2/templates/default/
```

### 22.4 Logica di risoluzione template

Ordine di caricamento:

1. Se `--template nome` → `~/.md2/templates/{nome}/`
2. Se esiste `~/.md2/templates/default/` → usalo
3. Altrimenti → template bundled nel pacchetto + auto-copia in `~/.md2/templates/default/`

Questo garantisce:
- Funziona sempre, anche senza setup
- L'utente ha sempre i file su disco per personalizzare
- `--template` è esplicito per template alternativi

### 22.5 Ereditarietà cross-template

Un template custom può estendere il default:

```jinja2
{% extends "default/base.html" %}

{% block css %}
<style>/* CSS completamente custom */</style>
{% endblock %}
```

Per abilitare questo, il `FileSystemLoader` deve puntare a `~/.md2/templates/` (parent), non alla directory del singolo template. Il `base.html` viene cercato nella sottocartella del template selezionato.

Configurazione Jinja2:
```python
loader = FileSystemLoader(str(Path.home() / ".md2" / "templates"))
env = Environment(loader=loader)
template = env.get_template(f"{template_name}/base.html")
```

### 22.6 Test

- Test `--init-templates` crea i file in una directory temporanea (mockare `Path.home()`)
- Test `--template nome` carica il template corretto
- Test template inesistente → errore chiaro
- Test ereditarietà: template custom che fa `{% extends "default/base.html" %}` e sovrascrive un blocco
- Test auto-setup al primo run
- Test che il default da `~/.md2/` produce output identico al bundled

---

## Milestone 23: README — documentazione sistema template ✅

### Cosa aggiungere

1. **Sezione "Template"** nel README con:
   - Spiegazione del concetto (un template = una directory con file Jinja2)
   - Struttura della directory `~/.md2/templates/`
   - Come usare `--template` e `--init-templates`

2. **Come creare un template custom**:
   - Copiare il default: `cp -r ~/.md2/templates/default ~/.md2/templates/mio-template`
   - Oppure creare da zero con `{% extends "default/base.html" %}`
   - Elenco dei `{% block %}` disponibili da sovrascrivere
   - Elenco delle variabili di contesto disponibili (`title`, `slides`, `cover`, etc.)

3. **Esempio pratico**: template "minimal" che rimuove sidebar e controlli

4. **Aggiornare la sezione "Opzioni"** con il flag `--template` e `--init-templates`

---

## M24: Frontmatter — parsing metadata del documento ✅

md2 non ha ancora supporto per il frontmatter YAML/TOML. Serve come prerequisito per il sistema palette e chart: è il punto dove l'utente dichiara `palette:` e `colors:` a livello di documento.

### 24.1 Formato supportato

Blocco TOML delimitato da `+++` all'inizio del file markdown:

```markdown
+++
title = "Report Q1 2026"
palette = "warm"
+++

# Report Q1 2026

Contenuti della presentazione...
```

Scelta TOML perché:
- `pyproject.toml` già nel progetto — coerenza
- `tomllib` nella stdlib da Python 3.11, zero dipendenze
- Per Python 3.9-3.10: aggiungere `tomli` come dipendenza (stessa API)

### 24.2 Campi supportati (fase 1)

| Campo | Tipo | Default | Descrizione |
|-------|------|---------|-------------|
| `title` | string | da `# H1` | Titolo della presentazione (override) |
| `palette` | string | `"default"` | Nome palette colori (file `.toml`) |
| `colors` | array di stringhe | — | Override inline dei colori della palette |
| `lang` | string | `"it"` | Lingua del documento |
| `dark` | bool | `false` | Dark mode di default |

### 24.3 Implementazione

**`core.py`** — nuova funzione `parse_frontmatter(markdown_text)`:

```python
def parse_frontmatter(markdown_text):
    """Extract TOML frontmatter and return (metadata_dict, remaining_markdown)."""
```

- Cerca `+++` come prima riga non-vuota del file
- Parsa il blocco tra i due `+++` come TOML
- Ritorna `(metadata, body)` — metadata è un dict, body è il markdown senza frontmatter
- Se non c'è frontmatter, ritorna `({}, markdown_text)` — backward-compatible

**`cli.py`** — `render_html()` chiama `parse_frontmatter()` prima di `prepare_context()`. I campi del frontmatter sovrascrivono i flag CLI (il frontmatter ha priorità sul default, ma il CLI ha priorità sul frontmatter? → **Il frontmatter vince sui default, il CLI vince sul frontmatter** per `lang` e `dark`).

### 24.4 Interazione con il titolo

Se `title` è nel frontmatter, viene usato al posto del `# H1` come titolo della presentazione. Il `# H1` nel markdown resta visibile nella cover slide ma non determina il `<title>` HTML.

Se `title` non è nel frontmatter, comportamento invariato (il `# H1` diventa il titolo).

### 24.5 Test

- [x] `test_no_frontmatter_backward_compat` — senza frontmatter, tutto funziona come prima
- [x] `test_frontmatter_parsed` — frontmatter TOML viene estratto correttamente
- [x] `test_frontmatter_title_override` — `title` nel frontmatter sovrascrive `# H1` nel `<title>`
- [x] `test_frontmatter_palette` — campo `palette` viene passato nel contesto
- [x] `test_frontmatter_colors` — campo `colors` viene passato nel contesto
- [x] `test_frontmatter_lang_dark` — `lang` e `dark` dal frontmatter funzionano
- [x] `test_cli_overrides_frontmatter` — `--lang en` sovrascrive `lang = "it"` nel frontmatter
- [x] `test_malformed_frontmatter` — frontmatter TOML invalido produce errore chiaro
- [x] `test_frontmatter_stripped_from_content` — il frontmatter non appare nell'HTML generato

---

## M25: Sistema palette colori — file TOML + cascata ✅

Palette colori come file TOML esterni, con meccanismo di lookup builtin → utente → frontmatter.

### 25.1 Struttura file palette

```
md2/palettes/default.toml      ← builtin, distribuita col pacchetto
md2/palettes/warm.toml
md2/palettes/cool.toml
md2/palettes/mono.toml
md2/palettes/vivid.toml
md2/palettes/pastel.toml
```

Utente:
```
~/.md2/palettes/corporate.toml   ← palette custom
~/.md2/palettes/warm.toml        ← override di una builtin
```

### 25.2 Formato file palette

```toml
name = "default"

colors = [
    "#4e79a7",
    "#f28e2b",
    "#e15759",
    "#76b7b2",
    "#59a14f",
    "#edc948",
    "#b07aa1",
    "#ff9da7",
]

[dark]
colors = [
    "#6fa0d6",
    "#f5b84c",
    "#f28e8e",
    "#9ed4cf",
    "#7ec87e",
    "#f5e08a",
    "#d4a3c7",
    "#ffb8c0",
]
```

Se la sezione `[dark]` è assente, il renderer calcola automaticamente varianti più luminose (+20% lightness in HSL) dai colori base.

### 25.3 Cascata di risoluzione

```
1. Palette builtin (md2/palettes/)
   ↓ sovrascritta da
2. Palette utente (~/.md2/palettes/)
   ↓ sovrascritta da
3. Frontmatter: palette = "nome"
   ↓ sovrascritta da
4. Frontmatter: colors = ["#...", "#..."]  (override totale o parziale)
```

Se nel frontmatter ci sono sia `palette` che `colors`:
- `palette` carica i colori base
- `colors` sovrascrive i primi N colori (merge parziale)

### 25.4 Implementazione

**`md2/palettes.py`** — nuovo modulo:

```python
BUILTIN_PALETTES_DIR = Path(__file__).parent / "palettes"
USER_PALETTES_DIR = Path.home() / ".md2" / "palettes"

def load_palette(name="default"):
    """Load palette by name. User dir takes priority over builtin."""

def resolve_colors(metadata):
    """Given frontmatter metadata, return final list of colors."""

def generate_palette_css(colors, dark_colors=None):
    """Generate CSS variables from color list."""
```

**Output CSS** generato da `generate_palette_css()`:

```css
:root {
    --md2-color-1: #4e79a7;
    --md2-color-2: #f28e2b;
    /* ... */
}
body.dark-mode {
    --md2-color-1: #6fa0d6;
    --md2-color-2: #f5b84c;
    /* ... */
}
```

Questo CSS viene iniettato nel `<style>` del template, dopo `style.css`.

**`cli.py`** — `render_html()` chiama `resolve_colors(metadata)` e passa il CSS generato nel contesto Jinja2 come variabile `palette_css`.

**`base.html`** — aggiunge:
```jinja2
{% if palette_css %}
<style>{{ palette_css }}</style>
{% endif %}
```

### 25.5 Palette builtin da creare

| Nome | Stile | Colori base (light) |
|------|-------|---------------------|
| `default` | Tableau-inspired, bilanciata | 8 colori ad alto contrasto |
| `warm` | Rossi, arancioni, gialli | Toni caldi, energia |
| `cool` | Blu, verdi, viola | Professionale, calmo |
| `mono` | Sfumature di un singolo colore (accent) | Minimalista |
| `vivid` | Saturazione alta | Impatto visivo, presentazioni |
| `pastel` | Toni morbidi, bassa saturazione | Leggibile, elegante |

### 25.6 Build e distribuzione

- Aggiungere `md2/palettes/*.toml` al package data in `pyproject.toml`
- La directory `~/.md2/palettes/` viene creata al primo uso se necessario (non al primo run come i template — le palette builtin funzionano senza copia)

### 25.7 Test

- [x] `test_load_builtin_palette` — `load_palette("default")` carica dalla dir builtin
- [x] `test_load_user_palette` — palette in `~/.md2/palettes/` ha priorità su builtin
- [x] `test_palette_not_found` — nome palette inesistente produce errore chiaro
- [x] `test_resolve_colors_default` — senza frontmatter, usa palette default
- [x] `test_resolve_colors_palette_name` — `palette = "warm"` carica la palette warm
- [x] `test_resolve_colors_inline_override` — `colors = [...]` sovrascrive
- [x] `test_resolve_colors_partial_merge` — `palette + colors` parziale = merge corretto
- [x] `test_generate_palette_css` — output CSS contiene le variabili `--md2-color-N`
- [x] `test_dark_auto_generated` — senza sezione `[dark]`, i colori dark vengono calcolati
- [x] `test_dark_explicit` — con sezione `[dark]`, i colori espliciti vengono usati
- [x] `test_palette_toml_format` — tutti i file `.toml` builtin sono validi e parsabili

---

## M26: Charts.css — embedding e direttiva `:::chart` ✅

Integrazione di Charts.css nel template e parsing della direttiva `:::chart` per trasformare tabelle markdown in grafici.

### 26.1 Embedding Charts.css

Scaricare la versione minificata di Charts.css e includerla nel template:

```
md2/templates/default/vendor/charts.min.css
```

Inclusa nel `<style>` solo quando il documento contiene almeno un chart (per non appesantire presentazioni senza grafici):

```jinja2
{% if has_charts %}
<style>{% include "vendor/charts.min.css" %}</style>
{% endif %}
```

Aggiornare `pyproject.toml` per includere la directory `vendor/` nel package data.

### 26.2 Direttiva `:::chart` — sintassi

```markdown
:::chart bar --labels --legend --stacked
| Prodotto | Q1  | Q2  | Q3  |
|----------|-----|-----|-----|
| Widget A | 50  | 80  | 65  |
| Widget B | 30  | 60  | 90  |
:::
```

Formato: `:::chart {tipo} [--opzione ...]`

**Tipi supportati:**

| Tipo | Classe Charts.css | Note |
|------|-------------------|------|
| `bar` | `.bar` | Barre orizzontali |
| `column` | `.column` | Barre verticali |
| `line` | `.line` | Grafico a linea |
| `area` | `.area` | Grafico ad area |
| `pie` | `.pie` | Torta (solo singola serie) |

**Opzioni strutturali:**

| Opzione | Effetto |
|---------|---------|
| `--labels` | Mostra etichette sugli assi |
| `--legend` | Mostra legenda (per multi-dataset) |
| `--stacked` | Barre/colonne impilate anziché affiancate |
| `--reverse` | Inverte la direzione del grafico |
| `--show-data` | Mostra i valori numerici sui dati |
| `--title "Titolo"` | Caption/titolo del grafico |

### 26.3 Implementazione — pipeline di trasformazione

Il processing avviene in due fasi, integrate nella pipeline esistente di `core.py`:

**Fase 1: Preprocessore** (prima di `markdown.markdown()`)

Nuovo in `core.py` — funzione `preprocess_chart_directives(markdown_text)`:

1. Trova tutti i blocchi `:::chart ... :::`
2. Per ogni blocco:
   - Estrae tipo e opzioni dalla prima riga
   - Estrae il contenuto markdown (la tabella)
   - Sostituisce il blocco con un marker HTML: `<div class="md2-chart" data-type="bar" data-options="labels,legend">` + tabella markdown + `</div>`
3. Ritorna il markdown modificato e un flag `has_charts`

Il markdown della tabella viene lasciato intatto — sarà `python-markdown` a parsarlo in `<table>`.

**Fase 2: Postprocessore** (dopo `markdown.markdown()` e `sanitize_html()`)

Nuovo in `core.py` — funzione `transform_charts(html_content)`:

1. Trova tutti i `<div class="md2-chart">` nel HTML
2. Per ogni div:
   - Legge `data-type` e `data-options`
   - Trova la `<table>` al suo interno
   - Trasforma la tabella nella struttura richiesta da Charts.css:
     - Aggiunge la classe `.charts-css` + classe tipo (`.bar`, `.column`, etc.)
     - Aggiunge classi opzioni (`.show-labels`, `.show-legend`, etc.)
     - Ristruttura `<td>` per aggiungere gli attributi `style="--size: ..."` richiesti da Charts.css
     - Se multi-dataset, aggiunge `--color` per serie usando le variabili `--md2-color-N`
   - Aggiunge legenda HTML se `--legend`
   - Aggiunge caption se `--title`
3. Ritorna l'HTML trasformato

**Calcolo `--size`**: Charts.css usa valori normalizzati 0-1. Il postprocessore:
- Legge tutti i valori numerici dalla tabella
- Trova il massimo
- Normalizza ogni valore: `--size: {value / max_value}`

### 26.4 Integrazione nella pipeline

In `core.py`, la funzione `process_markdown()` cambia:

```python
def process_markdown(text):
    text, has_charts = preprocess_chart_directives(text)
    raw_html = markdown.markdown(text, extensions=MD_EXTENSIONS)
    sanitized = sanitize_html(raw_html)
    autolinked = autolink(sanitized)
    if has_charts:
        autolinked = transform_charts(autolinked)
    return autolinked, has_charts
```

Nota: `process_markdown()` ora ritorna una tupla `(html, has_charts)`. Aggiornare tutti i chiamanti (`prepare_context()`, test).

`has_charts` viene propagato nel contesto Jinja2 per il conditional include del CSS Charts.css.

### 26.5 Sanitizzazione

`sanitize_html()` deve permettere i nuovi attributi:
- `data-type` e `data-options` su `<div>` — aggiungerli a `ALLOWED_ATTRIBUTES`
- `style` con `--size` e `--color` su `<td>` — già consentito via `CSSSanitizer`

Verificare che bleach non rimuova le classi `charts-css`, `bar`, `show-labels`, etc.

### 26.6 CSS aggiuntivo per i chart

In `style.css`, aggiungere stili di integrazione (non duplicando Charts.css, ma adattando al contesto md2):

```css
/* Chart wrapper */
.md2-chart {
    margin: 30px auto;
    max-width: 100%;
}

/* Chart usa i colori della palette */
.md2-chart .charts-css tbody tr:nth-child(1) td { --color: var(--md2-color-1); }
.md2-chart .charts-css tbody tr:nth-child(2) td { --color: var(--md2-color-2); }
/* ... fino a 8 */

/* Legenda styling */
.md2-chart .chart-legend {
    display: flex;
    gap: 15px;
    justify-content: center;
    margin-top: 10px;
    font-size: 0.85rem;
}

/* Dark mode compatibility */
body.dark-mode .md2-chart .charts-css {
    color: var(--text-color);
}
```

### 26.7 Test

- [x] `test_chart_directive_parsed` — `:::chart bar ... :::` viene riconosciuto
- [x] `test_chart_type_bar` — tipo `bar` produce classe `.bar`
- [x] `test_chart_type_column` — tipo `column` produce classe `.column`
- [x] `test_chart_type_line` — tipo `line` produce classe `.line`
- [x] `test_chart_type_area` — tipo `area` produce classe `.area`
- [x] `test_chart_type_pie` — tipo `pie` produce classe `.pie`
- [x] `test_chart_options_labels` — `--labels` produce classe `.show-labels`
- [x] `test_chart_options_legend` — `--legend` produce legenda HTML
- [x] `test_chart_options_stacked` — `--stacked` produce classe `.stacked`
- [x] `test_chart_options_reverse` — `--reverse` produce classe `.reverse`
- [x] `test_chart_options_show_data` — `--show-data` produce classe `.show-data-on-hover`
- [x] `test_chart_title` — `--title "..."` produce `<caption>`
- [x] `test_chart_size_normalization` — valori vengono normalizzati 0-1 correttamente
- [x] `test_chart_multi_dataset` — tabella con più colonne dati produce dataset multipli
- [x] `test_chart_colors_from_palette` — chart usa `--md2-color-N` per le serie
- [x] `test_chart_has_charts_flag` — `has_charts` è `True` solo quando ci sono chart
- [x] `test_no_charts_no_css` — senza chart, Charts.css non viene incluso nell'HTML
- [x] `test_chart_fallback_readable` — se Charts.css fallisce, la tabella resta leggibile
- [x] `test_chart_in_slide` — chart dentro una slide si renderizza correttamente
- [x] `test_multiple_charts` — più chart nella stessa presentazione funzionano
- [x] `test_chart_invalid_type` — tipo non supportato produce warning/fallback a tabella
- [x] `test_chart_non_numeric_values` — valori non numerici gestiti con errore chiaro

---

## M27: Documentazione e example — chart e palette ✅

### 27.1 README

- [x] Aggiungere sezione "Grafici" con sintassi `:::chart`, tipi supportati, opzioni
- [x] Aggiungere sezione "Palette colori" con spiegazione cascata, come creare palette custom
- [x] Aggiungere sezione "Frontmatter" con formato e campi supportati
- [x] Aggiornare sezione "Markdown supportato" con `:::chart`
- [x] Aggiornare sezione "Opzioni" con `palette` e `colors` nel frontmatter

### 27.2 Example

- [x] Aggiornare `examples/example.md` con almeno un chart (bar o column) per dimostrare la feature
- [x] Aggiungere `examples/charts.md` — showcase dedicato con tutti i tipi di chart e opzioni
- [x] Rigenerare `examples/example.html`

---

## M28: Chart sizing — altezze e dimensioni sensate per tipo ✅

Il chart rendering attuale non ha vincoli di dimensione: i grafici si espandono al 100% dello spazio disponibile. Un pie chart occupa l'intero viewport ed è inutilizzabile. Serve un sistema di sizing di default per tipo, con possibilità di override.

### 28.1 Problema

- **Pie/donut**: senza vincoli diventano enormi, illeggibili
- **Column/line/area**: occupano tutta la larghezza ma non hanno altezza definita, il risultato dipende dal contenuto
- **Bar**: l'altezza dipende dal numero di righe, serve un minimo sensato per riga
- **Tutti**: su schermi diversi il risultato è imprevedibile

### 28.2 Sizing di default per tipo

Regole CSS nel blocco `.md2-chart` in `style.css`:

| Tipo | Altezza | Larghezza | Note |
|------|---------|-----------|------|
| `bar` | auto (~40px/riga) | 100% | Cresce naturalmente con i dati |
| `column` | 250px | 100% | Altezza fissa, barre si adattano |
| `line` | 250px | 100% | Altezza fissa per leggibilità |
| `area` | 250px | 100% | Come line |
| `pie` | 200px | 200px, centrato | Quadrato, proporzionato |

Il wrapper `.md2-chart` imposta `max-width: 100%` e `margin: 30px auto` per centrare i chart.

### 28.3 Implementazione CSS

In `style.css`, specializzare le regole per tipo:

```css
.md2-chart .charts-css.bar { --labels-size: 80px; }
.md2-chart .charts-css.column { height: 250px; }
.md2-chart .charts-css.line { height: 250px; }
.md2-chart .charts-css.area { height: 250px; }
.md2-chart .charts-css.pie {
    height: 200px; width: 200px; margin: 0 auto;
}
```

### 28.4 Test

- [x] `test_chart_bar_no_fixed_height` — bar chart non ha altezza fissa nel CSS
- [x] `test_chart_column_has_height` — column chart ha height nel wrapper
- [x] `test_chart_pie_has_constrained_size` — pie chart ha height e width limitati
- [x] `test_chart_sizing_visual` — e2e: generare una presentazione con tutti i tipi di chart e verificare che l'HTML contenga le classi di sizing corrette

---

## M29: `:::columns` — layout a colonne nelle slide ✅

Le slide attuali sono single-column. Per presentazioni efficaci serve poter affiancare contenuti (testo + chart, due liste, immagine + descrizione).

### 29.1 Sintassi

```markdown
:::columns
Contenuto della colonna sinistra.

- Lista
- Di punti

---

:::chart bar --labels
| A | B |
|---|---|
| x | 50 |
:::

:::
```

- `:::columns` apre il container
- `---` separa le colonne (esattamente come il separatore slide, ma dentro `:::columns` ha significato diverso)
- `:::` chiude il container
- **Massimo 2 colonne** — nelle presentazioni, 3+ colonne sono quasi sempre illeggibili
- Se non c'è `---` → errore/fallback: tratta come singola colonna (nessun effetto)

### 29.2 Annidamento con `:::chart`

`:::chart` dentro `:::columns` funziona. Il preprocessore deve gestire l'annidamento:
- Prima processare i `:::chart` (più interni)
- Poi processare i `:::columns` (più esterni)

Oppure: usare un singolo pass che riconosce entrambi. Dato che `:::chart` è terminato da `:::` e `:::columns` anche, servono regole di disambiguazione:
- `:::chart` si chiude col primo `:::` che incontra
- `:::columns` si chiude col primo `:::` **che non fa parte di un `:::chart`** al suo interno

Approccio pratico: **processare `:::chart` prima di `:::columns`**. Dopo il preprocessamento dei chart, i blocchi `:::chart...:::` sono già stati sostituiti con `<div class="md2-chart">...</div>`. Quindi `:::columns` vede solo i marker HTML e non si confonde.

### 29.3 Implementazione

**`core.py`** — nuova funzione `preprocess_columns(markdown_text)`:

1. Trova i blocchi `:::columns ... :::`
2. Splitta il contenuto sul `---` separator
3. Wrappa ogni parte in `<div class="md2-col">`
4. Wrappa tutto in `<div class="md2-columns">`
5. Il markdown dentro ogni colonna viene processato normalmente

**Pipeline**: `preprocess_chart_directives()` → `preprocess_columns()` → `markdown.markdown()` → `sanitize_html()` → `transform_charts()`

Nota: come per i chart, il markdown dentro le colonne deve essere processato **indipendentemente** per evitare che il container HTML interferisca con il parsing markdown. Ogni colonna viene parsata separatamente con `markdown.markdown()`.

**`style.css`**:

```css
.md2-columns {
    display: flex;
    gap: 30px;
    align-items: flex-start;
    margin: 20px 0;
}
.md2-col {
    flex: 1;
    min-width: 0;
}

@media (max-width: 768px) {
    .md2-columns { flex-direction: column; }
}

@media print {
    .md2-columns { display: flex; gap: 20px; }
}
```

**Sanitizzazione**: aggiungere `md2-columns` e `md2-col` come classi consentite (già coperte dal `*: ['class']`).

### 29.4 Test

- [ ] `test_columns_directive_parsed` — `:::columns ... ::: ` viene riconosciuto
- [ ] `test_columns_two_columns` — il `---` separator produce due `.md2-col`
- [ ] `test_columns_no_separator_fallback` — senza `---`, nessun effetto colonne
- [ ] `test_columns_with_chart_inside` — `:::chart` dentro `:::columns` funziona
- [ ] `test_columns_markdown_preserved` — il markdown dentro le colonne viene parsato (bold, liste, ecc.)
- [ ] `test_columns_responsive` — CSS contiene la media query mobile
- [ ] `test_columns_in_slide_e2e` — e2e: colonne appaiono nell'HTML generato
- [ ] `test_multiple_columns_blocks` — più `:::columns` nella stessa presentazione

---

## M30: Print-optimized CSS — stampa di chart, colonne e palette ✅

Il CSS stampa attuale usa `* { color: #000 !important; background: #fff !important; }` che distrugge i colori dei chart. Serve un'ottimizzazione specifica per la stampa.

### 30.1 Problema attuale

- `* { background: #fff !important; }` → le barre dei chart diventano invisibili (bianche su bianco)
- `* { color: #000 !important; }` → le etichette perdono il colore semantico
- I chart senza colori sono inutilizzabili in stampa
- I pie chart senza riempimento colorato sono un cerchio vuoto
- Le colonne (`:::columns`) devono restare affiancate anche in stampa

### 30.2 Strategia

Invece del reset globale `* { color: #000; background: #fff }`, usare un approccio selettivo:

1. **Reset background/color** solo sugli elementi di layout (body, sidebar, slide, ecc.)
2. **Preservare** background e color sui chart (`.md2-chart`)
3. **Forzare** i colori della palette light in stampa (non quelli dark, anche se l'utente era in dark mode)
4. **Aggiungere** `-webkit-print-color-adjust: exact` e `print-color-adjust: exact` sui chart

### 30.3 Implementazione CSS

Sostituzione del blocco `@media print` in `style.css`:

```css
@media print {
    /* Layout: rimuovi UI */
    #sidebar, #theme-toggle, #menu-toggle, #progress-bar,
    #slide-indicator, #sidebar-toggle { display: none !important; }
    body { display: block; height: auto; overflow: visible; }
    #main {
        overflow: visible; padding: 0;
        scroll-snap-type: none;
    }
    .slide {
        min-height: auto; page-break-after: always;
        scroll-snap-align: none; border-bottom: none;
        padding: 20px 0; max-width: 100%;
    }
    .slide:last-child { page-break-after: avoid; }
    .cover { height: auto; page-break-after: always; }

    /* Reset colori solo su elementi di layout, NON sui chart */
    body, #main, .slide, .cover, .slide p, .slide li,
    .slide h2, .slide h3, .slide h4, .slide blockquote,
    .slide pre, .slide code, .slide a {
        color: #000 !important;
        background: #fff !important;
        box-shadow: none !important;
    }
    .slide th, .slide td {
        color: #000 !important;
        border-color: #999 !important;
    }
    .slide th { background-color: #f0f0f0 !important; }

    /* Chart: preserva colori */
    .md2-chart, .md2-chart * {
        print-color-adjust: exact !important;
        -webkit-print-color-adjust: exact !important;
    }

    /* Chart: usa colori light anche se era dark mode */
    .md2-chart .charts-css {
        color: #000;
    }

    /* Colonne: mantieni layout affiancato */
    .md2-columns { display: flex; gap: 20px; }

    /* Evita page break dentro un chart o un columns */
    .md2-chart, .md2-columns {
        break-inside: avoid;
        page-break-inside: avoid;
    }
}
```

### 30.4 Palette in stampa

In stampa la palette light viene sempre usata (anche se il documento è in dark mode). Questo avviene naturalmente perché la regola `body.dark-mode` non si applica — il reset CSS rimuove la classe. Ma dobbiamo verificare che le variabili `--md2-color-N` del `:root` (light) siano effettivamente usate dai chart in stampa.

### 30.5 Test

- [x] `test_print_css_no_global_reset` — il CSS di stampa non usa `* { color: #000 }`
- [x] `test_print_css_chart_colors_preserved` — il blocco print contiene `print-color-adjust: exact`
- [x] `test_print_css_chart_break_avoid` — i chart hanno `break-inside: avoid`
- [x] `test_print_css_columns_preserved` — le colonne restano flex in stampa
- [x] `test_print_css_layout_elements_reset` — body, slide, ecc. hanno reset colori
- [x] `test_print_visual_e2e` — e2e: l'HTML generato con chart contiene le regole di stampa corrette

---

## M31: Documentazione e example — columns, sizing, stampa ✅

### 31.1 README

- [x] Aggiungere sezione "Layout a colonne" con sintassi `:::columns`, esempio con chart
- [x] Aggiornare sezione "Interfaccia generata" con nota su stampa chart-friendly
- [x] Aggiornare sezione "Grafici" con nota su sizing automatico per tipo

### 31.2 Example

- [x] Aggiornare `examples/example.md` con almeno un uso di `:::columns` (testo + chart affiancati)
- [x] Rigenerare `examples/example.html`

---

## M32: Bugfix — colori pie chart e sizing responsivo ✅

### 32.1 Bug: pie chart senza colori

**Sintomo**: il pie chart appare come cerchio grigio senza colori per le fette.

**Causa**: le regole CSS per i colori palette usano `tr:nth-child(N) td` che funziona per bar/column (una `<td>` per riga = una barra). Ma nel pie chart, Charts.css tratta ogni `<td>` come una fetta — il colore va applicato diversamente. La struttura HTML generata da `transform_charts` ha una riga per fetta (corretto), ma il selettore potrebbe non applicarsi al pie perché Charts.css per i pie usa un meccanismo di rendering diverso (conic-gradient sulle `<td>`).

**Investigazione necessaria**:
- Verificare come Charts.css applica i colori nel pie: usa `--color` su `<td>`, su `<tr>`, o con `--color-N` sulle classi?
- Verificare che il nostro HTML generato per il pie abbia la struttura corretta per Charts.css
- Verificare che `--color` venga effettivamente settata e non sovrascritta

**Fix**: adattare le regole CSS e/o la generazione HTML per il pie.

### 32.2 Bug: pie sizing 200x200px troppo piccolo e non responsivo

**Sintomo**: su schermi grandi il pie chart a 200x200px è minuscolo e sproporzionato.

**Fix**: usare dimensionamento relativo al container, non fisso:
- Dentro `:::columns` (flex child): il pie si adatta alla colonna
- Standalone: il pie occupa una dimensione ragionevole (es. `min(300px, 100%)`)
- Usare `aspect-ratio: 1` per mantenere il quadrato senza fissare pixel

### 32.3 Test

- [x] `test_pie_chart_has_colors` — il pie chart renderizzato ha `--color` applicato alle fette
- [x] `test_pie_responsive_sizing` — il CSS del pie usa unità relative o aspect-ratio, non px fissi
- [x] `test_pie_in_columns_renders` — pie dentro :::columns ha dimensioni ragionevoli
- [x] `test_all_chart_types_have_colors` — ogni tipo di chart ha colori dalla palette

---

## M33: Refactor `:::columns` — sintassi `:::col` e fix pipeline ✅

**Why:** Il `---` dentro `:::columns` viene mangiato dal slide splitter in `prepare_context()` prima che `preprocess_columns` lo veda. Le columns non funzionano mai in pratica. Inoltre il `---` è semanticamente un thematic break, non un separatore di colonna.

**Approach:** Cambiare la sintassi a `:::col` esplicito per demarcare le colonne. Il preprocessor `preprocess_columns` cerca `:::columns ... :::col ... :::` e splitta su `:::col`. Nessun conflitto con `---` (slide separator) né con `:::chart`. L'ordine di processing nella pipeline resta: chart → columns → markdown → sanitize → transform.

Nuova sintassi:
```markdown
:::columns

:::col
Testo a sinistra.

:::col
Contenuto a destra.

:::
```

**Tasks:**
- [x] Aggiornare regex `_COLUMNS_DIRECTIVE_RE` per matchare `:::columns ... :::`
- [x] Aggiornare `preprocess_columns()` per splittare su `:::col` invece di `---`
- [x] Aggiornare tutti i test in `test_columns.py`
- [x] Aggiornare `examples/example.md` con la nuova sintassi
- [x] Aggiornare README sezione "Layout a colonne"
- [x] Test: unit — colonne con `:::col`, annidamento con chart, fallback senza `:::col`
- [x] Test: e2e — colonne renderizzate correttamente nell'HTML
- [x] Commit & push

**Done when:** `:::columns` con `:::col` produce due colonne affiancate nell'HTML generato, senza conflitto con il separatore slide `---`.

---

## M34: Chart sizing responsivo con unità viewport ✅

**Why:** I chart sono troppo piccoli su schermi grandi. 280px max-width per pie e 250px height per column/line/area non si adattano al viewport. Su un monitor 1440p il chart occupa un angolino della slide.

**Approach:** Usare unità viewport nel CSS per sizing proporzionato:
- Pie: `max-width: min(50vh, 50vw); aspect-ratio: 1` — si adatta al viewport mantenendo il cerchio
- Column/line/area: `height: min(300px, 40vh)` — minimo 300px o 40% del viewport, quale è minore
- Bar: invariato (auto, cresce con le righe)
- Dentro `:::columns` (flex child): i chart si adattano alla colonna naturalmente

**Tasks:**
- [x] Aggiornare CSS sizing per pie con `min(50vh, 50vw)`
- [x] Aggiornare CSS sizing per column/line/area con `min(300px, 40vh)`
- [x] Aggiornare test `test_chart_sizing.py` e `test_pie_bugfix.py` per le nuove regole
- [x] Rigenerare `examples/example.html`
- [x] Aggiornare README tabella dimensioni
- [x] Commit & push

**Done when:** I chart si ridimensionano proporzionalmente al viewport su schermi di diverse dimensioni.

---

## M35: Fix normalizzazione valori chart e gestione zero ✅

**Why:** La normalizzazione dei valori usa il max globale su tutte le colonne dati. Dati con scale diverse (Deploy/week=2-12 vs Uptime=99-100) producono barre invisibili (`--size: 0.02`). Inoltre `--size: 0` produce barre vuote con label "0" flottante nel vuoto.

**Approach:** In `transform_charts()` in `core.py`, cambiare la normalizzazione: per multi-dataset, normalizzare per colonna (ogni dataset ha il suo max). Per singolo dataset resta invariato. Per valori zero: non generare il `<span class="data">` quando il valore è 0, così Charts.css non mostra label flottanti. La normalizzazione per-colonna richiede ristrutturare il ciclo in `_transform_chart`: prima raccogliere i max per colonna, poi generare `--size` relativo al max della colonna.

**Tasks:**
- [x] Ristrutturare normalizzazione in `transform_charts()` per usare max per-colonna nei multi-dataset
- [x] Sopprimere `<span class="data">` per valori zero
- [x] Test: unit — multi-dataset con scale diverse produce --size ragionevoli (nessuno < 0.1 se il dato è significativo)
- [x] Test: unit — valore zero non genera span.data
- [x] Test: unit — singolo dataset normalizzazione invariata
- [x] Rigenerare example e verificare con Playwright
- [x] Commit & push

**Done when:** Nel bar chart multi-dataset Deploy/week (2→12) produce barre visibili e proporzionate all'interno della propria serie, non schiacciate dal max di Uptime (100).

---

## M36: Fix CSS — bar height, line visibility, label spacing ✅

**Why:** I bar chart sono schiacciati (nessuna altezza minima per riga). Il line chart è una striscia sottile (la linea è troppo fine). Le label si troncano su testi lunghi. I valori `show-data` si sovrappongono.

**Approach:** Modifiche CSS in `style.css`:
1. **Bar min-height per riga**: aggiungere `min-height: 40px` alle `<tr>` del bar chart, così ogni riga ha spazio sufficiente
2. **Line thickness**: settare `--line-size: 3px` per rendere le linee visibili
3. **Labels size**: aumentare `--labels-size` a `100px` per label più lunghe, con `text-overflow: ellipsis` come fallback
4. **Data overlay**: settare `--data-spacing` per distanziare i valori dalle barre
5. **Area chart**: come line, verificare che le aree abbiano spessore visibile

Tutte le modifiche sono solo CSS — nessun cambiamento alla logica Python.

**Tasks:**
- [x] Aggiungere min-height per riga nei bar chart
- [x] Settare --line-size per line e area chart
- [x] Aumentare --labels-size e aggiungere text-overflow
- [x] Settare --data-spacing per show-data
- [x] Test: unit — CSS contiene le nuove regole
- [x] Rigenerare example e verificare tutti i chart con Playwright
- [x] Commit & push

**Done when:** Tutti e 6 i chart nell'example sono visivamente leggibili: barre con altezza adeguata, linee visibili, label non troncate, valori non sovrapposti.

---

## M37: Chart visual polish — cornice, padding, colore testo dati ✅

**Why:** I chart flottano nel vuoto senza cornice visiva. I numeri dentro le barre sono incollati al bordo e il testo nero è illeggibile su barre scure (es. "62" nero su blu `#4e79a7`).

**Approach:** Modifiche CSS in `style.css`:
1. **Cornice**: aggiungere al wrapper `.md2-chart` lo stesso trattamento visivo delle tabelle — `border-radius: 8px`, `box-shadow`, `overflow: hidden`, e un padding interno
2. **Padding**: aggiungere padding al wrapper `.md2-chart` per dare respiro al contenuto e impedire che i valori escano dal contenitore
3. **Colore testo dati**: i `.data` dentro i chart diventano bianchi con `text-shadow` per contrasto su qualsiasi colore di barra. In dark mode resta bianco (funziona su entrambi i temi).

Tutte le modifiche sono solo CSS — nessun cambiamento alla logica Python.

**Tasks:**
- [x] Aggiungere box-shadow e border-radius al wrapper `.md2-chart`
- [x] Aggiungere padding interno al wrapper
- [x] Settare color: #fff e text-shadow sui `.data` span dentro i chart
- [x] Verificare dark mode — il bianco funziona anche su sfondo scuro
- [x] Test: unit — CSS contiene le nuove regole
- [x] Rigenerare example e verificare con Playwright
- [x] Commit & push

**Done when:** I chart hanno una cornice visiva coerente con le tabelle, i numeri hanno spazio e sono leggibili su qualsiasi colore di barra.

---

## M38: Chart CSS refinement — padding barre, caption, padding wrapper, legenda ✅

**Why:** I numeri dentro le barre sono incollati al bordo destro. Il wrapper ha troppo padding-top. La legenda ha un bordo/box indesiderato da Charts.css. I chart con `<caption>` non hanno uno stile coerente con gli header delle tabelle.

**Approach:** Modifiche CSS in `style.css`:
1. **Padding dentro le barre**: `padding-right` sulle `<td>` dei chart per distanziare i numeri dal bordo
2. **Caption come header tabella**: stilizzare `<caption>` con sfondo grigio chiaro, font bold, padding — stessa estetica dell'header delle tabelle normali
3. **Padding wrapper asimmetrico**: ridurre `padding-top` e tenere più padding sui lati/basso
4. **Legenda senza bordo**: rimuovere border/outline dalla `<ul>` legenda che Charts.css aggiunge di default

**Tasks:**
- [x] Aggiungere padding-right alle td dei chart
- [x] Stilizzare caption come header tabella
- [x] Rendere padding wrapper asimmetrico (meno top)
- [x] Rimuovere bordo dalla legenda
- [x] Test: unit — CSS contiene le nuove regole
- [x] Rigenerare example e verificare con Playwright
- [x] Commit & push

**Done when:** I numeri dentro le barre hanno respiro, la caption ha stile header, il wrapper non ha spazio vuoto eccessivo in alto, la legenda è pulita senza bordi.

---

## M39: Chart API semplificata — rimuovere opzioni, auto-defaults ✅

**Why:** L'utente deve scrivere solo markdown (tipo + dati), nessuna conoscenza di rendering. Filosofia LaTeX: separazione netta tra contenuto e presentazione. Le opzioni attuali (`--labels`, `--legend`, `--show-data`, `--stacked`, `--title`) violano questo principio — l'utente non dovrebbe decidere queste cose.

**Approach:** Rimuovere tutte le opzioni dalla direttiva `:::chart`. La sintassi diventa `:::chart TIPO` + tabella + eventuale `### Title` heading dentro il blocco. I tipi supportati aumentano per coprire le vecchie opzioni semanticamente: `stacked-bar` e `stacked-column` diventano tipi propri. Auto-applicazione:

- **Labels**: sempre on (altrimenti chart illeggibile)
- **Legend**: on se multi-dataset (altrimenti non si capisce)
- **Show-data**: on per `bar`, `column`, `pie`, `stacked-bar`, `stacked-column`; off per `line`, `area` (troppo rumore)
- **Title**: rilevato come primo `### H3` o `## H2` dentro il blocco chart
- **Stacked**: tipo esplicito `stacked-bar` / `stacked-column`, non flag

Modifiche in `core.py`: `_VALID_CHART_TYPES` estesi, `_parse_chart_options` rimosso/sostituito, regex `_CHART_DIRECTIVE_RE` semplificata (nessuna opzione), rilevamento heading-as-title nel preprocessore, auto-options in `transform_charts`.

**Tasks:**
- [x] Estendere `_VALID_CHART_TYPES` con `stacked-bar` e `stacked-column`
- [x] Rimuovere parsing opzioni da `preprocess_chart_directives` (semplificare la regex)
- [x] Rilevare `### Title` come prima riga non-vuota del blocco (se presente)
- [x] In `transform_charts`: auto-apply labels, legend (se multi-dataset), show-data (per tipo), stacked (se tipo `stacked-*`)
- [x] Mapping: `stacked-bar` → classi `bar stacked`, `stacked-column` → `column stacked`
- [x] Aggiornare tutti i test esistenti per la nuova sintassi
- [x] Aggiornare `examples/example.md` (rimuovere opzioni)
- [x] Aggiornare README sezione "Grafici" con nuova sintassi semplificata
- [x] Test: unit — auto-labels/legend/show-data per tipo
- [x] Test: unit — heading dentro chart viene estratto come titolo
- [x] Test: unit — `stacked-bar` produce classi `bar stacked`
- [x] Commit & push

**Done when:** `:::chart TIPO` + tabella (+ opzionale `### Title`) produce un chart completo e leggibile senza che l'utente abbia specificato nessuna opzione.

---

## M40: Title styling come intestazione di card ✅

**Why:** Il titolo del chart (rilevato dal heading) deve apparire graficamente come l'intestazione di una card — simile all'header di una tabella. Deve essere chiaramente "il titolo di quest'oggetto".

**Approach:** Nel `transform_charts`, il titolo rilevato diventa un `<div class="md2-chart-title">` inserito come primo child del wrapper `.md2-chart`, prima della tabella. CSS: sfondo `--table-header-bg`, font bold, padding, border-radius in alto coerente col wrapper.

Non usiamo `<caption>` della tabella perché: (1) Charts.css ha regole specifiche su caption, (2) vogliamo stile controllato, (3) semanticamente il titolo appartiene alla card, non alla tabella interna.

**Tasks:**
- [x] Generare `<div class="md2-chart-title">` nel transform quando c'è un titolo
- [x] CSS: styling .md2-chart-title con sfondo header, bold, padding, border-radius top
- [x] Adattare padding wrapper per non duplicare spazio quando c'è il titolo
- [x] Rimuovere vecchio styling `.md2-chart caption` (ora non usato)
- [x] Test: unit — titolo presente genera div con classe e testo corretti
- [x] Test: unit — senza titolo non appare il div
- [x] Rigenerare example e verificare con Playwright
- [x] Commit & push

**Done when:** Chart con titolo mostra un header bandeggio in alto, visivamente coerente con gli header delle tabelle.

---

## M41: Chart spacing — gap label/bars, row/group spacing, legend positioning ✅

**Why:** Nei multi-dataset le label degli assi sono attaccate alle barre, le righe (bar) o gruppi (column) sono attaccate tra loro rendendo difficile distinguere elementi separati, e la legenda si sovrappone alle label degli assi.

**Approach:** CSS su `style.css`:
1. **Gap label/bars**: aumentare `--labels-size` o aggiungere `padding-right` ai label cells
2. **Row spacing (bar)**: `--data-spacing` tra `<tr>` del bar
3. **Group spacing (column)**: spacing tra gruppi di colonne tramite `--data-spacing` orizzontale
4. **Legend margin**: `margin-top` sufficiente per stare sotto le label degli assi

Tutti CSS, nessuna logica Python.

**Tasks:**
- [x] Aumentare gap tra label e barre nel bar chart
- [x] Settare spacing verticale tra righe del bar chart
- [x] Settare spacing orizzontale tra gruppi del column chart
- [x] Legend con margin-top adeguato
- [x] Test: unit — CSS contiene le nuove regole di spacing
- [x] Rigenerare example e verificare con Playwright
- [x] Commit & push

**Done when:** Nei chart multi-dataset le label sono distanziate dalle barre, le righe/gruppi sono visibilmente separati, la legenda non si sovrappone.

---

## M42: Fix `.data` color per tipo — bianco dentro, colore testo fuori ✅

**Why:** Il testo `.data` è attualmente bianco per tutti i chart. Funziona per bar/pie (testo dentro barra/fetta colorata), ma produce bianco-su-bianco per column/line/area dove il testo è posizionato sopra/fuori dall'elemento colorato.

**Approach:** CSS specializzato per tipo. Charts.css posiziona `.data`:
- **Dentro segmenti colorati** (bar, pie, stacked-bar, stacked-column) → testo bianco con text-shadow
- **Sopra barre/punti** (column, line, area) → testo colore normale (var(--text-color)) senza ombra

Separare le regole CSS per tipo, rimuovere la regola generica `.md2-chart .data`.

**Tasks:**
- [x] Rimuovere regola generica `.md2-chart .data`
- [x] Aggiungere regola per `.bar .data`, `.pie .data`, `.stacked-bar .data`, `.stacked-column .data` (bianco + shadow)
- [x] Aggiungere regola per `.column .data`, `.line .data`, `.area .data` (colore normale)
- [x] Test: unit — CSS contiene regole separate per tipo
- [x] Rigenerare example e verificare con Playwright
- [x] Commit & push

**Done when:** I numeri sono leggibili in tutti i tipi di chart: bianchi dentro le barre, colore normale quando fuori.

---

## M43: Fix line chart ultimo valore invisibile ✅

**Why:** Nel line chart con 4 punti, il 4° valore (25000 nell'example) non appare visibile. La linea sembra fermarsi al 3° punto e il numero è nel vuoto.

**Approach:** Investigare le cause possibili:
1. Il punto al 100% è clippato dal container (overflow hidden sul wrapper)
2. Charts.css non renderizza l'ultima interpolazione
3. Normalizzazione errata (max_val troppo basso)
4. Padding del wrapper taglia l'ultimo elemento

Dopo investigazione, applicare il fix appropriato. Probabili candidati: aumentare padding-top del chart area, rimuovere `overflow: hidden` dal wrapper per i line/area chart, o aggiungere `padding-inline` specifico per line.

**Tasks:**
- [x] Riprodurre il bug con Playwright (screenshot + HTML ispezionato)
- [x] Identificare la causa (CSS clipping vs normalizzazione vs Charts.css)
- [x] Applicare il fix minimo che risolve il problema
- [x] Test: unit — line chart con 4+ punti mostra tutti i valori
- [x] Rigenerare example e verificare visivamente
- [x] Commit & push

**Done when:** Il line chart mostra tutti i punti inclusi il primo e l'ultimo, con valori leggibili.

---

## M44: Example showcase completo — tutti i tipi di chart ✅

**Why:** L'example attuale non usa tutti i tipi/combinazioni. Per dimostrare la feature e come test visivo di regressione, l'example deve coprire tutti i casi d'uso.

**Approach:** Espandere `examples/example.md` aggiungendo slide o chart per coprire:
- `bar` singola serie
- `bar` multi-dataset (già presente)
- `column` singola serie
- `column` multi-dataset (già presente)
- `stacked-bar`
- `stacked-column`
- `line` singola serie (già presente)
- `line` **multi-dataset** (nuovo — per mostrare più linee sovrapposte)
- `area` singola serie (già presente)
- `pie` (già presente)

Ogni chart con un titolo `### H3` per mostrare il rendering del titolo. I chart sono in contesti realistici nella presentazione (non una "galleria").

**Tasks:**
- [x] Aggiungere line chart multi-dataset (es. user growth per segmento)
- [x] Aggiungere stacked-bar chart (es. breakdown costi)
- [x] Aggiungere stacked-column chart (es. revenue per categoria nel tempo)
- [x] Assicurare che ogni chart abbia un `### Titolo`
- [x] Rigenerare `examples/example.html`
- [x] Verificare tutti i chart con Playwright
- [x] Commit & push

**Done when:** L'example contiene almeno un chart per ogni tipo supportato (inclusi stacked e line multi-dataset), tutti con titolo visualizzato.

---

## M45: Normalizzazione globale chart (rollback M35) ✅

**Why:** La normalizzazione per-riga introdotta in M35 rende ogni metrica self-comparable ma confonde l'utente perché due dataset sulla stessa scala visiva rappresentano valori molto diversi (Test Coverage 62 e Uptime 99 appaiono quasi uguali). L'utente preferisce la normalizzazione globale (scala comune) anche se metriche con range molto diverso producono barre piccole per i valori bassi — la scelta delle metriche da mettere insieme è responsabilità di chi scrive il markdown.

**Approach:** Ripristinare la normalizzazione globale in `transform_charts()`: un unico `max_val` su tutti i valori del chart, tutti i `--size` relativi a quello. Rimuovere `row_maxes` e la logica per-riga. Aggiornare `test_chart_normalization.py` di conseguenza.

**Tasks:**
- [x] Rimuovere `row_maxes` e normalizzazione per-riga da `transform_charts`
- [x] Tutti i `--size` usano `max_val` globale
- [x] Aggiornare test M35 per riflettere il nuovo comportamento
- [x] Test: unit — normalizzazione globale produce scala comune
- [x] Commit & push

**Done when:** Multi-dataset chart mostra tutte le barre sulla stessa scala globale (100% = max globale del chart).

---

## M46: Fix spacing verticale bar multi-dataset ✅

**Why:** Nel bar chart multi-dataset le righe logiche (metriche diverse) sono attaccate tra loro — non c'è spazio tra "Deploy/week" e "Test Coverage". `--data-spacing: 6px` del bar non produce il gap atteso perché Charts.css lo interpreta come spacing tra le barre DENTRO una riga (multi-dataset), non tra righe.

**Approach:** Investigare come Charts.css gestisce lo spacing tra righe in un bar multi-dataset. Probabilmente serve `padding-block` o `border-spacing` sulla table, oppure margin-bottom sulle `<tr>`. Applicare il fix CSS che produce spazio visibile tra metriche.

**Tasks:**
- [x] Investigare il CSS di Charts.css per `.bar.multiple` row spacing
- [x] Applicare il fix (margin/padding/border-spacing sulle tr o tbody)
- [x] Test: unit — CSS contiene la nuova regola di spacing tra righe
- [x] Verificare con Playwright
- [x] Commit & push

**Done when:** Nel bar chart multi-dataset c'è uno spazio visibile tra le metriche diverse.

---

## M47: Fix label verticale allineamento multi-dataset ✅

**Why:** Nel bar multi-dataset la label della riga (es. "Deploy/week") è allineata alla PRIMA barra del gruppo, non al centro del gruppo. Visivamente si legge come label della prima barra, non della coppia.

**Approach:** Charts.css posiziona le label a sinistra con `--labels-size`. L'allineamento verticale del testo nella label cell deve essere `center` rispetto alla riga completa (che contiene multiple barre). Fix CSS sulla `th` di label.

**Tasks:**
- [x] Aggiungere `vertical-align: middle` o flex centering sulle label cells del bar multi-dataset
- [x] Test: unit — CSS contiene la regola
- [x] Verificare con Playwright
- [x] Commit & push

**Done when:** Nel bar multi-dataset la label è centrata verticalmente rispetto al gruppo di barre.

---

## M48: Fix padding wrapper dopo il titolo ✅

**Why:** Dopo il titolo del chart c'è un doppio spazio bianco: il titolo ha `margin-bottom: 16px` e il wrapper ha `padding: 8px 20px 20px`. Risultato: troppo spazio prima che iniziino le barre.

**Approach:** Ridurre o rimuovere il margin-bottom del titolo (il wrapper padding è già sufficiente), oppure usare `padding: 0 20px 20px` sul wrapper quando c'è un titolo (ma questo è complicato). Soluzione più semplice: `margin-bottom: 0` sul titolo, il wrapper padding-top 0 quando c'è titolo via selettore adiacente. In alternativa: rimuovere `margin-bottom` e il wrapper ha già padding sufficiente.

**Tasks:**
- [x] Ridurre margin-bottom del title a 0 o valore minimo
- [x] Se necessario, usare selettore adiacente per ridurre padding-top del wrapper quando c'è title
- [x] Test: unit — regola CSS corretta
- [x] Verificare con Playwright (spazio ridotto dopo il titolo)
- [x] Commit & push

**Done when:** Lo spazio tra il titolo e l'inizio delle barre è ridotto a un gap ragionevole (~8-12px).

---

## M49: Fix legend — spacing e bullet colore ✅

**Why:** Due problemi nella legend: (1) troppo spazio bianco tra l'ultima barra e la legend, (2) i bullet prima dei label sono neri sottili invece che nei colori della palette (blu/arancione/ecc).

**Approach:**
1. **Spacing**: ridurre `margin-top` della legend (ora 24px, troppo)
2. **Bullet colorati**: Charts.css usa `legend-circle` / `legend-square` / ecc. come classi per la forma. Per i colori, le `<li>` devono avere una regola `::before` con `background: var(--color-N)`. Generare nel transform_charts le classi sui `<li>` (es. `.legend-item-1`, `.legend-item-2`) e aggiungere CSS per applicare i colori della palette.

**Tasks:**
- [x] Ridurre margin-top della legend (es. 12px)
- [x] In `transform_charts`, aggiungere classi numerate ai `<li>` della legend
- [x] CSS: regole per i bullet colorati con var(--md2-color-N)
- [x] Test: unit — legend html contiene classi numerate
- [x] Test: unit — CSS contiene regole per bullet colorati
- [x] Verificare con Playwright
- [x] Commit & push

**Done when:** La legend è vicina al chart e i bullet mostrano i colori della palette corrispondenti alle serie dati.

---

## M50: Fix bar row gap — non usare border-spacing con flex tr ✅

**Why:** Nel bar chart multi-dataset le righe di metriche diverse sono attaccate (y=827, 867, 907 — differenze di 40 = altezza riga, zero gap). `border-spacing: 0 10px` non funziona perché Charts.css applica layout flex alle `<tr>` del bar chart (margin-inline-start: var(--labels-size)), rendendo inefficace il border-spacing del table.

**Approach:** Applicare `margin-top: 12px` alle `.bar tbody tr:not(:first-child)` (o gap su tbody se è flex container). Rimuovere `border-spacing` che non produce effetto.

**Tasks:**
- [x] Rimuovere `border-spacing: 0 10px` da `.charts-css.bar`
- [x] Aggiungere `.bar tbody tr:not(:first-child) { margin-top: 12px }` o equivalente
- [x] Test: unit — CSS contiene margin-top su tr:not(:first-child)
- [x] Verificare con Playwright che le righe siano visibilmente separate
- [x] Commit & push

**Done when:** Le metriche diverse del bar multi-dataset hanno uno spazio visibile tra di loro (gap ≥ 10px).

---

## M51: Fix column chart gap e larghezza colonne ✅

**Why:** Nel column chart con poche categorie (3-4), ogni colonna occupa 1/N della larghezza totale (es. 280px ciascuna con 3 colonne), senza gap. Risultato: barre enormi attaccate tra loro, visivamente brutte. Il `--data-spacing: 16px` che avevo settato NON funziona perché Charts.css riconosce solo le classi `.data-spacing-N`, non la variabile direttamente.

**Approach:** Aggiungere `padding-inline` alle `.column tbody tr` per creare gap visivi. Charts.css rispetta il padding del tr (la barra è renderizzata tramite td::before dentro il tr, e il padding spinge il contenuto verso l'interno). Tipicamente `padding-inline: 2-5%` o un valore fisso tipo `20px` per lato.

Alternativa: settare `max-width: 600px` o simile sul `.column` per evitare che le colonne si allarghino troppo quando sono poche.

**Tasks:**
- [x] Sperimentare con padding-inline su .column tr e verificare con Playwright
- [x] Trovare un valore che produce gap visibile senza rompere il caso con molte colonne
- [x] Considerare max-width limitata per column chart
- [x] Test: unit — CSS contiene regole di spacing colonne
- [x] Verificare visualmente con 3, 4, 6 categorie
- [x] Commit & push

**Done when:** Nel column chart con 3-4 categorie, le colonne hanno larghezza ragionevole e gap visibili tra loro.

---

## M52: Fix legend positioning — sotto x-axis labels ✅

**Why:** Nelle slide column, line multi-dataset, e altri chart con show-labels sotto, la legenda si sovrappone alle label dell'asse x ("Growth" overlaps with "ML Specialists", "Q3" overlaps with "Enterprise"). Questo perché la legenda viene messa subito sotto la tabella ma le label dell'asse x occupano uno spazio in basso dentro la tabella.

**Approach:** Aumentare il `margin-top` della legenda a un valore che lasci spazio alle label dell'asse x. Investigare con Playwright lo spazio effettivo delle label per settare un margine sicuro (es. 40px). In alternativa, forzare display: block sulla legend con clear: both.

**Tasks:**
- [x] Investigare con Playwright la posizione delle x-axis labels
- [x] Aumentare margin-top legend a valore sicuro (probabilmente 32-48px)
- [x] Verificare che non sia troppo per bar chart (label a sinistra, non sotto)
- [x] Considerare selettori specifici: bar legend vs column/line legend
- [x] Test: unit — CSS contiene margin adeguato
- [x] Verificare con Playwright tutti i chart multi-dataset
- [x] Commit & push

**Done when:** La legenda non si sovrappone mai alle label dell'asse x in nessun tipo di chart.

---

## M53: Fix pie chart — rotazione label illeggibile ✅

**Why:** Nel pie chart le label dei valori ("24", "82") sono ruotate di 90° (scritte verticali) e illeggibili. Charts.css ruota le label per farle stare dentro le fette, ma questo è pessimo per numeri brevi.

**Approach:** Override CSS per le `.data` span dentro `.pie`: rimuovere la rotazione (`transform: none` o `rotate(0)`) e posizionare il testo al centro della fetta. Charts.css applica `transform: rotate(...)` sugli span per seguire l'angolo — noi lo annulliamo e usiamo posizionamento statico.

**Tasks:**
- [x] Investigare con Playwright come Charts.css posiziona le label pie
- [x] Trovare override CSS per fermare la rotazione
- [x] Posizionamento centrale leggibile
- [x] Test: unit — CSS contiene override rotazione pie
- [x] Verificare visualmente pie chart
- [x] Commit & push

**Done when:** I numeri nelle fette del pie chart sono leggibili orizzontalmente.

---

## M54: Line/area chart — rendere leggibili i valori ✅

**Why:** Il line chart "Projected User Growth" è inutile: non si vedono né assi Y né valori dei punti né scale. L'utente non può dedurre se 25000 è alto o basso. Stesso problema per area chart. La decisione precedente di non mostrare `.data` per line/area era basata su "troppo rumore" ma ha reso il chart inutilizzabile.

**Approach:** Tre opzioni:
1. **Mostrare sempre i valori** (come bar/column) — semplice, leggibile, ma può essere visivamente affollato su molti punti
2. **Mostrare solo primo e ultimo valore** — indica range (da X a Y)
3. **Tooltip on hover** — interactive, ma richiede JS
4. **Asse Y visibile** — Charts.css ha `.show-primary-axis` e `.show-secondary-axes` — mostra linee di riferimento con valori

La soluzione migliore per uso presentazione è **opzione 1** (sempre valori) come default. Il "rumore" di avere i numeri è preferibile a "non capire il chart". Per line, posizioniamo le label sopra i punti con un piccolo background per leggibilità.

**Tasks:**
- [x] Rimuovere `_CHART_TYPES_NO_DATA` — tutti i tipi mostrano dati
- [x] Per line/area: CSS per posizionare le label sopra i punti
- [x] Applicare background/shadow ai label per leggibilità su sfondo grafico
- [x] Test: unit — line chart HTML contiene `<span class="data">`
- [x] Test: unit — CSS contiene styling label per line/area
- [x] Rigenerare example e verificare con Playwright
- [x] Commit & push

**Done when:** Line e area chart mostrano sempre i valori sui punti in modo leggibile.

---

## M55: X-axis labels troncate (column, area, pie) ✅

**Why:** Nelle colonne "Visitor/Signup/Activation/Paid" le label sono troncate (si vede solo "Visitee", "Signup", "Activation", "Paid") perché sono ruotate o tagliate dal padding del wrapper. Stesso problema per area chart "00:00/04:00/..." dove le label sono troncate alla base. Nel pie chart le label delle fette sono scritte ruotate (non x-axis, ma correlato).

**Approach:** Investigare se Charts.css ruota le label x-axis per default e trovare come evitarlo. Forse serve aumentare `--labels-size` per column/line/area, o il padding-bottom del wrapper per dare spazio alle label sotto.

**Tasks:**
- [x] Investigare con Playwright posizione e rotazione delle x-axis labels
- [x] Applicare fix CSS (padding bottom, whitespace, etc)
- [x] Test: unit — CSS corretto
- [x] Verificare con Playwright column, line, area
- [x] Commit & push

**Done when:** Tutte le label dell'asse x sono leggibili e non troncate in tutti i chart.

---

## M56: Reduce `--labels-size` per column ✅

**Why:** Nel column chart `--labels-size: 100px` riserva 100px sotto le barre per le label. Le label sono testo singolo (~20px alto) → 80px di whitespace tra fine barra e label. Risultato: le label "Core/Growth/Intelligence" sembrano staccate dalle barre (image #14), e la legend è subito sotto le label (4px, troppo poco) perché la legend margin parte dopo i 100px riservati.

**Approach:** Ridurre `--labels-size` per column da 100px a 32px. Le label restano leggibili (text ~20px + padding 6px sopra/sotto), il whitespace eccessivo scompare, la legend mantiene il suo gap di 40px ma ora visivamente più vicino al chart.

Per il bar chart `--labels-size: 130px` è la WIDTH (label a sinistra), va lasciato.
Per line/area è già 24px (default Charts.css), va bene.

**Tasks:**
- [x] Cambiare `--labels-size` di `.charts-css.column` da 100px a 32px
- [x] Verificare visualmente con Playwright (Team Allocation, Q1 Conversion)
- [x] Test: unit — CSS contiene labels-size: 32px per column
- [x] Commit & push

**Done when:** Nelle colonne le label sono vicine alle barre (gap ≤ 16px), e la legend ha il suo spazio normale sotto le label.

---

## M57: Top padding per line/area chart area (anti-clipping max value) ✅

**Why:** Nel line/area chart il valore massimo (`--size: 1`) ha la label posizionata al top del chart area senza margine. Il bordo superiore della label (background pill) si estende fino al limite del chart, e visivamente sembra "tagliato" dal bordo o dal title bar (image #15 "50", image #16 "25000"). Misurato: in slide-8 line "25000" ha rect.y = 9578 = chart top esatto, h = 22.

**Approach:** Aggiungere `padding-block-start` alla `.charts-css.line` e `.charts-css.area` (es. 24px). Charts.css riduce automaticamente l'area dei bar per far spazio al padding, e le label dei valori massimi vengono spostate verso il basso di 24px → spazio sufficiente per il pill background.

Alternativa testata mentalmente: padding sul wrapper non funziona perché Charts.css usa l'altezza fissa del table (`height: min(300px, 40vh)`), il padding del wrapper non viene mai sottratto.

**Tasks:**
- [x] Aggiungere `padding-block-start: 24px` a `.charts-css.line` e `.charts-css.area`
- [x] Verificare con Playwright che la label max non sia clippata
- [x] Test: unit — CSS contiene padding-block-start su line e area
- [x] Commit & push

**Done when:** Il valore massimo (--size: 1) di un line/area chart è completamente visibile, non tagliato dal top del chart.

---

## M58: Hide data labels per multi-line e multi-area (anti-collision) ✅

**Why:** Nel line/area multi-dataset le label dei valori si sovrappongono pesantemente quando le serie convergono. Misurato in slide-10 (User Growth by Segment): `500/1200/1500` tutti a x≈552, y range 10294-10328 (34px verticali per 3 etichette + pill). I valori non sono leggibili perché sovrapposti.

**Approach:** Per **line/area multi-dataset** non mostrare i `.data` span — gli utenti capiscono il trend dalle linee, e la legend identifica le serie. Per **single-line/area** mantenere le label (sono leggibili e utili come scala).

Implementazione: in `transform_charts`, controllare `is_multiple` insieme al tipo. Se `chart_type in ('line', 'area') and is_multiple`, non emettere `.data` span.

**Tasks:**
- [x] Aggiungere logica `is_multiple_line_or_area` in `transform_charts`
- [x] Sopprimere data spans quando vero
- [x] Test: unit — line multi-dataset NON ha `<span class="data">`
- [x] Test: unit — line single-dataset HA `<span class="data">`
- [x] Test: unit — area multi-dataset NON ha span data
- [x] Verificare visualmente con Playwright
- [x] Commit & push

**Done when:** Line/area multi-dataset non mostrano label dati (no overlap), single-dataset le mostrano normalmente.

---

## M59: Audit visivo finale di tutti i chart ✅

**Why:** Dopo M56-M58 servirà un check visivo completo per assicurare che non ci siano regressioni e che tutti gli 8 chart dell'example siano davvero leggibili.

**Approach:** Script Playwright che screenshotta tutti i chart, ispezione visiva uno a uno. Se emergono problemi minori (spacing, alignment) li fixiamo inline.

**Tasks:**
- [x] Script Playwright per screenshot di ogni chart dell'example
- [x] Ispezione visiva uno a uno
- [x] Fix minori se necessari (no nuovi milestone, solo polish)
- [x] Commit finale con screenshot allegati nel commit message
- [x] Push

**Done when:** Tutti gli 8 chart dell'example sono visivamente puliti e leggibili.

---

## M60: Column data labels — torna a bianco (testo dentro la barra) ✅

**Why:** Nel column chart i numeri "100", "35", "22", "12" sono renderizzati neri su sfondo colorato (blu/arancione/rosso/verde) — illeggibili. Misurato: `.data` ha `color: rgb(51,51,51)` (nero), il padre `<td>` è dentro la barra colorata. Charts.css posiziona il `.data` con `align-items: flex-start` al top della barra colorata, quindi il testo è VISUALMENTE dentro la barra.

**Causa:** in M42 ho separato `bar/pie/stacked = bianco` da `column/line/area = nero`. Per column ho assunto "fuori dalla barra" ma in realtà i valori sono al top della barra colorata (dentro).

**Approach:** Spostare `.column .data` dalla regola "text-color" alla regola "white + shadow", insieme a `.bar/.pie/.stacked-*`. Solo `.line` e `.area` restano col colore testo (lì il testo è davvero sopra la linea, su sfondo card).

**Tasks:**
- [x] Aggiungere `.column .data` alla regola white+shadow
- [x] Rimuovere `.column .data` dalla regola text-color
- [x] Test: unit — CSS contiene `.column .data` con `#fff`
- [x] Verificare visualmente con Playwright (Q1 Conversion, Team Allocation)
- [x] Commit & push

**Done when:** I valori nelle column chart sono bianchi con text-shadow, leggibili sopra qualsiasi colore di barra.

---

## M61: Line/area — fix overflow x-labels fuori dalla card ✅

**Why:** Le label dell'asse x ("Q1, Q2, Q3, Q4" / "00:00...") di line e area appaiono FUORI dalla card, sotto il bordo. Misurato in slide-8 line: wrapper.bottom=9932, xLabels.y=9939 (7-31px sotto). Causa duplice:
1. Charts.css per line/area genera un `tbody` che è ~60px più alto del `table` (l'area labels è oltre la chart area). Il wrapper non riserva questo spazio.
2. In M57 ho aggiunto `padding-block-start: 24px` al table per il top clipping, ma questo padding RIDUCE l'area di disegno dentro il table mantenendo la stessa altezza, e Charts.css spinge le labels più in basso → fuori dal wrapper.

**Approach:** Due fix combinati:
1. **Rimuovere `padding-block-start: 24px`** da `.charts-css.line` e `.charts-css.area`
2. **Aggiungere padding extra al wrapper** per riservare lo spazio per le x-labels in line/area. Usare `.md2-chart:has(.line)` / `.md2-chart:has(.area)` con `padding-bottom: 56px` e `padding-top: 32px` extra.

Verificare con Playwright che:
- xLabels.bottom < wrapper.bottom
- Il max value pill è completamente visibile

**Tasks:**
- [x] Rimuovere `padding-block-start: 24px` da `.charts-css.line` e `.charts-css.area`
- [x] Aggiungere padding extra al wrapper line/area via `:has()`
- [x] Test: unit — CSS no padding-block-start su line/area table
- [x] Test: unit — wrapper ha padding-bottom esteso per line/area
- [x] Verificare con Playwright — xLabels.bottom < wrapper.bottom
- [x] Verificare con Playwright — max value pill completamente visibile
- [x] Commit & push

**Done when:** Le x-axis labels e il max value pill di line/area sono completamente dentro la card, nessun overflow visivo.

---

## M62: Data pill z-index fix per line/area ✅

**Why:** Nei line/area chart i pill background dei valori dati (es. "35", "50", "8500", "15000") hanno il bordo destro nascosto dal td sibling successivo. Il pill è dentro un `<td>` che ha `::before` colorato (area/linea), e il td successivo nel DOM sovrappone visivamente il pill del precedente perché Charts.css posiziona ogni td con position:relative e il pill (absolute) eredita lo stacking context del proprio td — il td successivo è "sopra" nel painting order.

**Approach:** Applicare `position: relative; z-index: 2;` al `.data` per line/area. Questo lo promuove nello stacking context del proprio td. Se non basta, bisogna anche settare `isolation: isolate` o `z-index: 2` sul `.data`'s td parent per assicurare che il pill esca dal layer del td successivo.

Investigare con Playwright dopo il primo tentativo per confermare.

**Tasks:**
- [x] Aggiungere `position: relative; z-index: 2;` a `.line .data, .area .data`
- [x] Verificare con Playwright che il pill sia completamente visibile
- [x] Se insufficiente, escalate: settare z-index sul td parent
- [x] Test: unit — CSS contiene z-index su .line/area .data
- [x] Commit & push

**Done when:** I pill dei valori nei line/area chart non sono coperti dal colore dei td sibling successivi.

---

## M63: Legend overlap con x-axis labels in line/area multi-dataset ✅

**Why:** Nel line multi-dataset "User Growth by Segment" la legend ("Enterprise", "SMB", "Self-serve") si sovrappone alle x-axis labels ("Q2" dentro "Enterprise", "Q3" dentro "Self-serve"). Motivo: M61 ha aggiunto `padding-bottom: 56px` al wrapper `:has(.line)` per riservare spazio alle x-labels, ma la legend è piazzata come sibling DOPO il tbody e usa `margin-top: 40px` (M52). In multi-dataset la legend viene aggiunta dopo il tbody, quindi si trova alla stessa y delle x-labels che sono nell'area overflow del tbody.

**Approach:** La legend deve stare SOTTO le x-labels, non alla stessa y. Fix: aumentare margin-top della legend per line/area multi-dataset, oppure spostare la legend FUORI del flow del tbody con posizionamento esplicito.

Soluzione più semplice: aumentare `margin-top` della legend per i tipi che hanno x-axis labels in overflow (line, area). Selettore: `.md2-chart:has(.line.multiple) ul.legend, .md2-chart:has(.area.multiple) ul.legend { margin-top: 72px; }`.

Verificare con Playwright che legend.y > xLabels.bottom.

**Tasks:**
- [x] Aggiungere regola CSS che aumenta margin-top della legend quando il chart è line/area multi-dataset
- [x] Verificare con Playwright — legend.y > xLabels.bottom
- [x] Test: unit — CSS contiene la regola
- [x] Commit & push

**Done when:** La legend nei line/area multi-dataset è sotto le x-axis labels, nessuna sovrapposizione.

---

## M64: Rethink radicale — data summary sotto il chart per line/area 🚫 SUPERSEDED

**Status:** Rigettato dall'utente. La data table sotto il chart è visivamente "un disastro" e separa i valori dal chart. Superseded da M64bis.

(contenuto originale mantenuto come reference storica. Vedi M65 sotto per l'approccio attuale.)

## M64 (bis — original content archived, see M65):

**Why (archived):** Da M43 in poi ho accumulato 5 milestone di fix per le label di line/area (M54 show values, M57 top padding, M61 wrapper padding, M62 z-index pill) senza mai arrivare a una soluzione pulita. Ogni fix risolve un sintomo e ne crea un altro:
- 25000 clipped al top → padding-top → x-labels fuori card → più padding → 50 ancora clipped
- Multi-dataset label collision → hide them → "grafico inutile, mancano numeri"
- Pill z-index nascosto da td sibling → z-index: 2 → ancora clipping top

**Root cause**: Charts.css usa `position: absolute` per i `.data` dentro i `<td>` ai coordinate del valore. Questo genera inevitabilmente: clipping ai bordi, z-index fights, collision in multi-dataset, spreco di spazio. L'approccio è sbagliato dall'inizio per i chart tipo "line/area" dove i valori sono SPARSI.

L'utente ha individuato la soluzione corretta: **non posizionare le label nel chart area**. Metterle in un'area dedicata sotto il chart.

**Approach:** Per `line` e `area` (e SOLO per loro — bar/column/pie funzionano bene con label inline dentro le barre colorate):

1. **Rimuovere completamente** la generazione di `<span class="data">` inline per line/area
2. **Generare una data summary HTML** dentro il wrapper, dopo il chart e prima della legend:
   - **Single-dataset**: `<div class="md2-chart-data">` con mini-tabella orizzontale. Header: x-categorie. Row: valori.
   - **Multi-dataset**: `<table class="md2-chart-data">` con una riga per serie. Prima colonna: color dot + nome serie. Colonne successive: valori per ogni x-categoria.
3. **Rimuovere** le regole CSS ora obsolete:
   - `padding-block-start` da `.line/.area` (M57) — già rimosso
   - `.md2-chart:has(.line/.area)` extra padding (M61) — può tornare a default
   - `.line/.area .data` z-index e position (M62) — non esistono più data span
   - Pill background su `.line/.area .data` — non esiste più
4. **Aggiungere CSS** per `.md2-chart-data`:
   - Font piccolo (0.85rem), color muted (text-color con opacity 0.9)
   - Compatto (padding 4-6px per cell)
   - Allineato a destra o centrato (valori numerici)
   - Color dots coerenti con le serie del chart (via `var(--md2-color-N)`)
5. **Eliminare** `margin-top: 72px` dalla legend multi-line/area (M63) — non serve più perché il chart area torna a dimensione normale
6. **Reset wrapper padding** per line/area ai valori default (come altri chart)

**Tasks:**
- [ ] In `transform_charts`: per `line`/`area`, non generare `<span class="data">` anche in single-dataset
- [ ] Aggiungere logica per generare `.md2-chart-data` HTML (single/multi)
- [ ] Inserire `.md2-chart-data` nel risultato wrapper (dopo tbody, prima della legend)
- [ ] CSS: nuova classe `.md2-chart-data` con stile compatto
- [ ] Rimuovere regole CSS obsolete da `style.css`: `.line .data`, `.area .data`, `.md2-chart:has(.line)` padding override, M63 multi-line legend margin-top override
- [ ] Aggiornare test obsoleti (M54, M62, M63, M57/M61 che verificavano padding)
- [ ] Aggiungere test: line single ha `.md2-chart-data`, line multi ha `.md2-chart-data` con tutti i valori
- [ ] Verificare con Playwright: tutti i valori visibili, nessun clipping, nessun overlap
- [ ] Commit & push

**Done when:** 
- Slide-8 single-line "Projected User Growth" mostra tutti i valori (3200, 8500, 15000, 25000) in una data summary sotto il chart, nessun clipping del chart area
- Slide-8 multi-line "User Growth by Segment" mostra tutti i 12 valori (3 serie × 4 quarter) in una tabella sotto il chart, con color dots
- Slide-6 area "Event Pipeline" mostra tutti i valori (12, 8, 35, 50, 48, 30) in una data summary, "50" non più clipped
- Nessun z-index/clipping/overlap visibile
- Il chart area stesso è pulito, senza pill dentro

---

## M65: Endpoint labels per multi-line/area con override robusto `.data` ✅

**Why:** Supersede M64 (data table sotto = rigettato). L'utente vuole valori SEMPRE visibili nel chart area, niente hover, niente tabelle separate, niente sparizioni. Print-ready stile LaTeX. Da M43 in poi ho accumulato 5 hack milestone (M54, M57, M61, M62, M63) per i line/area che non hanno mai funzionato bene perché combattevano il posizionamento nativo di Charts.css invece di sovrascriverlo in modo robusto. La ricerca della documentazione Charts.css ha confermato che la libreria NON supporta label inline robusti per line/area (gli esempi ufficiali usano `.hide-data`).

**Approach:** Sovrascrivere completamente il posizionamento `.data` di Charts.css per line/area con CSS override robusto, e usare il pattern canonico di data visualization professionale ("endpoint labels alla Bloomberg/FT"):

### Single-dataset line/area

Mostrare TUTTI i valori, uno sopra ogni punto della linea:
- CSS override: `.line .data, .area .data { position: absolute; transform: translate(-50%, -110%); z-index: 10; }`
- Il `-110%` sposta la label COMPLETAMENTE SOPRA il punto della linea (non sovrapposta)
- Wrapper padding-top riservato (es. 40px) per accogliere la label del max value (`--end: 1`)
- Pill background solido con shadow → leggibile su qualsiasi sfondo
- `z-index: 10` evita che il td sibling successivo nasconda il pill

### Multi-dataset line/area

Mostrare solo il valore FINALE di ogni serie, con formato "Nome: Valore" a destra del chart:
- In `transform_charts`: emettere `<span class="data">` solo per l'ultima colonna di ogni riga (o l'ultima riga per il formato column-per-series)
- Formato label: `{dataset_header}: {value}` (es. "Self-serve: 10000")
- Posizionamento: immediatamente a destra dell'ultimo punto, allineato verticalmente
- Wrapper padding-right aumentato (~120px) per ospitare le label
- Pill background con colore dot (usa `::before` con `background: currentColor` dove `color` è settato dalla regola `nth-of-type` di Charts.css per la serie)
- **Rimuovere la legenda classica** — inutile ora, la label endpoint ha sia nome sia valore

### Text truncation

Label names possono essere lunghi. CSS:
- `max-width: 140px`
- `overflow: hidden`
- `text-overflow: ellipsis`
- `white-space: nowrap`

### Cleanup pre-esistente (da rimuovere)

Questi hack diventano obsoleti:
1. **M54**: `_CHART_TYPES_SHOW_DATA` include già line/area, mantenere ✓
2. **M57**: `padding-block-start: 24px` su `.line/.area` → **RIMUOVERE**, non serve più
3. **M58**: `if is_multiple and chart_type in ('line', 'area'): show_data = False` → **RIMUOVERE** (ora mostriamo endpoint label)
4. **M61**: `.md2-chart:has(.line/.area)` wrapper padding → **SEMPLIFICARE** (resta padding-top 40px e padding-right 120px in multi, ma via selettore pulito)
5. **M62**: `.line .data, .area .data { z-index: 2; position: relative; }` → **MANTENERE/UNIFICARE** con il nuovo override
6. **M63**: `:has(.line.multiple) ul.legend { margin-top: 72px }` → **RIMUOVERE** (niente legenda per multi-line)

**Tasks:**
- [x] In `transform_charts`: per line/area multi-dataset, emettere `.data` span SOLO per l'ultima colonna di ogni riga (endpoint)
- [x] Il formato del span per multi-line endpoint: `{header}: {value}` (prefissato con il nome della serie)
- [x] Single-line/area resta invariato: tutti i valori, tutte le righe
- [x] **Rimuovere** la generazione automatica di `ul.legend` per line/area multi (la label endpoint fa da legenda)
- [x] CSS: override `.line .data, .area .data` con `transform: translate(-50%, -110%)`, `z-index: 10`, pill styling
- [x] CSS: per multi-line/area, override `.data` per label endpoint → posizionamento a destra del punto (`transform: translate(8px, -50%)`)
- [x] CSS: `max-width: 140px; text-overflow: ellipsis; white-space: nowrap` sulle label
- [x] CSS: rimuovere `padding-block-start: 24px` da `.line/.area` (obsoleto M57)
- [x] CSS: sostituire `:has(.line)/:has(.area)` padding con selettore più semplice (padding sempre, non conditional)
- [x] CSS: wrapper per multi-line/area ha `padding-right: 120px` extra per le endpoint labels
- [x] CSS: rimuovere `.md2-chart:has(.line.multiple/.area.multiple) ul.legend` margin override (M63 obsoleto)
- [x] Test: unit — single-line emette data span per ogni punto, multi-line solo per endpoint
- [x] Test: unit — multi-line label contiene `{header}:` prefix
- [x] Test: unit — CSS contiene transform/z-index override per .line/.area .data
- [x] Test: unit — CSS rimuove padding-block-start obsoleto
- [x] Test: unit — niente `ul.legend` nell'HTML per multi-line/area
- [x] Verificare con Playwright: single-line tutti i valori visibili senza clipping/overlap
- [x] Verificare con Playwright: multi-line "Enterprise: 6000", "SMB: 9000", "Self-serve: 10000" a destra, chart pulito a sinistra
- [x] Rigenerare example.html
- [x] Commit & push

**Done when:**
- Single-line "Projected User Growth": tutti i valori (3200, 8500, 15000, 25000) visibili come pill sopra i punti, nessun clipping, nessun overlap
- Multi-line "User Growth by Segment": solo i valori finali (Enterprise: 6000, SMB: 9000, Self-serve: 10000) visibili come pill a destra dei punti finali, niente ul.legend duplicata
- Area single-dataset: stessa logica di line single
- Nessun z-index issue, nessun clipping top/bottom, nessuna sovrapposizione
- Pulizia CSS: rimossi padding-block-start, legend margin hack, ecc

---

## M66: Fix residui — collision endpoint labels + top clipping area ✅

**Why:** Dopo M65, restano due problemi residui visibili negli screenshot:

1. **Multi-line endpoint label collision** (slide-8 "User Growth by Segment"): le label endpoint di SMB (9000) e Self-serve (10000) sono posizionate a x identico (right of last point) e y molto vicini (delta 10% del chart height ≈ 30px vs 22px label height). La label SMB è visivamente nascosta o sovrapposta da Self-serve. Enterprise (6000) invece è distante e visibile.

2. **Area chart "50" ancora parzialmente clippato al top** (slide-6 "Event Pipeline"): con `transform: translateY(-110%)` il pill è spostato 110% sopra la posizione naturale. Per `--end: 1` (chart top), la label esce SOPRA il chart top di 22px+10%. Il wrapper ha `padding-top: 40px` ma non è abbastanza perché il translate va oltre il padding.

**Approach:**

### Fix 1 — Stagger verticale endpoint labels in collision

Algoritmo in `transform_charts`:
1. Per multi-line/area, calcolare la y finale (ultima `--size`) di ogni serie
2. Ordinare le serie per y (alto→basso)
3. Verificare se c'è collision tra label adiacenti (delta y < soglia, es. 26px su chart 300px = 8.6% = 0.086 in unità --size)
4. Se collision, applicare un offset cumulativo alla label che si sovrappone
5. Emettere le label con `style="--label-offset: Npx"` che CSS usa per spostare verticalmente

Oppure più semplice: in CSS, usare `translateY(-50%)` base e aggiungere un offset per le label successive via `nth-of-type`:
- 1° label: `transform: translate(6px, -50%)`
- 2° label: `transform: translate(6px, calc(-50% - 24px))`
- 3° label: `transform: translate(6px, calc(-50% + 24px))`

Ma questo non conosce l'ordine dei valori, stagger fisso non funziona.

**Approccio pratico**: calcolare in Python le posizioni y di ogni serie endpoint, de-colliderle con algoritmo semplice, e passare `--label-y` come CSS variable inline. CSS poi usa `top: var(--label-y)` invece del posizionamento Charts.css nativo.

### Fix 2 — Aumentare padding-top wrapper per area chart

Incrementare `.md2-chart:has(.charts-css.line), .md2-chart:has(.charts-css.area)` da `padding-top: 40px` a `padding-top: 56px`. Oppure: modificare il `translateY(-110%)` a `translateY(-100%)` per ridurre l'overshoot.

**Tasks:**
- [x] Calcolare in `transform_charts` le posizioni normalizzate delle endpoint labels (per multi-line/area)
- [x] Implementare de-collision: se due label sono a < 0.09 di distanza, offset la seconda verso il basso/alto
- [x] Emettere `style="--label-offset: Npx"` inline sulla label span
- [x] CSS: `.line.multiple .data, .area.multiple .data` usa `translate(6px, calc(-50% + var(--label-offset, 0px)))`
- [x] Aumentare padding-top wrapper line/area da 40 a 56px
- [x] Test: unit — multi-line con valori vicini genera offset diversi
- [x] Test: unit — CSS padding-top è 56px
- [x] Verificare con Playwright: SMB e Self-serve separati visivamente
- [x] Verificare con Playwright: "50" in area chart non più clippato
- [x] Rigenerare example
- [x] Commit & push

**Done when:**
- Multi-line "User Growth by Segment": tutte e 3 le label (Enterprise: 6000, SMB: 9000, Self-serve: 10000) visibili e non sovrapposte
- Area "Event Pipeline": valore "50" al top completamente visibile, pill non clippato

---

## M67: Graduated Y-axis per line/area + cleanup endpoint labels ✅

**Why:** Dopo 8 milestone di fix fragili (M43, M54, M57, M58, M61, M62, M63, M65, M66) per mostrare i valori nei line/area chart, il pattern ufficiale di Charts.css (visibile nei suoi esempi: `show-primary-axis show-secondary-axes hide-data`) è più robusto. Un asse Y graduato con gridline e Y-labels risolve: zero collision, zero z-index, zero clipping, scalabile a N serie. In più fixa il phantom card sopra il titolo (il padding-top 56px del wrapper `:has(.line)` lascia 48px di area grigia vuota sopra il titolo). Allineato al canone del data visualization professionale (Excel, FT, Bloomberg).

**Approach:**

### Chart structure

Classi Charts.css sulle line/area:
- `charts-css line show-labels show-primary-axis show-4-secondary-axes`
- Per multi: anche `multiple`
- Ripristinare `<span class="data">` HIDDEN (no più endpoint labels o transform hacks)

### Generazione asse Y custom

In `transform_charts`, per line/area:
1. Calcolare `max_val` (già disponibile)
2. Calcolare 5 tick values "nice" (0, 25%, 50%, 75%, 100% di max, arrotondati a multipli puliti tipo 0/2500/5000/7500/10000)
3. Generare HTML:
   ```html
   <div class="md2-chart-yaxis">
     <span>10000</span>
     <span>7500</span>
     <span>5000</span>
     <span>2500</span>
     <span>0</span>
   </div>
   ```
4. Inserire nel wrapper `.md2-chart` insieme al chart table

### CSS per l'asse Y

```css
.md2-chart:has(.line), .md2-chart:has(.area) {
    position: relative;
    padding-left: 68px;  /* spazio per asse Y */
    padding-top: 16px;   /* normale, no 56px */
    padding-bottom: 16px;
}
.md2-chart-yaxis {
    position: absolute;
    top: [title_height + top_padding];
    left: 8px;
    bottom: [x_labels_height + bottom_padding];
    width: 50px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    text-align: right;
    font-size: 0.75rem;
    color: var(--text-color);
    opacity: 0.7;
}
.md2-chart-yaxis span { line-height: 1; }
```

### Tick value "nice number" algorithm

Per max=25000:
- raw step = 25000 / 4 = 6250
- nice step ≈ 7500 (ceil to 1/2/5 × 10^n)
- ticks: 0, 7500, 15000, 22500, 30000 → troppo grande, usa max esatto
- Più semplice: max_val, 75%, 50%, 25%, 0 arrotondati a 1/2/5 × 10^n del max

Implementazione: funzione `_nice_ticks(max_val)` che ritorna 5 valori [0, t1, t2, t3, t_max].

Formula base:
```python
def _nice_ticks(max_val):
    """Return 5 'nice' tick values from 0 to ~max_val."""
    # Find nice interval
    import math
    raw_step = max_val / 4
    power = 10 ** math.floor(math.log10(raw_step))
    normalized = raw_step / power
    if normalized <= 1:
        nice = 1
    elif normalized <= 2:
        nice = 2
    elif normalized <= 5:
        nice = 5
    else:
        nice = 10
    step = nice * power
    return [int(step * i) for i in range(5)]
```

### Cleanup

Rimuovere da `core.py`:
- Logic `is_multi_connected` per endpoint labels
- Il blocco `endpoint_offsets` con stagger algorithm
- La generazione di data span con formato "Name: Value"

Rimuovere da `style.css`:
- `.md2-chart .line .data` con transform/translate -110% !important
- `.md2-chart .line.multiple .data` con transform endpoint
- `.md2-chart:has(.charts-css.line)` padding-top 56px
- `.md2-chart:has(.charts-css.line.multiple)` padding-right 140px
- Le regole `--label-offset` inline

### Legenda per multi-dataset

Ripristinare la legenda classica (già presente per bar/column multi-dataset, solo rimossa dall'M65 per line/area):
- `ul.legend` con `<li>` per dataset
- Bullet colorati via `::before` che usano `--md2-color-N`
- Margin-top ragionevole sotto il chart

### Single vs multi

- **Single-dataset**: axis graduato + nessun endpoint label (l'utente legge dai tick)
- **Multi-dataset**: axis graduato + legenda con colori + nomi serie

Uniforme, semplice, no casi speciali.

### Data span strategy

Charts.css genera `<span class="data">` ma noi lo nascondiamo con CSS: `.md2-chart .line .data, .md2-chart .area .data { display: none !important; }`. O usiamo la classe Charts.css `.hide-data`.

Preferibile: aggiungere la classe `hide-data` al chart table nella generazione HTML. Così è il pattern Charts.css ufficiale.

### Phantom card fix

Il phantom sparisce automaticamente perché:
- Wrapper padding torna a `8px 20px 20px` (normale)
- Title con `margin: -8px -20px 8px` occupa esattamente la fascia superiore (8px reale = 8px negative margin)
- Niente area vuota sopra

**Tasks:**
- [x] Implementare `_nice_ticks(max_val)` in core.py con algoritmo nice number
- [x] In `transform_charts`, per line/area: aggiungere classi `show-primary-axis show-4-secondary-axes hide-data`
- [x] In `transform_charts`, per line/area: generare `<div class="md2-chart-yaxis">` con 5 tick span
- [x] Wrappare chart table + yaxis in una struttura che permetta posizionamento assoluto
- [x] CSS: `.md2-chart-yaxis` con flex column space-between, absolute left
- [x] CSS: `.md2-chart:has(.line), :has(.area)` con `position: relative`, `padding-left: 68px`, normale `padding-top/bottom`
- [x] CSS: rimuovere transform hacks su `.line .data, .area .data`
- [x] CSS: rimuovere `!important` e endpoint label styling
- [x] CSS: rimuovere `:has(.line) { padding-top: 56px; padding-bottom: 56px }`
- [x] CSS: rimuovere `:has(.line.multiple) { padding-right: 140px }`
- [x] core.py: rimuovere `is_multi_connected` logic e `endpoint_offsets` stagger
- [x] core.py: rimuovere formato "Name: Value" per multi-line/area
- [x] core.py: ripristinare `ul.legend` per multi-line/area (come bar/column)
- [x] Aggiornare/rimuovere test obsoleti: M65 endpoint tests, M66 stagger tests
- [x] Aggiungere test: line/area CSS contiene `md2-chart-yaxis` class rules
- [x] Aggiungere test: `_nice_ticks(25000)` produce `[0, 7500, 15000, 22500, 30000]` o simile
- [x] Aggiungere test: line/area HTML contiene `md2-chart-yaxis` div con 5 span
- [x] Verificare con Playwright: phantom card sparito, axis Y visibile a sinistra, gridline renderizzate
- [x] Verificare con Playwright: multi-line ha legenda sotto con colori
- [x] Rigenerare example.html
- [x] Commit & push

**Done when:**
- Chart line/area hanno un asse Y graduato a sinistra con 5 valori (0 → max)
- 4 gridline orizzontali visibili nel chart area
- Multi-line ha legenda classica sotto con bullet colorati
- Nessun phantom card sopra il titolo
- Codice CSS e Python semplificato (rimossi tutti gli hack M65/M66)
- Tutti i 8 chart dell'example visivamente puliti

---

## M68: Fix graduated Y-axis alignment con i dati ✅

**Why:** In M67 ho implementato l'asse Y graduato ma ci sono due bug critici visibili nello screenshot dell'utente:

1. **Normalizzazione errata**: i valori `--end`/`--size` sono normalizzati contro `max_val` (il massimo dei dati), non contro `ticks[-1]` (il massimo dell'asse Y). Quando `_nice_ticks(25000)` bumpa l'asse a [0, 10000, 20000, 30000, 40000], la linea raggiunge `--end: 1.0 = 25000` che visivamente corrisponde al TOP del chart, ma l'asse Y mostra il top come 40000. Risultato: il dato 25000 appare come 40000.

2. **Gridline disallineate dai tick**: `show-4-secondary-axes` crea 4 gridline a 20%/40%/60%/80%. I miei tick sono a 0%/25%/50%/75%/100% (5 valori). Le posizioni non coincidono. Deve essere `show-3-secondary-axes` (3 linee a 25%/50%/75%) + primary axis (0%) = 5 righe allineate con i 5 tick.

**Approach:**

### Fix 1 — Normalizzare contro tick_max

In `transform_charts`, per line/area:
- Calcolare `ticks = _nice_ticks(max_val)` **prima** del loop di generazione td
- Sostituire `max_val` con `tick_max = ticks[-1]` come denominatore di normalizzazione
- Così `--end` va da 0 a `max_val/tick_max` (≤ 1), e visivamente la linea si ferma al livello corretto dell'asse Y

### Fix 2 — 3 secondary axes invece di 4

Cambiare la classe `show-4-secondary-axes` → `show-3-secondary-axes` per line/area.
- Charts.css con `.show-3-secondary-axes` disegna 3 gridline orizzontali (a 25%, 50%, 75%)
- Combinate con primary-axis (baseline 0%) e top border del chart (100%) = 5 riferimenti visivi
- Coincidono con i 5 tick Y: 0, 25%, 50%, 75%, 100%

### Fix 3 — Verificare allineamento yaxis con chart area

Il `.md2-chart-yaxis` ha `top: 48px, bottom: 56px` hardcoded. Il chart area interno di Charts.css (zona dove le linee sono disegnate) ha un offset diverso perché:
- Il wrapper ha `padding-top` (normale per line/area dopo M67, ~8-16px)
- Il title (se presente) occupa ~40px
- Il tbody può avere padding/margin interno

I valori hardcoded sono un guess. Se il disallineamento persiste dopo Fix 1+2, misurare con Playwright le y esatte del chart tbody e adeguare `top`/`bottom` del yaxis.

**Tasks:**
- [x] Compute `ticks` **prima** del tbody loop, salvare `tick_max = ticks[-1]`
- [x] Sostituire `max_val` con `tick_max` nella normalizzazione `--end`/`--size` per line/area
- [x] Per bar/column/pie mantenere `max_val` invariato (non usano tick)
- [x] Cambiare `show-4-secondary-axes` → `show-3-secondary-axes` in `transform_charts`
- [x] Aggiornare test: line/area usano tick_max per normalizzazione
- [x] Aggiornare test: line/area hanno `show-3-secondary-axes`
- [x] Verificare con Playwright: linea raggiunge il livello corretto dell'asse Y
- [x] Verificare con Playwright: gridline coincidono con i tick Y
- [x] Se disallineamento yaxis residuo, misurare e correggere top/bottom CSS
- [x] Commit & push

**Done when:**
- La linea di `:::chart line` con max dato 25000 raggiunge esattamente il livello "25000" sull'asse Y (non il top)
- Le gridline orizzontali coincidono visivamente con i numeri dell'asse Y
- Tutti gli 8 chart dell'example ancora renderizzati correttamente

---

## M69: Parametrizzazione Y-axis intelligente (data_min + clustering detection) ✅

**Why:** Due problemi intrecciati con l'asse Y:

1. **tick_max troppo alto**: per `max=10000` l'algoritmo produce `tick_max=20000` (doppio). Chart usa metà altezza.
2. **Dati clustered non gestiti**: per `[50000, 55000, 60000]`, partire da 0 mette i dati nel 10% superiore, rendendo invisibili le differenze. Serve Y-axis `[48000, 51000, ..., 60000]`.

L'utente osserva: "dovresti parametrizzare bene da lasciare spazio sotto al più piccolo valore, o zero se sono tutti positivi, e sopra un piccolo spazio sopra il più alto".

**Approach:** Riscrivere `_nice_ticks(data_min, data_max)` (nuova firma con entrambi i parametri) con due migliorie:

### Fix 1 — Set di nice numbers più fitto

Da `[1, 2, 5, 10]` → `[1, 2, 2.5, 5, 7.5, 10]`:
- `max=10000`, step raw=2500 → normalized=2.5 → `nice=2.5` → step=2500 → `[0,2500,5000,7500,10000]` ✓
- `max=25000`, step raw=6250 → normalized=6.25 → `nice=7.5` → step=7500 → `[0,7500,15000,22500,30000]` ✓

### Fix 2 — Clustering detection per axis_min

Nuova logica:
```python
def _nice_ticks(data_min, data_max):
    if data_min > 0 and data_min > data_max * 0.5:
        # Clustered data — start from nice floor(data_min - padding)
        range_val = data_max - data_min
        padding = range_val * 0.1  # 10% headroom
        axis_start_raw = data_min - padding
        step = _nice_step((data_max + padding - axis_start_raw) / 4)
        axis_start = floor(axis_start_raw / step) * step
    else:
        # Default: all positive spanning range or includes 0 — start from 0
        axis_start = 0
        step = _nice_step(data_max / 4)
    # Generate 5 ticks starting from axis_start
    ticks = [axis_start + step * i for i in range(5)]
    # Ensure last tick >= data_max
    while ticks[-1] < data_max:
        ticks = [t + step for t in ticks]
    return ticks
```

**Soglia clustering**: `data_min > data_max * 0.5` (cioè `min/max > 0.5`, o `range/max < 0.5`). Standard in data viz (Excel, Tableau).

### Esempi esaustivi

| data | min/max | clustered? | axis | tick_max/max |
|---|---|---|---|---|
| `[500, 1200, 10000]` | 0.05 | no | `[0, 2500, 5000, 7500, 10000]` | 1.0 |
| `[3200, 25000]` | 0.128 | no | `[0, 7500, 15000, 22500, 30000]` | 1.2 |
| `[50000, 55000, 60000]` | 0.83 | sì | `[48000, 51000, 54000, 57000, 60000]` | 1.0 |
| `[90, 95, 100]` | 0.9 | sì | `[88, 91, 94, 97, 100]` | 1.0 |
| `[40, 80]` | 0.5 (borderline) | no (strict `>`) | `[0, 20, 40, 60, 80]` | 1.0 |
| `[30, 50]` | 0.6 | sì | `[28, 34, 40, 46, 52]` o simile | ~1.0 |

### Propagazione in transform_charts

La normalizzazione cambia da:
```python
norm = val / tick_max
```
a:
```python
norm_min = ticks[0]
norm_max = ticks[-1]
norm = (val - norm_min) / (norm_max - norm_min)
```

Per Charts.css `--start`/`--size`/`--end`, il valore va da 0 (a norm_min) a 1 (a norm_max). La linea di 60000 con axis `[48000..60000]` ha `--size = (60000 - 48000) / (60000 - 48000) = 1.0` (top del chart). 50000 → `(50000 - 48000) / 12000 = 0.167` (vicino al bottom).

### Fix CSS flex body (già sperimentato)

Applicare `.md2-chart-body { height: min(300px, 40vh); }` per forzare il body a coincidere col chart table, eliminando lo stretching a 360px che causava il disallineamento residuo.

**Tasks:**
- [x] Riscrivere `_nice_ticks(data_min, data_max)` con nuova firma
- [x] Aggiungere helper `_nice_step(raw_step)` con set `[1,2,2.5,5,7.5,10]`
- [x] Clustering detection `data_min > data_max * 0.5`
- [x] In `transform_charts` per line/area: calcolare `data_min_positive` (escludendo 0 e valori ≤ 0 — usare 0 se tutti ≥ 0 e nessuno > 0 oppure direttamente data min)
- [x] Passare `(data_min, data_max)` a `_nice_ticks`
- [x] Normalizzazione `(val - norm_min) / (norm_max - norm_min)` per line/area
- [x] CSS: `.md2-chart-body { height: min(300px, 40vh); }` per allineamento preciso
- [x] Test: unit — `_nice_ticks(0, 10000)` = `[0, 2500, 5000, 7500, 10000]`
- [x] Test: unit — `_nice_ticks(0, 25000)` = `[0, 7500, 15000, 22500, 30000]`
- [x] Test: unit — `_nice_ticks(50000, 60000)` = `[48000, 51000, 54000, 57000, 60000]` o simile (clustered)
- [x] Test: unit — `_nice_ticks(90, 100)` = ticks che partono da ~88
- [x] Test: unit — `_nice_ticks(0, 50)` — all positive non clustered = `[0, 15, 30, 45, 60]` o simile
- [x] Aggiornare test esistenti di `_nice_ticks` alla nuova firma
- [x] Aggiornare `test_line_chart_connection.py` per i nuovi valori normalizzati
- [x] Test: line chart con dati clustered mostra Y-axis partente da ~data_min
- [x] Verificare visualmente con Playwright tutti i line/area charts
- [x] Rigenerare example
- [x] Commit & push

**Done when:**
- `_nice_ticks(0, 10000)` = `[0, 2500, 5000, 7500, 10000]`
- `_nice_ticks(50000, 60000)` non parte da 0, usa tick vicini al range
- Multi-line "User Growth by Segment" con max 10000 ha Y-axis 0-10000
- Single-line "Projected User Growth" con max 25000 ha Y-axis 0-30000
- Y labels allineati visivamente con gridline (grazie a flex body height esplicito)
- Chart con dati clustered `[50, 55, 60]` usa tutta l'altezza del chart

## Milestone 70: Baseline alignment — decouple x-labels from Charts.css tbody ✅

**Why:** Dopo M67-M69 i dati line/area vengono ancora disegnati *sotto* il label "0" dello yaxis. Misure Playwright (chart "Projected User Growth"):
- `table.height = 300px` (forzato)
- `tbody.height = 335.56px` → tbody sfora la table di 35.56px
- `td.height = 310.56px`, `td.bottom = table.bottom + 10.56px`
- Yaxis "0" label center ≈ `table.bottom - 30px`
- Chart baseline reale (td.bottom) ≈ `table.bottom + 10.56px`
- **Disallineamento ~40px**: il punto 3200/30000 (norm 0.107) viene renderizzato 1.4px sotto il bottom del label "0" → visivamente i dati "spariscono" sotto la baseline.

Charts.css line/area con `show-labels` ospita i `<th scope="row">` come x-labels *overflow* della tbody oltre la table. Il nostro yaxis è constrainato a `height = table.height = 300px` e prova a compensare con `padding-bottom: 24px`, ma il baseline reale non è a `table.bottom - 24px`: è a `table.bottom + overflow` dove `overflow` dipende da font metrics + `--labels-size` implicito. Qualsiasi fix matematico sul padding è fragile.

**Approach:** disaccoppiare le x-labels dalla tabella Charts.css. La tabella gestisce solo il chart; le x-labels sono un `<div>` sibling sotto `md2-chart-body`.

1. In `transform_charts()` per line/area:
   - Continuare a emettere `<th scope="row">` nel HTML (per accessibilità) ma nasconderli via CSS.
   - Aggiungere `<div class="md2-chart-xlabels">` come sibling dopo `.md2-chart-body`, contenente uno `<span>` per ogni riga dati, nell'ordine delle righe.
2. In `style.css`:
   - `.md2-chart .charts-css.line, .md2-chart .charts-css.area { --labels-size: 0; }` → tbody non sfora, `td.bottom == table.bottom`.
   - Nascondere `th[scope="row"]` dentro line/area → zero spazio per etichette interne.
   - `.md2-chart-xlabels { display: flex; padding-left: calc(48px + 8px); font-size: 0.75rem; opacity: 0.7; margin-top: 4px; }` allineato all'inizio del td (yaxis 48px + gap 8px).
   - `.md2-chart-xlabels span { flex: 1; text-align: center; }` — ogni label centrato sotto il td corrispondente.
   - Rimuovere `padding-top: 6px` e `padding-bottom: 24px` dal `.md2-chart-yaxis`. Lasciare yaxis alto come chart table (300px). Per evitare clipping del primo/ultimo label: `margin-top: -0.5em` sul primo span, `margin-bottom: -0.5em` sull'ultimo, oppure `transform: translateY(-50%)` sul primo e `translateY(50%)` sull'ultimo.

**Why questa via è pulita:** elimina la dipendenza dall'overflow implicito di Charts.css e dal valore effettivo di `--labels-size`. Il chart data area diventa esattamente il table box; lo yaxis è 1:1 con quel box.

**Tasks:**
- [x] `transform_charts()`: per line/area generare `<div class="md2-chart-xlabels">` come sibling di `.md2-chart-body` dentro `.md2-chart`
- [x] **Root cause aggiuntiva scoperta:** Charts.css imposta `aspect-ratio: 21/9` su `.line/.area tbody`, costringendo `tbody.height = width * 9/21 ≈ 335px`, che sfora la table di 300px. Override con `aspect-ratio: auto; height: 100%`.
- [ ] `style.css`: `--labels-size: 0` su `.charts-css.line` e `.charts-css.area`
- [ ] `style.css`: nascondere `th[scope="row"]` dentro line/area
- [ ] `style.css`: classe `.md2-chart-xlabels` con flex + padding-left per allineamento ai td
- [ ] `style.css`: rimuovere padding top/bottom da `.md2-chart-yaxis`; gestire clipping primo/ultimo span
- [ ] Test unit: HTML per line/area contiene `md2-chart-xlabels` con N span = N righe dati
- [ ] Test unit: HTML per bar/column/pie/stacked NON contiene `md2-chart-xlabels`
- [ ] Test unit: span del xlabels in ordine originale (Q1, Q2, Q3, Q4)
- [ ] Test visuale Playwright: `|yaxis "0" span center - td.bottom| ≤ 2px` nel chart "Projected User Growth"
- [ ] Test visuale Playwright: `|yaxis top span center - td.top| ≤ 2px`
- [ ] Test visuale Playwright: il punto dati più basso (Q1=3200, norm 0.107) è disegnato SOPRA la linea del label "0"
- [ ] Rigenerare `examples/example.html` e ispezionare Event Pipeline, Projected User Growth, User Growth by Segment
- [ ] Commit & push

**Done when:**
- Screenshot dei chart "Event Pipeline", "Projected User Growth" e "User Growth by Segment" mostrano tutte le linee/aree sopra il label "0" dello yaxis
- Playwright: `|yaxis "0" span center - td.bottom| ≤ 2px` per tutti i line/area chart di esempio
- Playwright: `|yaxis top span center - td.top| ≤ 2px`
- X-labels (Q1, Q2, ...) visibili sotto il chart, allineate alle colonne td
- 372+ test unit passano

## Milestone 71: Line/area gridlines aligned to Y labels — show-4-secondary-axes ✅

**Why:** Con 5 tick label (es. 0, 2500, 5000, 7500, 10000), Charts.css `show-3-secondary-axes` disegna gridline orizzontali a 0%, 33%, 66% del tbody (3 strisce uguali), che corrispondono ai valori 0, 3333, 6667. Le label invece sono a 0%, 25%, 50%, 75%, 100% (4 gap). **Le righe non passano per i numeri.** Visivamente la "scala" sembra rotta. M68 aveva scelto show-3 per errore.

**Approach:** usare `show-4-secondary-axes` (4 strisce ⇒ gridline a 0%, 25%, 50%, 75%) + `show-primary-axis` (linea a 100%) = 5 linee orizzontali, una per ogni label.

**Tasks:**
- [ ] `core.py`: cambiare `show-3-secondary-axes` → `show-4-secondary-axes` per line/area
- [ ] Aggiornare i test M67/M68 che asseriscono `show-3-secondary-axes` / `show-4-secondary-axes not in`
- [ ] Test nuovo: `test_line_uses_4_secondary_axes`, `test_area_uses_4_secondary_axes`
- [ ] Test visuale Playwright: per il chart "User Growth by Segment", misurare le y delle 5 label dello yaxis e confrontarle con le y delle gridline reali (estratte dal background-image del tr o calcolate come `td.top + i*td.height/4`); ogni gridline deve coincidere (±2px) con il center del label corrispondente
- [ ] Rigenerare example, screenshot, ispezionare
- [ ] Commit & push

**Done when:**
- Le 5 gridline orizzontali coincidono visivamente con i label 0/2500/5000/7500/10000
- Tutti i test passano

## Milestone 72: Pie chart — value labels inside slices 🚧

**Why:** Le pie hanno la legenda sotto con `label (value)`. Sarebbe più leggibile avere il valore *dentro* la fetta, sempre orientato orizzontalmente (mai inclinato sulla rotazione della fetta).

**Approach:** in `transform_charts()` per pie, calcolare per ogni fetta:
- angolo medio in radianti: `theta_i = 2π * (cumulative_i + size_i/2) / total`
- posizione radiale in percentuale dal centro: `r = 30%` (compromesso tra centro e bordo per leggibilità)
- coordinate: `left = 50% + r·sin(theta)`, `top = 50% - r·cos(theta)` (CSS y cresce verso il basso, partenza a ore 12 = nord)

Renderizzare ogni etichetta come `<span class="md2-pie-label" style="left:..%; top:..%">value</span>` dentro un wrapper `position: relative` che ricopre la pie. Testo *non ruotato*, sempre orizzontale.

**Fallback:** per fette troppo piccole (size < 6% del totale) il testo non ci sta e si sovrappone al vicino. In quel caso: nascondere il label inline e mantenerlo nella legenda esistente (che resta sotto la pie). Per le altre fette, rimuovere il valore dalla legenda (lasciando solo il nome).

**Tasks:**
- [ ] `core.py`: per pie generare `<div class="md2-pie-wrapper">` con la table dentro + `<span class="md2-pie-label">` per ogni fetta con size ≥ 6%
- [ ] Calcolo trigonometrico in Python (math.sin/cos) per posizione
- [ ] Per fette < 6%: skip label inline, mantieni `(value)` nella legenda solo per quelle
- [ ] Per fette ≥ 6%: legenda mostra solo il nome (no parentesi)
- [ ] CSS: `.md2-pie-wrapper { position: relative }`, `.md2-pie-label { position: absolute; transform: translate(-50%, -50%); color: #fff; font-weight: 600; text-shadow: 0 1px 2px rgba(0,0,0,0.5); pointer-events: none; font-size: 0.85rem }`
- [ ] Test unit: HTML pie con 4 fette ~equilibrate ha 4 `md2-pie-label`
- [ ] Test unit: pie con una fetta da 3% non emette label inline per quella fetta, ma la legenda ha ancora il `(value)` per essa
- [ ] Test unit: posizioni left/top calcolate correttamente per fette singolari (es. 100%, 50%/50%, 25/25/25/25)
- [ ] Test visuale Playwright: screenshot di un chart pie con label visibili dentro le fette
- [ ] Rigenerare example, ispezionare
- [ ] Commit & push

**Done when:**
- Pie chart con fette ≥ 6% mostra il valore dentro la fetta, testo orizzontale
- Pie chart con fette piccole continua a usare la legenda esterna
- Tutti i test passano

## Milestone 73: Border around chart wrapper 🚧

**Why:** Le tabelle hanno un bordo visibile (vedi `.slide table`); le chart hanno solo `box-shadow`. L'utente vuole anche una border line per coerenza visiva con le tabelle.

**Approach:** aggiungere `border: 1px solid var(--table-border)` a `.md2-chart`, in linea con lo stile delle tabelle.

**Tasks:**
- [ ] `style.css`: aggiungere `border: 1px solid var(--table-border)` a `.md2-chart`
- [ ] Verificare in dark mode
- [ ] Test CSS: `.md2-chart` regola contiene `border:`
- [ ] Rigenerare example, screenshot
- [ ] Commit & push

**Done when:**
- Tutti i chart hanno un bordo simile a quello delle tabelle
- Test passano
