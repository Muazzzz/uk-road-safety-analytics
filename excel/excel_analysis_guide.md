# Excel Analysis Guide
## UK Road Safety Intelligence Platform

---

## Overview

Excel is used here for **quick-look analysis, pivot tables, and a KPI summary dashboard** — showing employers you can work fast in the tool that dominates UK business.

**File to create:** `excel/UK_Road_Safety_Excel.xlsx`
**Input data:** `data/exports/accidents_export.csv`

---

## Part 1 — Import the Data

### 1.1 Load the CSV
1. Open Excel → **Data** tab → **Get Data** → **From Text/CSV**
2. Navigate to `data/exports/accidents_export.csv`
3. Click **Transform Data** (opens Power Query Editor)

### 1.2 Power Query Transformations
In Power Query Editor:

| Column | Action |
|--------|--------|
| `accident_date` | Change type → **Date** |
| `hour` | Change type → **Whole Number** |
| `year`, `month` | Change type → **Whole Number** |
| `number_of_casualties`, `number_of_vehicles` | Change type → **Whole Number** |
| `is_fatal`, `is_serious`, `is_night`, `is_wet_road`, `is_weekend` | Change type → **Whole Number** |
| `latitude`, `longitude` | Change type → **Decimal Number** |

4. Click **Close & Load To…** → **Table** → Sheet named **"RawData"**

---

## Part 2 — Pivot Table Analysis

Create a new sheet called **"Pivot Analysis"**.

### Pivot 1: Annual Accident Trends

1. Select any cell in RawData → Insert → **PivotTable** → New Worksheet
2. Rename sheet: "Pivot Analysis"

**Configuration:**
- Rows: `year`
- Values:
  - Count of `accident_index` → rename **"Total Accidents"**
  - Sum of `is_fatal`          → rename **"Fatalities"**
  - Sum of `is_serious`        → rename **"Serious"**
  - Sum of `number_of_casualties` → rename **"Casualties"**

**Calculated Field** (PivotTable Analyze → Fields, Items & Sets → Calculated Field):
- Name: `Fatality Rate %`
- Formula: `=is_fatal / accident_count * 100`

**Add a Line Chart** from this pivot → title: *"UK Road Accidents 2019–2023"*

---

### Pivot 2: Severity by Year (Stacked Bar)

- Rows: `year`
- Columns: `severity_label`
- Values: Count of `accident_index`

**Insert → Stacked Bar Chart** → Format with colours:
- Slight = dark blue `#003f5c`
- Serious = orange `#ff7c43`
- Fatal = red `#d45087`

---

### Pivot 3: Hour-of-Day Analysis

- Rows: `hour`
- Values: Count of `accident_index`, Sum of `is_fatal`

**Calculated Field:** `Fatality Rate % = is_fatal / accident_count * 100`

**Insert → Line Chart with dual axis** (accidents on left, fatality rate on right)

---

### Pivot 4: Police Force League Table

- Rows: `police_force_label`
- Values:
  - Count of `accident_index` (→ "Accidents")
  - Sum of `is_fatal` (→ "Fatalities")
  - Sum of `number_of_casualties` (→ "Casualties")
- Sort by Accidents descending
- Filter: Top 15 by Accidents

**Insert → Horizontal Bar Chart** → rename sheet "Regional Analysis"

---

### Pivot 5: Conditions Matrix (Slicer-driven)

- Rows: `weather_label`
- Columns: `severity_label`
- Values: Count of `accident_index`

**Add Slicers:**
- PivotTable Analyze → Insert Slicer → select:
  - `year`
  - `urban_rural_label`
  - `speed_limit_label`

Connect all slicers to this pivot (right-click slicer → Report Connections → tick all pivots).

---

## Part 3 — Heatmap Calendar

Create sheet: **"Heatmap"**

### Step-by-step:

1. Create a new pivot: Rows = `day_of_week_label`, Columns = `hour`, Values = Count of accidents
2. Copy-paste as **Values** (not live pivot) to a clean area
3. Select the values range → **Home → Conditional Formatting → Color Scale**
   - Min: White, Mid: Light orange, Max: Dark red
4. Adjust column widths to make cells square
5. Add labels: hours 0–23 across top, days down the side

**Result:** A red-heat heatmap showing danger peaks

---

## Part 4 — KPI Dashboard

Create sheet: **"Dashboard"** — this is your showcase page.

### Layout (use no gridlines: View → uncheck Gridlines)

```
┌─────────────────────────────────────────────────────────────────────┐
│  🇬🇧 UK ROAD SAFETY DASHBOARD 2019–2023          [Year Slicer]      │
├──────────┬──────────┬──────────┬──────────┬──────────┬─────────────┤
│  TOTAL   │ TOTAL    │ KSI      │ FATALITY │ CASUALTY │  YOY        │
│ ACCIDENTS│FATALITIES│  RATE    │   RATE   │   RATE   │ CHANGE      │
│  741,235 │  14,890  │  8.4%    │  2.0%    │  1.38    │  -3.2%      │
├──────────┴──────────┴──────────┴──────────┴──────────┴─────────────┤
│  [Line Chart: Monthly Trend]    │  [Donut: Severity Split]          │
│                                 │                                   │
├─────────────────────────────────┴───────────────────────────────────┤
│  [Heatmap: Hour × Day]                                              │
│                                                                     │
├─────────────────────────────────┬───────────────────────────────────┤
│  [Bar: Top 10 Regions]          │  [Bar: Weather Risk]              │
└─────────────────────────────────┴───────────────────────────────────┘
```

### KPI Cards (use INDEX/MATCH formulas):

```excel
Total Accidents (2023):
=SUMPRODUCT((RawData[year]=2023)*1)

Total Fatalities (2023):
=SUMPRODUCT((RawData[year]=2023)*RawData[is_fatal])

KSI Rate (2023):
=SUMPRODUCT((RawData[year]=2023)*(RawData[is_fatal]+RawData[is_serious]))
 / SUMPRODUCT((RawData[year]=2023)*1)

YoY Change:
=(SUMPRODUCT((RawData[year]=2023)*1) - SUMPRODUCT((RawData[year]=2022)*1))
 / SUMPRODUCT((RawData[year]=2022)*1)
```

Format YoY Change cell as **Percentage with 1 decimal place** + conditional formatting:
- Red font if > 0 (more accidents = bad)
- Green font if < 0

### Sparklines (in KPI row):
- Insert → Sparklines → Line → data range = each year's monthly total

---

## Part 5 — Advanced Excel: COUNTIFS Analysis

On a sheet **"Advanced Formulas"**, demonstrate these:

```excel
-- Peak hour accidents
=COUNTIFS(RawData[hour],17, RawData[year],2023)

-- Night + wet road fatal accidents
=SUMPRODUCT((RawData[is_night]=1)*(RawData[is_wet_road]=1)*(RawData[is_fatal]=1))

-- % of accidents on a Friday PM peak
=COUNTIFS(RawData[day_of_week_label],"Friday",RawData[hour],17)
 / COUNTIFS(RawData[day_of_week_label],"Friday")

-- London vs rest: fatality rate comparison
=COUNTIFS(RawData[police_force_label],"Metropolitan Police",RawData[is_fatal],1)
 / COUNTIFS(RawData[police_force_label],"Metropolitan Police")

-- Worst year for fatal accidents
=INDEX(RawData[year], MATCH(MAX(
    COUNTIFS(RawData[year],{2019,2020,2021,2022,2023},RawData[is_fatal],1)
  ), COUNTIFS(RawData[year],{2019,2020,2021,2022,2023},RawData[is_fatal],1), 0))
```

---

## Part 6 — Formatting Tips for Portfolio Quality

1. **Theme:** File → Options → General → Office Theme → use a professional theme
2. **No gridlines** on dashboard: View → untick Gridlines
3. **Chart style:** Right-click chart → Change Chart Style → Style 8 (dark)
4. **Consistent colours:** Use the STATS19 brand palette `#003f5c` for primary bars
5. **Add data labels** to all bar charts
6. **Title font:** Calibri or Segoe UI, 14pt bold, dark navy
7. **Page layout** → Set print area → Fit to 1 page wide

---

## Part 7 — Save as Excel Workbook

1. File → Save As → `excel/UK_Road_Safety_Excel.xlsx`
2. Create a second version as: `excel/UK_Road_Safety_Excel_Presentation.xlsx`
   - On this version, hide the "RawData" tab (right-click → Hide)
   - Set Dashboard as the default active sheet

---

## Summary: What This Excel File Demonstrates

| Skill | Where Shown |
|-------|-------------|
| Power Query / data import | Part 1 |
| PivotTables & PivotCharts | Part 2 |
| Conditional formatting | Parts 3 & 4 |
| Advanced formulas (COUNTIFS, SUMPRODUCT, INDEX/MATCH) | Part 5 |
| Dashboard layout & design | Part 4 |
| Year-over-year KPI tracking | Part 4 |
| Data storytelling | Throughout |
