"""
Script 03: Exploratory Data Analysis (EDA)
Generates descriptive statistics, distributions, correlations, and
year-over-year trend summaries. Results are saved to outputs/reports/.
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR  = Path(__file__).resolve().parent.parent
PROC_DIR  = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# - Load data -

def load_data():
    print("Loading processed data...")
    acc = pd.read_csv(PROC_DIR / "accidents_clean.csv", low_memory=False)
    cas = pd.read_csv(PROC_DIR / "casualties_clean.csv", low_memory=False)
    veh = pd.read_csv(PROC_DIR / "vehicles_clean.csv", low_memory=False)
    print(f"  accidents: {len(acc):,}  |  casualties: {len(cas):,}  |  vehicles: {len(veh):,}")
    return acc, cas, veh


# - EDA sections -

def eda_national_trends(acc: pd.DataFrame) -> pd.DataFrame:
    """Year-on-year national KPIs."""
    print("\n[1] National Trends by Year")

    yearly = acc.groupby("year").agg(
        total_accidents    = ("accident_index", "count"),
        fatal_accidents    = ("is_fatal", "sum"),
        serious_accidents  = ("is_serious", "sum"),
        total_casualties   = ("number_of_casualties", "sum"),
        avg_casualties_per_accident = ("number_of_casualties", "mean"),
    ).reset_index()

    yearly["slight_accidents"] = yearly["total_accidents"] - yearly["fatal_accidents"] - yearly["serious_accidents"]
    yearly["fatality_rate_%"]  = (yearly["fatal_accidents"] / yearly["total_accidents"] * 100).round(2)
    yearly["yoy_change_%"]     = yearly["total_accidents"].pct_change() * 100
    yearly["yoy_change_%"]     = yearly["yoy_change_%"].round(1)

    print(yearly.to_string(index=False))
    yearly.to_csv(REPORT_DIR / "01_national_trends_yearly.csv", index=False)
    return yearly


def eda_severity_breakdown(acc: pd.DataFrame) -> None:
    """Severity distribution overall and by year."""
    print("\n[2] Severity Distribution")

    overall = acc["severity_label"].value_counts().rename_axis("severity").reset_index(name="count")
    overall["pct"] = (overall["count"] / overall["count"].sum() * 100).round(1)
    print(overall.to_string(index=False))
    overall.to_csv(REPORT_DIR / "02_severity_overall.csv", index=False)

    by_year = acc.groupby(["year", "severity_label"]).size().reset_index(name="count")
    pivot   = by_year.pivot(index="year", columns="severity_label", values="count").fillna(0)
    pivot.to_csv(REPORT_DIR / "02_severity_by_year.csv")
    print(pivot.to_string())


def eda_time_patterns(acc: pd.DataFrame) -> None:
    """Hour-of-day, day-of-week, and monthly patterns."""
    print("\n[3] Time Patterns")

    # Hour of day
    hourly = acc.groupby("hour").agg(
        total   = ("accident_index", "count"),
        fatal   = ("is_fatal", "sum"),
    ).reset_index()
    hourly["fatal_rate_%"] = (hourly["fatal"] / hourly["total"] * 100).round(2)
    peak_hour = hourly.loc[hourly["total"].idxmax(), "hour"]
    print(f"  Peak accident hour: {int(peak_hour):02d}:00")
    hourly.to_csv(REPORT_DIR / "03_accidents_by_hour.csv", index=False)

    # Day of week
    dow = acc.groupby("day_of_week_label").agg(
        total = ("accident_index", "count"),
        fatal = ("is_fatal", "sum"),
    ).reset_index()
    dow.to_csv(REPORT_DIR / "03_accidents_by_day.csv", index=False)

    # Month
    monthly = acc.groupby(["year", "month"]).agg(
        total = ("accident_index", "count"),
        fatal = ("is_fatal", "sum"),
    ).reset_index()
    monthly.to_csv(REPORT_DIR / "03_accidents_monthly.csv", index=False)

    # Time band
    if "time_band" in acc.columns:
        tband = acc.groupby("time_band").agg(
            total = ("accident_index", "count"),
            fatal = ("is_fatal", "sum"),
        ).reset_index()
        tband["fatal_rate_%"] = (tband["fatal"] / tband["total"] * 100).round(2)
        print(tband.to_string(index=False))
        tband.to_csv(REPORT_DIR / "03_accidents_by_timeband.csv", index=False)


def eda_geography(acc: pd.DataFrame) -> None:
    """Regional / police force breakdown."""
    print("\n[4] Geographic Distribution")

    if "police_force_label" not in acc.columns:
        print("  police_force_label column not found, skipping")
        return

    region = acc.groupby("police_force_label").agg(
        total_accidents  = ("accident_index", "count"),
        fatal_accidents  = ("is_fatal", "sum"),
        total_casualties = ("number_of_casualties", "sum"),
    ).reset_index().sort_values("total_accidents", ascending=False)

    region["fatal_rate_%"] = (region["fatal_accidents"] / region["total_accidents"] * 100).round(2)
    print(region.head(10).to_string(index=False))
    region.to_csv(REPORT_DIR / "04_accidents_by_region.csv", index=False)

    if "urban_rural_label" in acc.columns:
        ur = acc.groupby(["urban_rural_label", "severity_label"]).size().reset_index(name="count")
        pivot_ur = ur.pivot(index="urban_rural_label", columns="severity_label", values="count").fillna(0)
        pivot_ur.to_csv(REPORT_DIR / "04_urban_rural_severity.csv")
        print("\n  Urban vs Rural severity split:")
        print(pivot_ur.to_string())


def eda_conditions(acc: pd.DataFrame) -> None:
    """Environmental conditions and severity."""
    print("\n[5] Conditions Analysis")

    conditions = {
        "weather_label":       "Weather",
        "road_surface_label":  "Road Surface",
        "light_label":         "Light Conditions",
        "speed_limit_label":   "Speed Limit",
    }

    for col, label in conditions.items():
        if col not in acc.columns:
            continue
        grp = acc.groupby(col).agg(
            total     = ("accident_index", "count"),
            fatal     = ("is_fatal", "sum"),
            serious   = ("is_serious", "sum"),
        ).reset_index()
        grp["fatal_rate_%"]   = (grp["fatal"] / grp["total"] * 100).round(2)
        grp["serious_rate_%"] = (grp["serious"] / grp["total"] * 100).round(2)
        safe_col = col.replace(" ", "_")
        grp.to_csv(REPORT_DIR / f"05_{safe_col}.csv", index=False)
        print(f"\n  {label}:\n{grp.sort_values('fatal_rate_%', ascending=False).head(5).to_string(index=False)}")


def eda_casualties(cas: pd.DataFrame) -> None:
    """Casualty demographics and severity."""
    print("\n[6] Casualty Demographics")

    # Age band
    if "age_band" in cas.columns:
        age_grp = cas.groupby(["age_band", "casualty_severity_label"]).size().reset_index(name="count")
        age_pivot = age_grp.pivot(index="age_band", columns="casualty_severity_label", values="count").fillna(0)
        age_pivot.to_csv(REPORT_DIR / "06_casualties_by_age.csv")
        print("  Casualties by age band & severity:")
        print(age_pivot.to_string())

    # Sex
    if "sex_label" in cas.columns:
        sex_grp = cas[cas["sex_label"] != "Unknown"].groupby(
            ["sex_label", "casualty_severity_label"]
        ).size().reset_index(name="count")
        sex_grp.to_csv(REPORT_DIR / "06_casualties_by_sex.csv", index=False)

    # Road user type
    if "casualty_class_label" in cas.columns:
        class_grp = cas.groupby(["casualty_class_label", "casualty_severity_label"]).size().reset_index(name="count")
        class_grp.to_csv(REPORT_DIR / "06_casualties_by_class.csv", index=False)
        print("\n  Road user type breakdown:")
        print(class_grp.to_string(index=False))


def eda_vehicles(acc: pd.DataFrame, veh: pd.DataFrame) -> None:
    """Vehicle type involvement in fatal accidents."""
    print("\n[7] Vehicle Analysis")

    if "vehicle_type_label" not in veh.columns:
        return

    # Merge fatal flag from accidents
    fatal_acc = acc[acc["is_fatal"] == 1][["accident_index"]].copy()
    fatal_acc["fatal"] = 1

    veh_merged = veh.merge(fatal_acc, on="accident_index", how="left")
    veh_merged["fatal"] = veh_merged["fatal"].fillna(0).astype(int)

    vtype = veh_merged.groupby("vehicle_type_label").agg(
        total_involved = ("accident_index", "count"),
        in_fatal       = ("fatal", "sum"),
    ).reset_index()
    vtype["fatal_involvement_%"] = (vtype["in_fatal"] / vtype["total_involved"] * 100).round(2)
    vtype = vtype.sort_values("total_involved", ascending=False)

    print(vtype.head(12).to_string(index=False))
    vtype.to_csv(REPORT_DIR / "07_vehicle_type_analysis.csv", index=False)


def eda_correlation_matrix(acc: pd.DataFrame) -> None:
    """Numeric correlation heatmap data."""
    print("\n[8] Correlation Matrix")

    numeric_cols = [
        "accident_severity", "number_of_casualties", "number_of_vehicles",
        "speed_limit", "is_night", "is_wet_road", "is_weekend", "hour",
    ]
    available = [c for c in numeric_cols if c in acc.columns]
    corr = acc[available].corr().round(3)
    corr.to_csv(REPORT_DIR / "08_correlation_matrix.csv")
    print(corr.to_string())


# - Main -

def main():
    print("=" * 65)
    print("  UK Road Safety — Exploratory Data Analysis")
    print("=" * 65)

    acc, cas, veh = load_data()

    eda_national_trends(acc)
    eda_severity_breakdown(acc)
    eda_time_patterns(acc)
    eda_geography(acc)
    eda_conditions(acc)
    eda_casualties(cas)
    eda_vehicles(acc, veh)
    eda_correlation_matrix(acc)

    print("\n- EDA Complete -")
    print(f"  Reports saved to: {REPORT_DIR}")
    report_files = list(REPORT_DIR.glob("*.csv"))
    for f in sorted(report_files):
        print(f"    {f.name}")
    print("-")
    print("\nNext step: run  python/04_statistical_analysis.py")


if __name__ == "__main__":
    main()

