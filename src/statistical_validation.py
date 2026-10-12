
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs"

INPUT_FILE = OUTPUTS / "monthly_revenue.csv"
RESULT_FILE = OUTPUTS / "statistical_validation.csv"


def main():
    print("SIGNAL ATLAS - Statistical Validation")
    print("=" * 45)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Cannot find {INPUT_FILE}. "
            "Run discovery_engine.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    required = {"Month", "Revenue"}
    if not required.issubset(df.columns):
        raise ValueError(
            f"Expected columns: {sorted(required)}. "
            f"Found: {list(df.columns)}"
        )

    df["Month"] = pd.to_datetime(df["Month"], errors="coerce")
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce")
    df = df.dropna(subset=["Month", "Revenue"])
    df = df.sort_values("Month").reset_index(drop=True)

    if len(df) < 4:
        raise ValueError("At least four months are required.")

    revenue = df["Revenue"].to_numpy(dtype=float)

    mean_revenue = float(np.mean(revenue))
    median_revenue = float(np.median(revenue))
    std_revenue = float(np.std(revenue, ddof=1))

    cv = (
        std_revenue / abs(mean_revenue)
        if mean_revenue != 0
        else np.nan
    )

    midpoint = len(revenue) // 2
    first_half = revenue[:midpoint]
    second_half = revenue[midpoint:]

    test = stats.mannwhitneyu(
        first_half,
        second_half,
        alternative="two-sided",
    )

    if test.pvalue < 0.05:
        interpretation = (
            "Evidence of a difference between the two groups "
            "of months. Investigate possible business reasons."
        )
    else:
        interpretation = (
            "Insufficient evidence of a difference between "
            "the two groups at the 5% significance level."
        )

    results = [
        {
            "Metric": "Monthly observations",
            "Value": len(df),
            "Interpretation": "Number of months analyzed",
        },
        {
            "Metric": "Mean monthly revenue",
            "Value": mean_revenue,
            "Interpretation": "Average monthly revenue",
        },
        {
            "Metric": "Median monthly revenue",
            "Value": median_revenue,
            "Interpretation": "Median monthly revenue",
        },
        {
            "Metric": "Revenue standard deviation",
            "Value": std_revenue,
            "Interpretation": "Variation in monthly revenue",
        },
        {
            "Metric": "Revenue coefficient of variation",
            "Value": cv,
            "Interpretation": "Relative variability of revenue",
        },
        {
            "Metric": "Mann-Whitney U statistic",
            "Value": float(test.statistic),
            "Interpretation": "Comparison of the two month groups",
        },
        {
            "Metric": "Mann-Whitney p-value",
            "Value": float(test.pvalue),
            "Interpretation": interpretation,
        },
    ]

    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULT_FILE, index=False)

    print(results_df.to_string(index=False))
    print("\nSTATISTICAL VALIDATION COMPLETED!")
    print(f"Results saved to: {RESULT_FILE}")


if __name__ == "__main__":
    main()
