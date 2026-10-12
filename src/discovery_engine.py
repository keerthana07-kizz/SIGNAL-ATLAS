
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "outputs" / "retail_full.parquet"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

print("=" * 60)
print("SIGNAL ATLAS | DISCOVERY ENGINE")
print("=" * 60)

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Prepared dataset not found: {DATA_FILE}"
    )

print("\nLoading prepared dataset...")
df = pd.read_parquet(DATA_FILE)

print("Rows loaded:", f"{len(df):,}")
print("Columns:", df.columns.tolist())

# Calculate transaction value if it is not already present
if "TransactionValue" not in df.columns:
    df["TransactionValue"] = df["Quantity"] * df["Price"]

# Exclude cancelled invoices from the basic sales analysis
if "IsCancelled" in df.columns:
    sales_df = df[~df["IsCancelled"]].copy()
else:
    sales_df = df[
        ~df["Invoice"].astype("string").str.startswith("C", na=False)
    ].copy()

# Keep records with valid dates and numeric sales values
sales_df = sales_df.dropna(
    subset=["InvoiceDate", "Quantity", "Price"]
)

sales_df["TransactionValue"] = (
    sales_df["Quantity"] * sales_df["Price"]
)

# Monthly revenue
sales_df["Month"] = (
    sales_df["InvoiceDate"].dt.to_period("M").astype(str)
)

monthly_revenue = (
    sales_df.groupby("Month", as_index=False)
    ["TransactionValue"].sum()
    .rename(columns={"TransactionValue": "Revenue"})
    .sort_values("Month")
)

monthly_revenue.to_csv(
    OUTPUT_DIR / "monthly_revenue.csv", index=False
)

print("\nMONTHLY REVENUE — FIRST 12 MONTHS")
print(monthly_revenue.head(12).to_string(index=False))

# Top countries by revenue
country_revenue = (
    sales_df.groupby("Country", as_index=False)
    ["TransactionValue"].sum()
    .rename(columns={"TransactionValue": "Revenue"})
    .sort_values("Revenue", ascending=False)
)

country_revenue.to_csv(
    OUTPUT_DIR / "country_revenue.csv", index=False
)

print("\nTOP 10 COUNTRIES BY REVENUE")
print(country_revenue.head(10).to_string(index=False))

# Top products by revenue
product_revenue = (
    sales_df.groupby("Description", as_index=False)
    .agg(
        Revenue=("TransactionValue", "sum"),
        Units_Sold=("Quantity", "sum"),
        Transaction_Lines=("Invoice", "count")
    )
    .sort_values("Revenue", ascending=False)
)

product_revenue.to_csv(
    OUTPUT_DIR / "product_revenue.csv", index=False
)

print("\nTOP 10 PRODUCTS BY REVENUE")
print(product_revenue.head(10).to_string(index=False))

# Basic data-driven summary
summary = pd.DataFrame([
    {
        "Metric": "Total source rows",
        "Value": len(df)
    },
    {
        "Metric": "Sales records analyzed",
        "Value": len(sales_df)
    },
    {
        "Metric": "Countries represented",
        "Value": sales_df["Country"].nunique()
    },
    {
        "Metric": "Unique products",
        "Value": sales_df["Description"].nunique()
    },
    {
        "Metric": "Total analyzed revenue",
        "Value": round(sales_df["TransactionValue"].sum(), 2)
    }
])

summary.to_csv(
    OUTPUT_DIR / "discovery_summary.csv", index=False
)

print("\nDISCOVERY SUMMARY")
print(summary.to_string(index=False))
print("\nDiscovery engine completed successfully!")
