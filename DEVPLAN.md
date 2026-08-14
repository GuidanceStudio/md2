# DEVPLAN — Test Suite per md2

Closed milestones M16–M108 (except M29, M64 (both), M70–M75, M88–M92, M107 — not closed, see below) are archived in `DEVPLAN_ARCHIVE.md`.

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

## Milestone 72: Pie chart — value labels inside slices ✅

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

## Milestone 73: Border around chart wrapper ✅

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

## Milestone 74: Line/area — segment model (N-1 tds for N data points) ✅

**Why:** Attualmente il primo td di una line/area disegna una linea piatta dal bordo sinistro al centro del proprio td (artefatto di `--start = --size` introdotto in M69). Visivamente sembra che il valore fosse "costante prima di Q1", cosa falsa. Stesso problema simmetrico al bordo destro per l'ultimo punto: la linea va oltre il centro dell'ultimo td fino al bordo destro.

**Approach:** spostare i punti del primo e ultimo td al centro del td via `padding-left: 50%` sul primo td e `padding-right: 50%` sull'ultimo. Charts.css disegna la linea solo nel content-box del td → la linea del primo td occupa solo la metà destra (da Q1 verso Q2), e l'ultimo solo la metà sinistra (da Qn-1 verso Qn). Niente segmenti fantasma.

I td centrali si spartiscono lo spazio rimanente uniformemente — le x-label restano centrate sui punti dati grazie al flex della `.md2-chart-xlabels`.

**Tasks:**
- [ ] `style.css`: `.md2-chart .charts-css.line tbody tr td:first-child, .md2-chart .charts-css.area tbody tr td:first-child { padding-left: 50%; box-sizing: border-box; }` e simmetrico `:last-child { padding-right: 50% }`
- [ ] Verificare con la struttura HTML reale: ogni `<tr>` contiene un singolo `<td>` (single dataset) o multipli (multi dataset). Per multi-dataset, il selettore `:first-child` / `:last-child` agisce per `tr`, quindi tutte le serie del primo td sono shiftate insieme. ✓ Corretto.
- [ ] Test unit: HTML line/area generato non è cambiato (nessun test sul markup); il fix è puramente CSS
- [ ] Test CSS: la regola `.charts-css.line tbody tr td:first-child` esiste con `padding-left: 50%`
- [ ] Test CSS: simmetrico per `:last-child`
- [ ] Test visuale Playwright: misurare che la x del primo punto disegnato (estratto dall'`::before` clip-path o simile) coincide con il centro del primo td. Difficile da automatizzare → screenshot e verifica manuale
- [ ] Rigenerare example, screenshot di tutti i line/area
- [ ] Commit & push

**Done when:**
- Nei chart "User Growth by Segment", "Projected User Growth" e "Event Pipeline Throughput" non c'è più segmento piatto sotto Q1/00:00
- L'ultimo punto non sfora oltre il centro del suo td
- I punti restano allineati alle x-label
- Tutti i test passano

## Milestone 75: Unify area into `line filled` modifier ✅

**Why:** Area chart è oggi un tipo separato (`:::chart area`) ma condivide quasi 100% del codepath con line — ogni fix M67-M73 ha dovuto essere applicato a entrambi. Unificarli riduce la superficie API, dimezza i test di line/area, e semplifica la documentazione. Area resta utile ma come *variante visiva* di line, attivata da un modifier `filled`.

**Approach:** estendere il parser di `:::chart` per accettare un secondo token come modifier. Sintassi:
```
:::chart line filled
| ... |
:::
```
Internamente:
- Il modifier `filled` viene catturato e mappato a una classe CSS aggiuntiva sul `<table>`, es. `md2-line-filled`.
- CSS: `.md2-chart .charts-css.line.md2-line-filled td::before { background: var(--color, currentColor); /* riempi sotto la linea */ }` — riprende lo stile di `.charts-css.area`.
- `:::chart area` resta come alias deprecato che mappa internamente a `line + filled`. Print a stderr una volta per build se viene usato.
- Aggiornare `examples/example.md`: convertire `:::chart area` esistenti in `:::chart line filled`.

**Tasks:**
- [ ] `core.py`: parsing del modifier dopo `chart_type` nel `:::chart` directive
- [ ] `core.py`: se `chart_type == "area"`, normalizzare a `line + filled` e stampare deprecation warning
- [ ] `core.py`: emettere classe `md2-line-filled` sul `<table>` quando filled è attivo
- [ ] `style.css`: regola `.md2-chart .charts-css.line.md2-line-filled` che riproduce il fill di area (clip-path / gradient sotto la linea)
- [ ] Aggiornare `examples/example.md`: `:::chart area` → `:::chart line filled`
- [ ] Test unit: `:::chart line filled` produce table con classi `charts-css line md2-line-filled`
- [ ] Test unit: `:::chart area` continua a funzionare (alias) e produce lo stesso markup di `:::chart line filled`
- [ ] Test unit: `:::chart line` (no filled) NON ha la classe `md2-line-filled`
- [ ] Test unit: deprecation warning emesso quando si usa `:::chart area`
- [ ] Test visuale Playwright: screenshot di `:::chart line filled` ha lo stesso look del vecchio `:::chart area`
- [ ] README: aggiornare la sintassi documentata
- [ ] Commit & push

**Done when:**
- `:::chart line filled` produce un line chart con riempimento sotto la curva, identico visivamente al vecchio area
- `:::chart area` continua a funzionare con deprecation warning
- Una sola lista di test/regole CSS gestisce entrambi
- README aggiornato
- Tutti i test passano

---

## Milestone 88: X-labels separazione visiva netta dal chart-body ✅

**Problema:**
Dopo M85 i label X di column/bar sono in un `<div class="md2-chart-xlabels">` sibling con `margin-top: 6px`. Quando i bar si estendono fino al body-bottom (caso negativi: dominio `[-20000, 60000]` per il cashflow Guidance), i label X "toccano" visivamente la base delle barre. Senza un separatore, sembrano in sovrapposizione (osservato il 06/05/2026 sullo slide cashflow: "Maggio" e il data label `-2623` finiscono alla stessa Y).

**Approccio:**
- Aumentare `margin-top` di `.md2-chart-xlabels` da 6px a 16px (più respiro tra fine bar e label).
- Aggiungere un bordo inferiore al `.md2-chart-body` (baseline visiva) per delimitare chiaramente la fine del chart area, usando `border-bottom: 1px solid var(--md-border)` o equivalente coerente con il tema.
- Print mode (M77-M79): verificare che il bordo non sparisca o si mostri male in stampa.

**Tasks:**
- [ ] Test TDD (CSS): `.md2-chart-xlabels` ha `margin-top` ≥ 14px.
- [ ] Test TDD (CSS): `.md2-chart-body` ha `border-bottom` definito (non `none`).
- [ ] Test TDD (CSS): print rule `@media print` non azzera/altera il border-bottom in modo problematico.
- [ ] Implementare modifiche in `style.css`.
- [ ] Verifica visiva: rigenerare `examples/example.html` e controllare slide cashflow Guidance.

**Done when:**
- Test passano.
- Slide cashflow: label X chiaramente separati dal chart con baseline visibile.

---

## Milestone 89: Data labels — collision avoidance con xlabels ✅

**Problema:**
Le data label `outside` (M86) per bar negative sono posizionate da Charts.css sotto la barra. Quando la barra negativa arriva fino al body-bottom (es. -19597 vicinissimo a -20000 tick), il label "outside" finisce ALLA STESSA Y dei label X (xlabels div sotto body), causando collision visiva. Esempio cashflow: `-2623` (Maggio Cash burn) si sovrappone al label "Maggio".

**Approccio:**
- Quando una bar è negativa con `--size > 0.50` (estende per oltre metà del range), posizionare il data label SOPRA la bar (sopra il valore, vicino al zero baseline) invece che sotto.
- Implementazione lato `core.py`: emit `<span class="data outside above">` per bar negative grandi; CSS `data.outside.above { top: 0; ... }` posiziona sopra.
- Per bar negative piccole (< 0.50), il label resta sotto (l'esistente outside).

**Tasks:**
- [ ] Test TDD: bar negativa con `--size > 0.5` → span `data outside above`.
- [ ] Test TDD: bar negativa con `--size < 0.5` → span `data outside` (no above).
- [ ] Test TDD: CSS `.data.outside.above` posiziona il label sopra la bar.
- [ ] Implementare in `core.py` la condizione.
- [ ] Aggiungere CSS rule.

**Done when:**
- Test passano.
- Cashflow: `-19597` mostrato sopra la base della barra invece che sotto, niente collision con "Luglio".

---

## Milestone 90: Compact chart per fit in single A4 landscape page ✅

**Problema:**
Il chart con title + body 300px + xlabels + legend ora supera l'altezza utile di una slide A4 landscape, causando overflow su pagina nuova (osservato il 06/05/2026: nota italica del cashflow finita su slide 8 vuota).

**Approccio:**
- Ridurre l'altezza del chart-body da `min(300px, 40vh)` a `min(260px, 36vh)` (≈13% più compatto).
- Verificare che la riduzione non comprometta la leggibilità del Y-axis (5 tick devono restare distinti).
- Print mode: verificare che la nuova altezza valga anche in stampa (non solo a schermo).

**Tasks:**
- [ ] Test TDD (CSS): `.md2-chart .charts-css.column` ha height `min(260px, ...)`.
- [ ] Test TDD (CSS): `.md2-chart-body` ha la stessa height per coerenza flex.
- [ ] Verifica visiva: deck Guidance rigenerato → 10 pagine (non 11).
- [ ] Implementare modifiche `style.css`.

**Done when:**
- Test passano.
- Deck Guidance non eccede 10 pagine.
- Y-axis rimane leggibile.

---

## Milestone 91: `--size: 0` cells — niente data span (zero label hidden) ✅

**Problema:**
Per categorie con valore 0, M81 ha rimosso il guard `if num_val != 0` e M87 ha aggiunto la classe `.data.zero`. Ma con `--size: 0` Charts.css non sa dove posizionare lo span (cella collassa a 0px) e lo span finisce in posizioni casuali (sotto il chart, fuori dal card). Esempio reale: slide 5 aging, fascia 31-60 gg con valore 0 → `0` ghost appare in fondo al card lontano dalla cella.

**Approccio:**
Per chart con Y-axis (`has_yaxis=True`) e `num_val == 0`, NON emettere il `<span class="data zero">` proprio. La categoria è comunque visibile attraverso il label X (la fascia "31-60 gg" è ancora nell'asse). Il bar invisibile + label X bastano per comunicare "questa categoria a zero".

**Tasks:**
- [ ] Test TDD: chart `[10, 0, 5]` → `<td>` per il valore 0 ha `--size: 0` ma NESSUN `<span class="data">` interno.
- [ ] Test TDD: chart `[10, 5, 8]` (no zero) → tutti i `<td>` hanno il loro `<span class="data">`.
- [ ] Test TDD: chart pie `[30, 0, 70]` → comportamento di Charts.css preservato (pie ha logica diversa).
- [ ] Implementare in `core.py`: nel branch `if show_data`, escludere il caso `num_val == 0 and has_yaxis and not is_pie`.

**Done when:**
- Test passano.
- Slide 5 aging: niente più "0" ghost in posizione strana.

---

## Milestone 92: install.sh — sync template utente dopo reinstall binario ✅

**Problema:**
`install.sh` di md2 esegue `uv tool install . --force --reinstall` che reinstalla il binario `md2` nel `~/.local/bin/`. **Non sincronizza** i template utente in `~/.md2/templates/`. md2 al primo avvio copia i template dalla source, ma in upgrade successivi i template restano la versione vecchia. Risultato: modifiche CSS in `md2/templates/` NON arrivano al rendering reale.

Bug confermato il 06/05/2026: due ore spese a "patchare" CSS che non si applicava al deck Guidance perché i template utente erano in cache.

**Approccio:**
Aggiungere alla fine di `install.sh` uno step che sincronizza `~/.md2/templates/` con la source:

```bash
if [ -d "$HOME/.md2/templates" ]; then
    cp -r ./md2/templates/* "$HOME/.md2/templates/"
    echo "Template utente sincronizzati."
fi
```

**Tasks:**
- [ ] Test TDD: dopo `bash install.sh`, `~/.md2/templates/default/style.css` ha contenuto identico a `md2/md2/templates/default/style.css`.
- [ ] Implementare lo step di sync in `install.sh`.
- [ ] Documentare in `README.md` che l'install sincronizza anche i template.

**Done when:**
- Test passa.
- Modifiche CSS future arrivano automaticamente al rendering reale dopo `bash install.sh`.

## M107: Mobile media query leaks into print — qualify con `screen and` ✅

**Bug osservato:** sul deck telco (`<deck-project>/`)
le slide con tabelle markdown vengono renderizzate nel PDF stampato
con una scrollbar grigia visibile sotto la tabella e la colonna
più a destra **troncata**. Causa: il blocco
`@media (max-width: 768px)` in `templates/default/style.css:628-651`
non specifica il media-type `screen`, quindi fa match anche in print.
Il layout viewport di headless Chromium durante `--print-to-pdf` cade
a/sotto 768px (default cambiato tra versioni di Chromium), quindi le
regole mobile si attivano:

```css
@media (max-width: 768px) {
    /* ... */
    .slide table {
        display: block; overflow-x: auto; white-space: nowrap;
        margin: 30px 0; width: 100%;
    }
    .md2-columns { flex-direction: column; }
}
```

`.slide table { display: block; overflow-x: auto; white-space: nowrap }`
+ tabella più larga del foglio → Chrome stampa la scrollbar nel PDF e
clippa i contenuti oltre il bordo destro. Identico failure mode già
documentato sul lato deck per `.md2-columns` (vedi
`il DEVPLAN della skill deck` M16) e ora anche per
le tabelle (M17). Entrambi i workaround a valle in `render.sh` sono
necessari solo perché md2 non scope-a queste regole a `screen`.

**Approccio:**
Il fix è una singola modifica: aggiungere `screen and` al media query.
È l'idioma CSS standard per regole mobile-only — `screen` esclude
`print`, `speech`, `all`. Tutte le regole nel blocco sono per loro
natura screen-only (sidebar, font sizes responsivi, layout columns
verticali per touchscreen): nessuna di esse ha senso applicata in
print. Lo stesso media query a `(max-width: 1024px)` poco sopra ha
gli stessi sintomi potenziali; vale la stessa fix.

**Tasks:**
- [x] `md2/templates/default/style.css:628`: cambiato
      `@media (max-width: 768px) {` in
      `@media screen and (max-width: 768px) {`.
- [x] `md2/templates/default/style.css:621`: per coerenza, cambiato
      anche `@media (max-width: 1024px) {` in
      `@media screen and (max-width: 1024px) {`. Riguarda solo la
      sidebar / `#main` padding — nessun impatto funzionale in print
      ma elimina la classe di bug per future regole aggiunte al blocco.
- [x] `bash install.sh` per propagare la fix all'installazione
      `~/.local/share/uv/tools/md2-presenter/` e a `~/.md2/templates/`.
      Verificato con `grep`: entrambi i breakpoint ora hanno `screen and`.
- [x] Smoke test (in modalità combinata con il defensive override M17):
      re-rendered `<deck-project>/presentation.md`,
      l'HTML generato contiene `@media screen and (max-width: 768px)`
      confermando che la fix upstream è in vigore. La verifica
      empirica dell'isolamento (md2 da solo, senza l'override
      render.sh) non è stata eseguita esplicitamente — il cambio è
      una singola parola CSS, la correttezza è teorica. Le PDF
      generate mostrano tabelle complete senza scrollbar.
- [ ] Far girare la full test suite (`tests/test_all.sh`) per cercare
      regressioni residue. Da fare prima del push.
- [ ] Push.

**Done when:**
- Il blocco mobile media query è qualificato `screen and`.
- Re-render del deck telco mostra tabelle complete senza scrollbar
  e senza colonne troncate, indipendentemente dal workaround in
  `render.sh`.

---

## M109: Archive closed milestones — DEVPLAN.md e DEVPLAN_UI.md ✅

**Why:** `DEVPLAN.md` (86 milestone headings) e `DEVPLAN_UI.md` (15) sono
cresciuti a ~28.300 parole totali, in gran parte lavoro chiuso che
nessuno rilegge. `forge-flow` (`DESIGN.md` §Archive) prescrive di
comprimere ogni milestone chiuso a un puntatore `MNN | title | date |
sha`, lasciando che la sha in git porti al dettaglio.

**Approccio:** per ogni heading col done marker, verificare che tutti i
task siano `- [x]`; qualunque `- [ ]`/`- [~]` residuo esclude la
milestone (rimane nel piano attivo). Per ogni milestone chiusa, trovare
la commit di shipping via `git log --oneline --all | grep` e `git log -S
-- <path>`, verificarla con `git cat-file -e`, poi spostarla nel file di
archivio corrispondente e cancellarla dal piano attivo.

**Tasks:**
- [x] Enumerare le milestone con done marker in entrambi i file (98
      heading marcate ✅ in totale)
- [x] Escludere quelle con task non ticchettati: M29, M64 (entrambi i
      blocchi, nessuno dei due porta ✅), M70-M75, M88-M92, M107 — 13
      milestone in `DEVPLAN.md` restano nel piano attivo nonostante il
      marker
- [x] Trovare e verificare (`git cat-file -e`) la sha di shipping per le
      85 milestone effettivamente chiuse (70 in `DEVPLAN.md`, 15 in
      `DEVPLAN_UI.md`); per M46-M49 la sha del commit che introduce
      l'entry (`913fb06`) non contiene il CSS — verificato che il CSS
      reale è in `76f74aa` (commit M50-55) per confronto diretto del
      diff con Approach/Done-when di ciascuna
- [x] Scrivere `DEVPLAN_ARCHIVE.md` (70 righe) e
      `DEVPLAN_UI_ARCHIVE.md` (15 righe), newest-last, con header che
      spiega la sha come puntatore
- [x] Rimuovere i blocchi archiviati dai piani attivi, lasciare un
      pointer line in cima a ciascuno
- [x] Diff script sui set di ID prima/dopo (99 ID unici, active+archive)
      — nessuno perso, nessuno inventato
- [x] Suite di test invariata (nessuna modifica a codice applicativo)

**Done when:** ogni ID presente prima compare o nel piano attivo o
nell'archivio; nessuna milestone con task non ticchettati è stata
archiviata; entrambi i file di archivio verificati riga per riga contro
`git cat-file -e`.

