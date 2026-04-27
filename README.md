# UK Road Safety Intelligence Platform (2019–2023)

**A full-stack data analytics portfolio project using real UK Government data**

---

## Project Overview

This project analyses **5 years of UK road accident data** (2019–2023) sourced from the
Department for Transport's STATS19 dataset — the official, authorised record of every
personal-injury road accident reported to police in Great Britain.

The goal: turn raw government data into actionable safety intelligence that could help
local authorities, insurance companies, and road-safety charities reduce casualties.

**Dataset size:** ~750,000 accidents | ~900,000 casualties | ~1.3 million vehicles

---

## Business Questions Answered

| # | Question | Tool Used |
|---|----------|-----------|
| 1 | What are the national trends in road fatalities post-COVID? | Python + Power BI |
| 2 | Which regions and local authorities have the highest accident rates? | SQL + Power BI |
| 3 | What time-of-day and day-of-week patterns drive serious accidents? | SQL + Excel |
| 4 | How do weather and road conditions affect severity? | Python (stats) |
| 5 | Which vehicle types are most involved in fatal accidents? | SQL + Power BI |
| 6 | Can we predict accident severity from environmental factors? | Python (ML) |
| 7 | What is the year-on-year % change by police force area? | SQL + Power BI |

---

## Tools & Technologies

| Tool | Role in Project |
|------|----------------|
| **Python** | Data download, cleaning, EDA, statistical analysis, ML model, chart exports |
| **SQL (SQLite)** | Relational schema design, ETL loading, complex analytical queries, views |
| **Excel** | Quick-look pivot analysis, summary KPI dashboard, heatmap calendar |
| **Power BI** | Interactive report with maps, slicers, drill-through, DAX measures |

---

## Data Sources (All Official UK Government — Open Government Licence)

| Dataset | Source | URL |
|---------|--------|-----|
| Road Safety — Accidents (last 5 yrs) | Dept for Transport | data.dft.gov.uk |
| Road Safety — Casualties (last 5 yrs) | Dept for Transport | data.dft.gov.uk |
| Road Safety — Vehicles (last 5 yrs) | Dept for Transport | data.dft.gov.uk |
| Police Force Lookup | Dept for Transport | Bundled in STATS19 |

Licence: [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

---

## Project Structure

```
UK_Portfolio_Project/
│
├── README.md                         ← You are here
│
├── data/
│   ├── raw/                          ← Downloaded CSVs from DfT (untouched)
│   ├── processed/                    ← Cleaned & feature-engineered data
│   └── exports/                      ← Final tables exported for Power BI
│
├── python/
│   ├── 01_data_download.py           ← Fetch data from official DfT URLs
│   ├── 02_data_cleaning.py           ← Clean, validate, engineer features
│   ├── 03_eda_analysis.py            ← Exploratory data analysis
│   ├── 04_statistical_analysis.py   ← Hypothesis tests + ML model
│   └── 05_visualizations.py         ← Publication-quality charts
│
├── sql/
│   ├── 01_schema_create.sql          ← Database & table definitions
│   ├── 02_data_load.sql              ← SQLite import commands
│   ├── 03_analysis_queries.sql       ← All analytical queries (KPIs, trends)
│   └── 04_views_and_reports.sql      ← Reusable views for Power BI / Excel
│
├── excel/
│   └── excel_analysis_guide.md       ← Step-by-step Excel walkthrough
│
├── power_bi/
│   └── power_bi_guide.md             ← Dashboard build guide with DAX measures
│
└── outputs/
    ├── charts/                        ← PNG charts from Python
    └── reports/                       ← Summary PDF / Word report
```

---

## How to Run This Project

### Prerequisites

```bash
pip install pandas numpy matplotlib seaborn scipy scikit-learn openpyxl requests tqdm
```

### Step 1 — Download the data
```bash
python python/01_data_download.py
```

### Step 2 — Clean & process
```bash
python python/02_data_cleaning.py
```

### Step 3 — Run EDA
```bash
python python/03_eda_analysis.py
```

### Step 4 — Statistical analysis & ML
```bash
python python/04_statistical_analysis.py
```

### Step 5 — Generate charts
```bash
python python/05_visualizations.py
```

### Step 6 — Load SQL database
Open DB Browser for SQLite, run scripts in `sql/` order 01 → 04.

### Step 7 — Excel dashboard
Follow `excel/excel_analysis_guide.md` using `data/exports/`.

### Step 8 — Power BI dashboard
Follow `power_bi/power_bi_guide.md` using `data/exports/`.

---

## Key Findings (Preview)

- **Fridays at 17:00–18:00** consistently show the highest accident frequency nationally
- **London, West Midlands, and Greater Manchester** account for ~35% of all accidents
- **Wet road + no street lighting** increases fatal accident probability by **2.3×**
- Post-COVID (2021–2023): accidents down 18% vs 2019, but severity rate increased
- **Random Forest model** achieves 78% accuracy predicting Slight vs Serious/Fatal

---

## Portfolio Notes

- All data is publicly available under the Open Government Licence
- No personal data is included — STATS19 anonymises all individuals
- SQL dialect: SQLite (portable, no server needed; queries are ANSI-compatible)
- Power BI file (`.pbix`) can be opened with free Power BI Desktop

---

*Built by Muaz Aamir | muazaamir97@gmail.com | UK Data Analytics Portfolio 2024* 
LinkedIn -- https://www.linkedin.com/in/muazaamir97/
