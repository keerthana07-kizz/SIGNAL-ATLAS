
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# --------------------------------------------------
# SIGNAL ATLAS - ANOMALY DETECTION ENGINE
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs"
DATA_FILE = OUTPUTS / "retail_full.parquet"

OUTPUTS.mkdir(exist_ok=True)

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}\n"
        "Run src/prepare_dataset.py first."
    )

print("=" * 65)
print("SIGNAL ATLAS | ANOMALY DETECTION ENGINE")
print("=" * 65)


# --------------------------------------------------
# LOAD A REPRESENTATIVE SET OF PRODUCT FEATURES
# --------------------------------------------------

print("\nStep 1: Preparing product-level data...")

con = duckdb.connect(database=":memory:")

parquet_path = DATA_FILE.as_posix().replace("'", "''")

query = f"""
SELECT
    StockCode,
    ANY_VALUE(Description) AS Description,
    SUM(
        CASE
            WHEN IsCancelled = FALSE
             AND Quantity > 0
             AND Price > 0
            THEN TransactionValue
            ELSE 0
        END
    ) AS Sales_Value,
    SUM(
        CASE
            WHEN IsCancelled = FALSE
             AND Quantity > 0
             AND Price > 0
            THEN Quantity
            ELSE 0
        END
    ) AS Units_Sold,
    COUNT(
        CASE
            WHEN IsCancelled = FALSE
             AND Quantity > 0
             AND Price > 0
            THEN 1
        END
    ) AS Sales_Lines,
    COUNT(
        CASE
            WHEN IsCancelled = TRUE
            THEN 1
        END
    ) AS Cancellation_Lines
FROM read_parquet('{parquet_path}')
WHERE StockCode IS NOT NULL
GROUP BY StockCode
"""

products = con.execute(query).df()
con.close()

print(f"Products prepared: {len(products):,}")

if len(products) < 10:
    raise ValueError(
        "Not enough products for meaningful anomaly detection."
    )


# --------------------------------------------------
# CLEAN FEATURES
# --------------------------------------------------

print("\nStep 2: Cleaning product features...")

numeric_features = [
    "Sales_Value",
    "Units_Sold",
    "Sales_Lines",
    "Cancellation_Lines",
]

for column in numeric_features:
    products[column] = pd.to_numeric(
        products[column],
        errors="coerce",
    ).fillna(0)

products["Description"] = (
    products["Description"]
    .fillna("Unknown product")
    .astype(str)
)

# Log transforms reduce the influence of extremely large values.
feature_data = products[numeric_features].clip(lower=0)

X = np.log1p(feature_data)

# Standardize features so that they are on comparable scales.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# --------------------------------------------------
# RUN ISOLATION FOREST
# --------------------------------------------------

print("\nStep 3: Running Isolation Forest...")

model = IsolationForest(
    n_estimators=200,
    contamination=0.03,
    random_state=42,
    n_jobs=-1,
)

predictions = model.fit_predict(X_scaled)

products["Anomaly_Flag"] = np.where(
    predictions == -1,
    "Review",
    "Typical",
)

# Lower decision scores indicate more unusual observations.
products["Anomaly_Score"] = -model.decision_function(X_scaled)

products["Anomaly_Rank"] = (
    products["Anomaly_Score"]
    .rank(method="first", ascending=False)
    .astype(int)
)

print("Model completed.")


# --------------------------------------------------
# ADD EXPLAINABLE REASONS
# --------------------------------------------------

print("\nStep 4: Generating review reasons...")

def explain_anomaly(row):
    reasons = []

    if row["Sales_Value"] > products["Sales_Value"].quantile(0.99):
        reasons.append("Very high sales value")

    if row["Units_Sold"] > products["Units_Sold"].quantile(0.99):
        reasons.append("Very high units sold")

    if row["Sales_Lines"] > products["Sales_Lines"].quantile(0.99):
        reasons.append("Many sales lines")

    if row["Cancellation_Lines"] > 0:
        reasons.append("Has cancellation records")

    if not reasons:
        reasons.append(
            "Unusual combination of product-level features"
        )

    return "; ".join(reasons)


products["Review_Reason"] = products.apply(
    explain_anomaly,
    axis=1,
)


# --------------------------------------------------
# SORT AND EXPORT
# --------------------------------------------------

print("\nStep 5: Saving results...")

products = products.sort_values(
    ["Anomaly_Flag", "Anomaly_Score"],
    ascending=[True, False],
)

output_file = OUTPUTS / "product_anomalies.csv"

products.to_csv(output_file, index=False)

anomalies = products[
    products["Anomaly_Flag"] == "Review"
].copy()

anomaly_file = OUTPUTS / "flagged_product_anomalies.csv"

anomalies.to_csv(anomaly_file, index=False)


# --------------------------------------------------
# EXPORT MODEL SUMMARY
# --------------------------------------------------

summary = pd.DataFrame(
    [
        {
            "Metric": "Products analyzed",
            "Value": len(products),
        },
        {
            "Metric": "Products flagged for review",
            "Value": len(anomalies),
        },
        {
            "Metric": "Flagged percentage",
            "Value": round(
                len(anomalies) / len(products) * 100,
                2,
            ),
        },
        {
            "Metric": "Model",
            "Value": "Isolation Forest",
        },
        {
            "Metric": "Contamination setting",
            "Value": 0.03,
        },
    ]
)

summary_file = OUTPUTS / "anomaly_detection_summary.csv"
summary.to_csv(summary_file, index=False)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

print("\n" + "=" * 65)
print("ANOMALY DETECTION SUMMARY")
print("=" * 65)

print(summary.to_string(index=False))

print("\nTOP 20 PRODUCTS FLAGGED FOR REVIEW")
print("-" * 65)

if anomalies.empty:
    print("No products were flagged.")
else:
    display_columns = [
        "StockCode",
        "Description",
        "Sales_Value",
        "Units_Sold",
        "Sales_Lines",
        "Cancellation_Lines",
        "Anomaly_Score",
        "Review_Reason",
    ]

    print(
        anomalies[display_columns]
        .head(20)
        .to_string(index=False)
    )

print("\nFiles created:")
print(f"- {output_file}")
print(f"- {anomaly_file}")
print(f"- {summary_file}")

print("\nANOMALY DETECTION COMPLETED SUCCESSFULLY!")

