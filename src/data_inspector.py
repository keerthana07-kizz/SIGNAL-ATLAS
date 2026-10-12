from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "online_retail_II.xlsx"

print("=" * 60)
print("SIGNAL ATLAS | DATA INSPECTOR")
print("=" * 60)

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found at: {DATA_FILE}"
    )

print(f"\nDataset found: {DATA_FILE.name}")
print(f"File size: {DATA_FILE.stat().st_size / (1024**2):.2f} MB")
excel_file = pd.ExcelFile(DATA_FILE)

print("\nAvailable worksheets:")
for sheet in excel_file.sheet_names:
    print(f" - {sheet}")

sheet_name = excel_file.sheet_names[0]
df = pd.read_excel(DATA_FILE, sheet_name=sheet_name)

print(f"\nWorksheet loaded: {sheet_name}")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head().to_string())

print("\nMissing values per column:")
print(df.isnull().sum().to_string())

print("\nDuplicate rows:", df.duplicated().sum())

print("\nData types:")
print(df.dtypes.to_string())

print("\nInspection complete!")