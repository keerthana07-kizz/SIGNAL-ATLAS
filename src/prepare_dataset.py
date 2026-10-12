
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "online_retail_II.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("SIGNAL ATLAS | FULL DATASET PREPARATION")
print("=" * 60)

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

print("\nReading all worksheets...")
sheets = pd.read_excel(DATA_FILE, sheet_name=None)

frames = []

for sheet_name, sheet_df in sheets.items():
    sheet_df.columns = (
        sheet_df.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
    )

    print(f"Loaded '{sheet_name}': {len(sheet_df):,} rows")
    frames.append(sheet_df)

df = pd.concat(frames, ignore_index=True)

print("\nCombined dataset")
print("Total rows:", f"{len(df):,}")
print("Total columns:", len(df.columns))
print("Columns:", df.columns.tolist())

# Convert important columns safely
if "InvoiceDate" in df.columns:
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )

for column in ["Quantity", "Price"]:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

if "Invoice" in df.columns:
    invoice_text = df["Invoice"].astype("string").str.strip()
    df["IsCancelled"] = (
        invoice_text.str.upper().str.startswith("C").fillna(False)
    )

if {"Quantity", "Price"}.issubset(df.columns):
    df["TransactionValue"] = df["Quantity"] * df["Price"]

# Save the combined dataset in an efficient format

# Standardize mixed invoice values before saving

df["Invoice"] = df["Invoice"].astype("string")
df["StockCode"] = df["StockCode"].astype("string")
df["Description"] = df["Description"].astype("string")


output_file = OUTPUT_DIR / "retail_full.parquet"
df.to_parquet(output_file, index=False)

print("\nFull dataset saved successfully!")
print("Output:", output_file)
print("Rows saved:", f"{len(df):,}")

print("\nFull dataset saved successfully!")
print("Output:", output_file)
print("Rows saved:", f"{len(df):,}")
