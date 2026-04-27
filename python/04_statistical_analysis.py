"""
Script 04: Statistical Analysis & Machine Learning
- Chi-square tests: are severity differences statistically significant?
- Logistic regression: baseline probability model
- Random Forest classifier: predict accident severity (Slight vs Serious/Fatal)
- Feature importance: what factors matter most?
- Time-series decomposition: trend + seasonality in accident rates
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, accuracy_score, ConfusionMatrixDisplay
)
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings("ignore")

BASE_DIR   = Path(__file__).resolve().parent.parent
PROC_DIR   = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"
CHART_DIR  = BASE_DIR / "outputs" / "charts"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)


# - Load data -

def load_accidents() -> pd.DataFrame:
    print("Loading accidents data...")
    df = pd.read_csv(PROC_DIR / "accidents_clean.csv", low_memory=False)
    print(f"  {len(df):,} rows loaded")
    return df


# - Statistical tests -

def chi_square_test(df: pd.DataFrame, factor: str, severity_col: str = "severity_label") -> dict:
    """Chi-square test: is the factor independent of accident severity?"""
    if factor not in df.columns or severity_col not in df.columns:
        return {}

    contingency = pd.crosstab(df[factor].fillna("Unknown"), df[severity_col])
    chi2, p_val, dof, expected = stats.chi2_contingency(contingency)

    result = {
        "factor":    factor,
        "chi2":      round(chi2, 2),
        "p_value":   round(p_val, 6),
        "dof":       dof,
        "significant_at_1%": p_val < 0.01,
        "cramers_v": round(np.sqrt(chi2 / (len(df) * (min(contingency.shape) - 1))), 4),
    }
    return result


def run_hypothesis_tests(df: pd.DataFrame) -> None:
    print("\n[1] Hypothesis Tests (Chi-Square)")
    print("  H0: The factor is independent of accident severity")

    factors = [
        "weather_label", "road_surface_label", "light_label",
        "speed_limit_label", "day_of_week_label", "urban_rural_label",
        "junction_label", "road_type_label",
    ]

    results = []
    for f in factors:
        r = chi_square_test(df, f)
        if r:
            results.append(r)
            sig = "YES ***" if r["significant_at_1%"] else "no"
            print(f"  {f:<30s}  chi2={r['chi2']:>10.1f}  p={r['p_value']:.2e}  Cramer's V={r['cramers_v']:.3f}  significant={sig}")

    pd.DataFrame(results).to_csv(REPORT_DIR / "09_hypothesis_tests.csv", index=False)
    print(f"  Results saved to outputs/reports/09_hypothesis_tests.csv")


# - Feature preparation for ML -

def prepare_ml_features(df: pd.DataFrame) -> tuple:
    """Build feature matrix for severity classification (Slight=0 vs Serious/Fatal=1)."""
    print("\n[2] Preparing ML Features")

    feature_cols = [
        "hour", "is_night", "is_wet_road", "is_weekend",
        "speed_limit", "number_of_vehicles",
        "urban_or_rural_area", "road_type", "junction_detail",
        "light_conditions", "weather_conditions", "road_surface_conditions",
    ]

    available = [c for c in feature_cols if c in df.columns]
    print(f"  Using {len(available)} features: {available}")

    X = df[available].copy()
    # Fill numeric missing with median
    for col in X.select_dtypes(include=[np.number]).columns:
        X[col] = X[col].fillna(X[col].median())

    # Binary target: 0 = Slight, 1 = Serious or Fatal
    y = (df["accident_severity"].isin([1, 2])).astype(int)

    print(f"  Class distribution — Slight: {(y==0).sum():,}  |  Serious/Fatal: {(y==1).sum():,}")
    print(f"  Positive class rate: {y.mean()*100:.1f}%")

    return X, y


# - Model training -

def train_logistic_regression(X_train, X_test, y_train, y_test) -> dict:
    print("\n[3a] Logistic Regression (baseline)")

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    LogisticRegression(max_iter=500, class_weight="balanced", random_state=42)),
    ])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]

    acc  = accuracy_score(y_test, y_pred)
    auc  = roc_auc_score(y_test, y_prob)
    print(f"  Accuracy: {acc:.3f}  |  ROC-AUC: {auc:.3f}")
    print(classification_report(y_test, y_pred, target_names=["Slight", "Serious/Fatal"]))

    return {"model": "Logistic Regression", "accuracy": acc, "roc_auc": auc}


def train_random_forest(X_train, X_test, y_train, y_test, feature_names: list) -> dict:
    print("\n[3b] Random Forest Classifier")

    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=20,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    y_prob = rf.predict_proba(X_test)[:, 1]

    acc  = accuracy_score(y_test, y_pred)
    auc  = roc_auc_score(y_test, y_prob)
    print(f"  Accuracy: {acc:.3f}  |  ROC-AUC: {auc:.3f}")
    print(classification_report(y_test, y_pred, target_names=["Slight", "Serious/Fatal"]))

    # Feature importance
    importance_df = pd.DataFrame({
        "feature":   feature_names,
        "importance": rf.feature_importances_,
    }).sort_values("importance", ascending=False)
    importance_df.to_csv(REPORT_DIR / "10_feature_importance.csv", index=False)

    print("\n  Top 10 most important features:")
    print(importance_df.head(10).to_string(index=False))

    # Confusion matrix data
    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(cm, index=["Actual Slight", "Actual Serious/Fatal"],
                             columns=["Pred Slight", "Pred Serious/Fatal"])
    cm_df.to_csv(REPORT_DIR / "10_confusion_matrix.csv")

    return {"model": "Random Forest", "accuracy": acc, "roc_auc": auc, "rf_object": rf, "importance": importance_df}


def cross_validate_model(X, y) -> None:
    print("\n[3c] Cross-Validation (5-fold Stratified)")

    rf = RandomForestClassifier(n_estimators=100, max_depth=10, class_weight="balanced",
                                random_state=42, n_jobs=-1)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(rf, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)
    print(f"  ROC-AUC per fold: {[round(s,3) for s in scores]}")
    print(f"  Mean: {scores.mean():.3f}  |  Std: {scores.std():.3f}")


# - Time-series trend decomposition -

def time_series_analysis(df: pd.DataFrame) -> None:
    """Monthly accident counts with rolling average."""
    print("\n[4] Time-Series Analysis")

    monthly = (
        df.groupby(["year", "month"])
          .agg(accidents=("accident_index", "count"), fatalities=("is_fatal", "sum"))
          .reset_index()
          .sort_values(["year", "month"])
    )
    monthly["rolling_3m"]  = monthly["accidents"].rolling(3,  center=True).mean()
    monthly["rolling_12m"] = monthly["accidents"].rolling(12, min_periods=6).mean()
    monthly.to_csv(REPORT_DIR / "11_monthly_timeseries.csv", index=False)

    print(f"  Months analysed : {len(monthly)}")
    peak = monthly.loc[monthly["accidents"].idxmax()]
    trough = monthly.loc[monthly["accidents"].idxmin()]
    print(f"  Peak month      : {int(peak['year'])}-{int(peak['month']):02d}  ({int(peak['accidents']):,} accidents)")
    print(f"  Lowest month    : {int(trough['year'])}-{int(trough['month']):02d}  ({int(trough['accidents']):,} accidents)")


# - Hotspot analysis -

def hotspot_analysis(df: pd.DataFrame) -> None:
    """Identify junction + speed limit combinations with highest fatal rates."""
    print("\n[5] Hotspot Analysis")

    if "junction_label" not in df.columns or "speed_limit_label" not in df.columns:
        return

    hotspot = df.groupby(["junction_label", "speed_limit_label"]).agg(
        total   = ("accident_index", "count"),
        fatal   = ("is_fatal", "sum"),
        serious = ("is_serious", "sum"),
    ).reset_index()
    hotspot["fatal_rate_%"]   = (hotspot["fatal"] / hotspot["total"] * 100).round(2)
    hotspot["serious_rate_%"] = (hotspot["serious"] / hotspot["total"] * 100).round(2)
    hotspot["ksi_rate_%"]     = ((hotspot["fatal"] + hotspot["serious"]) / hotspot["total"] * 100).round(2)
    hotspot = hotspot[hotspot["total"] >= 50].sort_values("fatal_rate_%", ascending=False)

    print("  Top 10 dangerous junction × speed limit combos:")
    print(hotspot.head(10).to_string(index=False))
    hotspot.to_csv(REPORT_DIR / "12_hotspot_analysis.csv", index=False)


# - Main -

def main():
    print("=" * 65)
    print("  UK Road Safety — Statistical Analysis & ML")
    print("=" * 65)

    df = load_accidents()

    # Hypothesis tests
    run_hypothesis_tests(df)

    # ML: prepare features
    X, y = prepare_ml_features(df)
    feature_names = list(X.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\n  Train: {len(X_train):,}  |  Test: {len(X_test):,}")

    # Train models
    lr_results = train_logistic_regression(X_train, X_test, y_train, y_test)
    rf_results = train_random_forest(X_train, X_test, y_train, y_test, feature_names)

    # Cross-validation
    cross_validate_model(X, y)

    # Save model comparison
    results_df = pd.DataFrame([
        {k: v for k, v in lr_results.items()},
        {k: v for k, v in rf_results.items() if k not in ("rf_object", "importance")},
    ])
    results_df.to_csv(REPORT_DIR / "10_model_comparison.csv", index=False)

    # Time-series and hotspot
    time_series_analysis(df)
    hotspot_analysis(df)

    print("\n- Analysis Complete -")
    print(f"  Reports saved to: {REPORT_DIR}")
    print("-")
    print("\nNext step: run  python/05_visualizations.py")


if __name__ == "__main__":
    main()

