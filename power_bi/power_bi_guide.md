# Power BI Dashboard Guide
## UK Road Safety Intelligence Platform

---

## Overview

The Power BI dashboard is the **centrepiece** of this portfolio — an interactive,
multi-page report with maps, time-series, slicers, and drill-through. This is what
UK employers open first.

**Output file:** `power_bi/UK_Road_Safety_Report.pbix`

---

## Step 1 — Connect to Data

### Option A: Connect to SQLite (preferred — shows SQL skill)
1. Open Power BI Desktop
2. **Get Data → More → Database → ODBC**
3. DSN: browse to `data/road_safety.db` using SQLite ODBC driver
   - Download SQLite ODBC driver: http://www.ch-werner.de/sqliteodbc/
4. Import these views (from Script 04):
   - `vw_accident_summary`  — main fact table
   - `vw_kpi_by_year`
   - `vw_hourly_pattern`
   - `vw_region_metrics`
   - `vw_monthly_trend`
   - `vw_vehicle_risk`
   - `vw_casualty_demographics`

### Option B: Connect to CSV exports (fallback)
1. **Get Data → Text/CSV**
2. Load all files from `data/exports/`
3. In Power Query, set correct data types (see Excel guide Part 1)

---

## Step 2 — Data Model (Relationships)

In **Model View**, create these relationships:

```
vw_accident_summary (accident_index) ←→ vw_casualty_demographics (via accident_index)
vw_accident_summary (accident_index) ←→ vw_vehicle_risk (via vehicle_type_label) [inactive]
vw_kpi_by_year     (year)            ←→ vw_monthly_trend (year)
```

**Key settings:**
- Cross-filter direction: **Single** for all relationships
- Mark `vw_accident_summary` as the main fact table

---

## Step 3 — DAX Measures

Create a dedicated **"_Measures"** table (Enter Data → blank table, rename).

Paste all measures below into the Measures table:

```dax
-- ── KPI measures ───────────────────────────────────────────────

Total Accidents =
COUNTROWS(vw_accident_summary)

Total Fatalities =
SUM(vw_accident_summary[is_fatal])

Total Serious =
SUM(vw_accident_summary[is_serious])

Total KSI =
[Total Fatalities] + [Total Serious]

Total Casualties =
SUM(vw_accident_summary[number_of_casualties])

Fatality Rate % =
DIVIDE([Total Fatalities], [Total Accidents], 0) * 100

KSI Rate % =
DIVIDE([Total KSI], [Total Accidents], 0) * 100

Avg Casualties per Accident =
DIVIDE([Total Casualties], [Total Accidents], 0)


-- ── Year-on-Year comparisons ───────────────────────────────────

Accidents PY =
CALCULATE(
    [Total Accidents],
    SAMEPERIODLASTYEAR(vw_monthly_trend[year])
)

YoY Accident Change % =
DIVIDE(
    [Total Accidents] - [Accidents PY],
    [Accidents PY],
    BLANK()
) * 100

Fatalities PY =
CALCULATE(
    [Total Fatalities],
    SAMEPERIODLASTYEAR(vw_monthly_trend[year])
)

YoY Fatality Change % =
DIVIDE(
    [Total Fatalities] - [Fatalities PY],
    [Fatalities PY],
    BLANK()
) * 100


-- ── Dynamic title (responds to slicers) ───────────────────────

Selected Year =
IF(
    HASONEVALUE(vw_accident_summary[year]),
    "Year: " & SELECTEDVALUE(vw_accident_summary[year]),
    "All Years"
)

Report Subtitle =
"UK Road Accidents — " &
MIN(vw_accident_summary[year]) & "–" &
MAX(vw_accident_summary[year])


-- ── Ranking measures ───────────────────────────────────────────

Region Rank by Accidents =
RANKX(
    ALL(vw_accident_summary[police_force_label]),
    [Total Accidents],
    ,
    DESC,
    DENSE
)

Top N Regions =
IF([Region Rank by Accidents] <= 10, 1, 0)


-- ── Cumulative trend ──────────────────────────────────────────

Cumulative Accidents =
CALCULATE(
    [Total Accidents],
    FILTER(
        ALL(vw_monthly_trend[year], vw_monthly_trend[month]),
        vw_monthly_trend[year] * 100 + vw_monthly_trend[month]
        <= MAX(vw_monthly_trend[year]) * 100 + MAX(vw_monthly_trend[month])
    )
)


-- ── Conditional colour logic ──────────────────────────────────

KSI Color =
SWITCH(
    TRUE(),
    [KSI Rate %] > 10, "#d45087",   -- high risk: red
    [KSI Rate %] > 6,  "#ff7c43",   -- medium: orange
    "#003f5c"                         -- low: navy
)

YoY Direction =
IF([YoY Accident Change %] > 0, "▲", "▼")

YoY Color =
IF([YoY Accident Change %] > 0, "#d45087", "#27ae60")
```

---

## Step 4 — Report Pages

### Page 1: Executive Summary

**Layout:**

```
┌─────────────────────────────────────────────────────────────────────┐
│  HEADER: "UK Road Safety Intelligence Dashboard"  [year slicer]     │
├──────────┬──────────┬──────────┬──────────┬──────────┬─────────────┤
│  KPI Card│  KPI Card│  KPI Card│  KPI Card│  KPI Card│  KPI Card   │
│  Total   │ Fatalities│ Serious │ KSI Rate │ Casualties│ YoY Change │
│  Accidents│         │         │    %     │          │     %       │
├──────────┴──────────┼──────────┴──────────┴──────────┴─────────────┤
│  Line Chart:        │  Donut Chart:                                 │
│  Monthly Trend      │  Severity Split                               │
│  (with year slicer) │  (Fatal / Serious / Slight)                   │
├─────────────────────┼───────────────────────────────────────────────┤
│  Clustered Bar:     │  Ribbon Chart:                                │
│  Annual Accidents   │  Severity by Year                             │
│  by Year            │                                               │
└─────────────────────┴───────────────────────────────────────────────┘
```

**Visuals to add:**

1. **6× KPI Cards** (Card visual)
   - Measure: Total Accidents, Total Fatalities, Total Serious, KSI Rate %, Total Casualties, YoY Accident Change %
   - Format: Large number, conditional formatting on YoY card

2. **Line Chart: Monthly Trend**
   - X axis: year + month (hierarchy)
   - Y axis: Total Accidents
   - Secondary line: Total Fatalities (right axis)
   - Add constant line at pre-COVID 2019 average

3. **Donut Chart: Severity**
   - Legend: severity_label
   - Values: Total Accidents
   - Inner label: "Total: [Total Accidents]"
   - Colours: Slight=#003f5c, Serious=#ff7c43, Fatal=#d45087

4. **Clustered Bar: Annual Accidents**
   - X axis: year
   - Y axis: Total Accidents
   - Add data labels
   - Add trend line

5. **Ribbon/Stacked Bar: Severity by Year**
   - X: year, Y: Total Accidents, Legend: severity_label

6. **Slicer: Year** (top right, tile style)
7. **Slicer: Urban/Rural** (dropdown)
8. **Slicer: Police Force** (dropdown, searchable)

---

### Page 2: Time Patterns

**Visuals:**

1. **Heatmap (Matrix visual):**
   - Rows: day_of_week_label
   - Columns: hour (0–23)
   - Values: Total Accidents
   - Conditional formatting: background colour scale (white→red)
   - Sort rows: Monday–Sunday

2. **Stacked Area Chart: Time Band**
   - X: time_band
   - Y: Total Accidents, stacked by severity_label

3. **Line Chart: Day of Week**
   - X: day_of_week_label
   - Y: Total Accidents (bar) + Fatality Rate % (line, secondary axis)

4. **Bar Chart: Monthly Seasonality**
   - X: month_name
   - Y: Average accidents per month across years (use AVERAGEX)
   - Highlight December and November in darker colour

5. **Slicers:** Year (multi-select), Severity, Weekend toggle

---

### Page 3: Geographic Analysis (Map)

**Visuals:**

1. **Filled Map (Choropleth):**
   - Location: police_force_label
   - Values: Total Accidents (size) or KSI Rate % (colour)
   - Tooltip: Custom tooltip page with full breakdown
   - Note: Power BI may use Bing geocoding — add a "region" hierarchy if needed

2. **Bubble Map:**
   - Latitude: latitude field
   - Longitude: longitude field
   - Size: Total Accidents per grid cell
   - Colour: severity_label
   - (Use a sample of 50,000 rows for performance — create a sampled table)

3. **Horizontal Bar: Top 15 Police Forces**
   - Y: police_force_label
   - X: Total Accidents
   - Colour saturation: KSI Rate %
   - Filter: Top 15 by Total Accidents using visual-level filter

4. **Matrix: Region × Year**
   - Rows: region (from dim_police_force)
   - Columns: year
   - Values: Total Accidents
   - Conditional formatting: background colour on values

5. **Treemap: Local Authorities**
   - Group: local_authority_district
   - Values: Total KSI
   - Top 30 filter

---

### Page 4: Risk Factors

**Visuals:**

1. **Waterfall Chart: KSI Rate by Weather**
   - Category: weather_label
   - Values: KSI Rate %

2. **Clustered Bar: Road Surface vs Severity**
   - X: road_surface_label
   - Y: KSI Rate %
   - Sorted descending

3. **Scatter Plot: Speed Limit Risk**
   - X axis: speed_limit
   - Y axis: Fatality Rate %
   - Size: Total Accidents
   - Tooltip: accidents + fatalities

4. **2×2 Matrix (Custom visual or table):**
   Night/Day × Wet/Dry KSI rates — use a styled table
   ```
                  DRY ROAD    WET ROAD
   DAYLIGHT        x.x%        x.x%
   NIGHT           x.x%        x.x%   ← highest risk
   ```

5. **Column Chart: Junction Type**
   - X: junction_label
   - Y: Total Accidents + Fatal_Rate % line

6. **Slicers:** Speed Limit, Year, Urban/Rural

---

### Page 5: Vehicle & Casualty Analysis

**Visuals:**

1. **Horizontal Bar: Vehicle Type Involvement**
   - Y: vehicle_type_label
   - X: accidents_involved
   - Colour: fatal_pct (gradient)
   - Top 12 vehicle types

2. **Clustered Bar: Casualties by Age Band**
   - X: age_band
   - Y: casualties
   - Legend: sex_label (Male/Female)
   - Colour: Male=#003f5c, Female=#d45087

3. **Stacked Bar: Road User Type × Severity**
   - X: casualty_class_label (Driver/Passenger/Pedestrian)
   - Y: casualties
   - Legend: casualty_severity_label

4. **Funnel Chart: Young Drivers (17–25)**
   - Year-by-year trend of young driver accidents

5. **KPI Card Row:** Total Pedestrian Casualties | Cyclist Deaths | Motorcyclist KSI

---

### Page 6: Drill-Through Detail (hidden by default)

Create a drill-through page so users can right-click any police force bar and drill to:

1. Monthly trend for that force
2. Severity split
3. Conditions breakdown
4. Top 5 local authorities within the force

**Setup:**
- Add a **Drill-through** field: `police_force_label`
- Right-click any region chart → Drill through → this page
- Add a **Back button** (Insert → Buttons → Back)

---

## Step 5 — Formatting & Branding

### Colour Theme (import or set manually)
```json
{
  "name": "UK Road Safety",
  "dataColors": [
    "#003f5c", "#2f4b7c", "#665191", "#a05195",
    "#d45087", "#f95d6a", "#ff7c43", "#ffa600"
  ],
  "background": "#FFFFFF",
  "foreground": "#003f5c",
  "tableAccent": "#003f5c"
}
```

Save this as `power_bi/theme.json` → View → Themes → Browse for themes

### Page background
- Format → Canvas background → Colour: `#F5F7FA` (very light grey)

### Headers
- Use a **Text Box** at top of each page
- Font: Segoe UI, 18pt, bold, colour `#003f5c`
- Subtitle: 11pt, colour `#666666`

### KPI Card formatting
- Background: White with subtle drop shadow (Format → Effects → Shadow)
- Call-out value: 24pt, bold, navy
- Category label: 9pt, grey
- Add trend sparkline where possible

---

## Step 6 — Performance Optimisation

1. **Aggregation tables:** For the map bubble chart, create a summarised table in Power Query:
   ```m
   = Table.Group(accidents_export, {"latitude", "longitude", "severity_label"},
       {{"Count", each Table.RowCount(_), type number}})
   ```

2. **Remove unused columns** in Power Query before loading (right-click column → Remove)

3. **Turn off Auto date/time:** File → Options → Current File → Data Load → uncheck "Auto date/time"

4. **Import mode** (not DirectQuery) for SQLite for better performance

---

## Step 7 — Publish & Share

1. **Publish to Power BI Service:**
   - Home → Publish → select your workspace
   - URL will be: `app.powerbi.com/...`

2. **Export PDF:** File → Export → PDF (for CV attachment)

3. **Embed in portfolio website:**
   - Power BI Service → File → Embed report → Website or portal
   - Copy iframe code

---

## Summary: What This Dashboard Demonstrates

| Skill | Where Shown |
|-------|-------------|
| Data modelling (star schema) | Model view relationships |
| DAX measures (basic to advanced) | 15+ measures inc. YoY, RANKX, DIVIDE |
| Multiple chart types | 20+ visuals across 6 pages |
| Drill-through & tooltips | Page 6 |
| Custom theme & branding | All pages |
| Map visualisations | Page 3 |
| Performance optimisation | Step 6 |
| Storytelling with data | Dashboard narrative flow |
| Slicers & cross-filtering | All pages |
| Publishing & sharing | Step 7 |
