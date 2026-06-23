# tortas_cafe

Análisis de mix de ventas de café en estaciones de servicio Axion Energy. Genera un reporte HTML interactivo con gráficos de sunburst/treemap por red, cluster y estación.

## Descripción

Los datos provienen de exportaciones, agrupados por estación y hora. El análisis clasifica cada venta en una jerarquía de 5 niveles orientada a decisiones de promociones:

```
Llevar / Local
└── Solo / Algo
    └── Leche / Otros
        └── Sin Bakery / Bakery / Negro
            └── Sin Sandwich / Sandwich / Caramelo
```

El reporte se genera a 3 niveles de granularidad: red total, por cluster de estaciones y por estación individual.

El reporte incluye además un selector de día (todos los días / días de semana / fin de semana / día individual) que recalcula el sunburst, el treemap y los gráficos horarios de cada sección en el navegador, y un gráfico semanal continuo (168 puntos, lunes a domingo) con su propio toggle día/semana, independiente del selector de día.

## Estructura del proyecto

```
tortas_cafe/
├── data/
│   ├── raw/                    # Exportaciones CSV de Databricks (export_1.csv … export_17.csv)
│   └── processed/              # Asignación de clusters por estación (Excel)
├── src/
│   ├── extract_databricks.py   # Paso 1: extrae las 17 consultas de Databricks → data/raw/*.csv
│   └── tortas_cafe.py          # Paso 2: carga, transformación y reporte HTML
├── reports/                    # HTMLs generados (no versionados — ver .gitignore)
├── legacy/                     # Versión original en R + notebook Databricks legacy (solo referencia)
│   ├── Tortas_anidadas_Cafésv2.R
│   ├── Tortas_por_nivelesv2.Rmd
│   ├── Borrar.Rmd
│   └── older/                  # Versiones previas al refactor de mayo 2025
├── .env.example                # Plantilla de credenciales Databricks (.env real está en .gitignore)
└── CLAUDE.md
```

## Uso

Dos pasos separados: extracción (trae CSVs frescos de Databricks) y armado del reporte (lee lo que haya en `data/raw/`).

```bash
# 1. Extracción — requiere tortas_cafe/.env con credenciales (copiar de .env.example)
python src/extract_databricks.py --start-date 2025-01-01 --end-date 2026-06-22

# 2. Armado del reporte a partir de lo que esté en data/raw/
python src/tortas_cafe.py
```

El reporte se genera en `reports/tortas_cafe.html`.

### Credenciales de Databricks

Copiar `.env.example` a `.env` (gitignored) y completar:

```
DATABRICKS_SERVER_HOSTNAME=...
DATABRICKS_HTTP_PATH=...
DATABRICKS_TOKEN=...
```

## Dependencias

```
pip install pandas plotly openpyxl databricks-sql-connector python-dotenv
```

## Datos

Los CSVs en `data/raw/` son extraídos directamente de Databricks vía `extract_databricks.py`, agrupados por estación, día de semana (`dia_semana`, convención Spark/Hive: 1=domingo .. 7=sábado) y hora. Cada archivo corresponde a un nivel de la jerarquía de productos. Para actualizar los datos, volver a correr `extract_databricks.py` con el rango de fechas deseado — no hace falta tocar las consultas SQL.

`data/processed/df_cluster_resultados_finales.xlsx` contiene la asignación manual de cada estación a un cluster de comportamiento similar.
