
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd


# --------------------------------------------------
# SIGNAL ATLAS - CUSTOMER INTELLIGENCE (RFM)
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "outputs" / "retail_full.parquet"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\nSIGNAL ATLAS - Customer Intelligence")
print("-" * 45)

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}\n"
        "Run src/prepare_dataset.py first."
    )

# Load customer purchase information using DuckDB
con = duckdb.connect()

query = """
SELECT
    Customer_ID,
    Invoice,
    InvoiceDate,
    Quantity,
    Price,
    IsCancelled
FROM read_parquet(?)
WHERE Customer_ID IS NOT NULL
"""

df = con.execute(query, [str(DATA_FILE)]).fetchdf()
con.close()

# Standardize data types
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)
df["Quantity"] = pd.to_numeric(
    df["Quantity"], errors="coerce"
)
df["Price"] = pd.to_numeric(
    df["Price"], errors="coerce"
)

df = df.dropna(
    subset=["Customer_ID", "Invoice", "InvoiceDate", "Quantity", "Price"]
)

# Exclude cancelled invoices and invalid sales lines
df = df[
    (~df["IsCancelled"].fillna(False).astype(bool))
    & (df["Quantity"] > 0)
    & (df["Price"] > 0)
].copy()

df["Sales_Value"] = df["Quantity"] * df["Price"]

if df.empty:
    raise ValueError(
        "No valid customer purchase records remain after cleaning."
    )

# Calculate RFM values
analysis_date = df["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)

rfm = (
    df.groupby("Customer_ID")
    .agg(
        Last_Purchase=("InvoiceDate", "max"),
        Frequency=("Invoice", "nunique"),
        Monetary=("Sales_Value", "sum"),
    )
    .reset_index()
)

rfm["Recency_Days"] = (
    analysis_date - rfm["Last_Purchase"].dt.normalize()
).dt.days

# Score customers from 1 to 5
# Higher recency score = more recent purchase
rfm["R_Score"] = pd.qcut(
    rfm["Recency_Days"].rank(method="first"),
    5,
    labels=[5, 4, 3, 2, 1],
).astype(int)

rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5],
).astype(int)

rfm["M_Score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5],
).astype(int)

rfm["RFM_Score"] = (
    rfm["R_Score"].astype(str)
    + rfm["F_Score"].astype(str)
    + rfm["M_Score"].astype(str)
)

# Assign understandable customer segments
def assign_segment(row):
    if row["R_Score"] >= 4 and row["F_Score"] >= 4:
        return "High-Value Active"
    elif row["F_Score"] >= 4:
        return "Frequent Buyers"
    elif row["R_Score"] >= 4:
        return "Recently Active"
    elif row["R_Score"] <= 2 and row["F_Score"] <= 2:
        return "Needs Attention"
    else:
        return "Regular Customers"


rfm["Customer_Segment"] = rfm.apply(assign_segment, axis=1)

# Rank customers by total recorded purchase value
rfm = rfm.sort_values(
    "Monetary", ascending=False
).reset_index(drop=True)

rfm["Customer_Rank"] = np.arange(1, len(rfm) + 1)

# Save detailed customer analysis
customer_file = OUTPUT_DIR / "customer_rfm_analysis.csv"
rfm.to_csv(customer_file, index=False)

# Summarize customer segments
segment_summary = (
    rfm.groupby("Customer_Segment", as_index=False)
    .agg(
        Customer_Count=("Customer_ID", "nunique"),
        Total_Monetary=("Monetary", "sum"),
        Average_Monetary=("Monetary", "mean"),
        Average_Frequency=("Frequency", "mean"),
        Average_Recency_Days=("Recency_Days", "mean"),
    )
    .sort_values("Customer_Count", ascending=False)
)

segment_file = OUTPUT_DIR / "customer_segment_summary.csv"
segment_summary.to_csv(segment_file, index=False)

print(f"Customers analyzed: {len(rfm):,}")
print(f"Customer segments: {rfm['Customer_Segment'].nunique()}")
print("\nCustomer segment summary:")
print(segment_summary.to_string(index=False))

print(f"\nDetailed results saved to: {customer_file}")
print(f"Segment summary saved to: {segment_file}")
print("\nCUSTOMER INTELLIGENCE COMPLETED SUCCESSFULLY!")
