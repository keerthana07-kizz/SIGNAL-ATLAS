
from pathlib import Path

import pandas as pd

# SIGNAL ATLAS - WHAT-IF BUSINESS SIMULATOR

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"

INPUT_FILE = OUTPUT_DIR / "monthly_revenue.csv"
OUTPUT_FILE = OUTPUT_DIR / "what_if_simulation.csv"

print("\nSIGNAL ATLAS - What-If Business Simulator")
print("-" * 50)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Monthly revenue file not found: {INPUT_FILE}\n"
        "Run src/discovery_engine.py first."
    )

df = pd.read_csv(INPUT_FILE)

# Identify the revenue column
revenue_col = next(
    (col for col in df.columns if "revenue" in col.lower()),
    None,
)

if revenue_col is None:
    raise ValueError(
        f"Revenue column not found. Available columns: {list(df.columns)}"
    )

df[revenue_col] = pd.to_numeric(df[revenue_col], errors="coerce")
df = df.dropna(subset=[revenue_col]).copy()

if df.empty:
    raise ValueError("No valid monthly revenue values found.")

# Set business assumptions
sales_increase_percent = 10
sales_decrease_percent = 15
price_increase_percent = 5

baseline_revenue = df[revenue_col].sum()

# Calculate hypothetical scenarios
scenarios = [
    {
        "Scenario": "Baseline",
        "Assumption": "No change",
        "Change_Percent": 0,
    },
    {
        "Scenario": "Sales Increase",
        "Assumption": "Sales volume increases by 10%",
        "Change_Percent": sales_increase_percent,
    },
    {
        "Scenario": "Sales Decrease",
        "Assumption": "Sales volume decreases by 15%",
        "Change_Percent": -sales_decrease_percent,
    },
    {
        "Scenario": "Price Increase",
        "Assumption": "Prices increase by 5%; units sold unchanged",
        "Change_Percent": price_increase_percent,
    },
]

results = []

for scenario in scenarios:
    change = scenario["Change_Percent"] / 100
    simulated_revenue = baseline_revenue * (1 + change)

    results.append(
        {
            "Scenario": scenario["Scenario"],
            "Assumption": scenario["Assumption"],
            "Change_Percent": scenario["Change_Percent"],
            "Baseline_Revenue": baseline_revenue,
            "Simulated_Revenue": simulated_revenue,
            "Revenue_Impact": simulated_revenue - baseline_revenue,
        }
    )

results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_FILE, index=False)

print(f"Baseline revenue: {baseline_revenue:,.2f}")
print("\nSimulation results:")
print(
    results_df[
        ["Scenario", "Change_Percent", "Simulated_Revenue", "Revenue_Impact"]
    ].to_string(index=False)
)

print(f"\nResults saved to: {OUTPUT_FILE}")
print("\nWHAT-IF SIMULATOR COMPLETED SUCCESSFULLY!")
