# CLAUDE.md

## Project Overview

Sales mix analysis for Axion Energy café outlets at gas stations. Generates a self-contained interactive HTML report using Plotly (sunburst / treemap charts). Replaces a legacy R/plotrix nested pie chart report.

## Environment

- Conda env: `cafe_analysis` at `C:\Users\XEXR15\.conda\envs\cafe_analysis`
- Python executable: `C:\Users\XEXR15\.conda\envs\cafe_analysis\python.exe`

## Running the report

```bash
python src/tortas_cafe.py
```

Output: `reports/tortas_cafe.html` (self-contained, no server needed).

## Project structure

```
data/raw/           # 17 CSV exports from POS BI tool (export_1.csv … export_17.csv)
data/processed/     # df_cluster_resultados_finales.xlsx — station-to-cluster mapping
src/
  tortas_cafe.py    # Main script: load → clean → classify → build charts → export HTML
reports/            # Generated HTML reports (gitignored)
legacy/             # Original R implementation (reference only, not maintained)
  older/            # Pre-May-2025 versions
```

## Data

- Each CSV has columns: `estacion`, `hora`, and one or more `q_cafes_*` columns.
- `null` values in CSVs are string literals from the DB export — cast to numeric, treat as 0.
- The 17 files represent different levels of the product hierarchy and must be merged on `(estacion, hora)`.
- Minimum threshold: stations with fewer than 3500 total coffees are excluded from charts.
- Excluded stations: `DISC CARAFFA`, `DISC ECHEVERRIA`, `DISC PANAMERICANA`, `CORS EVENTOS`.

## Hierarchy

```
Level 1 — Nivel1:  LLevar / Local            (to-go vs sit-in)
Level 2 — Nivel2:  Solo / Algo               (no food / with food)
Level 3 — Nivel3:  Leche / Otros             (milk-based / other drink)
Level 4 — Nivel4:  Sin Bakery / Bakery / Negro   (food type or black coffee)
Level 5 — Nivel5:  Sin Sandwich / Sandwich / Caramelo
```

Detected from column names (e.g. `q_cafes_llevar_algo_leche_bakery`).

## Chart types (to implement)

- **Sunburst** — full 5-level hierarchy, interactive drill-down
- **Treemap** — same hierarchy, easier area comparison
- **Hourly distribution** — line chart, % of daily volume by hour
- **Unit count** — 1-unit vs >1-unit tickets

Report sections: Red Total → Nivel Cluster → Nivel Estación.
Both raw-total and station-median-normalized versions for network and cluster sections.

## Dependencies

```
pip install pandas plotly openpyxl
```
