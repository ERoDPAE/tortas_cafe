# CLAUDE.md

## Project Overview

Sales mix analysis for Axion Energy café outlets at gas stations. Generates a self-contained interactive HTML report using Plotly (sunburst / treemap charts). Replaces a legacy R/plotrix nested pie chart report.

## Environment

- Target conda env: `cafe_analysis` (not yet created — use base for now)
- Current Python: `C:\ProgramData\Anaconda3\python.exe` (base env, has all required packages)
- To create dedicated env: `conda create -n cafe_analysis python=3.11 pandas plotly openpyxl`

## Running the pipeline

Two separate stages: extraction (pulls fresh CSVs from Databricks) and report-building (reads
whatever CSVs are in `data/raw/` and builds the HTML report). Run extraction only when you want
fresh data; re-run the report any time without re-extracting.

```bash
# 1. Extract — requires tortas_cafe/.env with Databricks credentials (copy from .env.example)
python src/extract_databricks.py --start-date 2025-01-01 --end-date 2025-05-01

# 2. Build the report from whatever is in data/raw/
python src/tortas_cafe.py
```

Output: `reports/tortas_cafe.html` (self-contained, no server needed).

### Databricks credentials

Copy `.env.example` to `.env` (gitignored) and fill in:

```
DATABRICKS_SERVER_HOSTNAME=...
DATABRICKS_HTTP_PATH=...
DATABRICKS_TOKEN=...
```

## Project structure

```
data/raw/                # 17 CSV exports (export_1.csv … export_17.csv), written by extract_databricks.py
data/processed/           # df_cluster_resultados_finales.xlsx — station-to-cluster mapping
src/
  extract_databricks.py  # Stage 1: pulls the 17 queries from Databricks for a date range → data/raw/*.csv
  tortas_cafe.py          # Stage 2: load → clean → classify → build charts → export HTML
reports/                  # Generated HTML reports (gitignored)
legacy/                   # Original R implementation + legacy Databricks notebook (reference only, not maintained)
  older/                  # Pre-May-2025 versions
.env.example              # Template for the required Databricks credentials (.env is gitignored)
```

## Data

- Each CSV has columns: `estacion`, `dia_semana`, `hora`, and one or more `q_cafes_*` columns.
- `dia_semana` follows Spark/Hive's `dayofweek()` convention: 1=Sunday .. 7=Saturday (see `WEEKDAY_ES`/`WEEKDAY_ORDER` in `tortas_cafe.py`, which reorders to Monday-first for display).
- `null` values in CSVs are string literals from the DB export — cast to numeric, treat as 0.
- The 17 files represent different levels of the product hierarchy and must be merged on `(estacion, dia_semana, hora)`.
- Minimum threshold: stations with fewer than 3500 total coffees are excluded from charts.
- Excluded stations: `DISC CARAFFA`, `DISC ECHEVERRIA`, `DISC PANAMERICANA`, `CORS EVENTOS`,
  `OPERADOR LOGISTICO 2`, `OPERADOR LOGISTICO` (the last two: unclustered, 0% llevar, ~100%
  multi-unit tickets — look like internal logistics/depot accounts rather than customer-facing
  cafés; they were driving spurious peaks in the Red Total hourly/weekly charts since Red Total
  includes unclustered stations that "Por Cluster" sections don't).

## Day-of-week selector and weekly chart

- The header day-selector (Todos los días / Días de semana / Fin de semana / individual day) recomputes
  the sunburst, treemap, and the two 24h daily line charts client-side (`Plotly.restyle`, no server, no
  re-render) — it does **not** affect the weekly chart below them.
- The weekly chart (168 continuous points, Mon 00h → Sun 23h) is always all-days; it has its own
  independent day-normalized / week-normalized toggle in the header, separate from the day-selector.
- Implementation: each section embeds a compact `(dia_semana, hora)` → counts payload
  (`SECTION_DATA[slug]`, columns referenced by index via `DATA_COLS` to keep the JSON small); Red Total
  and Cluster sections additionally embed a per-station breakdown so the "Normalizada" (median-per-station)
  sunburst/treemap variant stays exactly correct under any day filter. The JS in `HTML_TEMPLATE` mirrors
  `_build_tree()` / `make_hourly()` / `sunburst_data_normalized()` exactly — keep them in sync if either side changes.

## Hierarchy

```
Level 1 — Nivel1:  Llevar / Local            (to-go vs sit-in)
Level 2 — Nivel2:  Solo / Algo               (no food / with food)
Level 3 — Nivel3:  Leche / Otros             (milk-based / other drink)
Level 4 — Nivel4:  Sin Bakery / Bakery / Negro   (food type or black coffee)
Level 5 — Nivel5:  Sin Sandwich / Sandwich / Caramelo
```

Detected from column names (e.g. `q_cafes_llevar_algo_leche_bakery`).

## Chart types

- **Sunburst** — full 5-level hierarchy, interactive drill-down (`maxdepth=-1`, all 5 levels rendered —
  a previous `maxdepth=4` silently dropped the Sandwich/Caramelo/Sin Sandwich leaf level)
- **Treemap** — same hierarchy, easier area comparison
- **Hourly distribution** — line chart, % of daily volume by hour (day-selector applies)
- **Unit count** — 1-unit vs >1-unit tickets (day-selector applies)
- **Weekly distribution / weekly unit count** — 168-point continuous Mon→Sun line charts, day-norm/week-norm toggle (day-selector does not apply)
- **Aporte por estación** — horizontal bar of total volume per station (Red Total + Cluster sections only,
  via `make_station_contribution`), sorted descending. Diagnostic chart to catch a single station dominating
  an aggregate — not affected by the day-selector, built once from all-days data. Stations under `MIN_COFFEES`
  (3500) are greyed out and a dashed line marks the threshold, with hover text stating whether each station is
  included in or excluded from the "Normalizada" view — makes explicit that the raw/plain sums on every other
  chart still include every station shown here, but the median-per-station "Normalizada" sunburst/treemap drops
  anything below the line.

Report sections: Red Total → Nivel Cluster → Nivel Estación.
Both raw-total and station-median-normalized versions for network and cluster sections.

## Dependencies

```
pip install pandas plotly openpyxl databricks-sql-connector python-dotenv
```
