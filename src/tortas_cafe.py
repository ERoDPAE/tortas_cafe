"""
tortas_cafe.py — Café sales mix analysis for Axion Energy stations.

Generates a self-contained HTML report with interactive Plotly charts.
Three sections: Red Total, Por Cluster, Por Estación.

Usage:
    python src/tortas_cafe.py
    python src/tortas_cafe.py --output reports/custom.html
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROC = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

# ── Constants ─────────────────────────────────────────────────────────────────

EXCLUDED_STATIONS = {"DISC CARAFFA", "DISC ECHEVERRIA", "DISC PANAMERICANA", "CORS EVENTOS"}
MIN_COFFEES = 3500

# Spark/Hive dayofweek() convention: 1=Sunday .. 7=Saturday.
WEEKDAY_ES = {1: "Domingo", 2: "Lunes", 3: "Martes", 4: "Miércoles", 5: "Jueves", 6: "Viernes", 7: "Sábado"}
WEEKDAY_SHORT = {1: "Dom", 2: "Lun", 3: "Mar", 4: "Mié", 5: "Jue", 6: "Vie", 7: "Sáb"}
WEEKDAY_ORDER = [2, 3, 4, 5, 6, 7, 1]  # Monday-first display order

# Columns used by the daily/weekly line charts (make_hourly / make_unit_count).
LINE_CHART_COLS = [
    "q_cafes_llevar", "q_cafes_local", "q_cafes_local_algo", "q_cafes_local_solo",
    "q_cafes_llevar_1", "q_cafes_llevar_mas_1", "q_cafes_local_1", "q_cafes_local_mas_1",
]

# Leaf nodes of the product hierarchy (non-overlapping, exhaustive).
# Each entry maps a column name → (nivel1, nivel2, nivel3, nivel4, nivel5).
# None means the branch ends at that level.
LEAF_MAP = {
    # LLevar > Solo
    "q_cafes_llevar_solo_leche":                                    ("LLevar", "Solo", "Leche",       None,         None),
    "q_cafes_llevar_solo_otros_negro1":                             ("LLevar", "Solo", "Otros",        "Negro",      None),
    "q_cafes_llevar_solo_otros_nonegro":                            ("LLevar", "Solo", "Otros",        "No Negro",   None),
    # LLevar > Algo > Leche
    "q_cafes_llevar_algo_leche_bakery":                             ("LLevar", "Algo", "Leche",        "Bakery",     None),
    "q_cafes_llevar_algo_leche_sinbakery_sandwiches":               ("LLevar", "Algo", "Leche",        "Sin Bakery", "Sandwich"),
    "q_cafes_llevar_algo_leche_sinbakery_sinsandwiches_caramelos":  ("LLevar", "Algo", "Leche",        "Sin Bakery", "Caramelo"),
    "q_cafes_llevar_algo_leche_sinbakery_sinsandwich_sin_caramelo": ("LLevar", "Algo", "Leche",        "Sin Bakery", "Sin Sandwich"),
    # LLevar > Algo > Otros
    "q_cafes_llevar_algo_otros_bakery":                             ("LLevar", "Algo", "Otros",        "Bakery",     None),
    "q_cafes_llevar_algo_otros_sinbakery_sandwiches":               ("LLevar", "Algo", "Otros",        "Sin Bakery", "Sandwich"),
    "q_cafes_llevar_algo_otros_sinbakery_sinsandwiches_caramelos":  ("LLevar", "Algo", "Otros",        "Sin Bakery", "Caramelo"),
    "q_cafes_llevar_algo_otros_sinbakery_sinsandwich_sin_caramelo": ("LLevar", "Algo", "Otros",        "Sin Bakery", "Sin Sandwich"),
    # Local > Solo
    "q_cafes_local_solo_leche":                                     ("Local",  "Solo", "Leche",        None,         None),
    "q_cafes_local_solo_otros_negro1":                              ("Local",  "Solo", "Otros",        "Negro",      None),
    "q_cafes_local_solo_otros_nonegro":                             ("Local",  "Solo", "Otros",        "No Negro",   None),
    # Local > Algo > Leche
    "q_cafes_local_algo_leche_bakery":                              ("Local",  "Algo", "Leche",        "Bakery",     None),
    "q_cafes_local_algo_leche_sinbakery_sandwiches":                ("Local",  "Algo", "Leche",        "Sin Bakery", "Sandwich"),
    "q_cafes_local_algo_leche_sinbakery_sinsandwiches_caramelos":   ("Local",  "Algo", "Leche",        "Sin Bakery", "Caramelo"),
    "q_cafes_local_algo_leche_sinbakery_sinsandwich_sin_caramelo":  ("Local",  "Algo", "Leche",        "Sin Bakery", "Sin Sandwich"),
    # Local > Algo > Otros
    "q_cafes_local_algo_otros_bakery":                              ("Local",  "Algo", "Otros",        "Bakery",     None),
    "q_cafes_local_algo_otros_sinbakery_sandwiches":                ("Local",  "Algo", "Otros",        "Sin Bakery", "Sandwich"),
    "q_cafes_local_algo_otros_sinbakery_sinsandwiches_caramelos":   ("Local",  "Algo", "Otros",        "Sin Bakery", "Caramelo"),
    "q_cafes_local_algo_otros_sinbakery_sinsandwich_sin_caramelo":  ("Local",  "Algo", "Otros",        "Sin Bakery", "Sin Sandwich"),
}

# Fixed column order for the compact per-section day-filter payloads embedded in the
# report: columns are referenced by index (not name) to keep the embedded JSON small.
DATA_COLS = list(LEAF_MAP.keys()) + LINE_CHART_COLS
DATA_COL_INDEX = {c: i for i, c in enumerate(DATA_COLS)}

NODE_COLORS = {
    "LLevar":       "#E8735A",
    "Local":        "#C0392B",
    "Solo":         "#7FB3F5",
    "Algo":         "#1A5276",
    "Leche":        "#82E0AA",
    "Otros":        "#1E8449",
    "Bakery":       "#F9E79F",
    "Sin Bakery":   "#D4E157",
    "Negro":        "#7D6608",
    "No Negro":     "#F4D03F",
    "Sandwich":     "#C0392B",
    "Caramelo":     "#D7BDE2",
    "Sin Sandwich": "#F5EEF8",
}

# ── Data loading ──────────────────────────────────────────────────────────────

def load_raw() -> pd.DataFrame:
    csvs = sorted(DATA_RAW.glob("export_*.csv"))
    if not csvs:
        raise FileNotFoundError(f"No CSVs found in {DATA_RAW}")

    base = pd.read_csv(csvs[0])
    for path in csvs[1:]:
        df = pd.read_csv(path)
        base = base.merge(df, on=["estacion", "dia_semana", "hora"], how="outer")

    num_cols = [c for c in base.columns if c not in ("estacion", "dia_semana", "hora")]
    base[num_cols] = base[num_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    return base


def derive_columns(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()

    for side in ("llevar", "local"):
        for drink in ("leche", "otros"):
            sinbakery = f"q_cafes_{side}_algo_{drink}_sinbakery"
            solo_drink = f"q_cafes_{side}_solo_{drink}"
            sandwiches = f"q_cafes_{side}_algo_{drink}_sinbakery_sandwiches"
            caramelos  = f"q_cafes_{side}_algo_{drink}_sinbakery_sinsandwiches_caramelos"
            sinsandwich = f"q_cafes_{side}_algo_{drink}_sinbakery_sinsandwich_sin_caramelo"

            if sinbakery in d.columns and solo_drink in d.columns:
                d[sinbakery] = d[sinbakery] - d[solo_drink]

            if all(c in d.columns for c in [sinbakery, sandwiches, caramelos]):
                d[sinsandwich] = d[sinbakery] - d[sandwiches] - d[caramelos]

        otros  = f"q_cafes_{side}_solo_otros"
        negro1 = f"q_cafes_{side}_solo_otros_negro1"
        if otros in d.columns and negro1 in d.columns:
            d[f"q_cafes_{side}_solo_otros_nonegro"] = d[otros] - d[negro1]

        total = f"q_cafes_{side}"
        mas1  = f"q_cafes_{side}_mas_1"
        if total in d.columns and mas1 in d.columns:
            d[f"q_cafes_{side}_1"] = d[total] - d[mas1]

    leaf_and_derived = [c for c in d.columns if c.startswith("q_cafes_")]
    d[leaf_and_derived] = d[leaf_and_derived].clip(lower=0)
    return d


def load_clusters() -> pd.DataFrame:
    xl = pd.read_excel(DATA_PROC / "df_cluster_resultados_finales.xlsx")
    xl = xl[["PBL Name", "Cluster_combinado"]].copy()
    xl["PBL Name"] = xl["PBL Name"].str.upper().str.strip()
    return xl


def load_data() -> pd.DataFrame:
    df = load_raw()
    df = derive_columns(df)

    clusters = load_clusters()
    df["estacion"] = df["estacion"].str.upper().str.strip()
    df = df.merge(clusters, left_on="estacion", right_on="PBL Name", how="left")
    df = df[~df["estacion"].isin(EXCLUDED_STATIONS)].copy()
    return df


# ── Hierarchy aggregation ─────────────────────────────────────────────────────

def _build_tree(leaf_values: dict) -> pd.DataFrame:
    """
    Given {col_name: value}, build a DataFrame of sunburst nodes
    with id, label, parent, value (parent values = sum of children).
    """
    node_values: dict[str, float] = {}
    node_meta:   dict[str, tuple[str, str]] = {}  # id → (label, parent_id)
    children:    dict[str, list[str]] = {}

    for col, levels in LEAF_MAP.items():
        path = [lvl for lvl in levels if lvl is not None]
        val  = float(leaf_values.get(col, 0.0))

        for depth in range(len(path)):
            node_id   = " > ".join(path[: depth + 1])
            parent_id = " > ".join(path[:depth]) if depth > 0 else ""

            if node_id not in node_meta:
                node_meta[node_id]   = (path[depth], parent_id)
                node_values[node_id] = 0.0
                children[node_id]    = []

            if depth > 0:
                parent_id_of_node = " > ".join(path[:depth])
                if node_id not in children[parent_id_of_node]:
                    children[parent_id_of_node].append(node_id)

            if depth == len(path) - 1:
                node_values[node_id] += val

    def propagate(nid: str) -> float:
        if not children[nid]:
            return node_values[nid]
        total = sum(propagate(c) for c in children[nid])
        node_values[nid] = total
        return total

    for nid, (_, parent) in node_meta.items():
        if parent == "":
            propagate(nid)

    rows = [
        {"id": nid, "label": label, "parent": parent, "value": node_values[nid]}
        for nid, (label, parent) in node_meta.items()
    ]
    return pd.DataFrame(rows)


def sunburst_data(df: pd.DataFrame) -> pd.DataFrame:
    leaf_cols = [c for c in LEAF_MAP if c in df.columns]
    totals    = df[leaf_cols].sum().to_dict()
    return _build_tree(totals)


def sunburst_data_normalized(df: pd.DataFrame) -> pd.DataFrame:
    """Median-per-station normalization to avoid volume bias from large stations."""
    leaf_cols   = [c for c in LEAF_MAP if c in df.columns]
    total_cols  = ["q_cafes_llevar", "q_cafes_local"]
    group_cols  = leaf_cols + [c for c in total_cols if c in df.columns]

    by_station = df.groupby("estacion")[group_cols].sum()
    total_per_station = by_station[[c for c in total_cols if c in by_station.columns]].sum(axis=1)

    valid = total_per_station[total_per_station >= MIN_COFFEES].index
    if len(valid) == 0:
        return sunburst_data(df)

    by_station = by_station.loc[valid]
    total_per_station = total_per_station.loc[valid]

    props = by_station[leaf_cols].div(total_per_station, axis=0)
    median_props = props.median()

    if median_props.sum() > 0:
        median_props = median_props / median_props.sum()

    scale = total_per_station.sum()
    leaf_values = (median_props * scale).to_dict()
    return _build_tree(leaf_values)


# ── Chart builders ────────────────────────────────────────────────────────────

def _node_color(node_id: str) -> str:
    label = node_id.split(" > ")[-1]
    return NODE_COLORS.get(label, "#BDC3C7")


def make_sunburst(tree: pd.DataFrame, title: str) -> go.Figure:
    colors = [_node_color(row["id"]) for _, row in tree.iterrows()]
    total  = tree[tree["parent"] == ""]["value"].sum()

    fig = go.Figure(go.Sunburst(
        ids=tree["id"],
        labels=tree["label"],
        parents=tree["parent"],
        values=tree["value"],
        branchvalues="total",
        marker=dict(colors=colors, line=dict(color="white", width=1.5)),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "%{value:,.0f} unidades<br>"
            "%{percentRoot:.1%} del total<extra></extra>"
        ),
        insidetextorientation="radial",
        maxdepth=4,
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        margin=dict(t=50, l=10, r=10, b=10),
        height=480,
    )
    return fig


def make_treemap(tree: pd.DataFrame, title: str) -> go.Figure:
    colors = [_node_color(row["id"]) for _, row in tree.iterrows()]

    fig = go.Figure(go.Treemap(
        ids=tree["id"],
        labels=tree["label"],
        parents=tree["parent"],
        values=tree["value"],
        branchvalues="total",
        marker=dict(colors=colors, line=dict(color="white", width=1.5)),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "%{value:,.0f} unidades<br>"
            "%{percentRoot:.1%} del total<extra></extra>"
        ),
        textinfo="label+percent root",
        maxdepth=4,
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        margin=dict(t=50, l=10, r=10, b=10),
        height=480,
    )
    return fig


def _line_layout(title: str) -> dict:
    return dict(
        title=dict(text=title, font=dict(size=13)),
        xaxis=dict(title="Hora", tickmode="linear", tick0=0, dtick=2, range=[-0.5, 23.5]),
        yaxis=dict(title="% del volumen diario"),
        height=360,
        margin=dict(t=45, b=90, l=50, r=20),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5),
        template="plotly_white",
        hovermode="x unified",
    )


def make_hourly(df: pd.DataFrame, title: str) -> go.Figure:
    series = {
        "q_cafes_llevar":      ("LLevar",        "#E8735A", "solid"),
        "q_cafes_local":       ("Local",          "#C0392B", "solid"),
        "q_cafes_local_algo":  ("Local + Algo",   "#1A5276", "dot"),
        "q_cafes_local_solo":  ("Local + Solo",   "#7FB3F5", "dot"),
    }

    fig = go.Figure()
    for col, (name, color, dash) in series.items():
        if col not in df.columns:
            continue
        hourly = df.groupby("hora")[col].sum()
        if hourly.sum() == 0:
            continue
        pct = (hourly / hourly.sum() * 100).reset_index()
        fig.add_trace(go.Scatter(
            x=pct["hora"], y=pct[col],
            name=name, mode="lines+markers",
            line=dict(color=color, width=2, dash=dash),
            marker=dict(size=5),
            meta=col,
        ))

    fig.update_layout(**_line_layout(title))
    return fig


def make_unit_count(df: pd.DataFrame, title: str) -> go.Figure:
    series = {
        "q_cafes_llevar_1":    ("LLevar 1 ud",    "#E8735A", "solid"),
        "q_cafes_llevar_mas_1":("LLevar >1 ud",   "#A93226", "dot"),
        "q_cafes_local_1":     ("Local 1 ud",     "#7FB3F5", "solid"),
        "q_cafes_local_mas_1": ("Local >1 ud",    "#1A5276", "dot"),
    }

    fig = go.Figure()
    for col, (name, color, dash) in series.items():
        if col not in df.columns:
            continue
        hourly = df.groupby("hora")[col].sum()
        if hourly.sum() == 0:
            continue
        pct = (hourly / hourly.sum() * 100).reset_index()
        fig.add_trace(go.Scatter(
            x=pct["hora"], y=pct[col],
            name=name, mode="lines+markers",
            line=dict(color=color, width=2, dash=dash),
            marker=dict(size=5),
            meta=col,
        ))

    fig.update_layout(**_line_layout(title))
    return fig


# ── Weekly (168h, Mon→Sun) charts ─────────────────────────────────────────────

def _weekly_layout(title: str) -> dict:
    boundaries = list(range(0, 169, 24))
    return dict(
        title=dict(text=title, font=dict(size=13)),
        xaxis=dict(
            title="Día de la semana",
            tickmode="array",
            tickvals=boundaries[:-1],
            ticktext=[WEEKDAY_SHORT[d] for d in WEEKDAY_ORDER],
            range=[-1, 169],
        ),
        yaxis=dict(title="% del volumen"),
        height=360,
        margin=dict(t=45, b=70, l=50, r=20),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5),
        template="plotly_white",
        hovermode="x unified",
        shapes=[
            dict(type="line", x0=b, x1=b, y0=0, y1=1, yref="paper",
                 line=dict(color="#CBD5E1", width=1, dash="dot"))
            for b in boundaries[1:-1]
        ],
    )


def _weekly_hour_of_week(df: pd.DataFrame) -> pd.Series:
    day_pos = {d: i for i, d in enumerate(WEEKDAY_ORDER)}
    return df["dia_semana"].map(day_pos) * 24 + df["hora"]


def _make_weekly_fig(df: pd.DataFrame, title: str, normalize: str, series: dict) -> go.Figure:
    d = df.copy()
    d["hour_of_week"] = _weekly_hour_of_week(d)

    fig = go.Figure()
    for col, (name, color, dash) in series.items():
        if col not in d.columns:
            continue
        by_how = d.groupby("hour_of_week")[col].sum().reindex(range(168), fill_value=0)
        if normalize == "week":
            total = by_how.sum()
            pct = (by_how / total * 100) if total else by_how.astype(float)
        else:  # "day"
            pct = by_how.astype(float).copy()
            for day_start in range(0, 168, 24):
                day_slice = by_how.iloc[day_start:day_start + 24]
                day_total = day_slice.sum()
                pct.iloc[day_start:day_start + 24] = (
                    day_slice / day_total * 100 if day_total else 0
                )
        fig.add_trace(go.Scatter(
            x=list(range(168)), y=pct.values,
            name=name, mode="lines",
            line=dict(color=color, width=2, dash=dash),
            meta=col,
        ))

    fig.update_layout(**_weekly_layout(title))
    return fig


def make_weekly_hourly(df: pd.DataFrame, title: str, normalize: str) -> go.Figure:
    series = {
        "q_cafes_llevar":      ("LLevar",        "#E8735A", "solid"),
        "q_cafes_local":       ("Local",          "#C0392B", "solid"),
        "q_cafes_local_algo":  ("Local + Algo",   "#1A5276", "dot"),
        "q_cafes_local_solo":  ("Local + Solo",   "#7FB3F5", "dot"),
    }
    return _make_weekly_fig(df, title, normalize, series)


def make_weekly_unit_count(df: pd.DataFrame, title: str, normalize: str) -> go.Figure:
    series = {
        "q_cafes_llevar_1":    ("LLevar 1 ud",    "#E8735A", "solid"),
        "q_cafes_llevar_mas_1":("LLevar >1 ud",   "#A93226", "dot"),
        "q_cafes_local_1":     ("Local 1 ud",     "#7FB3F5", "solid"),
        "q_cafes_local_mas_1": ("Local >1 ud",    "#1A5276", "dot"),
    }
    return _make_weekly_fig(df, title, normalize, series)


# ── Per-section day×hour data, embedded for client-side day-filter recompute ──

def _section_daydata(df: pd.DataFrame) -> dict:
    cols = [c for c in DATA_COLS if c in df.columns]
    grouped = df.groupby(["dia_semana", "hora"])[cols].sum()
    out = {}
    for (dia, hora), row in grouped.iterrows():
        nonzero = {str(DATA_COL_INDEX[c]): int(round(v)) for c, v in row.items() if v}
        if nonzero:
            out[f"{int(dia)}_{int(hora)}"] = nonzero
    return out


def _section_daydata_by_station(df: pd.DataFrame) -> dict:
    cols = [c for c in DATA_COLS if c in df.columns]
    grouped = df.groupby(["estacion", "dia_semana", "hora"])[cols].sum()
    out = {}
    for (estacion, dia, hora), row in grouped.iterrows():
        nonzero = {str(DATA_COL_INDEX[c]): int(round(v)) for c, v in row.items() if v}
        if nonzero:
            out[f"{estacion}|{int(dia)}_{int(hora)}"] = nonzero
    return out


def _json_for_script(obj) -> str:
    return json.dumps(obj, separators=(",", ":")).replace("</", "<\\/")


def _slugify(s: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return slug or "section"


# ── HTML assembly ─────────────────────────────────────────────────────────────

def _fig_div(fig: go.Figure, div_id: str | None = None) -> str:
    return fig.to_html(full_html=False, include_plotlyjs=False, config={"responsive": True}, div_id=div_id)


def _charts_grid(divs: list[str]) -> str:
    inner = "".join(f"<div>{d}</div>" for d in divs)
    cls = "charts-grid charts-grid--single" if len(divs) == 1 else "charts-grid"
    return f'<div class="{cls}">{inner}</div>'


def _section_charts(df: pd.DataFrame, label: str, normalized: bool, slug: str) -> str:
    total = df[["q_cafes_llevar", "q_cafes_local"]].values.sum()
    if total < MIN_COFFEES:
        return f'<p class="skip">Sin datos suficientes (&lt;{MIN_COFFEES:,} cafés)</p>'

    tree      = sunburst_data(df)
    tree_norm = sunburst_data_normalized(df) if normalized else None

    label_norm = f"{label} — Normalizada"

    sb_divs = [_fig_div(make_sunburst(tree, label), div_id=f"sunburst-{slug}-plain")]
    tm_divs = [_fig_div(make_treemap(tree, label), div_id=f"treemap-{slug}-plain")]
    if tree_norm is not None:
        sb_divs.append(_fig_div(make_sunburst(tree_norm, label_norm), div_id=f"sunburst-{slug}-norm"))
        tm_divs.append(_fig_div(make_treemap(tree_norm, label_norm), div_id=f"treemap-{slug}-norm"))

    mix_charts = (
        f'<div class="chart-mode sunburst-mode">{_charts_grid(sb_divs)}</div>'
        f'<div class="chart-mode treemap-mode" style="display:none">{_charts_grid(tm_divs)}</div>'
    )

    line_charts = _charts_grid([
        _fig_div(make_hourly(df,     f"Distribución horaria — {label}"), div_id=f"hourly-{slug}"),
        _fig_div(make_unit_count(df, f"Unidades por ticket — {label}"), div_id=f"unitcount-{slug}"),
    ])

    weekly_day = _charts_grid([
        _fig_div(make_weekly_hourly(df,     f"Distribución semanal — {label}", "day"), div_id=f"weekly-hourly-{slug}-day"),
        _fig_div(make_weekly_unit_count(df, f"Unidades por ticket (semanal) — {label}", "day"), div_id=f"weekly-unitcount-{slug}-day"),
    ])
    weekly_week = _charts_grid([
        _fig_div(make_weekly_hourly(df,     f"Distribución semanal — {label}", "week"), div_id=f"weekly-hourly-{slug}-week"),
        _fig_div(make_weekly_unit_count(df, f"Unidades por ticket (semanal) — {label}", "week"), div_id=f"weekly-unitcount-{slug}-week"),
    ])
    weekly_charts = (
        f'<div class="chart-mode weekly-day-mode">{weekly_day}</div>'
        f'<div class="chart-mode weekly-week-mode" style="display:none">{weekly_week}</div>'
    )

    payload = {"data": _section_daydata(df), "normalized": normalized}
    if normalized:
        payload["byStation"] = _section_daydata_by_station(df)
    section_script = f'<script>SECTION_DATA["{slug}"] = {_json_for_script(payload)};</script>'

    return mix_charts + line_charts + weekly_charts + section_script


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Análisis Cafés — Axion Energy</title>
  <script>{plotly_js}</script>
  <style>
    :root {{
      --bg:         #F8FAFC;
      --surface:    #FFFFFF;
      --surface2:   #F1F5F9;
      --border:     #E2E8F0;
      --accent:     #4F46E5;
      --accent-bg:  #EEF2FF;
      --text:       #1E293B;
      --text-dim:   #64748B;
      --header-bg:  #0F172A;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Inter", ui-sans-serif, system-ui, -apple-system, sans-serif;
      background: var(--bg); color: var(--text); font-size: 14px;
    }}
    header {{
      background: var(--header-bg);
      padding: 0.8rem 2rem; position: sticky; top: 0; z-index: 200;
      display: flex; align-items: center; justify-content: space-between;
    }}
    header h1 {{
      font-size: 0.95rem; font-weight: 600; letter-spacing: 0.01em; color: #F8FAFC;
    }}
    header h1 span {{ color: #818CF8; }}
    .chart-toggle {{
      display: flex; gap: 2px; background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 3px;
    }}
    .chart-toggle button {{
      background: transparent; border: none; color: #94A3B8;
      font-size: 0.78rem; font-weight: 500; padding: 5px 14px;
      border-radius: 6px; cursor: pointer; transition: all 0.15s;
    }}
    .chart-toggle button.active {{
      background: #FFFFFF; color: var(--accent); font-weight: 600;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }}
    .chart-toggle button:hover:not(.active) {{ color: #E2E8F0; }}
    nav {{
      background: var(--surface); border-bottom: 1px solid var(--border);
      padding: 0rem 2rem; position: sticky; top: 49px; z-index: 100;
      display: flex; gap: 0; align-items: center;
    }}
    nav a {{
      text-decoration: none; color: var(--text-dim); font-size: 0.82rem;
      font-weight: 500; padding: 0.65rem 1rem;
      border-bottom: 2px solid transparent;
      transition: color 0.15s, border-color 0.15s;
    }}
    nav a:hover {{ color: var(--accent); border-bottom-color: var(--accent); }}
    main {{ max-width: 1440px; margin: 0 auto; padding: 1.5rem 2rem 3rem; }}
    .section {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 12px; padding: 1.5rem; margin-bottom: 1.25rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03);
    }}
    .section > h2 {{
      font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em;
      text-transform: uppercase; color: var(--text-dim);
      margin-bottom: 1.25rem; padding-bottom: 0.75rem;
      border-bottom: 1px solid var(--border);
    }}
    details {{
      background: var(--surface2); border: 1px solid var(--border);
      border-radius: 8px; margin-bottom: 0.4rem; padding: 0.7rem 1rem;
      transition: border-color 0.15s, background 0.15s;
    }}
    details[open] {{ background: var(--surface); border-color: #C7D2FE; }}
    summary {{
      cursor: pointer; font-weight: 500; font-size: 0.88rem;
      color: var(--text); user-select: none; list-style: none;
      display: flex; align-items: center; gap: 0.5rem;
    }}
    summary::before {{
      content: "\\25B6"; font-size: 0.55rem; color: var(--text-dim);
      transition: transform 0.2s;
    }}
    details[open] summary::before {{ transform: rotate(90deg); color: var(--accent); }}
    summary:hover {{ color: var(--accent); }}
    .charts-grid {{
      display: grid; grid-template-columns: 1fr 1fr;
      gap: 0.75rem; margin-top: 1rem; overflow: hidden;
    }}
    .charts-grid > div {{ min-width: 0; overflow: hidden; }}
    @media (max-width: 960px) {{ .charts-grid {{ grid-template-columns: 1fr; }} }}
    .charts-grid--single {{
      grid-template-columns: minmax(0, 680px);
      justify-content: center;
    }}
    .skip {{
      color: var(--text-dim); font-style: italic;
      padding: 0.5rem 0; font-size: 0.9rem;
    }}
    .station-count {{
      font-size: 0.75rem; color: var(--text-dim);
      font-weight: 400; margin-left: 0.4rem;
    }}
    .header-controls {{ display: flex; gap: 0.6rem; align-items: center; }}
    #day-filter {{
      background: rgba(255,255,255,0.08); color: #F1F5F9;
      border: 1px solid rgba(255,255,255,0.12); border-radius: 8px;
      font-size: 0.78rem; font-weight: 500; padding: 6px 10px; cursor: pointer;
    }}
    #day-filter:hover {{ border-color: rgba(255,255,255,0.3); }}
  </style>
</head>
<body>
  <header>
    <h1>Análisis Cafés — <span>Axion Energy</span></h1>
    <div class="header-controls">
      <select id="day-filter" onchange="setDayFilter(this.value)">
        <option value="all">Todos los días</option>
        <option value="weekdays">Días de semana</option>
        <option value="weekend">Fin de semana</option>
        <option value="2">Lunes</option>
        <option value="3">Martes</option>
        <option value="4">Miércoles</option>
        <option value="5">Jueves</option>
        <option value="6">Viernes</option>
        <option value="7">Sábado</option>
        <option value="1">Domingo</option>
      </select>
      <div class="chart-toggle">
        <button class="active" onclick="setChartMode('sunburst', this)">Sunburst</button>
        <button onclick="setChartMode('treemap', this)">Treemap</button>
      </div>
      <div class="chart-toggle">
        <button class="active" onclick="setWeeklyMode('weekly-day', this)">Semanal x Día</button>
        <button onclick="setWeeklyMode('weekly-week', this)">Semanal x Semana</button>
      </div>
    </div>
  </header>
  <nav>
    <a href="#red-total">Red Total</a>
    <a href="#clusters">Por Cluster</a>
    <a href="#estaciones">Por Estación</a>
  </nav>
  <script>
    var SECTION_DATA = {{}};
    var LEAF_MAP_JS = {leaf_map_json};
    var DATA_COLS = {data_cols_json};
    var MIN_COFFEES = {min_coffees};
    var DAY_GROUPS = {{
      all: [1, 2, 3, 4, 5, 6, 7],
      weekdays: [2, 3, 4, 5, 6],
      weekend: [7, 1],
      "1": [1], "2": [2], "3": [3], "4": [4], "5": [5], "6": [6], "7": [7]
    }};
  </script>
  <main>
    {body}
  </main>
  <script>
    function triggerResize() {{
      setTimeout(function() {{ window.dispatchEvent(new Event('resize')); }}, 50);
    }}
    function setChartMode(mode, btn) {{
      var other = mode === 'sunburst' ? 'treemap' : 'sunburst';
      document.querySelectorAll('.chart-mode.' + mode + '-mode').forEach(function(el) {{ el.style.display = ''; }});
      document.querySelectorAll('.chart-mode.' + other + '-mode').forEach(function(el) {{ el.style.display = 'none'; }});
      btn.closest('.chart-toggle').querySelectorAll('button').forEach(function(b) {{ b.classList.remove('active'); }});
      btn.classList.add('active');
      triggerResize();
    }}
    function setWeeklyMode(mode, btn) {{
      var other = mode === 'weekly-day' ? 'weekly-week' : 'weekly-day';
      document.querySelectorAll('.chart-mode.' + mode + '-mode').forEach(function(el) {{ el.style.display = ''; }});
      document.querySelectorAll('.chart-mode.' + other + '-mode').forEach(function(el) {{ el.style.display = 'none'; }});
      btn.closest('.chart-toggle').querySelectorAll('button').forEach(function(b) {{ b.classList.remove('active'); }});
      btn.classList.add('active');
      triggerResize();
    }}

    // ── Day-selector client-side recompute ──────────────────────────────────

    function buildTree(leafTotals) {{
      var nodeValues = {{}};
      var children = {{}};
      var parentOf = {{}};
      Object.keys(LEAF_MAP_JS).forEach(function(col) {{
        var path = LEAF_MAP_JS[col];
        var val = leafTotals[col] || 0;
        for (var depth = 0; depth < path.length; depth++) {{
          var nodeId = path.slice(0, depth + 1).join(" > ");
          var parentId = depth > 0 ? path.slice(0, depth).join(" > ") : "";
          if (!(nodeId in parentOf)) {{
            parentOf[nodeId] = parentId;
            nodeValues[nodeId] = 0;
            children[nodeId] = [];
          }}
          if (depth > 0 && children[parentId].indexOf(nodeId) === -1) {{
            children[parentId].push(nodeId);
          }}
          if (depth === path.length - 1) {{
            nodeValues[nodeId] += val;
          }}
        }}
      }});
      function propagate(nid) {{
        if (children[nid].length === 0) return nodeValues[nid];
        var total = 0;
        for (var i = 0; i < children[nid].length; i++) total += propagate(children[nid][i]);
        nodeValues[nid] = total;
        return total;
      }}
      Object.keys(parentOf).forEach(function(nid) {{
        if (parentOf[nid] === "") propagate(nid);
      }});
      return nodeValues;
    }}

    function applyTreeValues(divId, nodeValues) {{
      var gd = document.getElementById(divId);
      if (!gd || !gd.data || !gd.data[0]) return;
      var ids = gd.data[0].ids;
      var values = ids.map(function(id) {{ return nodeValues[id] || 0; }});
      Plotly.restyle(gd, {{values: [values]}});
    }}

    function aggregateLeafTotals(daydata, daySet) {{
      var totals = {{}};
      Object.keys(daydata).forEach(function(key) {{
        var dia = parseInt(key.split("_")[0], 10);
        if (!daySet[dia]) return;
        var vals = daydata[key];
        Object.keys(vals).forEach(function(idx) {{
          var col = DATA_COLS[idx];
          totals[col] = (totals[col] || 0) + vals[idx];
        }});
      }});
      return totals;
    }}

    function applyLineValues(divId, daydata, daySet) {{
      var gd = document.getElementById(divId);
      if (!gd || !gd.data) return;
      var hourlyByCol = {{}};
      Object.keys(daydata).forEach(function(key) {{
        var parts = key.split("_");
        var dia = parseInt(parts[0], 10);
        var hora = parseInt(parts[1], 10);
        if (!daySet[dia]) return;
        var vals = daydata[key];
        Object.keys(vals).forEach(function(idx) {{
          var col = DATA_COLS[idx];
          if (!hourlyByCol[col]) hourlyByCol[col] = new Array(24).fill(0);
          hourlyByCol[col][hora] += vals[idx];
        }});
      }});
      for (var i = 0; i < gd.data.length; i++) {{
        var col = gd.data[i].meta;
        var hourly = hourlyByCol[col] || new Array(24).fill(0);
        var total = hourly.reduce(function(a, b) {{ return a + b; }}, 0);
        var pct = total > 0 ? hourly.map(function(v) {{ return v / total * 100; }}) : hourly.slice();
        Plotly.restyle(gd, {{y: [pct]}}, [i]);
      }}
    }}

    function median(arr) {{
      if (arr.length === 0) return 0;
      var sorted = arr.slice().sort(function(a, b) {{ return a - b; }});
      var mid = Math.floor(sorted.length / 2);
      return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    }}

    function aggregateLeafTotalsFromStations(stationTotals) {{
      var totals = {{}};
      Object.keys(stationTotals).forEach(function(estacion) {{
        var vals = stationTotals[estacion];
        Object.keys(vals).forEach(function(col) {{
          totals[col] = (totals[col] || 0) + vals[col];
        }});
      }});
      return totals;
    }}

    function computeNormalizedTree(byStation, daySet) {{
      var stationTotals = {{}};
      Object.keys(byStation).forEach(function(key) {{
        var sep = key.indexOf("|");
        var estacion = key.slice(0, sep);
        var rest = key.slice(sep + 1).split("_");
        var dia = parseInt(rest[0], 10);
        if (!daySet[dia]) return;
        if (!stationTotals[estacion]) stationTotals[estacion] = {{}};
        var vals = byStation[key];
        Object.keys(vals).forEach(function(idx) {{
          var col = DATA_COLS[idx];
          stationTotals[estacion][col] = (stationTotals[estacion][col] || 0) + vals[idx];
        }});
      }});

      var leafCols = Object.keys(LEAF_MAP_JS);
      var totalCols = ["q_cafes_llevar", "q_cafes_local"];
      var propsPerLeaf = {{}};
      leafCols.forEach(function(c) {{ propsPerLeaf[c] = []; }});
      var scaleSum = 0;
      var validCount = 0;

      Object.keys(stationTotals).forEach(function(estacion) {{
        var totals = stationTotals[estacion];
        var totalPerStation = totalCols.reduce(function(s, c) {{ return s + (totals[c] || 0); }}, 0);
        if (totalPerStation < MIN_COFFEES) return;
        validCount += 1;
        scaleSum += totalPerStation;
        leafCols.forEach(function(c) {{ propsPerLeaf[c].push((totals[c] || 0) / totalPerStation); }});
      }});

      if (validCount === 0) {{
        return buildTree(aggregateLeafTotalsFromStations(stationTotals));
      }}

      var medianProps = {{}};
      leafCols.forEach(function(c) {{ medianProps[c] = median(propsPerLeaf[c]); }});
      var sumMedian = Object.values(medianProps).reduce(function(a, b) {{ return a + b; }}, 0);
      if (sumMedian > 0) {{
        leafCols.forEach(function(c) {{ medianProps[c] = medianProps[c] / sumMedian; }});
      }}
      var leafValues = {{}};
      leafCols.forEach(function(c) {{ leafValues[c] = medianProps[c] * scaleSum; }});
      return buildTree(leafValues);
    }}

    function setDayFilter(dayKey) {{
      var daySet = {{}};
      DAY_GROUPS[dayKey].forEach(function(d) {{ daySet[d] = true; }});
      Object.keys(SECTION_DATA).forEach(function(slug) {{
        var sec = SECTION_DATA[slug];
        var nodeValues = buildTree(aggregateLeafTotals(sec.data, daySet));
        applyTreeValues('sunburst-' + slug + '-plain', nodeValues);
        applyTreeValues('treemap-' + slug + '-plain', nodeValues);
        if (sec.normalized) {{
          var nodeValuesNorm = computeNormalizedTree(sec.byStation, daySet);
          applyTreeValues('sunburst-' + slug + '-norm', nodeValuesNorm);
          applyTreeValues('treemap-' + slug + '-norm', nodeValuesNorm);
        }}
        applyLineValues('hourly-' + slug, sec.data, daySet);
        applyLineValues('unitcount-' + slug, sec.data, daySet);
      }});
      triggerResize();
    }}

    window.addEventListener('load', triggerResize);
  </script>
</body>
</html>
"""


def build_report(df: pd.DataFrame, output_path: Path) -> None:
    REPORTS.mkdir(exist_ok=True)

    sections = []

    # ── Red Total ─────────────────────────────────────────────────────────────
    n_stations = df["estacion"].nunique()
    content = _section_charts(df, "Red Total", normalized=True, slug="red-total")
    sections.append(
        f'<section class="section" id="red-total">'
        f'<h2>Red Total <span class="station-count">({n_stations} estaciones)</span></h2>'
        f'{content}</section>'
    )

    # ── Por Cluster ───────────────────────────────────────────────────────────
    cluster_items = []
    for cluster in sorted(df["Cluster_combinado"].dropna().unique()):
        sub = df[df["Cluster_combinado"] == cluster]
        n   = sub["estacion"].nunique()
        slug = f"cluster-{_slugify(str(cluster))}"
        content = _section_charts(sub, f"Cluster {cluster}", normalized=True, slug=slug)
        cluster_items.append(
            f'<details>'
            f'<summary>Cluster {cluster}'
            f'<span class="station-count">({n} estaciones)</span></summary>'
            f'{content}</details>'
        )
    sections.append(
        f'<section class="section" id="clusters">'
        f'<h2>Por Cluster</h2>'
        + "".join(cluster_items)
        + "</section>"
    )

    # ── Por Estación ──────────────────────────────────────────────────────────
    station_items = []
    for estacion in sorted(df["estacion"].unique()):
        sub     = df[df["estacion"] == estacion]
        cluster = sub["Cluster_combinado"].dropna().mode()
        cluster_label = f"Cluster {cluster.iloc[0]}" if len(cluster) else "—"
        slug = f"estacion-{_slugify(estacion)}"
        content = _section_charts(sub, estacion, normalized=False, slug=slug)
        station_items.append(
            f'<details>'
            f'<summary>{estacion.title()}'
            f'<span class="station-count">({cluster_label})</span></summary>'
            f'{content}</details>'
        )
    sections.append(
        f'<section class="section" id="estaciones">'
        f'<h2>Por Estación</h2>'
        + "".join(station_items)
        + "</section>"
    )

    leaf_map_js = {col: [lvl for lvl in levels if lvl is not None] for col, levels in LEAF_MAP.items()}
    html = HTML_TEMPLATE.format(
        plotly_js=get_plotlyjs(),
        body="\n".join(sections),
        leaf_map_json=_json_for_script(leaf_map_js),
        data_cols_json=_json_for_script(DATA_COLS),
        min_coffees=MIN_COFFEES,
    )
    output_path.write_text(html, encoding="utf-8")
    print(f"Report written: {output_path}  ({output_path.stat().st_size / 1_048_576:.1f} MB)")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Axion café sales mix report.")
    parser.add_argument(
        "--output", type=Path,
        default=REPORTS / "tortas_cafe.html",
        help="Output HTML path (default: reports/tortas_cafe.html)",
    )
    args = parser.parse_args()

    print("Loading data…")
    df = load_data()
    print(f"  {len(df):,} rows | {df['estacion'].nunique()} stations | "
          f"{df['Cluster_combinado'].nunique()} clusters")

    print("Building report…")
    build_report(df, args.output)


if __name__ == "__main__":
    main()
