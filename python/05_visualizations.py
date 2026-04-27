"""
Script 05: Visualizations
Generates publication-quality charts using Matplotlib and Seaborn.
All charts saved as PNG to outputs/charts/ — ready for portfolio / report.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent
PROC_DIR   = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"
CHART_DIR  = BASE_DIR / "outputs" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

# - Style -
BRAND_PALETTE = ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087",
                 "#f95d6a", "#ff7c43", "#ffa600"]
sns.set_theme(style="whitegrid", palette=BRAND_PALETTE)
plt.rcParams.update({
    "figure.dpi":       150,
    "savefig.dpi":      200,
    "figure.facecolor": "white",
    "axes.spines.top":  False,
    "axes.spines.right": False,
    "font.family":      "sans-serif",
})

def save(name: str) -> None:
    path = CHART_DIR / f"{name}.png"
    plt.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Saved: {path.name}")


# - Load data -

def load_data():
    print("Loading data for visualizations...")
    acc = pd.read_csv(PROC_DIR / "accidents_clean.csv", low_memory=False)
    cas = pd.read_csv(PROC_DIR / "casualties_clean.csv", low_memory=False)
    return acc, cas


# - Chart functions -

def chart_yearly_trend(acc: pd.DataFrame) -> None:
    yearly = acc.groupby("year").agg(
        total   = ("accident_index", "count"),
        fatal   = ("is_fatal", "sum"),
        serious = ("is_serious", "sum"),
    ).reset_index()
    yearly["slight"] = yearly["total"] - yearly["fatal"] - yearly["serious"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Stacked bar
    ax = axes[0]
    bars_slight  = ax.bar(yearly["year"], yearly["slight"],  color=BRAND_PALETTE[0], label="Slight")
    bars_serious = ax.bar(yearly["year"], yearly["serious"], bottom=yearly["slight"], color=BRAND_PALETTE[4], label="Serious")
    bars_fatal   = ax.bar(yearly["year"], yearly["fatal"],   bottom=yearly["slight"]+yearly["serious"], color=BRAND_PALETTE[6], label="Fatal")
    ax.set_title("UK Road Accidents by Severity & Year", fontweight="bold", fontsize=13)
    ax.set_xlabel("Year"); ax.set_ylabel("Number of Accidents")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))
    ax.legend()

    # Line: year-on-year change
    ax2 = axes[1]
    yoy = yearly["total"].pct_change() * 100
    colors = ["#d45087" if v < 0 else "#003f5c" for v in yoy]
    ax2.bar(yearly["year"], yoy, color=colors)
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.set_title("Year-on-Year % Change in Total Accidents", fontweight="bold", fontsize=13)
    ax2.set_xlabel("Year"); ax2.set_ylabel("% Change vs Prior Year")
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter())

    plt.suptitle("National Road Safety Trend 2019–2023", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    save("01_yearly_trend")


def chart_hourly_heatmap(acc: pd.DataFrame) -> None:
    """Heat map: day-of-week × hour of day accident intensity."""
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    acc2 = acc.dropna(subset=["day_of_week_label", "hour"])
    acc2["hour_int"] = acc2["hour"].astype(int)

    pivot = acc2.groupby(["day_of_week_label", "hour_int"]).size().unstack(fill_value=0)
    pivot = pivot.reindex(dow_order)

    fig, ax = plt.subplots(figsize=(16, 5))
    sns.heatmap(
        pivot, ax=ax, cmap="YlOrRd", linewidths=0.3,
        cbar_kws={"label": "Number of Accidents"},
        fmt="d",
    )
    ax.set_title("Accident Frequency: Day of Week × Hour of Day", fontweight="bold", fontsize=14)
    ax.set_xlabel("Hour of Day (24h)"); ax.set_ylabel("")
    plt.tight_layout()
    save("02_dow_hour_heatmap")


def chart_severity_donut(acc: pd.DataFrame) -> None:
    sev = acc["severity_label"].value_counts()
    colors = [BRAND_PALETTE[0], BRAND_PALETTE[4], BRAND_PALETTE[6]]

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        sev.values, labels=sev.index, colors=colors,
        autopct="%1.1f%%", startangle=90,
        wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 13},
    )
    for at in autotexts:
        at.set_fontsize(12); at.set_color("white"); at.set_fontweight("bold")
    ax.set_title("Accident Severity Distribution\n(2019–2023 Total)", fontweight="bold", fontsize=14)
    centre_text = f"Total\n{sev.sum():,}"
    ax.text(0, 0, centre_text, ha="center", va="center", fontsize=13, fontweight="bold")
    plt.tight_layout()
    save("03_severity_donut")


def chart_top_regions(acc: pd.DataFrame) -> None:
    if "police_force_label" not in acc.columns:
        return

    region = (
        acc.groupby("police_force_label")["accident_index"]
           .count()
           .reset_index(name="count")
           .sort_values("count", ascending=False)
           .head(15)
    )
    fatal_by_region = (
        acc[acc["is_fatal"] == 1]
           .groupby("police_force_label")["accident_index"]
           .count()
           .reset_index(name="fatal")
    )
    region = region.merge(fatal_by_region, on="police_force_label", how="left").fillna(0)
    region["fatal_rate_percent"] = (region["fatal"] / region["count"] * 100).round(1)

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(region["police_force_label"][::-1], region["count"][::-1],
                   color=BRAND_PALETTE[0], edgecolor="white")

    # Overlay fatal rate as text
    for i, row in enumerate(region.iloc[::-1].itertuples()):
        ax.text(row.count + 500, i, f"{row.fatal_rate_percent:.1f}% fatal",
                va="center", fontsize=9, color="#d45087", fontweight="bold")

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))
    ax.set_title("Top 15 Police Forces by Total Accidents (2019–2023)", fontweight="bold", fontsize=13)
    ax.set_xlabel("Total Accidents")
    plt.tight_layout()
    save("04_top_regions")


def chart_weather_severity(acc: pd.DataFrame) -> None:
    if "weather_label" not in acc.columns:
        return

    top_weather = acc["weather_label"].value_counts().head(6).index
    acc2 = acc[acc["weather_label"].isin(top_weather)]

    pct = (
        acc2.groupby(["weather_label", "severity_label"])
           .size()
           .unstack(fill_value=0)
           .apply(lambda r: r / r.sum() * 100, axis=1)
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    pct[["Fatal", "Serious", "Slight"]].plot(
        kind="bar", stacked=True, ax=ax,
        color=[BRAND_PALETTE[6], BRAND_PALETTE[4], BRAND_PALETTE[0]],
        edgecolor="white",
    )
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.set_title("Accident Severity by Weather Condition", fontweight="bold", fontsize=13)
    ax.set_xlabel(""); ax.set_ylabel("% Share")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha="right")
    ax.legend(title="Severity", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    save("05_weather_severity")


def chart_speed_limit_fatality(acc: pd.DataFrame) -> None:
    if "speed_limit_label" not in acc.columns:
        return

    grp = acc.groupby("speed_limit_label").agg(
        total = ("accident_index", "count"),
        fatal = ("is_fatal", "sum"),
    ).reset_index()
    grp["fatal_rate_%"] = grp["fatal"] / grp["total"] * 100
    grp = grp[grp["total"] > 100].sort_values("speed_limit_label")

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()
    x = np.arange(len(grp))
    width = 0.4

    ax1.bar(x - width/2, grp["total"], width=width, color=BRAND_PALETTE[1], label="Total Accidents")
    ax2.bar(x + width/2, grp["fatal_rate_%"], width=width, color=BRAND_PALETTE[6], label="Fatality Rate %")

    ax1.set_xticks(x); ax1.set_xticklabels(grp["speed_limit_label"])
    ax1.set_ylabel("Total Accidents", color=BRAND_PALETTE[1])
    ax2.set_ylabel("Fatality Rate (%)", color=BRAND_PALETTE[6])
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax1.set_title("Accidents & Fatality Rate by Speed Limit", fontweight="bold", fontsize=13)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    plt.tight_layout()
    save("06_speed_limit_fatality")


def chart_casualty_age_sex(cas: pd.DataFrame) -> None:
    if "age_band" not in cas.columns or "sex_label" not in cas.columns:
        return

    pivot = (
        cas[cas["sex_label"].isin(["Male", "Female"])]
           .groupby(["age_band", "sex_label"])
           .size()
           .unstack(fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    pivot.plot(kind="bar", ax=ax, color=["#003f5c", "#f95d6a"], edgecolor="white")
    ax.set_title("Casualties by Age Band and Sex", fontweight="bold", fontsize=13)
    ax.set_xlabel("Age Band"); ax.set_ylabel("Number of Casualties")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.legend(title="Sex")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))
    plt.tight_layout()
    save("07_casualties_age_sex")


def chart_monthly_trend(acc: pd.DataFrame) -> None:
    acc2 = acc.copy()
    acc2["period"] = acc2["year"].astype(str) + "-" + acc2["month"].astype(str).str.zfill(2)
    monthly = acc2.groupby("period").agg(
        total   = ("accident_index", "count"),
        fatal   = ("is_fatal", "sum"),
    ).reset_index().sort_values("period")

    monthly["rolling_avg"] = monthly["total"].rolling(3, center=True).mean()

    fig, ax = plt.subplots(figsize=(16, 5))
    ax.fill_between(range(len(monthly)), monthly["total"], alpha=0.2, color=BRAND_PALETTE[0])
    ax.plot(range(len(monthly)), monthly["total"], color=BRAND_PALETTE[0], linewidth=1.2, label="Monthly accidents")
    ax.plot(range(len(monthly)), monthly["rolling_avg"], color=BRAND_PALETTE[6], linewidth=2.5, label="3-month rolling avg")

    # Shade COVID lockdown period (approx months 14–20 in series if starting Jan 2019)
    ax.set_xticks(range(0, len(monthly), 6))
    ax.set_xticklabels(monthly["period"].iloc[::6], rotation=45, ha="right")
    ax.set_title("Monthly UK Road Accidents (2019–2023) with COVID Context", fontweight="bold", fontsize=13)
    ax.set_ylabel("Number of Accidents")
    ax.legend()
    plt.tight_layout()
    save("08_monthly_trend")


def chart_feature_importance() -> None:
    fi_path = REPORT_DIR / "10_feature_importance.csv"
    if not fi_path.exists():
        print("  Feature importance file not found — run script 04 first")
        return

    fi = pd.read_csv(fi_path).head(12)

    fig, ax = plt.subplots(figsize=(9, 6))
    colors = [BRAND_PALETTE[i % len(BRAND_PALETTE)] for i in range(len(fi))]
    ax.barh(fi["feature"][::-1], fi["importance"][::-1], color=colors[::-1])
    ax.set_title("Random Forest — Top Feature Importances\n(Predicting Serious/Fatal vs Slight)", fontweight="bold", fontsize=13)
    ax.set_xlabel("Importance Score")
    plt.tight_layout()
    save("09_feature_importance")


def chart_light_conditions(acc: pd.DataFrame) -> None:
    if "light_label" not in acc.columns:
        return

    grp = acc.groupby("light_label").agg(
        total     = ("accident_index", "count"),
        fatal     = ("is_fatal", "sum"),
        serious   = ("is_serious", "sum"),
    ).reset_index()
    grp["ksi_rate_%"] = (grp["fatal"] + grp["serious"]) / grp["total"] * 100
    grp = grp[grp["total"] > 100].sort_values("ksi_rate_%", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(grp["light_label"], grp["ksi_rate_%"], color=BRAND_PALETTE, edgecolor="white")
    ax.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=9)
    ax.set_title("Killed & Seriously Injured (KSI) Rate by Light Condition", fontweight="bold", fontsize=13)
    ax.set_ylabel("KSI Rate (%)")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=15, ha="right")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    plt.tight_layout()
    save("10_light_conditions_ksi")


# - Main -

def main():
    print("=" * 65)
    print("  UK Road Safety — Visualizations")
    print("=" * 65)

    acc, cas = load_data()

    print("\nGenerating charts...")
    chart_yearly_trend(acc)
    chart_hourly_heatmap(acc)
    chart_severity_donut(acc)
    chart_top_regions(acc)
    chart_weather_severity(acc)
    chart_speed_limit_fatality(acc)
    chart_casualty_age_sex(cas)
    chart_monthly_trend(acc)
    chart_feature_importance()
    chart_light_conditions(acc)

    charts = list(CHART_DIR.glob("*.png"))
    print(f"\n- Done — {len(charts)} charts saved to: {CHART_DIR} -")
    for c in sorted(charts):
        print(f"  {c.name}")
    print("-")
    print("\nAll Python analysis complete.")
    print("Next steps:")
    print("  -> Load SQL: open DB Browser for SQLite, run sql/01 -> sql/04")
    print("  -> Excel:    follow excel/excel_analysis_guide.md")
    print("  -> Power BI: follow power_bi/power_bi_guide.md")


if __name__ == "__main__":
    main()

