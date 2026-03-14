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

## Milestone 21: Ristrutturazione a pacchetto + refactoring Jinja2

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

## Milestone 22: Sistema template utente — `--template` e `--init-templates`

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

## Milestone 23: README — documentazione sistema template

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
