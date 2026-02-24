import os
import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px

# ==========================================
# CONFIGURATION
# ==========================================

DATA_FOLDER = Path("data")

st.set_page_config(
    page_title="UNO MINDA Supplier Dashboard",
    layout="wide"
)

st.title("UNO MINDA Supplier Performance Dashboard")


# ==========================================
# SAFE ROUND FUNCTION
# ==========================================

def safe_round(value):

    if value is None:
        return None

    if pd.isna(value):
        return None

    return round(float(value), 1)


# ==========================================
# EXTRACT FILE INFO (VERY FAST)
# ==========================================

def extract_file_info(filename):

    name = filename.replace(".xlsx", "")
    parts = name.split("_")

    year = int(parts[0])
    month = int(parts[1])
    plant = "_".join(parts[2:])

    date = pd.to_datetime(f"{year}-{month}-01")

    return date, plant


# ==========================================
# FAST SCORE EXTRACTION
# reads only first 60 rows (very fast)
# ==========================================

def extract_scores(filepath):

    try:

        df = pd.read_excel(
            filepath,
            header=None,
            nrows=60,
            engine="openpyxl"
        )

    except:
        return None, None, None

    supplier = None
    quality = None
    delivery = None

    for i in range(len(df)):

        row = df.iloc[i].astype(str).str.upper()

        # Supplier score
        if row.str.contains("CURRENT MONTH RATING").any():

            idx = row[row.str.contains("CURRENT MONTH RATING")].index[0]

            val = df.iloc[i, idx+1]

            if isinstance(val, (int, float)):
                supplier = float(val)

        # Quality score
        if "QUALITY" in " ".join(row):

            for cell in df.iloc[i]:

                try:
                    num = float(str(cell).replace("%", ""))

                    if 50 <= num <= 100:
                        quality = num

                except:
                    pass

        # Delivery score
        if "DELIVERY" in " ".join(row):

            for cell in df.iloc[i]:

                try:
                    num = float(str(cell).replace("%", ""))

                    if 50 <= num <= 100:
                        delivery = num

                except:
                    pass

    return supplier, quality, delivery


# ==========================================
# LOAD DATA WITH CACHING (EXTREMELY FAST)
# ==========================================

@st.cache_data
def load_data():

    records = []

    if not DATA_FOLDER.exists():
        return pd.DataFrame()

    files = os.listdir(DATA_FOLDER)

    for file in files:

        if file.endswith(".xlsx"):

            filepath = DATA_FOLDER / file

            try:

                date, plant = extract_file_info(file)

                supplier, quality, delivery = extract_scores(filepath)

                records.append({

                    "Date": date,
                    "Plant": plant,
                    "Supplier Score": supplier,
                    "Quality Score": quality,
                    "Delivery Score": delivery

                })

            except:
                pass

    df = pd.DataFrame(records)

    if not df.empty:
        df = df.sort_values("Date")

    return df


# LOAD ONCE (FAST)
data = load_data()


# ==========================================
# SIDEBAR FILTER (PLANT SLICER)
# ==========================================

st.sidebar.header("Filter")

plant_options = ["All"] + list(data["Plant"].dropna().unique())

selected_plant = st.sidebar.selectbox(
    "Select Plant",
    plant_options
)

filtered_data = data.copy()

if selected_plant != "All":
    filtered_data = data[data["Plant"] == selected_plant]


# ==========================================
# KPI CARDS
# ==========================================

st.subheader("Performance Summary")

col1, col2, col3 = st.columns(3)

latest_supplier = safe_round(filtered_data.iloc[-1]["Supplier Score"]) if not filtered_data.empty else None
latest_quality = safe_round(filtered_data.iloc[-1]["Quality Score"]) if not filtered_data.empty else None
latest_delivery = safe_round(filtered_data.iloc[-1]["Delivery Score"]) if not filtered_data.empty else None

col1.metric("Latest Supplier Score (%)", latest_supplier)
col2.metric("Latest Quality Score (%)", latest_quality)
col3.metric("Latest Delivery Score (%)", latest_delivery)


# ==========================================
# SUPPLIER SCORE GRAPH
# ==========================================

st.subheader("Supplier Score Trend")

fig1 = px.line(
    filtered_data,
    x="Date",
    y="Supplier Score",
    color="Plant",
    markers=True
)

fig1.update_layout(
    yaxis_title="Supplier Score (%)",
    xaxis_title="Date"
)

st.plotly_chart(fig1, use_container_width=True)


# ==========================================
# QUALITY SCORE GRAPH
# ==========================================

st.subheader("Quality Score Trend")

fig2 = px.line(
    filtered_data,
    x="Date",
    y="Quality Score",
    color="Plant",
    markers=True
)

fig2.update_layout(
    yaxis_title="Quality Score (%)",
    xaxis_title="Date"
)

st.plotly_chart(fig2, use_container_width=True)


# ==========================================
# DELIVERY SCORE GRAPH
# ==========================================

st.subheader("Delivery Score Trend")

fig3 = px.line(
    filtered_data,
    x="Date",
    y="Delivery Score",
    color="Plant",
    markers=True
)

fig3.update_layout(
    yaxis_title="Delivery Score (%)",
    xaxis_title="Date"
)

st.plotly_chart(fig3, use_container_width=True)


# ==========================================
# DATA TABLE
# ==========================================

st.subheader("Data Table")

st.dataframe(filtered_data, use_container_width=True)


# ==========================================
# REFRESH BUTTON
# ==========================================

if st.button("Refresh Dashboard"):
    st.cache_data.clear()
    st.rerun()