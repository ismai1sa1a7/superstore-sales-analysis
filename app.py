import pandas as pd
import streamlit as st

st.set_page_config(page_title="Superstore Dashboard", layout="wide")


@st.cache_data
def load_data():
    data = pd.read_csv("Data/Sample - Superstore.csv", encoding="latin1")
    data["Order Date"] = pd.to_datetime(data["Order Date"], format="%m/%d/%Y")
    return data


df = load_data()

st.title("Superstore Sales Dashboard")
st.caption("Practice project: Sample Superstore dataset (2014-2017)")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

years = sorted(df["Order Date"].dt.year.unique())
selected_years = st.sidebar.multiselect("Year", years, default=years)

categories = sorted(df["Category"].unique())
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

filtered = df[
    df["Order Date"].dt.year.isin(selected_years)
    & df["Category"].isin(selected_categories)
]

if filtered.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ---------- KPIs ----------
total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
total_orders = filtered["Order ID"].nunique()
margin = total_profit / total_sales * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Profit", f"${total_profit:,.0f}")
col3.metric("Total Orders", f"{total_orders:,}")
col4.metric("Profit Margin", f"{margin:.1f}%")

st.divider()

# ---------- Chart 1: Monthly sales ----------
st.subheader("Monthly Sales Trend")
monthly_sales = filtered.groupby(filtered["Order Date"].dt.to_period("M"))["Sales"].sum()
monthly_sales.index = monthly_sales.index.to_timestamp()
st.line_chart(monthly_sales)


st.subheader("Profit by Sub-Category")
subcat_profit = filtered.groupby("Sub-Category")["Profit"].sum().sort_values()
st.bar_chart(subcat_profit)

st.subheader("Profit Margin by Discount Level")
bands = pd.cut(filtered["Discount"], bins=[-0.01, 0, 0.2, 0.4, 1.0], labels=["No discount", "1-20%", "21-40%", "Over 40%"])
band_analysis = filtered.groupby(bands, observed=True).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
band_margin = (band_analysis["Profit"] / band_analysis["Sales"] * 100).round(1)
st.bar_chart(band_margin)
st.caption("Margin (%) turns negative once discounts exceed 20%.")
