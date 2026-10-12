
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# SIGNAL ATLAS - ADVANCED STATISTICAL VALIDATION

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"

INPUT_FILE = OUTPUT_DIR / "monthly_revenue.csv"
OUTPUT_FILE = OUTPUT_DIR / "advanced_validation.csv"

print("\nSIGNAL ATLAS - Advanced Statistical Validation")
print("-" * 50)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Monthly revenue file not found: {INPUT_FILE}\n"
        "Run src/discovery_engine.py first."
    )

df = pd.read_csv(INPUT_FILE)

# Identify the month and revenue columns
month_col = next(
    (c for c in df.columns if "month" in c.lower() or "date" in c.lower()),
    None,
)
revenue_col = next(
    (c for c in df.columns if "revenue" in c.lower()),
    None,
)

if month_col is None or revenue_col is None:
    raise ValueError(
        f"Could not identify month and revenue columns. "
        f"Available columns: {list(df.columns)}"
    )

df[month_col] = pd.to_datetime(df[month_col], errors="coerce")
df[revenue_col] = pd.to_numeric(df[revenue_col], errors="coerce")

df = (
    df.dropna(subset=[month_col, revenue_col])
    .sort_values(month_col)
    .reset_index(drop=True)
)

if len(df) < 4:
    raise ValueError("At least four monthly observations are required.")

revenue = df[revenue_col].astype(float)
mean_revenue = revenue.mean()
std_revenue = revenue.std(ddof=1)

# Calculate month-to-month changes
df["Previous_Month_Revenue"] = revenue.shift(1)
df["Revenue_Change"] = (
    revenue - df["Previous_Month_Revenue"]
)
df["Revenue_Change_Percent"] = (
    df["Revenue_Change"]
    / df["Previous_Month_Revenue"].replace(0, np.nan)
) * 100

# Flag unusually high or low months using the IQR rule
q1 = revenue.quantile(0.25)
q3 = revenue.quantile(0.75)
iqr = q3 - q1

lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

df["Revenue_Pattern"] = np.select(
    [
        revenue < lower_bound,
        revenue > upper_bound,
    ],
    [
        "Unusually Low",
        "Unusually High",
    ],
    default="Within Typical Range",
)

# Describe the direction of the linear time trend
time_index = np.arange(len(df))
if revenue.nunique() > 1:
    correlation, p_value = spearmanr(time_index, revenue)
else:
    correlation, p_value = np.nan, np.nan

if pd.isna(c_value := correlation):
    trend_description = "Unable to estimate"
elif correlation > 0:
    trend_description = "Generally Increasing"
elif correlation < 0:
    trend_description = "Generally Decreasing"
else:
    trend_description = "No Monotonic Trend"

# Save month-level results
df.to_csv(OUTPUT_FILE, index=False)

# Save a separate summary
summary = pd.DataFrame(
    [
        {"Metric": "Monthly Observations", "Value": len(df)},
        {"Metric": "Mean Monthly Revenue", "Value": mean_revenue},
        {"Metric": "Median Monthly Revenue", "Value": revenue.median()},
        {"Metric": "Revenue Standard Deviation", "Value": std_revenue},
        {"Metric": "Minimum Monthly Revenue", "Value": revenue.min()},
        {"Metric": "Maximum Monthly Revenue", "Value": revenue.max()},
        {"Metric": "IQR Lower Bound", "Value": lower_bound},
        {"Metric": "IQR Upper Bound", "Value": upper_bound},
        {"Metric": "Spearman Correlation with Time", "Value": correlation},
        {"Metric": "Spearman p-value", "Value": p_value},
        {"Metric": "Trend Description", "Value": trend_description},
    ]
)

summary_file = OUTPUT_DIR / "advanced_validation_summary.csv"
summary.to_csv(summary_file, index=False)

print(f"Monthly observations: {len(df)}")
print(f"Trend description: {trend_description}")
print(f"Spearman correlation: {correlation:.4f}")
print(f"Spearman p-value: {p_value:.4f}")
print("\nMonthly revenue pattern counts:")
print(df["Revenue_Pattern"].value_counts().to_string())
print(f"\nDetailed results saved to: {OUTPUT_FILE}")
print(f"Summary saved to: {summary_file}")
print("\nADVANCED VALIDATION COMPLETED SUCCESSFULLY!")
