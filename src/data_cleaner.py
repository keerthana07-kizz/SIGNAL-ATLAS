from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "online_retail_II.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("SIGNAL ATLAS | DATA CLEANING")
print("=" * 60)

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

df = pd.read_excel(DATA_FILE, sheet_name=0)

print("Original rows:", f"{len(df):,}")
print("Original columns:", df.columns.tolist())
# Standardize column names
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.replace(r"\s+", "_", regex=True)
)

# Convert fields to appropriate types when present
if "InvoiceDate" in df.columns:
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )

for column in ["Quantity", "Price"]:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

# Identify cancelled invoices
if "Invoice" in df.columns:
    invoice_text = df["Invoice"].astype("string").str.strip()
    df["IsCancelled"] = invoice_text.str.upper().str.startswith("C").fillna(False)
else:
    df["IsCancelled"] = False

# Calculate transaction value where possible
if {"Quantity", "Price"}.issubset(df.columns):
    df["TransactionValue"] = df["Quantity"] * df["Price"]

print("\nMissing values:")
print(df.isna().sum().to_string())

print("\nDuplicate rows:", f"{df.duplicated().sum():,}")
print("Cancelled records:", f"{df['IsCancelled'].sum():,}")
# Keep a cleaned copy; preserve the original dataset
clean_df = df.drop_duplicates().copy()

clean_path = OUTPUT_DIR / "retail_cleaned.csv"
report_path = OUTPUT_DIR / "data_quality_report.csv"

clean_df.to_csv(clean_path, index=False)

quality_report = pd.DataFrame({
    "Column": df.columns,
    "Data_Type": [str(df[c].dtype) for c in df.columns],
    "Missing_Values": [int(df[c].isna().sum()) for c in df.columns],
    "Missing_Percent": [
        round(df[c].isna().mean() * 100, 2) for c in df.columns
    ],
})

quality_report.to_csv(report_path, index=False)

print("\nCleaning complete!")
print("Cleaned rows:", f"{len(clean_df):,}")
print("Cleaned file:", clean_path)
print("Quality report:", report_path)