# UK Road Safety Intelligence Platform (2020–2023)

**A full-stack data analytics portfolio project using real UK Government data**

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python) ![SQL](https://img.shields.io/badge/SQL-SQLite-lightgrey?logo=sqlite) ![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow?logo=powerbi) ![Excel](https://img.shields.io/badge/Excel-Dashboard-green?logo=microsoft-excel) ![Licence](https://img.shields.io/badge/Data-Open%20Government%20Licence-blue)

---

## Project Overview

This project analyses **4 years of UK road accident data** (2020–2023) sourced from the
Department for Transport's STATS19 dataset — the official, authorised record of every
personal-injury road accident reported to police in Great Britain.

**Goal:** Turn 400,000+ raw government records into actionable safety intelligence for
local authorities, insurance companies, and road-safety charities.

| Metric | Value |
|--------|-------|
| Total accidents analysed | 402,548 |
| Total casualties | 512,250 |
| Total vehicles | 737,178 |
| Years covered | 2020 – 2023 |
| Fatal accidents | 5,989 |
| Data source | UK Dept for Transport (STATS19) |
| Licence | Open Government Licence v3.0 |

---

## Key Findings

| Finding | Detail |
|---------|--------|
| Peak accident hour | **17:00** (Friday PM rush) |
| Deadliest time | **Overnight 00:00–06:00** — 3.4% fatality rate |
| Most dangerous road | **60 mph rural roads** — 4.0% fatality rate, 34% KSI rate |
| COVID impact visible | April 2020: lowest month ever (3,298 accidents) |
| Weather risk | Fog increases KSI rate to 26.7% vs 23% in fine weather |
| Night + no lighting | **5% fatality rate** — 4× higher than daylight |
| ML model | Random Forest ROC-AUC **0.637**, speed limit = top predictor |
| Statistics | All 8 environmental factors statistically significant (p < 0.001) |

---

## Charts & Visualisations

### National Trend & Year-on-Year Change
![Yearly Trend](outputs/charts/01_yearly_trend.png)

### Accident Heatmap — Day of Week × Hour of Day
![Heatmap](outputs/charts/02_dow_hour_heatmap.png)

### Severity Distribution
![Severity Donut](outputs/charts/03_severity_donut.png)

### Top 15 Police Forces by Accident Volume
![Top Regions](outputs/charts/04_top_regions.png)

### Severity by Weather Condition
![Weather Severity](outputs/charts/05_weather_severity.png)

### Fatality Rate by Speed Limit
![Speed Limit](outputs/charts/06_speed_limit_fatality.png)

### Casualties by Age Band and Sex
![Age Sex](outputs/charts/07_casualties_age_sex.png)

### Monthly Trend with COVID Context
![Monthly Trend](outputs/charts/08_monthly_trend.png)

### Random Forest — Feature Importances
![Feature Importance](outputs/charts/09_feature_importance.png)

### KSI Rate by Light Condition
![Light Conditions](outputs/charts/10_light_conditions_ksi.png)

---

## Business Questions Answered

| # | Question | Tool |
|---|----------|------|
| 1 | What are the national trends in road fatalities post-COVID? | Python + SQL |
| 2 | Which regions and local authorities have the highest accident rates? | SQL + Power BI |
| 3 | What time-of-day and day-of-week patterns drive serious accidents? | Python + Excel |
| 4 | How do weather and road conditions affect severity? | Python (chi-square) |
| 5 | Which vehicle types are most involved in fatal accidents? | SQL + Power BI |
| 6 | Can we predict accident severity from environmental factors? | Python (ML) |
| 7 | What is the year-on-year % change by police force area? | SQL |

---

## Tools & Technologies

| Tool | Role |
|------|------|
| **Python** | Data download, cleaning, EDA, chi-square tests, Random Forest ML, 10 charts |
| **SQL (SQLite)** | Relational schema, ETL, 16 analytical queries, 7 reusable views |
| **Excel** | Pivot tables, KPI dashboard, heatmap, COUNTIFS/SUMPRODUCT analysis |
| **Power BI** | 6-page interactive report, maps, drill-through, 15+ DAX measures |

---

## Project Structure

```
UK_Portfolio_Project/
├── python/
│   ├── 01_data_download.py           ← Fetch real data from DfT official URLs
│   ├── 02_data_cleaning.py           ← Clean, decode, feature engineer
│   ├── 03_eda_analysis.py            ← Descriptive stats → 18 report CSVs
│   ├── 04_statistical_analysis.py   ← Chi-square tests + Random Forest ML
│   └── 05_visualizations.py         ← 10 publication-quality charts
├── sql/
│   ├── 01_schema_create.sql          ← Tables, indexes, police force dimension
│   ├── 02_data_load.sql              ← Load + integrity checks
│   ├── 03_analysis_queries.sql       ← 16 queries across 6 analytical sections
│   └── 04_views_and_reports.sql      ← 7 reusable views for Power BI / Excel
├── excel/
│   └── excel_analysis_guide.md       ← Step-by-step Excel build guide
├── power_bi/
│   ├── power_bi_guide.md             ← 6-page dashboard guide with DAX measures
│   └── theme.json                    ← Custom Power BI colour theme
├── outputs/
│   ├── charts/                       ← 10 PNG charts (above)
│   └── reports/                      ← 18 CSV analysis reports
└── data/
    ├── raw/                          ← Run 01_data_download.py to populate
    ├── processed/                    ← Run 02_data_cleaning.py to populate
    └── exports/                      ← CSV exports for Excel / Power BI
```

---

## How to Run

```bash
# 1. Install dependencies
pip install -r python/requirements.txt

# 2. Download real UK government data (~150 MB)
python python/01_data_download.py

# 3. Clean & feature engineer
python python/02_data_cleaning.py

# 4. Exploratory data analysis
python python/03_eda_analysis.py

# 5. Statistical analysis & ML model
python python/04_statistical_analysis.py

# 6. Generate all charts
python python/05_visualizations.py
```

Then open **DB Browser for SQLite**, load `data/exports/`, run `sql/01` → `sql/04`.

Excel and Power BI: follow the step-by-step guides in `excel/` and `power_bi/`.

---

## Data Source

All data published under the **Open Government Licence v3.0** — free to use, share, and adapt.

| File | Source |
|------|--------|
| Collisions 2020–2023 | [DfT STATS19](https://www.data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-accidents-safety-data) |
| Casualties 2020–2023 | [DfT STATS19](https://www.data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-accidents-safety-data) |
| Vehicles 2020–2023 | [DfT STATS19](https://www.data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-accidents-safety-data) |

---

*Built by Muaz Aamir | [muazaamir97@gmail.com](mailto:muazaamir97@gmail.com) | [LinkedIn](https://www.linkedin.com/in/muazaamir97/) | UK Data Analytics Portfolio 2025*
