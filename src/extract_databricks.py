"""
extract_databricks.py — Pull café sales-mix CSV exports directly from Databricks.

Ports the 17 export queries from legacy/06_Datos_torta_anidada.ipynb, parameterized
by date range and grouped additionally by day-of-week (dia_semana).

Usage:
    python src/extract_databricks.py --start-date 2025-01-01 --end-date 2025-05-01

Requires a .env file (see .env.example) with DATABRICKS_SERVER_HOSTNAME,
DATABRICKS_HTTP_PATH, DATABRICKS_TOKEN.
"""

import argparse
import os
from pathlib import Path

import pandas as pd
from databricks import sql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

ARTICLE_LECHE = (
    "7182,6315,8040,4580,4581,4100,6081,6317,4312,7191,7478,7197,7196,6837,6808,"
    "9306,9305,9301,6442,7315,6784,7322,7311,2200,3719,3715,3723,7661,5014,5016,6793,7657,2641"
)
ARTICLE_NEGRO = "6873,7185,6905,6874,6875,2649"

# export_N → SQL template. {start_date}/{end_date} are filled in at run time.
# Every query selects "estacion, hora, dia_semana" and groups by all three.
QUERIES: dict[int, str] = {
    1: """
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' then d.quantity end) as q_cafes_llevar,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' then d.quantity end) as q_cafes_local

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{start_date}' and DATE(d.date_time)<='{end_date}'
group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    9: """
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' then d.quantity end) as q_cafes_local_mas_1

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{start_date}' and DATE(d.date_time)<='{end_date}'
and h.saleId in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{start_date}' and DATE(d.date_time)<='{end_date}'
group by h.saleId having sum(case when c.parentcategoryId in (32) then d.quantity end)>1)

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    10: """
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' then d.quantity end) as q_cafes_llevar_mas_1

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{start_date}' and DATE(d.date_time)<='{end_date}'
and h.saleId in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{start_date}' and DATE(d.date_time)<='{end_date}'
group by h.saleId having sum(case when c.parentcategoryId in (32) then d.quantity end)>1)

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    2: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' then d.quantity end) as q_cafes_llevar_solo,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' then d.quantity end) as q_cafes_local_solo,

sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_solo_leche,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_solo_otros,

sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_solo_leche,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_solo_otros,

sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_llevar_solo_otros_negro,
sum(case when c.parentcategoryId in (32) and upper(a.description) not LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_local_solo_otros_negro

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'
and h.saleId not in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}' and c.parentcategoryId not in (32)
group by h.saleId)

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    12: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,

sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_llevar_solo_otros_negro1,
sum(case when c.parentcategoryId in (32) and upper(a.description) not LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_local_solo_otros_negro1

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'
and h.saleId not in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}' and c.parentcategoryId not in (32)
group by h.saleId)

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    3: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' then d.quantity end) as q_cafes_llevar_algo,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' then d.quantity end) as q_cafes_local_algo,

sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_leche,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_otros,

sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_leche,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_otros

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'
and h.saleId in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}' and c.parentcategoryId not in (32)
group by h.saleId)

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    13: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,

sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_llevar_algo_otros_negro1,
sum(case when c.parentcategoryId in (32) and upper(a.description) not LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_local_algo_otros_negro1

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'
and h.saleId in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}' and c.parentcategoryId not in (32)
group by h.saleId)

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    4: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_leche_bakery,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_otros_bakery,

sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_leche_bakery,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_otros_bakery

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'
and h.saleId in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.parentcategoryId in (15) and DATE(d.date_time)<='{{end_date}}')

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    15: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_llevar_algo_bakery_negro1,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_local_algo_bakery_negro1

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'
and h.saleId in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.parentcategoryId in (15) and DATE(d.date_time)<='{{end_date}}')

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    5: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_leche_sinbakery,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_otros_sinbakery,

sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_leche_sinbakery,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_otros_sinbakery

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'
and h.saleId not in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.parentcategoryId in (15) and DATE(d.date_time)<='{{end_date}}')

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    14: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_llevar_algo_otros_sinbakery_negro,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_local_algo_otros_sinbakery_negro

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'
and h.saleId not in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.parentcategoryId in (15) and DATE(d.date_time)<='{{end_date}}')

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    16: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_llevar_algo_otros_sinbakery_negro_choco,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_local_algo_otros_sinbakery_negro_choco

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'
and h.saleId not in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.parentcategoryId in (15) and DATE(d.date_time)<='{{end_date}}')

and h.saleId in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.categoryId in (86) and DATE(d.date_time)<='{{end_date}}')

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    17: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_llevar_algo_otros_sinbakery_negro_caramelonochoco,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_NEGRO})
then d.quantity end) as q_cafes_local_algo_otros_sinbakery_negro_caramelonochoco

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'

and h.saleId in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.parentcategoryId in (9) and DATE(d.date_time)<='{{end_date}}')

and h.saleId not in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.parentcategoryId in (15) and DATE(d.date_time)<='{{end_date}}')

and h.saleId not in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.categoryId in (86) and DATE(d.date_time)<='{{end_date}}')

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    6: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_leche_sinbakery_alfajor,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_otros_sinbakery_alfajor,

sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_leche_sinbakery_alfajor,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_otros_sinbakery_alfajor

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'
and h.saleId not in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.parentcategoryId in (15) and DATE(d.date_time)<='{{end_date}}')

and h.saleId in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and upper(a.description) LIKE '%ALFAJOR%' and DATE(d.date_time)<='{{end_date}}')

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    8: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_leche_sinbakery_sandwiches,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_otros_sinbakery_sandwiches,

sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_leche_sinbakery_sandwiches,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_otros_sinbakery_sandwiches

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'
and h.saleId not in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.parentcategoryId in (15) and DATE(d.date_time)<='{{end_date}}')

and h.saleId in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.categoryId in (224,109) and DATE(d.date_time)<='{{end_date}}')

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    11: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_leche_sinbakery_sinsandwiches_caramelos,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_otros_sinbakery_sinsandwiches_caramelos,

sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_leche_sinbakery_sinsandwiches_caramelos,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_otros_sinbakery_sinsandwiches_caramelos

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'

and h.saleId in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.parentcategoryId in (9) and DATE(d.date_time)<='{{end_date}}')

and h.saleId not in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.parentcategoryId in (15) and DATE(d.date_time)<='{{end_date}}')

and h.saleId not in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.categoryId in (224,109) and DATE(d.date_time)<='{{end_date}}')

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
    7: f"""
select
s.name as estacion, HOUR(d.date_time) as hora, dayofweek(d.date_time) as dia_semana,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_leche_sinbakery_alfajor_cachafaz,
sum(case when c.parentcategoryId in (32) and upper(a.description) LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_llevar_algo_otros_sinbakery_alfajor_cachafaz,

sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_leche_sinbakery_alfajor_cachafaz,
sum(case when c.parentcategoryId in (32) and upper(a.description) NOT LIKE '%LLEVAR%' and a.articleId not IN ({ARTICLE_LECHE})
then d.quantity end) as q_cafes_local_algo_otros_sinbakery_alfajor_cachafaz

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and DATE(d.date_time)<='{{end_date}}'
and h.saleId not in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and c.parentcategoryId in (15) and DATE(d.date_time)<='{{end_date}}')

and h.saleId in (select distinct(h.saleId)

from rot.sale_detail d, rot.article a, rot.site s, rot.sale_header h, rot.art_category c

where d.articleId=a.articleId and a.categoryId=c.categoryId and d.siteId=s.siteId and d.saleId=h.saleId and
c.categoryLevelId=3 and DATE(d.date_time)>='{{start_date}}' and upper(a.description) LIKE '%CACHAFAZ%' and DATE(d.date_time)<='{{end_date}}')

group by estacion, HOUR(d.date_time), dayofweek(d.date_time)
""",
}


def connect():
    load_dotenv()
    hostname = os.getenv("DATABRICKS_SERVER_HOSTNAME")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    token = os.getenv("DATABRICKS_TOKEN")

    missing = [k for k, v in {
        "DATABRICKS_SERVER_HOSTNAME": hostname,
        "DATABRICKS_HTTP_PATH": http_path,
        "DATABRICKS_TOKEN": token,
    }.items() if not v]
    if missing:
        raise RuntimeError(f"Missing Databricks connection variables: {missing}")

    return sql.connect(server_hostname=hostname, http_path=http_path, access_token=token)


def dbsql(connection, query: str) -> pd.DataFrame:
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(rows, columns=columns)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract café sales-mix CSVs from Databricks.")
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD (inclusive)")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD (inclusive)")
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "raw",
        help="Directory to write export_N.csv files (default: data/raw)",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    connection = connect()

    for export_num in sorted(QUERIES):
        query = QUERIES[export_num].format(start_date=args.start_date, end_date=args.end_date)
        print(f"Ejecutando consulta para export_{export_num}...")
        df = dbsql(connection, query)
        out_path = args.output_dir / f"export_{export_num}.csv"
        df.to_csv(out_path, index=False)
        print(f"  {len(df):,} filas -> {out_path}")

    print("Extracción completa.")


if __name__ == "__main__":
    main()
