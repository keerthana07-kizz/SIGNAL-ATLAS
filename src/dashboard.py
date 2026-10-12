from pathlib import Path


import pandas as pd

import plotly.express as px

import streamlit as st


# --------------------------------------------------

# PAGE CONFIGURATION

# --------------------------------------------------


st.set_page_config(

    page_title="SIGNAL ATLAS | Retail Intelligence",

    page_icon="✦",

    layout="wide",

    initial_sidebar_state="expanded",

)


# --------------------------------------------------

# COLOR THEME: PASTEL BACKGROUNDS + DARK TEXT

# --------------------------------------------------


st.markdown(

    """

    <style>

    /* Main colors */

    :root {

        --background: #FAF8F4;

        --surface: #FFFFFF;

        --text: #282536;

        --muted: #514B60;

        --border: #D8D1E2;

        --lavender: #E8DFF5;

        --sage: #DDEBDD;

        --peach: #F9E1D5;

        --yellow: #F8EDC8;

        --blue: #DDEAF7;

    }


    /* Main app background */

    .stApp,

    [data-testid="stAppViewContainer"],

    [data-testid="stMain"] {

        background-color: var(--background) !important;

        color: var(--text) !important;

    }


    /* Force readable dark text throughout the app */

    html,

    body,

    [data-testid="stApp"],

    [data-testid="stMain"],

    [data-testid="stMain"] *,

    [data-testid="stSidebar"] *,

    .stMarkdown,

    .stMarkdown p,

    .stMarkdown span,

    .stMarkdown li,

    .stMarkdown label,

    .stCaption,

    label,

    legend {

        color: var(--text) !important;

    }


    /* Headings */

    h1, h2, h3, h4, h5, h6,

    [data-testid="stHeader"],

    [data-testid="stTitle"] {

        color: #282536 !important;

        font-weight: 750 !important;

    }


    h1 {

        letter-spacing: -1px;

    }


    /* Sidebar */

    section[data-testid="stSidebar"] {

        background-color: #EEE8F7 !important;

        border-right: 1px solid #D8CDE8 !important;

    }


    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],

    section[data-testid="stSidebar"] p,

    section[data-testid="stSidebar"] span,

    section[data-testid="stSidebar"] label,

    section[data-testid="stSidebar"] h1,

    section[data-testid="stSidebar"] h2,

    section[data-testid="stSidebar"] h3 {

        color: #29243A !important;

    }


    /* Input boxes, dropdowns and text fields */

    div[data-baseweb="select"] > div,

    div[data-baseweb="input"] > div,

    div[data-baseweb="base-input"],

    div[data-baseweb="textarea"] {

        background-color: #FFFFFF !important;

        border-color: #BEB3D0 !important;

        color: #282536 !important;

    }


    div[data-baseweb="select"] *,

    div[data-baseweb="input"] *,

    div[data-baseweb="base-input"] *,

    div[data-baseweb="textarea"] *,

    input,

    textarea {

        color: #282536 !important;

        -webkit-text-fill-color: #282536 !important;

    }


    input::placeholder,

    textarea::placeholder {

        color: #625B70 !important;

        -webkit-text-fill-color: #625B70 !important;

        opacity: 1 !important;

    }


    /* Dropdown popup and options */

    div[data-baseweb="popover"],

    div[data-baseweb="popover"] > div,

    ul[role="listbox"],

    li[role="option"] {

        background-color: #FFFFFF !important;

        color: #282536 !important;

    }


    li[role="option"] *,

    div[data-baseweb="menu"] *,

    div[data-baseweb="popover"] * {

        color: #282536 !important;

    }


    li[role="option"]:hover {

        background-color: #E8DFF5 !important;

    }


    /* Multiselect selected items */

    span[data-baseweb="tag"],

    div[data-baseweb="tag"] {

        background-color: #E8DFF5 !important;

        border: 1px solid #C8B9E0 !important;

    }


    span[data-baseweb="tag"] *,

    div[data-baseweb="tag"] * {

        color: #282536 !important;

        -webkit-text-fill-color: #282536 !important;

    }


    /* Metric cards */

    [data-testid="stMetric"] {

        background-color: #FFFFFF !important;

        border: 1px solid #DCD4E7 !important;

        border-radius: 16px !important;

        padding: 20px !important;

        box-shadow: 0 3px 12px rgba(49, 39, 65, 0.05);

    }


    [data-testid="stMetric"] label,

    [data-testid="stMetricLabel"],

    [data-testid="stMetricLabel"] *,

    [data-testid="stMetricValue"],

    [data-testid="stMetricValue"] *,

    [data-testid="stMetricDelta"],

    [data-testid="stMetricDelta"] * {

        color: #282536 !important;

        -webkit-text-fill-color: #282536 !important;

    }


    [data-testid="stMetricValue"] {

        font-weight: 750 !important;

    }


    /* General cards and containers */

    [data-testid="stVerticalBlockBorderWrapper"] {

        border-color: #DED7E8 !important;

    }


    /* Tabs */

    button[data-baseweb="tab"] {

        color: #40384F !important;

        font-weight: 650 !important;

    }


    button[data-baseweb="tab"] * {

        color: #40384F !important;

    }


    button[data-baseweb="tab"][aria-selected="true"] {

        border-bottom-color: #75609B !important;

    }


    button[data-baseweb="tab"][aria-selected="true"] *,

    button[data-baseweb="tab"][aria-selected="true"] p {

        color: #29243A !important;

    }


    /* Buttons */

    .stButton > button,

    .stDownloadButton > button,

    button[kind="primary"],

    button[kind="secondary"] {

        background-color: #E8DFF5 !important;

        color: #282536 !important;

        border: 1px solid #C7B8DE !important;

        border-radius: 10px !important;

        font-weight: 700 !important;

    }


    .stButton > button *,

    .stDownloadButton > button *,

    button[kind="primary"] *,

    button[kind="secondary"] * {

        color: #282536 !important;

        -webkit-text-fill-color: #282536 !important;

    }


    .stButton > button:hover,

    .stDownloadButton > button:hover {

        background-color: #D9CBEF !important;

        border-color: #A997C9 !important;

    }


    /* Slider */

    [data-testid="stSlider"] *,

    [data-testid="stCheckbox"] *,

    [data-testid="stRadio"] *,

    [data-testid="stSelectbox"] *,

    [data-testid="stMultiSelect"] * {

        color: #282536 !important;

    }


    /* Dataframes and tables */

    [data-testid="stDataFrame"],

    [data-testid="stTable"] {

        background-color: #FFFFFF !important;

        border: 1px solid #DCD4E7 !important;

        border-radius: 12px !important;

    }


    [data-testid="stDataFrame"] *,

    [data-testid="stTable"] * {

        color: #282536 !important;

    }


    /* Alerts and info boxes */

    [data-testid="stAlert"] {

        background-color: #EAF0F8 !important;

        border: 1px solid #CBD9E9 !important;

    }


    [data-testid="stAlert"] *,

    [data-testid="stAlert"] p {

        color: #282536 !important;

    }


    /* Expanders */

    [data-testid="stExpander"] {

        background-color: #FFFFFF !important;

        border: 1px solid #DCD4E7 !important;

        border-radius: 12px !important;

    }


    [data-testid="stExpander"] summary,

    [data-testid="stExpander"] summary *,

    [data-testid="stExpander"] p {

        color: #282536 !important;

    }


    /* Hero section */

    .hero {

        background: linear-gradient(

            115deg,

            #E8DFF5 0%,

            #DDEBDD 50%,

            #F9E1D5 100%

        );

        border: 1px solid #D6CEE0;

        border-radius: 22px;

        padding: 28px 32px;

        margin-bottom: 22px;

    }


    .hero h1 {

        color: #282536 !important;

        font-size: 2.35rem;

        margin-bottom: 8px;

    }


    .hero p {

        color: #40384F !important;

        font-size: 1.05rem;

        margin-bottom: 0;

    }


    .section-label {

        color: #51436D !important;

        font-size: 0.82rem;

        font-weight: 800;

        letter-spacing: 1.5px;

        text-transform: uppercase;

    }


    .small-note {

        color: #514B60 !important;

        font-size: 0.9rem;

    }


    /* Download and status text */

    .stDownloadButton,

    .stProgress,

    [data-testid="stStatusWidget"] {

        color: #282536 !important;

    }


    /* Footer */

    .footer {

        border-top: 1px solid #DCD4E7;

        margin-top: 36px;

        padding-top: 16px;

        color: #514B60 !important;

        font-size: 0.85rem;

    }


    </style>

    """,

    unsafe_allow_html=True,

)


# --------------------------------------------------

# FILE LOCATIONS

# --------------------------------------------------


ROOT = Path(__file__).resolve().parent.parent

OUTPUTS = ROOT / "outputs"


# --------------------------------------------------

# LOAD DISCOVERY RESULTS

# --------------------------------------------------


@st.cache_data

def load_data():

    required_files = {

        "monthly": OUTPUTS / "monthly_revenue.csv",

        "country": OUTPUTS / "country_revenue.csv",

        "product": OUTPUTS / "product_revenue.csv",

        "summary": OUTPUTS / "discovery_summary.csv",

    }


    missing_files = [

        str(path)

        for path in required_files.values()

        if not path.exists()

    ]


    if missing_files:

        raise FileNotFoundError(

            "These output files are missing:\n"

            + "\n".join(missing_files)

        )


    monthly = pd.read_csv(required_files["monthly"])

    country = pd.read_csv(required_files["country"])

    product = pd.read_csv(required_files["product"])

    summary = pd.read_csv(required_files["summary"])


    # Standardize column names

    for frame in [monthly, country, product, summary]:

        frame.columns = frame.columns.str.strip()


    # Convert revenue columns to numeric values

    for frame in [monthly, country, product]:

        if "Revenue" in frame.columns:

            frame["Revenue"] = pd.to_numeric(

                frame["Revenue"], errors="coerce"

            ).fillna(0)


    if "Month" in monthly.columns:

        monthly["Month"] = monthly["Month"].astype(str)


    if "Country" in country.columns:

        country["Country"] = country["Country"].fillna("Unknown")


    if "Description" in product.columns:

        product["Description"] = (

            product["Description"].fillna("Unknown")

        )


    return monthly, country, product, summary


# --------------------------------------------------

# LOAD DATA SAFELY

# --------------------------------------------------


try:

    monthly_df, country_df, product_df, summary_df = load_data()


except Exception as error:

    st.error("The dashboard could not load its data files.")

    st.write("Check that the four CSV files exist in the outputs folder.")

    st.code(str(error))

    st.stop()


# --------------------------------------------------

# HERO SECTION

# --------------------------------------------------


st.markdown(

    """

    <div class="hero">

        <div class="section-label">RETAIL DATA INTELLIGENCE</div>

        <h1>✦ SIGNAL ATLAS</h1>

        <p>

            Don't just show the data. Reveal what the data is hiding.

            Explore sales patterns, product performance and country-level

            revenue using a large retail dataset.

        </p>

    </div>

    """,

    unsafe_allow_html=True,

)


# --------------------------------------------------

# SIDEBAR / EXPLORE FILTERS

# --------------------------------------------------


st.sidebar.markdown("# ✦ Explore")

st.sidebar.markdown(

    "Choose what you want to investigate."

)


st.sidebar.markdown("---")


available_countries = sorted(

    country_df["Country"].dropna().astype(str).unique().tolist()

) if "Country" in country_df.columns else []


selected_countries = st.sidebar.multiselect(

    "Countries",

    options=available_countries,

    default=available_countries,

    help="Select one or more countries to filter the country chart.",

)


max_products = max(len(product_df), 1)


product_limit = st.sidebar.slider(

    "Products to display",

    min_value=5 if max_products >= 5 else 1,

    max_value=min(30, max_products),

    value=min(10, max_products),

    step=1,

)


st.sidebar.markdown("---")

st.sidebar.markdown("### About this dashboard")

st.sidebar.markdown(

    """

    \\SIGNAL ATLAS\\ explores retail sales data using:


    - Python and Pandas

    - Statistical summaries

    - Interactive Plotly charts

    - Exportable analysis tables

    """

)


st.sidebar.caption(

    "Figures shown here are preliminary descriptive results."

)


# --------------------------------------------------

# SUMMARY METRICS

# --------------------------------------------------


def get_summary_value(metric_name, default=0):

    if not {"Metric", "Value"}.issubset(summary_df.columns):

        return default


    matching_rows = summary_df[

        summary_df["Metric"].astype(str).str.strip().str.lower()

        == metric_name.strip().lower()

    ]


    if matching_rows.empty:

        return default


    try:

        return float(matching_rows.iloc[0]["Value"])

    except (TypeError, ValueError):

        return default


total_rows = get_summary_value("Total source rows")

sales_records = get_summary_value("Sales records analyzed")

total_countries = get_summary_value("Countries represented")

total_products = get_summary_value("Unique products")

total_revenue = get_summary_value("Total analyzed revenue")


st.markdown("## At a glance")


metric1, metric2, metric3, metric4 = st.columns(4)


with metric1:

    st.metric(

        label="Source rows",

        value=f"{total_rows:,.0f}",

    )


with metric2:

    st.metric(

        label="Records analyzed",

        value=f"{sales_records:,.0f}",

    )


with metric3:

    st.metric(

        label="Countries",

        value=f"{total_countries:,.0f}",

    )


with metric4:

    st.metric(

        label="Products",

        value=f"{total_products:,.0f}",

    )


st.caption(

    f"Total analyzed transaction value in the current summary: "

    f"{total_revenue:,.2f}. The dataset's currency should be verified "

    "before treating this value as a confirmed monetary total."

)


# --------------------------------------------------

# PREPARE FILTERED COUNTRY DATA

# --------------------------------------------------


if "Country" in country_df.columns:

    if selected_countries:

        filtered_country_df = country_df[

            country_df["Country"].astype(str).isin(selected_countries)

        ].copy()

    else:

        filtered_country_df = country_df.iloc[0:0].copy()

else:

    filtered_country_df = pd.DataFrame()


# --------------------------------------------------

# CHART STYLE

# --------------------------------------------------


PLOT_BG = "#FFFFFF"

PAPER_BG = "#FAF8F4"

DARK_TEXT = "#282536"

GRID_COLOR = "#E8E2ED"


PASTEL_SEQUENCE = [

    "#B9A6D8",

    "#A9C8AE",

    "#F0C6AF",

    "#E6D28D",

    "#A9C9E8",

    "#D8B5CA",

]


def style_chart(fig, height=390):

    fig.update_layout(

        height=height,

        paper_bgcolor=PAPER_BG,

        plot_bgcolor=PLOT_BG,

        font=dict(

            family="Arial, sans-serif",

            size=12,

            color=DARK_TEXT,

        ),

        title_font=dict(

            size=17,

            color=DARK_TEXT,

        ),

        legend=dict(

            font=dict(color=DARK_TEXT),

            bgcolor="rgba(255,255,255,0.8)",

        ),

        margin=dict(l=25, r=25, t=65, b=45),

        hoverlabel=dict(

            bgcolor="#FFFFFF",

            font=dict(color=DARK_TEXT, size=12),

            bordercolor="#C7B8DE",

        ),

    )


    fig.update_xaxes(

        title_font=dict(color=DARK_TEXT),

        tickfont=dict(color=DARK_TEXT),

        gridcolor=GRID_COLOR,

        linecolor="#D8D1E2",

        zerolinecolor=GRID_COLOR,

    )


    fig.update_yaxes(

        title_font=dict(color=DARK_TEXT),

        tickfont=dict(color=DARK_TEXT),

        gridcolor=GRID_COLOR,

        linecolor="#D8D1E2",

        zerolinecolor=GRID_COLOR,

    )


    return fig


# --------------------------------------------------

# CHARTS

# --------------------------------------------------


st.markdown("---")

st.markdown("## Explore the signals")


tab1, tab2, tab3 = st.tabs(

    [

        "Monthly revenue",

        "Country performance",

        "Product performance",

    ]

)


# Monthly revenue chart

with tab1:

    st.markdown("### How revenue changes over time")


    if {"Month", "Revenue"}.issubset(monthly_df.columns):

        chart_df = monthly_df.copy()


        fig = px.area(

            chart_df,

            x="Month",

            y="Revenue",

            markers=True,

            title="Monthly transaction value",

        )


        fig.update_traces(

            line=dict(color="#8066A8", width=3),

            fillcolor="rgba(185, 166, 216, 0.35)",

            marker=dict(color="#8066A8", size=6),

            hovertemplate=(

                "Month: %{x}<br>"

                "Transaction value: %{y:,.2f}"

                "<extra></extra>"

            ),

        )


        fig.update_layout(

            xaxis_title="Month",

            yaxis_title="Transaction value",

        )


        st.plotly_chart(

            style_chart(fig, 420),

            width="stretch",

        )


        st.caption(

            "This chart shows the monthly values in the prepared summary. "

            "Returns and unusual transaction types may affect interpretation."

        )


        with st.expander("View monthly revenue table"):

            st.dataframe(

                chart_df,

                width="stretch",

                hide_index=True,

            )


            st.download_button(

                "Download monthly data",

                data=chart_df.to_csv(index=False).encode("utf-8"),

                file_name="signal_atlas_monthly_revenue.csv",

                mime="text/csv",

            )

    else:

        st.warning(

            "The monthly revenue file needs Month and Revenue columns."

        )


# Country performance chart

with tab2:

    st.markdown("### Which countries contribute the most?")


    if (

        not filtered_country_df.empty

        and {"Country", "Revenue"}.issubset(filtered_country_df.columns)

    ):

        chart_df = filtered_country_df.sort_values(

            "Revenue", ascending=False

        ).head(20)


        fig = px.bar(

            chart_df.sort_values("Revenue"),

            x="Revenue",

            y="Country",

            orientation="h",

            title="Country revenue comparison",

            color_discrete_sequence=["#A9C8AE"],

            text_auto=".3s",

        )


        fig.update_traces(

            textfont=dict(color=DARK_TEXT, size=11),

            hovertemplate=(

                "Country: %{y}<br>"

                "Transaction value: %{x:,.2f}"

                "<extra></extra>"

            ),

        )


        fig.update_layout(

            xaxis_title="Transaction value",

            yaxis_title="Country",

        )


        st.plotly_chart(

            style_chart(fig, max(400, len(chart_df) * 27)),

            width="stretch",

        )


        with st.expander("View country revenue table"):

            st.dataframe(

                filtered_country_df.sort_values(

                    "Revenue", ascending=False

                ),

                width="stretch",

                hide_index=True,

            )


            st.download_button(

                "Download country data",

                data=filtered_country_df.to_csv(

                    index=False

                ).encode("utf-8"),

                file_name="signal_atlas_country_revenue.csv",

                mime="text/csv",

            )

    else:

        st.info(

            "Select at least one country in the Explore sidebar "

            "to display country performance."

        )


# Product performance chart

with tab3:

    st.markdown("### Which products generate the most value?")


    if (

        not product_df.empty

        and {"Description", "Revenue"}.issubset(product_df.columns)

    ):

        chart_df = product_df.sort_values(

            "Revenue", ascending=False

        ).head(product_limit).copy()


        fig = px.bar(

            chart_df.sort_values("Revenue"),

            x="Revenue",

            y="Description",

            orientation="h",

            title=f"Top {len(chart_df)} products by transaction value",

            color_discrete_sequence=["#F0C6AF"],

            text_auto=".3s",

        )


        fig.update_traces(

            textfont=dict(color=DARK_TEXT, size=10),

            hovertemplate=(

                "Product: %{y}<br>"

                "Transaction value: %{x:,.2f}"

                "<extra></extra>"

            ),

        )


        fig.update_layout(

            xaxis_title="Transaction value",

            yaxis_title="Product",

        )


        st.plotly_chart(

            style_chart(fig, max(420, len(chart_df) * 34)),

            width="stretch",

        )


        with st.expander("View product revenue table"):

            st.dataframe(

                chart_df,

                width="stretch",

                hide_index=True,

            )


            st.download_button(

                "Download product data",

                data=chart_df.to_csv(

                    index=False

                ).encode("utf-8"),

                file_name="signal_atlas_product_revenue.csv",

                mime="text/csv",

            )

    else:

        st.warning(

            "The product revenue file needs Description and Revenue columns."

        )


# --------------------------------------------------

# SUMMARY TABLE

# --------------------------------------------------


st.markdown("---")

st.markdown("## Discovery summary")

st.markdown(

    "Review the summary generated by the current analysis pipeline."

)


st.dataframe(

    summary_df,

    width="stretch",

    hide_index=True,

)


st.download_button(

    "Download discovery summary",

    data=summary_df.to_csv(index=False).encode("utf-8"),

    file_name="signal_atlas_discovery_summary.csv",

    mime="text/csv",

)

# --------------------------------------------------

# ANOMALY DETECTION

# --------------------------------------------------


st.markdown("---")

st.markdown("## Anomaly Detection")

st.markdown(

    "Explore products flagged by the Isolation Forest model. "

    "These are unusual patterns to investigate, not confirmed errors."

)


anomaly_file = OUTPUTS / "product_anomalies.csv"

flagged_file = OUTPUTS / "flagged_product_anomalies.csv"

anomaly_summary_file = OUTPUTS / "anomaly_detection_summary.csv"


if anomaly_file.exists() and flagged_file.exists():

    anomaly_df = pd.read_csv(anomaly_file)

    flagged_df = pd.read_csv(flagged_file)


    if anomaly_summary_file.exists():

        anomaly_summary_df = pd.read_csv(anomaly_summary_file)


        if {"Metric", "Value"}.issubset(anomaly_summary_df.columns):

            st.markdown("### Model summary")


            summary_display = anomaly_summary_df.copy()

            st.dataframe(

                summary_display,

                width="stretch",

                hide_index=True,

            )


    if "Anomaly_Flag" in anomaly_df.columns:

        review_count = int(

            (anomaly_df["Anomaly_Flag"] == "Review").sum()

        )

    else:

        review_count = len(flagged_df)


    total_products_checked = len(anomaly_df)


    col1, col2 = st.columns(2)


    with col1:

        st.metric(

            "Products analyzed",

            f"{total_products_checked:,}",

        )


    with col2:

        st.metric(

            "Products flagged for review",

            f"{review_count:,}",

        )


    st.markdown("### Products flagged for review")


    if flagged_df.empty:

        st.success("No products were flagged by the model.")

    else:

        if "Anomaly_Score" in flagged_df.columns:

            flagged_df["Anomaly_Score"] = pd.to_numeric(

                flagged_df["Anomaly_Score"],

                errors="coerce",

            )


            flagged_df = flagged_df.sort_values(

                "Anomaly_Score",

                ascending=False,

            )


        st.dataframe(

            flagged_df,

            width="stretch",

            hide_index=True,

        )


        st.download_button(

            "Download flagged products",

            data=flagged_df.to_csv(index=False).encode("utf-8"),

            file_name="signal_atlas_flagged_products.csv",

            mime="text/csv",

        )


    with st.expander("View all analyzed products"):

        st.dataframe(

            anomaly_df,

            width="stretch",

            hide_index=True,

        )


        st.download_button(

            "Download all anomaly results",

            data=anomaly_df.to_csv(index=False).encode("utf-8"),

            file_name="signal_atlas_all_anomaly_results.csv",

            mime="text/csv",

        )


else:

    st.info(

        "Anomaly results were not found. Run "

        "`python src/anomaly_detection.py` first."

    )


# --------------------------------------------------

# STATISTICAL VALIDATION

# --------------------------------------------------


st.markdown("---")

st.markdown("## Statistical Validation")


validation_file = OUTPUTS / "statistical_validation.csv"


if validation_file.exists():

    validation_df = pd.read_csv(validation_file)


    st.dataframe(

        validation_df,

        width="stretch",

        hide_index=True,

    )


    st.download_button(

        "Download statistical validation report",

        data=validation_df.to_csv(index=False).encode("utf-8"),

        file_name="signal_atlas_statistical_validation.csv",

        mime="text/csv",

    )

else:

    st.info(

        "Results not found. Run "

        "`python src/statistical_validation.py` first."

    )


# --------------------------------------------------

# CUSTOMER INTELLIGENCE - RFM ANALYSIS

# --------------------------------------------------


st.header("Customer Intelligence")

st.caption(

    "Understand customer purchasing behaviour using "

    "Recency, Frequency, and Monetary analysis."

)


rfm_file = OUTPUTS / "customer_rfm_analysis.csv"

segment_file = OUTPUTS / "customer_segment_summary.csv"


if rfm_file.exists() and segment_file.exists():

    rfm_df = pd.read_csv(rfm_file)

    segment_df = pd.read_csv(segment_file)


    # Customer overview metrics

    total_customers = rfm_df["Customer_ID"].nunique()

    high_value_customers = (

        rfm_df["Customer_Segment"] == "High-Value Active"

    ).sum()

    attention_customers = (

        rfm_df["Customer_Segment"] == "Needs Attention"

    ).sum()


    col1, col2, col3 = st.columns(3)


    col1.metric("Customers Analysed", f"{total_customers:,}")

    col2.metric("High-Value Active", f"{high_value_customers:,}")

    col3.metric("Needs Attention", f"{attention_customers:,}")


   
    st.subheader("Customer Segment Distribution")

    # Prepare customer count data
    segment_plot = segment_df.copy()

    segment_plot["Customer_Count"] = pd.to_numeric(
        segment_plot["Customer_Count"],
        errors="coerce"
    ).fillna(0)

    segment_plot = segment_plot.sort_values(
        "Customer_Count",
        ascending=False
    )

    # Plot customer segment distribution
    fig_customers = px.bar(
        segment_plot,
        x="Customer_Segment",
        y="Customer_Count",
        title="Number of Customers by Segment",
        labels={
            "Customer_Segment": "Customer Segment",
            "Customer_Count": "Number of Customers",
        },
        color="Customer_Segment",
        color_discrete_sequence=PASTEL_SEQUENCE,
    )

    fig_customers.update_layout(
        yaxis=dict(
            rangemode="tozero",
            tickformat=",d"
        ),
        xaxis_tickangle=-25,
        showlegend=False,
    )

    st.plotly_chart(
        style_chart(fig_customers, 420),
        width="stretch",
    )

    st.subheader("Customer Spending by Segment")

    # Prepare customer spending data
    spending_plot = segment_df.copy()

    spending_plot["Total_Monetary"] = pd.to_numeric(
        spending_plot["Total_Monetary"],
        errors="coerce"
    ).fillna(0)

    spending_plot = spending_plot.sort_values(
        "Total_Monetary",
        ascending=False
    )

    # Plot customer spending by segment
    fig_spending = px.bar(
        spending_plot,
        x="Customer_Segment",
        y="Total_Monetary",
        title="Total Customer Spending by Segment",
        labels={
            "Customer_Segment": "Customer Segment",
            "Total_Monetary": "Total Spending",
        },
        color="Customer_Segment",
        color_discrete_sequence=PASTEL_SEQUENCE,
    )

    fig_spending.update_layout(
        yaxis=dict(
            rangemode="tozero",
            tickformat=",.0f"
        ),
        xaxis_tickangle=-25,
        showlegend=False,
    )

    st.plotly_chart(
        style_chart(fig_spending, 420),
        width="stretch",
    )


    st.subheader("Customer RFM Details")


    # Search and filter customer segments

    available_segments = sorted(

        rfm_df["Customer_Segment"].dropna().unique().tolist()

    )


    selected_segments = st.multiselect(

        "Filter by customer segment",

        options=available_segments,

        default=available_segments,

    )


    filtered_customers = rfm_df[

        rfm_df["Customer_Segment"].isin(selected_segments)

    ]


    display_columns = [

        "Customer_ID",

        "Recency_Days",

        "Frequency",

        "Monetary",

        "RFM_Score",

        "Customer_Segment",

        "Customer_Rank",

    ]


    st.dataframe(

    filtered_customers[display_columns],

    width="stretch",

    hide_index=True,

)


    # Download detailed customer analysis

    st.download_button(

        label="Download Customer RFM Analysis",

        data=filtered_customers.to_csv(index=False).encode("utf-8"),

        file_name="signal_atlas_customer_rfm.csv",

        mime="text/csv",

    )


    # Download segment summary

    st.download_button(

        label="Download Customer Segment Summary",

        data=segment_df.to_csv(index=False).encode("utf-8"),

        file_name="signal_atlas_customer_segments.csv",

        mime="text/csv",

    )


else:

    st.info(

        "Customer analysis files are not available yet. "

        "Run customer_intelligence.py first."

    )


# --------------------------------------------------

# WHAT-IF BUSINESS SIMULATOR

# --------------------------------------------------


st.header("What-If Business Simulator")


st.caption(

    "Explore hypothetical revenue changes using interactive assumptions."

)


monthly_file = OUTPUTS / "monthly_revenue.csv"


if monthly_file.exists():

    monthly_df = pd.read_csv(monthly_file)


    revenue_col = next(

        (col for col in monthly_df.columns if "revenue" in col.lower()),

        None,

    )


    if revenue_col is not None:

        monthly_df[revenue_col] = pd.to_numeric(

            monthly_df[revenue_col], errors="coerce"

        )


        baseline_revenue = monthly_df[revenue_col].dropna().sum()


        sales_change = st.slider(

            "Sales volume change (%)",

            min_value=-50,

            max_value=100,

            value=10,

            step=5,

        )


        price_change = st.slider(

            "Price change (%)",

            min_value=-30,

            max_value=50,

            value=5,

            step=5,

        )


        simulated_revenue = (

            baseline_revenue

            * (1 + sales_change / 100)

            * (1 + price_change / 100)

        )


        impact = simulated_revenue - baseline_revenue


        col1, col2, col3 = st.columns(3)


        col1.metric(

            "Baseline Revenue",

            f"{baseline_revenue:,.2f}",

        )


        col2.metric(

            "Simulated Revenue",

            f"{simulated_revenue:,.2f}",

            delta=f"{impact:+,.2f}",

        )


        percent_change = (

            (simulated_revenue / baseline_revenue - 1) * 100

            if baseline_revenue != 0

            else 0

        )


        col3.metric(

            "Revenue Change",

            f"{percent_change:+.1f}%",

        )


        comparison = pd.DataFrame({

            "Scenario": ["Baseline", "What-If Scenario"],

            "Revenue": [baseline_revenue, simulated_revenue],

        })


        st.subheader("Revenue Comparison")

        st.bar_chart(

            comparison.set_index("Scenario"),

            y="Revenue",

            width="stretch",

        )


        st.download_button(

            "Download What-If Results",

            data=comparison.to_csv(index=False).encode("utf-8"),

            file_name="signal_atlas_what_if_results.csv",

            mime="text/csv",

        )


        st.caption(

            "This is a hypothetical calculation, not a sales or profit forecast. "

            "It assumes sales volume and price changes multiply."

        )


    else:

        st.error("No revenue column was found in monthly_revenue.csv.")


else:

    st.warning(

        "Monthly revenue data is missing. Run discovery_engine.py first."

    )


# --------------------------------------------------

# FOOTER

# --------------------------------------------------


st.markdown(

    """

    <div class="footer">

        <strong>SIGNAL ATLAS</strong> · Retail Data Intelligence<br>

        Built with Python, Pandas, Streamlit and Plotly.

        <br><br>

        <span>

            Preliminary exploratory analysis — findings should be validated

            before being used for business decisions.

        </span>

    </div>

    """,

    unsafe_allow_html=True,

)
