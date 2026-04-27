"""
Script 02: Data Cleaning & Feature Engineering
Cleans STATS19 raw data, decodes numeric codes, engineers analytical features,
and saves tidy CSVs ready for SQL loading and Power BI.
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR  = BASE_DIR / "data" / "raw"
PROC_DIR = BASE_DIR / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

# - Lookup dictionaries (from DfT STATS19 data guide) -

ACCIDENT_SEVERITY = {1: "Fatal", 2: "Serious", 3: "Slight"}

DAY_OF_WEEK = {
    1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday",
    5: "Thursday", 6: "Friday", 7: "Saturday",
}

ROAD_TYPE = {
    1: "Roundabout", 2: "One way street", 3: "Dual carriageway",
    6: "Single carriageway", 7: "Slip road", 9: "Unknown", 12: "One way street/Slip road",
}

LIGHT_CONDITIONS = {
    1: "Daylight", 4: "Darkness - lights lit", 5: "Darkness - lights unlit",
    6: "Darkness - no lighting", 7: "Darkness - lighting unknown",
}

WEATHER_CONDITIONS = {
    1: "Fine no high winds", 2: "Raining no high winds", 3: "Snowing no high winds",
    4: "Fine + high winds", 5: "Raining + high winds", 6: "Snowing + high winds",
    7: "Fog or mist", 8: "Other", 9: "Unknown",
}

ROAD_SURFACE = {
    1: "Dry", 2: "Wet or damp", 3: "Snow", 4: "Frost or ice",
    5: "Flood over 3cm", 6: "Oil or diesel", 7: "Mud", -1: "Data missing",
}

URBAN_RURAL = {1: "Urban", 2: "Rural", 3: "Unallocated"}

JUNCTION_DETAIL = {
    0: "Not at junction", 1: "Roundabout", 2: "Mini-roundabout",
    3: "T or staggered junction", 5: "Slip road", 6: "Crossroads",
    7: "More than 4 arms", 8: "Private drive", 9: "Other junction", 99: "Unknown",
}

SPEED_LIMIT_BAND = {
    20: "20 mph", 30: "30 mph", 40: "40 mph", 50: "50 mph",
    60: "60 mph", 70: "70 mph",
}

VEHICLE_TYPE = {
    1: "Pedal cycle", 2: "Motorcycle 50cc and under", 3: "Motorcycle 125cc and under",
    4: "Motorcycle over 125cc and up to 500cc", 5: "Motorcycle over 500cc",
    8: "Taxi/Private hire car", 9: "Car", 10: "Minibus (8-16 passenger seats)",
    11: "Bus or coach (over 16 passenger seats)", 16: "Ridden horse",
    17: "Agricultural vehicle", 18: "Tram", 19: "Van / Goods 3.5 tonnes mgw or under",
    20: "Goods over 3.5t. and under 7.5t", 21: "Goods 7.5 tonnes mgw and over",
    22: "Mobility scooter", 23: "Electric motorcycle", 90: "Other vehicle",
    97: "Motorcycle - unknown cc", 98: "Goods vehicle - unknown weight",
}

CASUALTY_CLASS = {1: "Driver or rider", 2: "Passenger", 3: "Pedestrian"}
CASUALTY_SEVERITY = {1: "Fatal", 2: "Serious", 3: "Slight"}
SEX = {1: "Male", 2: "Female", -1: "Unknown"}

POLICE_FORCE = {
    1: "Metropolitan Police", 3: "Cumbria", 4: "Lancashire", 5: "Merseyside",
    6: "Greater Manchester", 7: "Cheshire", 10: "Northumbria", 11: "Durham",
    12: "North Yorkshire", 13: "West Yorkshire", 14: "South Yorkshire",
    16: "Humberside", 17: "Cleveland", 20: "West Midlands", 21: "Staffordshire",
    22: "West Mercia", 23: "Warwickshire", 25: "Derbyshire", 26: "Nottinghamshire",
    27: "Lincolnshire", 28: "Northamptonshire", 30: "Leicestershire", 31: "Cambridgeshire",
    32: "Norfolk", 33: "Suffolk", 35: "Hertfordshire", 36: "Bedfordshire",
    37: "Thames Valley", 40: "Hampshire", 42: "Sussex", 43: "Surrey",
    44: "Kent", 45: "Essex", 46: "City of London", 47: "Avon and Somerset",
    48: "Gloucestershire", 49: "Wiltshire", 50: "Dorset", 52: "Devon and Cornwall",
    53: "Dyfed-Powys", 54: "Gwent", 55: "South Wales", 56: "North Wales",
    60: "Northern Ireland (PSNI)",
    # Scotland
    96: "Police Scotland",
}


# - Cleaning functions -

def clean_accidents(path: Path) -> pd.DataFrame:
    print("  Loading accidents...")
    df = pd.read_csv(path, low_memory=False)
    print(f"    Raw shape: {df.shape}")

    # Normalise column names — DfT uses both "accident_severity" and "collision_severity"
    rename_map = {
        "collision_severity":           "accident_severity",
        "collision_date":               "date",
        "collision_time":               "time",
        "accident_year":                "year",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Parse date/time — handle both "date" and direct year column
    if "date" in df.columns:
        df["accident_date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        df["year"]  = df["accident_date"].dt.year
        df["month"] = df["accident_date"].dt.month
        df["quarter"] = df["accident_date"].dt.quarter
    else:
        # New format has year column but no date string
        df["accident_date"] = pd.to_datetime(df["year"].astype(str) + "-01-01", errors="coerce")
        df["month"] = 1
        df["quarter"] = 1

    df["month_name"] = df["accident_date"].dt.strftime("%b")

    if "time" in df.columns:
        df["hour"] = df["time"].astype(str).str[:2].replace("nan", None)
        df["hour"] = pd.to_numeric(df["hour"], errors="coerce")
    else:
        df["hour"] = None

    # Decode categoricals (safe: only map if column exists)
    def safe_map(col, lookup):
        if col in df.columns:
            df[col + "_label"] = df[col].map(lookup)

    safe_map("accident_severity", ACCIDENT_SEVERITY)
    safe_map("day_of_week",       DAY_OF_WEEK)
    safe_map("road_type",         ROAD_TYPE)
    safe_map("light_conditions",  LIGHT_CONDITIONS)
    safe_map("weather_conditions", WEATHER_CONDITIONS)
    safe_map("road_surface_conditions", ROAD_SURFACE)
    safe_map("urban_or_rural_area", URBAN_RURAL)
    safe_map("junction_detail",   JUNCTION_DETAIL)
    safe_map("police_force",      POLICE_FORCE)
    safe_map("speed_limit",       SPEED_LIMIT_BAND)

    # Keep readable column names used elsewhere
    if "accident_severity_label" not in df.columns and "accident_severity" in df.columns:
        df["severity_label"] = df["accident_severity"].map(ACCIDENT_SEVERITY)
    elif "accident_severity_label" in df.columns:
        df["severity_label"] = df["accident_severity_label"]

    for src, dst in [
        ("day_of_week_label",          "day_of_week_label"),
        ("road_type_label",            "road_type_label"),
        ("light_conditions_label",     "light_label"),
        ("weather_conditions_label",   "weather_label"),
        ("road_surface_conditions_label", "road_surface_label"),
        ("urban_or_rural_area_label",  "urban_rural_label"),
        ("junction_detail_label",      "junction_label"),
        ("police_force_label",         "police_force_label"),
        ("speed_limit_label",          "speed_limit_label"),
    ]:
        if src in df.columns and src != dst:
            df[dst] = df[src]

    # Feature engineering
    df["is_fatal"]   = (df["accident_severity"] == 1).astype(int)
    df["is_serious"] = (df["accident_severity"] == 2).astype(int)
    df["is_night"]   = df["light_conditions"].isin([4, 5, 6, 7]).astype(int)
    df["is_wet_road"] = df["road_surface_conditions"].isin([2, 3, 4, 5]).astype(int)

    # Time bands
    bins   = [-1, 6, 9, 12, 15, 18, 21, 24]
    labels = ["Overnight (0-6)", "AM Peak (7-9)", "Mid-Morning (10-12)",
              "Afternoon (13-15)", "PM Peak (16-18)", "Evening (19-21)", "Night (22-24)"]
    df["time_band"] = pd.cut(df["hour"], bins=bins, labels=labels)

    # Weekend flag
    df["is_weekend"] = df["day_of_week"].isin([1, 7]).astype(int)

    # Drop rows with no date
    before = len(df)
    df = df.dropna(subset=["accident_date"])
    print(f"    Dropped {before - len(df)} rows with missing dates")
    print(f"    Clean shape: {df.shape}")

    return df


def clean_casualties(path: Path) -> pd.DataFrame:
    print("  Loading casualties...")
    df = pd.read_csv(path, low_memory=False)
    print(f"    Raw shape: {df.shape}")

    df["casualty_class_label"]    = df["casualty_class"].map(CASUALTY_CLASS)
    df["casualty_severity_label"] = df["casualty_severity"].map(CASUALTY_SEVERITY)
    df["sex_label"]               = df["sex_of_casualty"].map(SEX)

    # New format uses casualty_type; old format used vehicle_type inside casualties
    type_col = "casualty_type" if "casualty_type" in df.columns else "vehicle_type"
    if type_col in df.columns:
        df["vehicle_type_label"] = df[type_col].map(VEHICLE_TYPE)

    # Age band — new format has pre-computed age_band_of_casualty
    if "age_band_of_casualty" in df.columns:
        df["age_band"] = df["age_band_of_casualty"].astype(str)
    elif "age_of_casualty" in df.columns:
        bins   = [0, 15, 25, 40, 60, 75, 150]
        labels = ["0-15", "16-25", "26-40", "41-60", "61-75", "75+"]
        df["age_band"] = pd.cut(df["age_of_casualty"], bins=bins, labels=labels)

    df["is_fatal"]   = (df["casualty_severity"] == 1).astype(int)
    df["is_serious"] = (df["casualty_severity"] == 2).astype(int)

    print(f"    Clean shape: {df.shape}")
    return df


def clean_vehicles(path: Path) -> pd.DataFrame:
    print("  Loading vehicles...")
    df = pd.read_csv(path, low_memory=False)
    print(f"    Raw shape: {df.shape}")

    df["vehicle_type_label"] = df["vehicle_type"].map(VEHICLE_TYPE)

    # New format has age_of_vehicle directly; old format had vehicle_year_of_manufacture
    if "age_of_vehicle" in df.columns:
        df["vehicle_age"] = pd.to_numeric(df["age_of_vehicle"], errors="coerce").clip(0, 50)
    elif "vehicle_year_of_manufacture" in df.columns:
        df["vehicle_age"] = (2024 - df["vehicle_year_of_manufacture"]).clip(0, 50)
    else:
        df["vehicle_age"] = np.nan

    bins   = [0, 3, 7, 15, 25, 51]
    labels = ["New (0-3y)", "Mid (4-7y)", "Old (8-15y)", "Ageing (16-25y)", "Very old (25y+)"]
    df["vehicle_age_band"] = pd.cut(df["vehicle_age"], bins=bins, labels=labels)

    if "engine_capacity_cc" in df.columns:
        df["engine_over_2000cc"] = (pd.to_numeric(df["engine_capacity_cc"], errors="coerce") > 2000).astype(int)

    print(f"    Clean shape: {df.shape}")
    return df


# - Main -

def main():
    print("=" * 65)
    print("  UK Road Safety — Data Cleaning & Feature Engineering")
    print("=" * 65)

    acc_path = RAW_DIR / "accidents_2019_2023.csv"
    cas_path = RAW_DIR / "casualties_2019_2023.csv"
    veh_path = RAW_DIR / "vehicles_2019_2023.csv"

    for p in [acc_path, cas_path, veh_path]:
        if not p.exists():
            raise FileNotFoundError(f"Missing raw file: {p}\nRun 01_data_download.py first.")

    accidents  = clean_accidents(acc_path)
    casualties = clean_casualties(cas_path)
    vehicles   = clean_vehicles(veh_path)

    # Save processed data
    print("\nSaving processed files...")
    accidents.to_csv(PROC_DIR / "accidents_clean.csv", index=False)
    casualties.to_csv(PROC_DIR / "casualties_clean.csv", index=False)
    vehicles.to_csv(PROC_DIR / "vehicles_clean.csv", index=False)

    # Save Power BI / Excel export (lighter, key columns only)
    export_cols_acc = [
        "accident_index", "year", "month", "month_name", "quarter",
        "day_of_week_label", "hour", "time_band", "is_weekend",
        "accident_severity", "severity_label", "is_fatal", "is_serious",
        "number_of_casualties", "number_of_vehicles",
        "police_force_label", "local_authority_district",
        "urban_rural_label", "speed_limit", "speed_limit_label",
        "road_type_label", "junction_label",
        "light_label", "weather_label", "road_surface_label",
        "is_night", "is_wet_road",
        "latitude", "longitude",
    ]
    export_cols_acc = [c for c in export_cols_acc if c in accidents.columns]

    export_dir = BASE_DIR / "data" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    accidents[export_cols_acc].to_csv(export_dir / "accidents_export.csv", index=False)
    casualties.to_csv(export_dir / "casualties_export.csv", index=False)
    vehicles.to_csv(export_dir / "vehicles_export.csv", index=False)

    print("\n- Summary -")
    print(f"  Accidents  : {len(accidents):>9,} rows")
    print(f"  Casualties : {len(casualties):>9,} rows")
    print(f"  Vehicles   : {len(vehicles):>9,} rows")
    print(f"  Years      : {accidents['year'].min()} – {accidents['year'].max()}")
    print(f"  Fatal accidents : {accidents['is_fatal'].sum():,}")
    print(f"  Severity split  : {accidents['severity_label'].value_counts().to_dict()}")
    print("-")
    print(f"\nProcessed data saved to: {PROC_DIR}")
    print(f"Export data saved to:    {export_dir}")
    print("\nNext step: run  python/03_eda_analysis.py")


if __name__ == "__main__":
    main()

