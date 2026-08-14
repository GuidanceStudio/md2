# DEVPLAN — Archive

Closed milestones from `DEVPLAN.md`, compressed to a pointer. The sha is
the pointer to the detail — Why, Approach, tasks and Deviations all live
in that commit's diff and message; run `git show <sha>` to read them.
Ordered oldest-shipped first.

```
MNN | title | date | sha
```

M16 | Shortcut tastiera per toggle sidebar | 2026-03-14 | c1bba0f
M17 | Flag per tema dark di default | 2026-03-14 | f132246
M18 | Shortcut tastiera per toggle tema dark/light | 2026-03-14 | b100130
M19 | Sidebar scroll — lista slide scrollabile con istruzioni fisse in fondo | 2026-03-14 | 17e58f3
M20 | README — documentazione completa formato Markdown e funzionalità supportate | 2026-03-14 | 2ee2843
M21 | Ristrutturazione a pacchetto + refactoring Jinja2 | 2026-03-14 | bc6147c
M22 | Sistema template utente — `--template` e `--init-templates` | 2026-03-14 | 3c5c796
M23 | README — documentazione sistema template | 2026-03-14 | c37f149
M24 | Frontmatter — parsing metadata del documento | 2026-04-11 | ba28e9d
M25 | Sistema palette colori — file TOML + cascata | 2026-04-11 | 5a27289
M26 | Charts.css — embedding e direttiva `:::chart` | 2026-04-11 | 8ffbf2b
M27 | Documentazione e example — chart e palette | 2026-04-11 | 2fab1d7
M28 | Chart sizing — altezze e dimensioni sensate per tipo | 2026-04-11 | 61fb80b
M30 | Print-optimized CSS — stampa di chart, colonne e palette | 2026-04-11 | 49e7b3e
M31 | Documentazione e example — columns, sizing, stampa | 2026-04-11 | 133ca53
M32 | Bugfix — colori pie chart e sizing responsivo | 2026-04-11 | 4b75d5c
M33 | Refactor `:::columns` — sintassi `:::col` e fix pipeline | 2026-04-11 | d331dd4
M34 | Chart sizing responsivo con unità viewport | 2026-04-11 | 873f507
M35 | Fix normalizzazione valori chart e gestione zero | 2026-04-11 | 8c359cf
M36 | Fix CSS — bar height, line visibility, label spacing | 2026-04-11 | f14cfb9
M37 | Chart visual polish — cornice, padding, colore testo dati | 2026-04-11 | 874cd80
M38 | Chart CSS refinement — padding barre, caption, padding wrapper, legenda | 2026-04-11 | 1728bc5
M39 | Chart API semplificata — rimuovere opzioni, auto-defaults | 2026-04-12 | 243007c
M40 | Title styling come intestazione di card | 2026-04-12 | f6f5ea8
M41 | Chart spacing — gap label/bars, row/group spacing, legend positioning | 2026-04-12 | df8c18c
M42 | Fix `.data` color per tipo — bianco dentro, colore testo fuori | 2026-04-12 | f66ec9f
M43 | Fix line chart ultimo valore invisibile | 2026-04-12 | 7030a79
M44 | Example showcase completo — tutti i tipi di chart | 2026-04-12 | 72a3a2c
M45 | Normalizzazione globale chart (rollback M35) | 2026-04-12 | 913fb06
M46 | Fix spacing verticale bar multi-dataset | 2026-04-12 | 76f74aa
M47 | Fix label verticale allineamento multi-dataset | 2026-04-12 | 76f74aa
M48 | Fix padding wrapper dopo il titolo | 2026-04-12 | 76f74aa
M49 | Fix legend — spacing e bullet colore | 2026-04-12 | 76f74aa
M50 | Fix bar row gap — non usare border-spacing con flex tr | 2026-04-12 | 76f74aa
M51 | Fix column chart gap e larghezza colonne | 2026-04-12 | 76f74aa
M52 | Fix legend positioning — sotto x-axis labels | 2026-04-12 | 76f74aa
M53 | Fix pie chart — rotazione label illeggibile | 2026-04-12 | 76f74aa
M54 | Line/area chart — rendere leggibili i valori | 2026-04-12 | 76f74aa
M55 | X-axis labels troncate (column, area, pie) | 2026-04-12 | 76f74aa
M56 | Reduce `--labels-size` per column | 2026-04-12 | 6a4510d
M57 | Top padding per line/area chart area (anti-clipping max value) | 2026-04-12 | 6a4510d
M58 | Hide data labels per multi-line e multi-area (anti-collision) | 2026-04-12 | 6a4510d
M59 | Audit visivo finale di tutti i chart | 2026-04-12 | 6a4510d
M60 | Column data labels — torna a bianco (testo dentro la barra) | 2026-04-12 | 8009d7d
M61 | Line/area — fix overflow x-labels fuori dalla card | 2026-04-12 | 8009d7d
M62 | Data pill z-index fix per line/area | 2026-04-12 | 50e8731
M63 | Legend overlap con x-axis labels in line/area multi-dataset | 2026-04-12 | 50e8731
M65 | Endpoint labels per multi-line/area con override robusto `.data` | 2026-04-12 | 42a4fc6
M66 | Fix residui — collision endpoint labels + top clipping area | 2026-04-12 | e93626d
M67 | Graduated Y-axis per line/area + cleanup endpoint labels | 2026-04-13 | 1382966
M68 | Fix graduated Y-axis alignment con i dati | 2026-04-13 | 316dff7
M69 | Parametrizzazione Y-axis intelligente (data_min + clustering detection) | 2026-04-13 | 3090192
M76 | Fix — sidebar-toggle visibile in stampa PDF | 2026-04-14 | 3a6a319
M77 | Fix print — chart axis labels, table headers, table border-radius | 2026-04-14 | 15e5080
M78 | Fix regression M77 — chart bar colors killed in print | 2026-04-14 | 5c7ddb6
M79 | Print — consistent page margins via `@page` | 2026-04-14 | fe5cac2
M80 | Graduated Y-axis per column/bar charts | 2026-05-06 | 5fc48bc
M81 | Column/bar — floating-bar rendering per valori negativi e zero | 2026-05-06 | 7463418
M82 | Stacked column/bar con valori negativi — degrade graceful | 2026-05-06 | 4a392c9
M83 | Audit `.md2-chart` card padding post-Y-axis | 2026-05-06 | 6302144
M84 | Fix `--title "..."` directive parsing for charts | 2026-05-06 | 49aac0e
M85 | X-axis labels decoupled per column/bar (estende M70) | 2026-05-06 | 96b8ffe
M86 | Data label posizionamento condizionale (out-of-bar per piccoli/negativi) | 2026-05-06 | c5c0d36
M87 | Zero-value bar — clean baseline rendering | 2026-05-06 | e2eaefa
M102 | Negative bar labels stay inside + tighter Y-axis on mid-range data | 2026-05-07 | 01b9699
M103 | Bar chart non riempie la larghezza + Column x-labels sovrapposte | 2026-07-18 | 8dd9318
M104 | Bar chart — label lunghe coperte dalla barra adiacente | 2026-07-18 | 8dd9318
M105 | Chapter cover — nuovo tipo di slide divisore d'atto (`:::chapter`) | 2026-07-18 | 56a2549
M106 | `---` dentro un code fence spezza la slide | 2026-07-18 | e1bfcc5
M108 | Devplan compliance pass — done markers, duplicate ID, test comment cleanup | 2026-08-14 | deecb0b
