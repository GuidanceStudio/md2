# DEVPLAN — Migliorie Grafiche Renderer Default

Tutte le modifiche vanno applicate in `md2.py`, nella funzione `generate_css()` e dove necessario nel rendering HTML.

---

## Milestone 1: Tipografia ✅

### 1.1 Line-height del body
- Portare il `line-height` del contenuto slide da `1.3` a `1.6` per migliorare la leggibilità
- Mantenere `1.7` per il mobile

### 1.2 Font-size con `clamp()`
- Sostituire le unità `vh` con `clamp()` per evitare dimensioni estreme su monitor non standard:
  - `h2`: `clamp(1.4rem, 3vh, 2.2rem)`
  - `h3`: `clamp(1.15rem, 2.2vh, 1.6rem)`
  - `h4`: `clamp(1rem, 1.8vh, 1.3rem)`
  - `p, li, td`: `clamp(0.95rem, 2vh, 1.25rem)`
  - `pre, code` (blocchi): `clamp(0.8rem, 1.5vh, 1rem)`

### 1.3 Font-weight differenziato per heading
- `h2`: `font-weight: 700`
- `h3`: `font-weight: 600`
- `h4`: `font-weight: 500`

### 1.4 Font monospace esplicito
- Specificare uno stack di font monospace per `<code>` e `<pre>`:
  `"Fira Code", "JetBrains Mono", "Cascadia Code", "Consolas", monospace`

---

## Milestone 2: Colori e Contrasto ✅

### 2.1 Contrasto testo principale
- Cambiare `--text-color` da `#444` a `#333` per migliorare il rapporto di contrasto

### 2.2 Sidebar più distinguibile
- Aggiungere `box-shadow: 2px 0 8px rgba(0,0,0,0.06)` alla sidebar
- In dark mode: `box-shadow: 2px 0 8px rgba(0,0,0,0.3)`

### 2.3 Blockquote con colore di accento
- Aggiungere un colore dedicato per il bordo sinistro del blockquote: `--blockquote-accent: #3498db`
- Applicare `border-left: 4px solid var(--blockquote-accent)` al blockquote
- In dark mode: `--blockquote-accent: #5dade2`

### 2.4 Dark mode con toni più caldi
- Cambiare `--text-color` dark da `#e0e0e0` a `#c9d1d9` (tono leggermente blu, stile GitHub)
- Cambiare `--bg-color` dark da `#1e1e1e` a `#0d1117` (più profondo, meno grigio)
- Cambiare `--sidebar-bg` dark da `#252526` a `#161b22`
- Cambiare `--code-bg` dark da `#2d2d2d` a `#1c2128`

---

## Milestone 3: Layout e Spaziatura ✅

### 3.1 Max-width sul contenuto principale
- Aggiungere `max-width: 960px` e `margin: 0 auto` al contenuto dentro `#main` per evitare righe troppo lunghe su schermi ultrawide

### 3.2 Spaziatura tra elementi nelle slide
- Aumentare `margin-bottom` su `p` a `1em` (attuale è il default del browser)
- `ul, ol`: `margin-bottom: 1em`
- `pre`: `margin: 1.2em 0`

### 3.3 Separatore tra slide
- Cambiare il bordo da `1px dashed` a `1px solid` con colore più leggero
- Aumentare il padding verticale tra slide: `padding: 60px 0 40px 0`

### 3.4 Cover slide: separatore decorativo
- Aggiungere un `<hr>` stilizzato o un `border-bottom` sotto il titolo h1 della cover:
  `width: 80px; height: 3px; background: #3498db; border: none; margin: 20px auto 30px;`

---

## Milestone 4: Elementi Specifici ✅

### 4.1 Tabelle: border-radius
- Aggiungere `border-radius: 8px` e `overflow: hidden` alle tabelle per coerenza con le immagini

### 4.2 Code block migliorati
- Aggiungere `border: 1px solid var(--table-border)` ai code block per definirli meglio
- Aggiungere `line-height: 1.5` ai blocchi `<pre>` per leggibilità del codice

### 4.3 Link nella sidebar: indicatore slide attiva
- Aggiungere una classe `.active` ai link della sidebar con stile:
  `border-left: 3px solid #3498db; background: var(--sidebar-hover); font-weight: 600;`
- Implementare JavaScript `IntersectionObserver` per aggiornare la slide attiva durante lo scroll

### 4.4 Immagini: hover interattivo
- Aggiungere `transition: transform 0.2s ease, box-shadow 0.2s ease`
- Hover: `transform: scale(1.02); box-shadow: 0 6px 20px rgba(0,0,0,0.15)`

---

## Milestone 5: Animazioni e UX ✅

### 5.1 Scroll-snap sulle slide
- Aggiungere `scroll-snap-type: y mandatory` su `#main`
- Aggiungere `scroll-snap-align: start` su ogni `.slide`
- Assicurarsi che ogni slide abbia `min-height: 100vh`

### 5.2 Barra di progresso
- Aggiungere un elemento `<div id="progress-bar">` fisso in cima alla pagina
- Stile: `height: 3px; background: #3498db; position: fixed; top: 0; left: 0; z-index: 1100; transition: width 0.2s;`
- JavaScript: aggiornare la larghezza in base alla posizione di scroll (`scrollTop / scrollHeight * 100%`)

### 5.3 Theme toggle con icona SVG
- Sostituire l'emoji `🌗` con due icone SVG inline (sole/luna)
- Toggle tra le due icone a seconda del tema attivo
- Dimensione icona: `20px × 20px`, colore: `currentColor`

---

## Milestone 6: Responsive ✅

### 6.1 Breakpoint intermedio per tablet (1024px)
- Aggiungere `@media (max-width: 1024px)`:
  - Sidebar: `width: 220px` (ridotta da 280px)
  - Main padding: `30px 40px` (ridotto da 40px 60px)
  - Font-size leggermente ridotte

### 6.2 Menu hamburger con SVG
- Sostituire il carattere Unicode `☰` con un'icona SVG inline (3 linee)
- Dimensione: `24px × 24px`, colore: `currentColor`
- Aggiungere animazione di transizione hamburger → X quando il menu è aperto

---

## Milestone 9: Markdown Parser — Estensioni mancanti ✅

### 9.1 Fenced code blocks
- Aggiungere l'estensione `fenced_code` alla chiamata `markdown.markdown()` in `render_presentation()`
- Blocchi ` ``` ` devono produrre `<pre><code>` correttamente
- Supportare l'attributo di linguaggio (` ```python `) per futuri syntax highlighting

### 9.2 Autolink
- Aggiungere un'estensione o post-processing per convertire URL nudi (`https://...`) in `<a href="...">` cliccabili
- Usare l'estensione custom o regex: trovare URL che non sono già dentro un tag `<a>` e wrappare

### 9.3 Footnotes
- Aggiungere l'estensione `footnotes` al parser markdown
- Stilizzare le footnote nel CSS: font-size ridotto, separatore `<hr>` sottile prima delle note

---

## Milestone 10: Tipografia Cover e Contenuto ✅

### 10.1 Titolo cover con `clamp()`
- Cambiare `.cover h1` da `font-size: 3.5rem` fisso a `clamp(1.8rem, 5vw, 3.5rem)` per evitare overflow su schermi stretti

### 10.2 Allineamento testo cover
- Aggiungere `text-align: center` al `<div>` contenuto della cover per coerenza con il layout centrato flex

---

## Milestone 11: Navigazione e UX avanzata ✅

### 11.1 Navigazione da tastiera
- Aggiungere listener JavaScript per le frecce:
  - `ArrowDown` / `ArrowRight` / `PageDown`: scroll alla slide successiva
  - `ArrowUp` / `ArrowLeft` / `PageUp`: scroll alla slide precedente
  - `Home`: torna alla cover
  - `End`: vai all'ultima slide
- Usare `scrollIntoView({ behavior: 'smooth' })` sugli elementi `.slide`

### 11.2 Sidebar collassabile su desktop
- Aggiungere un bottone toggle sulla sidebar (icona SVG `«`/`»`)
- Click: sidebar si riduce a `0` con transizione, il main prende tutto lo spazio
- Salvare la preferenza in `localStorage`

### 11.3 Indicatore slide corrente
- Aggiungere un elemento fisso in basso a destra che mostra "2 / 4" (slide corrente / totale)
- Aggiornato dall'`IntersectionObserver` già presente
- Stile discreto: font-size piccolo, colore attenuato, `opacity: 0.6`

---

## Milestone 12: Stile e polish ✅

### 12.1 Print stylesheet
- Aggiungere `@media print` con:
  - Nascondere sidebar, theme-toggle, menu-toggle, progress-bar, indicatore slide
  - Rimuovere `min-height: 100vh` dalle slide
  - Ogni slide come `page-break-after: always`
  - Layout single-column, `max-width: 100%`
  - Colori forzati a nero su bianco

### 12.2 Favicon inline
- Aggiungere un `<link rel="icon">` con data-uri SVG nel `<head>` per evitare il 404 nel browser
- Icona semplice: un quadrato con "M" stilizzato o un documento

### 12.3 Transizione contenuto slide
- Aggiungere un'animazione CSS di fade-in sul `.content` delle slide quando entrano nel viewport
- Usare `@keyframes fadeIn` con `opacity: 0 → 1` e `transform: translateY(10px) → 0`
- Triggare via `IntersectionObserver` aggiungendo classe `.visible`

---

## Milestone 13: Meta e struttura HTML ✅

### 13.1 Attributo `lang` dinamico
- Aggiungere un parametro opzionale `--lang` al CLI (default: `it`)
- Usare il valore nel tag `<html lang="...">`

### 13.2 Meta tag Open Graph
- Aggiungere nel `<head>`:
  - `<meta property="og:title" content="...">` (titolo della presentazione)
  - `<meta property="og:type" content="website">`
  - `<meta property="og:description" content="...">` (prime righe del contenuto cover)
- Opzionale: `<meta name="description" content="...">`

---

## Milestone 14: Test per le nuove milestone (9-13) ✅

### 14.1 Unit test aggiuntivi — `test_render_presentation.py`

- **test_fenced_code_blocks**: ` ```code``` ` produce `<pre><code>`
- **test_fenced_code_with_language**: ` ```python ` produce `<code class="language-python">` o simile
- **test_autolink_url**: URL nudi `https://example.com` diventano `<a href="...">`
- **test_autolink_no_double_wrap**: URL già in `[testo](url)` non vengono wrappati due volte
- **test_footnotes_rendered**: `[^1]` e `[^1]: testo` producono footnote HTML
- **test_cover_text_centered**: il contenuto cover contiene `text-align: center`

### 14.2 Unit test aggiuntivi — `test_generate_css.py`

- **test_print_stylesheet**: il CSS contiene `@media print`
- **test_print_hides_sidebar**: nel `@media print` la sidebar ha `display: none`
- **test_print_page_break**: nel `@media print` le slide hanno `page-break-after`
- **test_cover_h1_clamp**: `.cover h1` usa `clamp()` per il font-size
- **test_slide_indicator_style**: il CSS contiene regole per `#slide-indicator`
- **test_sidebar_collapse_button**: il CSS contiene regole per il toggle sidebar desktop
- **test_fade_in_animation**: il CSS contiene `@keyframes fadeIn`

### 14.3 Unit test aggiuntivi — `test_main_cli.py`

- **test_lang_flag_default**: senza `--lang`, l'HTML ha `lang="it"`
- **test_lang_flag_custom**: con `--lang en`, l'HTML ha `lang="en"`

### 14.4 Live test aggiuntivi — `test_ui_improvements_e2e.py`

- **test_output_has_keyboard_navigation**: il JavaScript contiene `ArrowDown` e `ArrowUp`
- **test_output_has_slide_indicator**: l'HTML contiene `id="slide-indicator"`
- **test_output_has_print_styles**: il CSS contiene `@media print`
- **test_output_has_favicon**: l'HTML contiene `<link rel="icon"`
- **test_output_has_og_tags**: l'HTML contiene `og:title`
- **test_output_has_lang_attribute**: l'HTML contiene `lang="it"` (default)
- **test_fenced_code_e2e**: markdown con ` ``` ` produce `<pre><code>` nell'HTML finale
- **test_autolink_e2e**: URL nudi nell'HTML finale sono cliccabili (`<a href=`)

---

## Milestone 15: Sidebar UX — default aperta, toggle in alto, shortcut guide

### 15.1 Sidebar aperta di default
- Rimuovere il ripristino da `localStorage` all'avvio che poteva lasciare la sidebar chiusa
- La sidebar parte sempre aperta; lo stato collapsed viene comunque salvato in `localStorage` per la sessione corrente, ma al primo caricamento è sempre visibile

### 15.2 Pulsante toggle in alto nella sidebar
- Spostare il bottone `«`/`»` dalla posizione attuale (fixed a metà altezza sul bordo della sidebar) all'interno della sidebar, in alto
- Stile: riga in cima alla sidebar con il bottone allineato a destra, padding coerente con i link
- Quando la sidebar è collapsed, il bottone diventa un'icona fixed in alto a sinistra (`»`) per riaprirla
- Assicurarsi che su mobile il bottone resti nascosto (si usa l'hamburger)

### 15.3 Shortcut guide in fondo alla sidebar
- Aggiungere un blocco `<div id="sidebar-shortcuts">` in fondo alla sidebar (dopo la lista link, prima del toggle)
- Contenuto: mini-guida con le scorciatoie da tastiera, in formato compatto:
  - `↓` `→` Slide successiva
  - `↑` `←` Slide precedente
  - `Home` Prima slide
  - `End` Ultima slide
- Stile: font-size ridotto (`0.75rem`), colore attenuato (`opacity: 0.5`), padding `15px 20px`, bordo superiore sottile
- La guida scompare quando la sidebar è collapsed
- Su mobile: nascosta (troppo piccola per essere utile)

### 15.4 Test

**Unit test — `test_generate_css.py`:**
- **test_sidebar_shortcuts_style**: il CSS contiene regole per `#sidebar-shortcuts`
- **test_sidebar_toggle_top**: il CSS per `#sidebar-toggle` non usa più `top: 50%`

**Unit test — `test_render_presentation.py`:**
- **test_sidebar_has_shortcuts_guide**: il body_html contiene `id="sidebar-shortcuts"`
- **test_sidebar_shortcuts_content**: il body_html contiene le stringhe degli shortcut (es. `↓`, `↑`, `Home`, `End`)

**Live test — `test_ui_improvements_e2e.py`:**
- **test_sidebar_open_by_default**: l'HTML generato NON contiene codice JS che aggiunge `collapsed` all'avvio
- **test_sidebar_has_shortcut_guide_e2e**: l'HTML contiene `sidebar-shortcuts` con testo delle scorciatoie

---

## Milestone 7: Unit Test (`tests/unit/`) ✅

Test delle funzioni pure, senza I/O su disco.

### 7.1 `test_sanitize_html.py` — Sanitizzazione HTML

- **test_strips_script_tags**: `<script>alert('xss')</script>` viene rimosso
- **test_strips_onclick**: attributi event handler (`onclick`, `onerror`) vengono rimossi
- **test_allows_safe_tags**: tag consentiti (`p`, `h1`, `ul`, `table`, `code`, `pre`, `img`) passano intatti
- **test_allows_iframe**: `<iframe src="...">` viene preservato (usato per embed)
- **test_allows_style_attribute**: attributo `style` su elementi consentiti viene mantenuto
- **test_allows_img_attributes**: `src`, `alt`, `width`, `height` su `<img>` vengono mantenuti
- **test_strips_dangerous_href**: `href="javascript:..."` viene gestito
- **test_empty_input**: stringa vuota restituisce stringa vuota
- **test_nested_dangerous_tags**: `<div><script>...</script></div>` rimuove solo lo script, mantiene il div
- **test_allows_class_and_id**: attributi `class` e `id` vengono mantenuti su qualsiasi tag

### 7.2 `test_generate_css.py` — Generazione CSS

**Funzionalità esistenti:**
- **test_default_theme**: senza parametri usa i colori di `DEFAULT_THEME` (`#f9f9f9`, `#444`, ecc.)
- **test_custom_theme_override**: passando un dict parziale, i valori vengono sovrascritti
- **test_custom_theme_full**: passando tutti i valori, nessun default rimane
- **test_contains_dark_mode**: il CSS contiene le regole `body.dark-mode`
- **test_contains_responsive**: il CSS contiene la media query `@media (max-width: 768px)`
- **test_contains_css_variables**: il CSS contiene `:root` con tutte le variabili attese
- **test_contains_sidebar_styles**: il CSS contiene regole per `#sidebar`
- **test_contains_slide_styles**: il CSS contiene regole per `.slide`
- **test_contains_cover_styles**: il CSS contiene regole per `.cover`
- **test_contains_theme_toggle**: il CSS contiene regole per `#theme-toggle`

**Migliorie grafiche (dopo implementazione Milestone 1-6):**
- **test_clamp_font_sizes**: i font-size usano `clamp()` invece di unità `vh` nude
- **test_font_weight_headings**: h2 ha `700`, h3 ha `600`, h4 ha `500`
- **test_monospace_font_stack**: `<code>` usa lo stack `"Fira Code"...monospace`
- **test_line_height_body**: il contenuto slide ha `line-height: 1.6`
- **test_text_color_contrast**: `--text-color` è `#333` (non `#444`)
- **test_sidebar_box_shadow**: la sidebar ha `box-shadow`
- **test_blockquote_accent**: blockquote usa `--blockquote-accent` per il bordo sinistro
- **test_dark_mode_colors_updated**: dark mode usa i nuovi colori (`#0d1117`, `#c9d1d9`, ecc.)
- **test_slide_border_solid**: il separatore slide è `solid` (non `dashed`)
- **test_table_border_radius**: le tabelle hanno `border-radius: 8px`
- **test_code_block_border**: i code block hanno `border: 1px solid`
- **test_image_hover**: le immagini hanno `transition` e regole `:hover`
- **test_sidebar_active_style**: esiste lo stile per `#sidebar a.active`
- **test_scroll_snap**: `#main` ha `scroll-snap-type` e `.slide` ha `scroll-snap-align`
- **test_progress_bar_style**: il CSS contiene regole per `#progress-bar`
- **test_tablet_breakpoint**: esiste la media query `@media (max-width: 1024px)`
- **test_max_width_content**: il contenuto ha `max-width: 960px`

### 7.3 `test_render_presentation.py` — Logica di rendering

**Funzionalità esistenti:**
- **test_cover_title_extraction**: il primo `# Titolo` diventa il titolo della presentazione
- **test_cover_default_title**: senza `# H1`, il titolo di default è `"Presentation"`
- **test_cover_content**: il testo sotto il titolo di copertina viene incluso nel body HTML
- **test_slide_splitting**: `---` separa correttamente le slide
- **test_slide_titles**: ogni `## H2` diventa il titolo della slide corrispondente
- **test_slide_default_title**: slide senza `## H2` riceve titolo `"Slide N"`
- **test_sidebar_contains_all_titles**: la sidebar contiene link a tutte le slide
- **test_sidebar_contains_cover_link**: la sidebar include il link alla copertina con `href="#cover"`
- **test_markdown_tables_rendered**: tabelle markdown vengono convertite in `<table>`
- **test_markdown_code_blocks_rendered**: blocchi di codice vengono convertiti in `<pre><code>`
- **test_markdown_lists_rendered**: liste `ul` e `ol` vengono convertite correttamente
- **test_markdown_links_rendered**: link `[testo](url)` vengono convertiti in `<a href="...">`
- **test_markdown_images_rendered**: `![alt](src)` viene convertito in `<img>`
- **test_markdown_blockquote_rendered**: `> testo` viene convertito in `<blockquote>`
- **test_markdown_inline_code_rendered**: `` `codice` `` viene convertito in `<code>`
- **test_empty_input**: input vuoto non genera errori, produce struttura valida
- **test_single_slide_no_separator**: input senza `---` produce solo la copertina
- **test_result_structure**: il risultato contiene le chiavi `title`, `body_html`, `css`
- **test_result_title_type**: `result["title"]` è una stringa
- **test_result_css_type**: `result["css"]` è una stringa non vuota
- **test_slide_ids_sequential**: le slide hanno id `slide-0`, `slide-1`, ecc.
- **test_cover_has_correct_classes**: la cover ha `class="slide cover"` e `id="cover"`
- **test_multiple_slides**: 5 slide producono 5 `<div class="slide"` + 1 cover
- **test_html_sanitized_in_slides**: tag `<script>` nel markdown vengono rimossi dall'output
- **test_custom_theme_passed_to_css**: passando un tema custom, il CSS riflette i colori

**Migliorie grafiche (dopo implementazione Milestone 4-5):**
- **test_progress_bar_in_html**: l'HTML generato contiene `id="progress-bar"` (dopo Milestone 5.2)
- **test_svg_theme_toggle**: l'HTML contiene SVG per il theme toggle (dopo Milestone 5.3)
- **test_svg_menu_toggle**: l'HTML contiene SVG per il menu hamburger (dopo Milestone 6.2)
- **test_intersection_observer_script**: l'HTML contiene il JavaScript per `IntersectionObserver` (dopo Milestone 4.3)

### 7.4 `test_main_cli.py` — Parsing CLI (senza scrivere file)

- **test_missing_file_exits**: file inesistente causa `sys.exit(1)`
- **test_no_arguments_exits**: nessun argomento causa errore argparse
- **test_output_filename_derived**: il file di output ha estensione `.html` al posto di `.md`

---

## Milestone 8: Live Test (`tests/live/`) ✅

Test end-to-end che leggono/scrivono file su disco. Usano `tmp_path` di pytest.

### 8.1 `test_conversion_e2e.py` — Conversione completa

- **test_example_file_converts**: `examples/example.md` viene convertito senza errori e produce un file `.html`
- **test_output_is_valid_html**: l'output contiene `<!DOCTYPE html>`, `<html`, `<head>`, `<body>`
- **test_output_contains_sidebar**: l'HTML generato contiene `id="sidebar"`
- **test_output_contains_theme_toggle**: l'HTML contiene il bottone `id="theme-toggle"`
- **test_output_contains_slides**: l'HTML contiene almeno un `<div class="slide"`
- **test_output_contains_cover**: l'HTML contiene `<div class="slide cover"`
- **test_output_contains_css**: l'HTML contiene un blocco `<style>` con CSS non vuoto
- **test_output_contains_javascript**: l'HTML contiene `<script>` con `toggleTheme` e `toggleMenu`
- **test_cli_generates_file**: eseguire `md2 file.md` da CLI crea effettivamente `file.html` su disco
- **test_cli_stdout_message**: l'output stdout contiene `"Success!"`

### 8.2 `test_edge_cases_e2e.py` — Casi limite end-to-end

- **test_empty_file**: un file `.md` vuoto produce comunque un HTML valido con struttura base
- **test_only_cover**: file senza `---` produce HTML con solo la copertina
- **test_unicode_content**: contenuto con emoji e caratteri Unicode (`日本語`, `🎉`) viene gestito correttamente
- **test_large_file**: file con molte slide (50+) viene processato senza errori e contiene tutte le slide
- **test_special_characters_in_title**: caratteri speciali (`<`, `>`, `&`, `"`) nel titolo vengono escaped
- **test_output_overwrites_existing**: se il file `.html` esiste già, viene sovrascritto senza errori
- **test_nested_markdown**: markdown complesso (liste dentro blockquote, codice dentro liste) viene renderizzato
- **test_multiple_separators_consecutive**: `---` ripetuti consecutivamente producono slide vuote senza crash
- **test_only_separators**: file con solo `---` produce struttura valida
- **test_xss_in_markdown**: contenuto con `<script>` nel markdown non appare nell'HTML finale

### 8.3 `test_ui_improvements_e2e.py` — Migliorie grafiche end-to-end (dopo Milestone 1-6)

- **test_output_has_progress_bar**: l'HTML contiene `id="progress-bar"`
- **test_output_has_svg_icons**: l'HTML contiene elementi `<svg` per toggle e hamburger
- **test_output_has_intersection_observer**: il JavaScript contiene `IntersectionObserver`
- **test_css_has_clamp**: il CSS nell'output usa `clamp(` per i font-size
- **test_css_has_scroll_snap**: il CSS contiene `scroll-snap-type`
- **test_css_has_tablet_breakpoint**: il CSS contiene `max-width: 1024px`
