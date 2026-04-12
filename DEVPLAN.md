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

## M46: Fix spacing verticale bar multi-dataset

**Why:** Nel bar chart multi-dataset le righe logiche (metriche diverse) sono attaccate tra loro — non c'è spazio tra "Deploy/week" e "Test Coverage". `--data-spacing: 6px` del bar non produce il gap atteso perché Charts.css lo interpreta come spacing tra le barre DENTRO una riga (multi-dataset), non tra righe.

**Approach:** Investigare come Charts.css gestisce lo spacing tra righe in un bar multi-dataset. Probabilmente serve `padding-block` o `border-spacing` sulla table, oppure margin-bottom sulle `<tr>`. Applicare il fix CSS che produce spazio visibile tra metriche.

**Tasks:**
- [ ] Investigare il CSS di Charts.css per `.bar.multiple` row spacing
- [ ] Applicare il fix (margin/padding/border-spacing sulle tr o tbody)
- [ ] Test: unit — CSS contiene la nuova regola di spacing tra righe
- [ ] Verificare con Playwright
- [ ] Commit & push

**Done when:** Nel bar chart multi-dataset c'è uno spazio visibile tra le metriche diverse.

---

## M47: Fix label verticale allineamento multi-dataset

**Why:** Nel bar multi-dataset la label della riga (es. "Deploy/week") è allineata alla PRIMA barra del gruppo, non al centro del gruppo. Visivamente si legge come label della prima barra, non della coppia.

**Approach:** Charts.css posiziona le label a sinistra con `--labels-size`. L'allineamento verticale del testo nella label cell deve essere `center` rispetto alla riga completa (che contiene multiple barre). Fix CSS sulla `th` di label.

**Tasks:**
- [ ] Aggiungere `vertical-align: middle` o flex centering sulle label cells del bar multi-dataset
- [ ] Test: unit — CSS contiene la regola
- [ ] Verificare con Playwright
- [ ] Commit & push

**Done when:** Nel bar multi-dataset la label è centrata verticalmente rispetto al gruppo di barre.

---

## M48: Fix padding wrapper dopo il titolo

**Why:** Dopo il titolo del chart c'è un doppio spazio bianco: il titolo ha `margin-bottom: 16px` e il wrapper ha `padding: 8px 20px 20px`. Risultato: troppo spazio prima che iniziino le barre.

**Approach:** Ridurre o rimuovere il margin-bottom del titolo (il wrapper padding è già sufficiente), oppure usare `padding: 0 20px 20px` sul wrapper quando c'è un titolo (ma questo è complicato). Soluzione più semplice: `margin-bottom: 0` sul titolo, il wrapper padding-top 0 quando c'è titolo via selettore adiacente. In alternativa: rimuovere `margin-bottom` e il wrapper ha già padding sufficiente.

**Tasks:**
- [ ] Ridurre margin-bottom del title a 0 o valore minimo
- [ ] Se necessario, usare selettore adiacente per ridurre padding-top del wrapper quando c'è title
- [ ] Test: unit — regola CSS corretta
- [ ] Verificare con Playwright (spazio ridotto dopo il titolo)
- [ ] Commit & push

**Done when:** Lo spazio tra il titolo e l'inizio delle barre è ridotto a un gap ragionevole (~8-12px).

---

## M49: Fix legend — spacing e bullet colore

**Why:** Due problemi nella legend: (1) troppo spazio bianco tra l'ultima barra e la legend, (2) i bullet prima dei label sono neri sottili invece che nei colori della palette (blu/arancione/ecc).

**Approach:**
1. **Spacing**: ridurre `margin-top` della legend (ora 24px, troppo)
2. **Bullet colorati**: Charts.css usa `legend-circle` / `legend-square` / ecc. come classi per la forma. Per i colori, le `<li>` devono avere una regola `::before` con `background: var(--color-N)`. Generare nel transform_charts le classi sui `<li>` (es. `.legend-item-1`, `.legend-item-2`) e aggiungere CSS per applicare i colori della palette.

**Tasks:**
- [ ] Ridurre margin-top della legend (es. 12px)
- [ ] In `transform_charts`, aggiungere classi numerate ai `<li>` della legend
- [ ] CSS: regole per i bullet colorati con var(--md2-color-N)
- [ ] Test: unit — legend html contiene classi numerate
- [ ] Test: unit — CSS contiene regole per bullet colorati
- [ ] Verificare con Playwright
- [ ] Commit & push

**Done when:** La legend è vicina al chart e i bullet mostrano i colori della palette corrispondenti alle serie dati.
