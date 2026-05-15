"""
RetailIQ – Streamlit Analytics Dashboard
Run: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RetailIQ Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background: #161b22; border-radius: 12px; padding: 16px;
                border: 1px solid #30363d; }
    .stMetric label { color: #8b949e !important; font-size: 12px !important; }
    .stMetric [data-testid="stMetricValue"] { color: #f0f6fc !important; font-size: 24px !important; }
    .stSelectbox label, .stMultiSelect label { color: #8b949e; }
    [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #21262d; }
    h1, h2, h3 { color: #f0f6fc; }
    .section-title {
        font-size: 18px; font-weight: 700; color: #f0f6fc;
        border-left: 4px solid #e94560; padding-left: 12px; margin: 20px 0 12px 0;
    }
</style>
""", unsafe_allow_html=True)

COLORS = ["#e94560","#f5a623","#00b4d8","#0f3460","#48cae4",
          "#90e0ef","#023e8a","#03045e","#f72585","#4cc9f0"]

# ── Data Loader ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data = os.path.join(base, "data")
    tx   = pd.read_csv(f"{data}/transactions.csv", parse_dates=["date"])
    cust = pd.read_csv(f"{data}/customers.csv")
    prod = pd.read_csv(f"{data}/products.csv")
    stor = pd.read_csv(f"{data}/stores.csv")

    df = (tx
          .merge(cust[["customer_id","city","age","gender","segment","is_loyalty_member"]], on="customer_id", how="left")
          .merge(prod[["product_id","product_name","category","brand"]], on="product_id", how="left")
          .merge(stor[["store_id","store_name","region"]], on="store_id", how="left"))
    df["month_label"] = df["date"].dt.to_period("M").astype(str)
    return df

df_all = load_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filters")

    years = sorted(df_all["year"].unique())
    sel_years = st.multiselect("Year", years, default=years)

    categories = sorted(df_all["category"].dropna().unique())
    sel_cats = st.multiselect("Category", categories, default=categories)

    segments = sorted(df_all["segment"].dropna().unique())
    sel_segs = st.multiselect("Customer Segment", segments, default=segments)

    channels = sorted(df_all["channel"].dropna().unique())
    sel_chan = st.multiselect("Channel", channels, default=channels)

    st.markdown("---")
    st.markdown("**RetailIQ v1.0**  \n📊 50K transactions · 2K customers")

# ── Filtered Data ─────────────────────────────────────────────────────────────
df = df_all[
    df_all["year"].isin(sel_years) &
    df_all["category"].isin(sel_cats) &
    df_all["segment"].isin(sel_segs) &
    df_all["channel"].isin(sel_chan)
]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🛒 RetailIQ — Sales & Customer Analytics")
st.markdown(f"*Showing **{len(df):,}** transactions · {df['year'].min()}–{df['year'].max()}*")
st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Key Performance Indicators</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5, k6, k7, k8 = st.columns(8)
total_rev  = df["total_amount"].sum()
total_prof = df["profit"].sum()
margin     = total_prof / total_rev * 100 if total_rev > 0 else 0
aov        = df["total_amount"].mean()
returns    = df["is_returned"].mean() * 100
rating     = df["rating"].mean()
uniq_cust  = df["customer_id"].nunique()
total_ord  = len(df)

k1.metric("Total Revenue",   f"₹{total_rev/1e7:.2f}Cr")
k2.metric("Total Profit",    f"₹{total_prof/1e7:.2f}Cr")
k3.metric("Profit Margin",   f"{margin:.1f}%")
k4.metric("Total Orders",    f"{total_ord:,}")
k5.metric("Unique Customers",f"{uniq_cust:,}")
k6.metric("Avg Order Value", f"₹{aov:,.0f}")
k7.metric("Return Rate",     f"{returns:.1f}%")
k8.metric("Avg Rating",      f"⭐ {rating:.2f}")

st.markdown("---")

# ── Row 1: Revenue Trend + Category Split ─────────────────────────────────────
st.markdown('<div class="section-title">📈 Revenue Trends</div>', unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])

with col1:
    monthly = (df.groupby(["year","month"])["total_amount"]
               .sum().reset_index().sort_values(["year","month"]))
    monthly["label"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)
    fig = px.line(monthly, x="label", y="total_amount", color="year",
                  title="Monthly Revenue by Year",
                  color_discrete_sequence=COLORS,
                  labels={"total_amount": "Revenue (₹)", "label": "Month"})
    fig.update_layout(
        plot_bgcolor="#161b22", paper_bgcolor="#161b22",
        font_color="#c9d1d9", legend_title_text="Year",
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    qtr = df.groupby(["year","quarter"])["total_amount"].sum().reset_index()
    fig2 = px.bar(qtr, x="quarter", y="total_amount", color="year",
                  barmode="group", title="Quarterly Revenue YoY",
                  color_discrete_sequence=COLORS,
                  labels={"total_amount": "Revenue (₹)"})
    fig2.update_layout(
        plot_bgcolor="#161b22", paper_bgcolor="#161b22",
        font_color="#c9d1d9"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Category + Top Products ───────────────────────────────────────────
st.markdown('<div class="section-title">🏷️ Product & Category Performance</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)

with col3:
    cat_df = (df.groupby("category")
                .agg(revenue=("total_amount","sum"), profit=("profit","sum"))
                .reset_index()
                .sort_values("revenue", ascending=False))
    cat_df["margin"] = (cat_df["profit"] / cat_df["revenue"] * 100).round(1)
    fig3 = px.bar(cat_df, x="revenue", y="category", orientation="h",
                  color="margin", color_continuous_scale="RdYlGn",
                  title="Revenue & Margin by Category",
                  labels={"revenue": "Revenue (₹)", "margin": "Margin %"})
    fig3.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#161b22", font_color="#c9d1d9")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    top_prod = (df.groupby("product_name")["total_amount"]
                  .sum().nlargest(10).reset_index()
                  .sort_values("total_amount"))
    fig4 = px.bar(top_prod, x="total_amount", y="product_name", orientation="h",
                  title="Top 10 Products by Revenue",
                  color_discrete_sequence=["#e94560"],
                  labels={"total_amount": "Revenue (₹)", "product_name": "Product"})
    fig4.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#161b22", font_color="#c9d1d9")
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Customer Analytics ─────────────────────────────────────────────────
st.markdown('<div class="section-title">👥 Customer Analytics</div>', unsafe_allow_html=True)
col5, col6, col7 = st.columns(3)

with col5:
    seg_df = df.groupby("segment")["total_amount"].sum().reset_index()
    fig5 = px.pie(seg_df, values="total_amount", names="segment",
                  title="Revenue by Segment",
                  color_discrete_sequence=COLORS)
    fig5.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#161b22", font_color="#c9d1d9")
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    df2 = df.copy()
    df2["age_group"] = pd.cut(df2["age"], bins=[17,25,35,45,55,70],
                               labels=["18-25","26-35","36-45","46-55","56+"])
    age_df = df2.groupby("age_group", observed=True)["total_amount"].sum().reset_index()
    fig6 = px.bar(age_df, x="age_group", y="total_amount",
                  title="Revenue by Age Group",
                  color_discrete_sequence=["#00b4d8"],
                  labels={"total_amount":"Revenue (₹)","age_group":"Age Group"})
    fig6.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#161b22", font_color="#c9d1d9")
    st.plotly_chart(fig6, use_container_width=True)

with col7:
    loyalty = df.groupby("is_loyalty_member")["total_amount"].agg(["sum","mean"]).reset_index()
    loyalty["label"] = loyalty["is_loyalty_member"].map({True:"Loyalty Member", False:"Non-Member"})
    fig7 = px.bar(loyalty, x="label", y="mean",
                  title="Avg Order Value: Loyalty vs Non-Loyalty",
                  color_discrete_sequence=["#f5a623"],
                  labels={"mean":"Avg Order (₹)","label":""})
    fig7.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#161b22", font_color="#c9d1d9")
    st.plotly_chart(fig7, use_container_width=True)

# ── Row 4: Regional + Payment ─────────────────────────────────────────────────
st.markdown('<div class="section-title">🗺️ Regional & Channel Performance</div>', unsafe_allow_html=True)
col8, col9 = st.columns(2)

with col8:
    city_df = (df.groupby("city")["total_amount"]
                 .sum().nlargest(12).reset_index()
                 .sort_values("total_amount"))
    fig8 = px.bar(city_df, x="total_amount", y="city", orientation="h",
                  title="Top Cities by Revenue",
                  color="total_amount", color_continuous_scale="Blues",
                  labels={"total_amount":"Revenue (₹)","city":"City"})
    fig8.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#161b22", font_color="#c9d1d9")
    st.plotly_chart(fig8, use_container_width=True)

with col9:
    pay_df = df.groupby("payment_method")["total_amount"].sum().reset_index()
    fig9 = px.pie(pay_df, values="total_amount", names="payment_method",
                  title="Revenue by Payment Method",
                  color_discrete_sequence=COLORS, hole=0.4)
    fig9.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#161b22", font_color="#c9d1d9")
    st.plotly_chart(fig9, use_container_width=True)

# ── Row 5: RFM + Discount ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">🧠 Advanced Analytics</div>', unsafe_allow_html=True)
col10, col11 = st.columns(2)

with col10:
    # RFM quick view from data
    rfm_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "data", "rfm_segments.csv")
    if os.path.exists(rfm_path):
        rfm = pd.read_csv(rfm_path)
        seg_cnt = rfm["Segment"].value_counts().reset_index()
        seg_cnt.columns = ["Segment","Count"]
        fig10 = px.pie(seg_cnt, values="Count", names="Segment",
                       title="RFM Customer Segments",
                       color_discrete_sequence=COLORS)
        fig10.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#161b22", font_color="#c9d1d9")
        st.plotly_chart(fig10, use_container_width=True)

with col11:
    disc = df.groupby("discount_pct").agg(avg_rev=("total_amount","mean"),
                                           count=("total_amount","count")).reset_index()
    fig11 = px.scatter(disc, x="discount_pct", y="avg_rev", size="count",
                       title="Discount % vs Avg Revenue",
                       color="avg_rev", color_continuous_scale="Reds",
                       labels={"discount_pct":"Discount %","avg_rev":"Avg Revenue (₹)"})
    fig11.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#161b22", font_color="#c9d1d9")
    st.plotly_chart(fig11, use_container_width=True)

# ── Data Table ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Transaction Data Explorer</div>', unsafe_allow_html=True)
cols_show = ["transaction_id","date","product_name","category","segment","city",
             "channel","payment_method","quantity","total_amount","profit","rating"]
sample = df[cols_show].sort_values("date", ascending=False).head(500)
st.dataframe(sample.style.format({
    "total_amount": "₹{:,.0f}",
    "profit":       "₹{:,.0f}",
    "rating":       "{:.0f}⭐"
}), use_container_width=True, height=350)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#8b949e; font-size:13px'>"
    "RetailIQ Analytics Dashboard · Built with Python, Pandas, Plotly & Streamlit"
    "</div>",
    unsafe_allow_html=True
)
