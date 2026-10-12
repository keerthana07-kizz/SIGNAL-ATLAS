
from pathlib import Path

import duckdb


# --------------------------------------------------
# SIGNAL ATLAS - SQL ANALYSIS ENGINE
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

con = duckdb.connect(database=":memory:")

# Register the Parquet dataset as a SQL view.
# The file stays unchanged on disk.
parquet_path = DATA_FILE.as_posix().replace("'", "''")

con.execute(
    f"""
    CREATE VIEW retail AS
    SELECT *
    FROM read_parquet('{parquet_path}')
    """
)

row_count = con.execute(
    "SELECT COUNT(*) FROM retail"
).fetchone()[0]

print("=" * 65)
print("SIGNAL ATLAS | SQL DISCOVERY ENGINE")
print("=" * 65)
print(f"\nRows available for analysis: {row_count:,}")


# --------------------------------------------------
# HELPER TO DISPLAY AND EXPORT RESULTS
# --------------------------------------------------

def run_analysis(title, query, output_file, limit=20):
    print(f"\n{'-' * 65}")
    print(title)
    print("-" * 65)

    result = con.execute(query).df()

    if result.empty:
        print("No results found.")
    else:
        print(result.head(limit).to_string(index=False))

    output_path = OUTPUTS / output_file
    result.to_csv(output_path, index=False)

    print(f"\nSaved: {output_path}")

    return result


# --------------------------------------------------
# 1. MONTHLY REVENUE
# --------------------------------------------------

monthly_query = """
SELECT
    strftime(InvoiceDate, '%Y-%m') AS Month,
    ROUND(SUM(TransactionValue), 2) AS Revenue,
    COUNT(DISTINCT Invoice) AS Invoice_Count
FROM retail
WHERE IsCancelled = FALSE
  AND Quantity > 0
  AND Price > 0
  AND InvoiceDate IS NOT NULL
GROUP BY Month
ORDER BY Month
"""

monthly = run_analysis(
    "1. MONTHLY REVENUE",
    monthly_query,
    "sql_monthly_revenue.csv",
)


# --------------------------------------------------
# 2. TOP COUNTRIES
# --------------------------------------------------

country_query = """
SELECT
    Country,
    ROUND(SUM(TransactionValue), 2) AS Revenue,
    SUM(Quantity) AS Units_Sold,
    COUNT(DISTINCT Invoice) AS Invoice_Count
FROM retail
WHERE IsCancelled = FALSE
  AND Quantity > 0
  AND Price > 0
  AND Country IS NOT NULL
GROUP BY Country
ORDER BY Revenue DESC
LIMIT 20
"""

countries = run_analysis(
    "2. TOP 20 COUNTRIES BY REVENUE",
    country_query,
    "sql_country_analysis.csv",
)


# --------------------------------------------------
# 3. TOP PRODUCTS
# --------------------------------------------------

product_query = """
SELECT
    Description,
    ROUND(SUM(TransactionValue), 2) AS Revenue,
    SUM(Quantity) AS Units_Sold,
    COUNT(*) AS Transaction_Lines
FROM retail
WHERE IsCancelled = FALSE
  AND Quantity > 0
  AND Price > 0
  AND Description IS NOT NULL
GROUP BY Description
ORDER BY Revenue DESC
LIMIT 20
"""

products = run_analysis(
    "3. TOP 20 PRODUCTS BY REVENUE",
    product_query,
    "sql_product_analysis.csv",
)


# --------------------------------------------------
# 4. CANCELLATION ANALYSIS
# --------------------------------------------------

cancellation_query = """
SELECT
    IsCancelled,
    COUNT(*) AS Transaction_Lines,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS Percentage_of_Rows
FROM retail
GROUP BY IsCancelled
ORDER BY IsCancelled
"""

cancellations = run_analysis(
    "4. CANCELLATION ANALYSIS",
    cancellation_query,
    "sql_cancellation_analysis.csv",
)


# --------------------------------------------------
# 5. COUNTRY MONTHLY TRENDS
# --------------------------------------------------

country_month_query = """
SELECT
    Country,
    strftime(InvoiceDate, '%Y-%m') AS Month,
    ROUND(SUM(TransactionValue), 2) AS Revenue
FROM retail
WHERE IsCancelled = FALSE
  AND Quantity > 0
  AND Price > 0
  AND InvoiceDate IS NOT NULL
  AND Country IS NOT NULL
GROUP BY Country, Month
ORDER BY Country, Month
"""

country_month = run_analysis(
    "5. COUNTRY-MONTH REVENUE TRENDS",
    country_month_query,
    "sql_country_month_trends.csv",
    limit=20,
)


# --------------------------------------------------
# 6. DATA QUALITY CHECKS
# --------------------------------------------------

quality_query = """
SELECT
    COUNT(*) AS Total_Rows,

    SUM(
        CASE WHEN InvoiceDate IS NULL
        THEN 1 ELSE 0 END
    ) AS Missing_InvoiceDate,

    SUM(
        CASE WHEN Customer_ID IS NULL
        THEN 1 ELSE 0 END
    ) AS Missing_Customer_ID,

    SUM(
        CASE WHEN Description IS NULL
        THEN 1 ELSE 0 END
    ) AS Missing_Description,

    SUM(
        CASE WHEN Quantity < 0
        THEN 1 ELSE 0 END
    ) AS Negative_Quantity_Rows,

    SUM(
        CASE WHEN Price < 0
        THEN 1 ELSE 0 END
    ) AS Negative_Price_Rows,

    SUM(
        CASE WHEN IsCancelled = TRUE
        THEN 1 ELSE 0 END
    ) AS Cancelled_Rows

FROM retail
"""

quality = run_analysis(
    "6. DATA QUALITY CHECKS",
    quality_query,
    "sql_data_quality.csv",
    limit=10,
)


# --------------------------------------------------
# 7. CUSTOMER VALUE
# --------------------------------------------------

customer_query = """
SELECT
    Customer_ID,
    COUNT(DISTINCT Invoice) AS Invoice_Count,
    ROUND(SUM(TransactionValue), 2) AS Revenue,
    SUM(Quantity) AS Units_Purchased
FROM retail
WHERE IsCancelled = FALSE
  AND Quantity > 0
  AND Price > 0
  AND Customer_ID IS NOT NULL
GROUP BY Customer_ID
ORDER BY Revenue DESC
LIMIT 20
"""

customers = run_analysis(
    "7. TOP 20 CUSTOMERS BY REVENUE",
    customer_query,
    "sql_customer_analysis.csv",
)


# --------------------------------------------------
# 8. EXPORT A COMBINED SQL SUMMARY
# --------------------------------------------------

summary_query = """
SELECT
    COUNT(*) AS Total_Source_Rows,

    SUM(
        CASE WHEN IsCancelled = FALSE
                  AND Quantity > 0
                  AND Price > 0
             THEN 1 ELSE 0 END
    ) AS Positive_Sales_Lines,

    COUNT(DISTINCT Country) AS Unique_Countries,

    COUNT(DISTINCT StockCode) AS Unique_Stock_Codes,

    COUNT(DISTINCT Customer_ID) AS Customers_With_ID,

    ROUND(
        SUM(
            CASE WHEN IsCancelled = FALSE
                      AND Quantity > 0
                      AND Price > 0
                 THEN TransactionValue ELSE 0 END
        ),
        2
    ) AS Positive_Sales_Value

FROM retail
"""

summary = run_analysis(
    "8. SQL SUMMARY",
    summary_query,
    "sql_discovery_summary.csv",
    limit=10,
)


# --------------------------------------------------
# COMPLETION
# --------------------------------------------------

print("\n" + "=" * 65)
print("SQL ANALYSIS COMPLETED SUCCESSFULLY!")
print("=" * 65)
print("\nFiles created in the outputs folder:")
print("- sql_monthly_revenue.csv")
print("- sql_country_analysis.csv")
print("- sql_product_analysis.csv")
print("- sql_cancellation_analysis.csv")
print("- sql_country_month_trends.csv")
print("- sql_data_quality.csv")
print("- sql_customer_analysis.csv")
print("- sql_discovery_summary.csv")

con.close()
