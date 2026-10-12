
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import (
    Font,
    PatternFill,
    Border,
    Side,
    Alignment,
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs"
REPORT_PATH = OUTPUTS / "SIGNAL_ATLAS_Excel_Report.xlsx"

OUTPUTS.mkdir(exist_ok=True)


# --------------------------------------------------
# LOAD EXISTING ANALYSIS FILES
# --------------------------------------------------

monthly = pd.read_csv(OUTPUTS / "monthly_revenue.csv")
countries = pd.read_csv(OUTPUTS / "country_revenue.csv")
products = pd.read_csv(OUTPUTS / "product_revenue.csv")
summary = pd.read_csv(OUTPUTS / "discovery_summary.csv")


# --------------------------------------------------
# CHECK REQUIRED COLUMNS
# --------------------------------------------------

required_columns = [
    (monthly, ["Month", "Revenue"], "monthly_revenue.csv"),
    (countries, ["Country", "Revenue"], "country_revenue.csv"),
    (products, ["Description", "Revenue"], "product_revenue.csv"),
    (summary, ["Metric", "Value"], "discovery_summary.csv"),
]

for dataframe, columns, filename in required_columns:
    missing = [column for column in columns if column not in dataframe.columns]

    if missing:
        raise ValueError(
            f"{filename} is missing required columns: {missing}"
        )


# --------------------------------------------------
# PREPARE DATA
# --------------------------------------------------

for dataframe in [monthly, countries, products]:
    dataframe["Revenue"] = pd.to_numeric(
        dataframe["Revenue"], errors="coerce"
    ).fillna(0)

monthly = monthly.sort_values("Month")
countries = countries.sort_values("Revenue", ascending=False)
products = products.sort_values("Revenue", ascending=False)

# Excel worksheets support a maximum of 1,048,576 rows.
# These sheets contain aggregated results, not the full raw dataset.
countries = countries.head(43)
products = products.head(100)

# Summary metric values
summary_lookup = {}

for _, row in summary.iterrows():
    summary_lookup[str(row["Metric"]).strip()] = row["Value"]


# --------------------------------------------------
# CREATE WORKBOOK
# --------------------------------------------------

wb = Workbook()

dashboard = wb.active
dashboard.title = "Executive Summary"

monthly_ws = wb.create_sheet("Monthly Revenue")
country_ws = wb.create_sheet("Country Analysis")
product_ws = wb.create_sheet("Product Analysis")
summary_ws = wb.create_sheet("Discovery Summary")


# --------------------------------------------------
# THEME
# --------------------------------------------------

NAVY = "302D3D"
PURPLE = "E8DFF5"
SAGE = "DDEBDD"
PEACH = "F9E1D5"
YELLOW = "F8EDC8"
BLUE = "DDEAF7"
WHITE = "FFFFFF"
LIGHT_BG = "FAF8F4"
BORDER_COLOR = "D8D1E2"
MUTED = "514B60"

thin_border = Border(
    left=Side(style="thin", color=BORDER_COLOR),
    right=Side(style="thin", color=BORDER_COLOR),
    top=Side(style="thin", color=BORDER_COLOR),
    bottom=Side(style="thin", color=BORDER_COLOR),
)


# --------------------------------------------------
# HELPER: WRITE DATAFRAME TO WORKSHEET
# --------------------------------------------------

def write_dataframe(ws, dataframe, table_name):
    ws.sheet_view.showGridLines = False

    for col_index, column in enumerate(dataframe.columns, start=1):
        cell = ws.cell(row=1, column=col_index, value=str(column))
        cell.fill = PatternFill("solid", fgColor=PURPLE)
        cell.font = Font(
            name="Aptos",
            bold=True,
            color=NAVY,
            size=11,
        )
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
        )
        cell.border = thin_border

    for row_index, row in enumerate(
        dataframe.itertuples(index=False, name=None),
        start=2,
    ):
        for col_index, value in enumerate(row, start=1):
            if pd.isna(value):
                value = None

            cell = ws.cell(
                row=row_index,
                column=col_index,
                value=value,
            )

            cell.font = Font(
                name="Aptos",
                color=NAVY,
                size=10,
            )
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center")

            if row_index % 2 == 0:
                cell.fill = PatternFill(
                    "solid",
                    fgColor=LIGHT_BG,
                )

            if str(dataframe.columns[col_index - 1]).lower() == "revenue":
                cell.number_format = '#,##0.00'

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    ws.row_dimensions[1].height = 25

    for col_index, column in enumerate(dataframe.columns, start=1):
        values = [str(column)] + [
            str(value)
            for value in dataframe[column].head(100).tolist()
            if pd.notna(value)
        ]

        max_length = max(len(value) for value in values)
        ws.column_dimensions[get_column_letter(col_index)].width = min(
            max(max_length + 3, 14),
            42,
        )

    if len(dataframe) > 0 and len(dataframe.columns) > 0:
        table_ref = f"A1:{get_column_letter(len(dataframe.columns))}{len(dataframe) + 1}"

        table = Table(
            displayName=table_name,
            ref=table_ref,
        )

        style = TableStyleInfo(
            name="TableStyleMedium4",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False,
        )

        table.tableStyleInfo = style
        ws.add_table(table)


# --------------------------------------------------
# MONTHLY REVENUE SHEET
# --------------------------------------------------

write_dataframe(
    monthly_ws,
    monthly,
    "MonthlyRevenueTable",
)

if len(monthly) >= 1:
    chart = LineChart()
    chart.title = "Monthly Revenue Trend"
    chart.style = 13
    chart.y_axis.title = "Transaction Value"
    chart.x_axis.title = "Month"
    chart.height = 8
    chart.width = 17

    data = Reference(
        monthly_ws,
        min_col=2,
        min_row=1,
        max_row=len(monthly) + 1,
    )

    categories = Reference(
        monthly_ws,
        min_col=1,
        min_row=2,
        max_row=len(monthly) + 1,
    )

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)
    chart.legend = None

    monthly_ws.add_chart(chart, "E2")


# --------------------------------------------------
# COUNTRY ANALYSIS SHEET
# --------------------------------------------------

write_dataframe(
    country_ws,
    countries,
    "CountryRevenueTable",
)

if len(countries) > 0:
    chart = BarChart()
    chart.type = "bar"
    chart.style = 10
    chart.title = "Top Countries by Revenue"
    chart.x_axis.title = "Transaction Value"
    chart.y_axis.title = "Country"
    chart.height = 10
    chart.width = 18

    data = Reference(
        country_ws,
        min_col=2,
        min_row=1,
        max_row=min(len(countries), 10) + 1,
    )

    categories = Reference(
        country_ws,
        min_col=1,
        min_row=2,
        max_row=min(len(countries), 10) + 1,
    )

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)
    chart.legend = None

    country_ws.add_chart(chart, "E2")


# --------------------------------------------------
# PRODUCT ANALYSIS SHEET
# --------------------------------------------------

write_dataframe(
    product_ws,
    products,
    "ProductRevenueTable",
)

if len(products) > 0:
    chart = BarChart()
    chart.type = "bar"
    chart.style = 12
    chart.title = "Top 10 Products by Revenue"
    chart.x_axis.title = "Transaction Value"
    chart.y_axis.title = "Product"
    chart.height = 12
    chart.width = 22

    top_count = min(len(products), 10)

    data = Reference(
        product_ws,
        min_col=2,
        min_row=1,
        max_row=top_count + 1,
    )

    categories = Reference(
        product_ws,
        min_col=1,
        min_row=2,
        max_row=top_count + 1,
    )

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)
    chart.legend = None

    product_ws.add_chart(chart, "E2")


# --------------------------------------------------
# DISCOVERY SUMMARY SHEET
# --------------------------------------------------

write_dataframe(
    summary_ws,
    summary,
    "DiscoverySummaryTable",
)


# --------------------------------------------------
# EXECUTIVE SUMMARY DASHBOARD
# --------------------------------------------------

dashboard.sheet_view.showGridLines = False

dashboard.merge_cells("A1:H1")
dashboard["A1"] = "SIGNAL ATLAS"
dashboard["A1"].font = Font(
    name="Aptos Display",
    size=24,
    bold=True,
    color=NAVY,
)
dashboard["A1"].fill = PatternFill("solid", fgColor=PURPLE)
dashboard["A1"].alignment = Alignment(
    horizontal="left",
    vertical="center",
)
dashboard.row_dimensions[1].height = 42

dashboard.merge_cells("A2:H2")
dashboard["A2"] = (
    "Retail Data Intelligence | Executive Summary"
)
dashboard["A2"].font = Font(
    name="Aptos",
    size=12,
    italic=True,
    color=MUTED,
)
dashboard["A2"].fill = PatternFill("solid", fgColor=LIGHT_BG)

metrics = [
    ("Total source rows", "Total source rows", PURPLE),
    ("Sales records analyzed", "Sales records analyzed", SAGE),
    ("Countries represented", "Countries represented", PEACH),
    ("Unique products", "Unique products", YELLOW),
    ("Total analyzed revenue", "Total analyzed revenue", BLUE),
]

row_start = 4

for index, (label, lookup_key, fill_color) in enumerate(metrics):
    col = 1 + index * 2

    label_cell = dashboard.cell(
        row=row_start,
        column=col,
        value=label,
    )
    label_cell.fill = PatternFill(
        "solid",
        fgColor=fill_color,
    )
    label_cell.font = Font(
        name="Aptos",
        bold=True,
        color=NAVY,
        size=10,
    )
    label_cell.alignment = Alignment(
        horizontal="center",
        vertical="center",
        wrap_text=True,
    )
    label_cell.border = thin_border

    value = summary_lookup.get(lookup_key, "Not available")

    try:
        value = float(value)
        if lookup_key == "Total analyzed revenue":
            formatted_value = f"{value:,.2f}"
        else:
            formatted_value = f"{value:,.0f}"
    except (TypeError, ValueError):
        formatted_value = str(value)

    value_cell = dashboard.cell(
        row=row_start + 1,
        column=col,
        value=formatted_value,
    )
    value_cell.fill = PatternFill(
        "solid",
        fgColor=WHITE,
    )
    value_cell.font = Font(
        name="Aptos Display",
        bold=True,
        color=NAVY,
        size=15,
    )
    value_cell.alignment = Alignment(
        horizontal="center",
        vertical="center",
        wrap_text=True,
    )
    value_cell.border = thin_border

    dashboard.column_dimensions[
        get_column_letter(col)
    ].width = 21

    dashboard.column_dimensions[
        get_column_letter(col + 1)
    ].width = 4

dashboard.row_dimensions[4].height = 38
dashboard.row_dimensions[5].height = 38

dashboard.merge_cells("A8:H8")
dashboard["A8"] = "KEY OBSERVATIONS"
dashboard["A8"].font = Font(
    name="Aptos",
    size=14,
    bold=True,
    color=NAVY,
)
dashboard["A8"].fill = PatternFill("solid", fgColor=SAGE)

observations = [
    "1. Review the Monthly Revenue sheet to identify changes over time.",
    "2. Review the Country Analysis sheet to compare country-level values.",
    "3. Review the Product Analysis sheet to find high-value product lines.",
    "4. Validate returns, cancellations and unusual transaction types before drawing conclusions.",
    "5. Treat the current totals as preliminary exploratory analysis.",
]

for row_num, text in enumerate(observations, start=9):
    dashboard.merge_cells(
        start_row=row_num,
        start_column=1,
        end_row=row_num,
        end_column=8,
    )

    cell = dashboard.cell(
        row=row_num,
        column=1,
        value=text,
    )

    cell.font = Font(
        name="Aptos",
        color=NAVY,
        size=11,
    )
    cell.fill = PatternFill(
        "solid",
        fgColor=LIGHT_BG if row_num % 2 else WHITE,
    )
    cell.alignment = Alignment(
        vertical="center",
        wrap_text=True,
    )
    cell.border = thin_border
    dashboard.row_dimensions[row_num].height = 29

dashboard.merge_cells("A16:H17")
dashboard["A16"] = (
    "Important: The revenue figures are based on the existing analysis outputs. "
    "Verify the source currency and handling of returns before using them "
    "as confirmed financial results."
)
dashboard["A16"].font = Font(
    name="Aptos",
    color=NAVY,
    italic=True,
    size=10,
)
dashboard["A16"].fill = PatternFill("solid", fgColor=YELLOW)
dashboard["A16"].alignment = Alignment(
    wrap_text=True,
    vertical="center",
)
dashboard["A16"].border = thin_border

dashboard.freeze_panes = "A4"

# Consistent worksheet appearance
for ws in wb.worksheets:
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.outlinePr.summaryBelow = True

# --------------------------------------------------
# SAVE WORKBOOK
# --------------------------------------------------

wb.save(REPORT_PATH)

print("SIGNAL ATLAS Excel report created successfully!")
print(f"Saved to: {REPORT_PATH}")
print(f"File size: {REPORT_PATH.stat().st_size / 1024:.1f} KB")
print("Sheets created:")
for ws in wb.worksheets:
    print(f"- {ws.title}")
