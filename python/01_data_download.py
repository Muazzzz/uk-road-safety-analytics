"""
Script 01: Data Download
Downloads official STATS19 road safety data from the UK Department for Transport.
Source: https://www.data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-accidents-safety-data
Licence: Open Government Licence v3.0

NOTE: DfT renamed "accident" -> "collision" in 2024. Files are per-year.
      This script downloads 2019-2023, combines them, and standardises column names.
"""

import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm

BASE_DIR     = Path(__file__).resolve().parent.parent
RAW_DIR      = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

YEARS = [2019, 2020, 2021, 2022, 2023]

BASE_URL = "https://data.dft.gov.uk/road-accidents-safety-data"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/csv,*/*",
}

# Per-year file templates
FILE_TEMPLATES = {
    "collisions": "dft-road-casualty-statistics-collision-{year}.csv",
    "casualties": "dft-road-casualty-statistics-casualty-{year}.csv",
    "vehicles":   "dft-road-casualty-statistics-vehicle-{year}.csv",
}

# Final combined output filenames (used by script 02 onwards)
OUTPUT_FILES = {
    "collisions": "accidents_2019_2023.csv",
    "casualties": "casualties_2019_2023.csv",
    "vehicles":   "vehicles_2019_2023.csv",
}

LOOKUP_URL      = f"{BASE_URL}/dft-road-casualty-statistics-road-safety-open-data-guide-2024.xlsx"
LOOKUP_FILENAME = "data_guide_lookup.xlsx"


# - Helpers -

def download_file(url: str, dest: Path, label: str = "") -> bool:
    if dest.exists():
        print(f"  Exists ({dest.stat().st_size/1_048_576:.1f} MB)  — skipping: {dest.name}")
        return True
    print(f"  Downloading: {label or dest.name}")
    try:
        r = requests.get(url, headers=HEADERS, stream=True, timeout=120)
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(dest, "wb") as f, tqdm(total=total, unit="B", unit_scale=True,
                                          desc=dest.name[:40], ncols=72) as bar:
            for chunk in r.iter_content(65536):
                f.write(chunk)
                bar.update(len(chunk))
        print(f"  Saved {dest.stat().st_size/1_048_576:.1f} MB -> {dest.name}")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        if dest.exists():
            dest.unlink()
        return False


def combine_years(table: str) -> pd.DataFrame:
    """Download per-year CSVs and concatenate into one DataFrame."""
    frames = []
    template = FILE_TEMPLATES[table]
    for year in YEARS:
        filename = template.format(year=year)
        url  = f"{BASE_URL}/{filename}"
        dest = RAW_DIR / filename
        ok = download_file(url, dest, f"{table} {year}")
        if ok and dest.exists():
            df = pd.read_csv(dest, low_memory=False)
            frames.append(df)
        else:
            print(f"  WARNING: {year} {table} not available, skipping")

    if not frames:
        raise RuntimeError(f"No data downloaded for {table}")

    combined = pd.concat(frames, ignore_index=True)

    # Standardise: DfT renamed collision_index -> accident_index
    if "collision_index" in combined.columns:
        combined = combined.rename(columns={"collision_index": "accident_index"})
    if "collision_year" in combined.columns:
        combined = combined.rename(columns={"collision_year": "year"})
    if "collision_ref_no" in combined.columns:
        combined = combined.rename(columns={"collision_ref_no": "accident_ref_no"})

    return combined


# - Main -

def main():
    print("=" * 65)
    print("  UK Road Safety Data — Download Script")
    print("  Source : Department for Transport (STATS19)")
    print("  Licence: Open Government Licence v3.0")
    print("  Years  : 2019 – 2023")
    print("=" * 65)

    for table, out_file in OUTPUT_FILES.items():
        out_path = RAW_DIR / out_file
        if out_path.exists():
            print(f"\n[{table}] Combined file already exists — skipping download")
            continue

        print(f"\n[{table.upper()}]")
        df = combine_years(table)
        df.to_csv(out_path, index=False)
        print(f"  Combined {len(df):,} rows -> {out_file}")

    # Try to download lookup file (non-critical)
    lookup_dest = RAW_DIR / LOOKUP_FILENAME
    if not lookup_dest.exists():
        print(f"\n[LOOKUP]")
        download_file(LOOKUP_URL, lookup_dest, "Data guide & lookup codes (xlsx)")

    # Verification summary
    print("\n-- Verification ------------------------------------------------")
    for table, out_file in OUTPUT_FILES.items():
        path = RAW_DIR / out_file
        if path.exists():
            df = pd.read_csv(path, nrows=0)
            size = path.stat().st_size / 1_048_576
            # count rows without loading full df again if large
            with open(path) as f:
                row_count = sum(1 for _ in f) - 1
            print(f"  {table:12s}: {row_count:>9,} rows | {len(df.columns)} cols | {size:.1f} MB")
        else:
            print(f"  {table:12s}: NOT FOUND")
    print("----------------------------------------------------------------")
    print("\nAll downloads complete.")
    print(f"Data saved to: {RAW_DIR}")
    print("\nNext step: python python/02_data_cleaning.py")


if __name__ == "__main__":
    main()

