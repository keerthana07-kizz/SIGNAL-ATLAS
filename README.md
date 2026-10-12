
# SIGNAL ATLAS
### Don't just show the data. Reveal what the data is hiding.

SIGNAL ATLAS is a data intelligence project that transforms retail transaction data into actionable business insights. It combines Python, SQL, statistical analysis, anomaly detection, customer segmentation, Excel reporting, and an interactive Streamlit dashboard.

## Features

- **Data Preparation:** Clean and standardize retail transaction data.
- **Revenue Analysis:** Explore monthly, country-level, and product-level sales.
- **SQL Analytics:** Analyze retail performance using DuckDB SQL.
- **Customer Intelligence:** Segment customers using RFM (Recency, Frequency, Monetary) analysis.
- **Anomaly Detection:** Flag unusual product-level sales patterns for further investigation.
- **Statistical Validation:** Evaluate monthly revenue patterns using statistical methods.
- **Discovery Graph:** Represent key countries, products, and customer segments as connected nodes.
- **What-If Simulator:** Explore hypothetical revenue changes under different business assumptions.
- **Excel Reporting:** Generate a multi-sheet report for business analysis.
- **Interactive Dashboard:** Explore metrics and charts with Streamlit and Plotly.

## Technology Stack

- Python
- Pandas and NumPy
- DuckDB and SQL
- SciPy and scikit-learn
- OpenPyXL
- Streamlit and Plotly
- Matplotlib, Seaborn, and NetworkX

## Project Structure

```text
SIGNAL-ATLAS/
├── assets/
├── data/
├── outputs/
├── src/
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup

1. Install Python 3.12 or a compatible version.
2. Clone or download this repository.
3. Open a terminal in the project folder.
4. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

5. Activate it on Windows:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

6. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

7. Ensure the required source dataset is available in the `data/` folder.
8. Run the dashboard:

   ```bash
   python -m streamlit run src/dashboard.py
   ```

## Outputs

Analysis scripts generate CSV reports and an Excel workbook in the `outputs/` folder. The raw dataset and generated outputs are excluded from version control by default.

## Important Notes

- Anomaly detection identifies unusual patterns; it does not establish fraud or errors.
- What-if simulations are hypothetical scenarios, not guaranteed forecasts.
- Statistical findings should be interpreted in the context of seasonality, data quality, and the assumptions of each test.
- The raw dataset is not included in this repository. Provide the required dataset locally before running the complete pipeline.

## Future Improvements

- Improve relationships in the discovery graph using transaction-level evidence.
- Add automated tests and stronger data-quality checks.
- Deploy the dashboard for public access.
- Add reproducible sample data and documented validation results.

## Project Status

Developed as a data analytics portfolio project. Testing and deployment are ongoing.
