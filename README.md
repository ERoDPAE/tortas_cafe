# tortas_cafe

Análisis de mix de ventas de café en estaciones de servicio Axion Energy. Genera un reporte HTML interactivo con gráficos de sunburst/treemap por red, cluster y estación.

## Descripción

Los datos provienen de exportaciones del sistema POS, agrupados por estación y hora. El análisis clasifica cada venta en una jerarquía de 5 niveles orientada a decisiones de promociones:

```
LLevar / Local
└── Solo / Algo
    └── Leche / Otros
        └── Sin Bakery / Bakery / Negro
            └── Sin Sandwich / Sandwich / Caramelo
```

El reporte se genera a 3 niveles de granularidad: red total, por cluster de estaciones y por estación individual.

## Estructura del proyecto

```
tortas_cafe/
├── data/
│   ├── raw/                    # Exportaciones CSV del POS (export_1.csv … export_17.csv)
│   └── processed/              # Asignación de clusters por estación (Excel)
├── src/
│   └── tortas_cafe.py          # Pipeline principal: carga, transformación y reporte HTML
├── reports/                    # HTMLs generados (no versionados — ver .gitignore)
├── legacy/                     # Versión original en R
│   ├── Tortas_anidadas_Cafésv2.R
│   ├── Tortas_por_nivelesv2.Rmd
│   ├── Borrar.Rmd
│   └── older/                  # Versiones previas al refactor de mayo 2025
└── CLAUDE.md
```

## Uso

```bash
python src/tortas_cafe.py
```

El reporte se genera en `reports/tortas_cafe.html`.

## Dependencias

```
pip install pandas plotly openpyxl
```

Requiere Python en el entorno conda `cafe_analysis`.

## Datos

Los CSVs en `data/raw/` son exportaciones del sistema POS agrupadas por estación y hora. Cada archivo corresponde a un nivel de la jerarquía de productos. Para actualizar los datos, re-exportar las 17 consultas desde la herramienta BI de origen y reemplazar los archivos.

`data/processed/df_cluster_resultados_finales.xlsx` contiene la asignación manual de cada estación a un cluster de comportamiento similar.
