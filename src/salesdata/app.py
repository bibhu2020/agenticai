"""
app.py — Professional Sales Intelligence Dashboard
"""

import httpx
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import time
from datetime import datetime

# ── Config & Database ────────────────────────────────────────────────────────
API_BASE_URL = "http://localhost:8080"
DB_URL = "postgresql://neondb_owner:npg_h4FkSJfs9taC@ep-young-brook-a8mnh7la-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(DB_URL)

# ── Page setup ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InsightPulse Dashboard",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: #0f1116;
        color: #e0e0e0;
    }

    /* Glassmorphism containers */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stChart {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 10px;
    }

    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #16191f;
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    /* Push Streamlit elements down to make room for fixed banner */
    header[data-testid="stHeader"] {
        top: 65px !important;
        background-color: transparent !important;
    }
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        padding-top: 65px !important;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Global scrollbar fix */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0f1116; }
    ::-webkit-scrollbar-thumb { background: #313136; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    query = """
    SELECT 
        o.order_date,
        c.category_name as category,
        cust.type as customer_type,
        cust.region,
        (od.unit_price * od.quantity) as revenue,
        p.product_name,
        cust.company_name as customer
    FROM order_details od
    JOIN orders o ON od.order_id = o.order_id
    JOIN products p ON od.product_id = p.product_id
    JOIN categories c ON p.category_id = c.category_id
    JOIN customers cust ON o.customer_id = cust.customer_id
    """
    df = pd.read_sql(query, engine)
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Failed to connect to Neon DB: {e}")
    st.stop()

# ── State Management ─────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── Header / Hero Banner (Fixed at absolute top) ──────────────────────────────
st.markdown("""
<div style="position: fixed; top: 0; left: 0; width: 100%; background: linear-gradient(135deg, #1e1e2f 0%, #111119 100%); padding: 10px 30px; border-bottom: 1px solid rgba(255,255,255,0.1); z-index: 999999; display: flex; align-items: center; justify-content: space-between; height: 65px;">
    <div style="text-align: left; display: flex; align-items: center; gap: 15px;">
        <h2 style="margin: 0; color: #ffffff; font-size: 1.5rem;">InsightPulse <span style="color: #6366f1;">Intelligence</span></h2>
        <div style="width: 1px; height: 25px; background: rgba(255,255,255,0.1);"></div>
        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0; font-weight: 500;">Executive Sales Governance</p>
    </div>
    <div style="display: flex; gap: 12px;">
        <div style="background: rgba(99, 102, 241, 0.1); padding: 4px 12px; border-radius: 6px; border: 1px solid rgba(99, 102, 241, 0.2); font-size: 0.75rem;">
            <span style="color: #818cf8; font-weight: 700;">AGENT ACTIVE</span>
        </div>
        <div style="background: rgba(16, 185, 129, 0.1); padding: 4px 12px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.2); font-size: 0.75rem;">
            <span style="color: #34d399; font-weight: 700;">NEON CLOUD</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Main Layout: 2 Columns (Dashboard | Chat) ────────────────────────────────
col_main, col_chat = st.columns([2.8, 1.2])

with col_main:
    # Row 1: KPI Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_rev = df['revenue'].sum()
    avg_order = df.groupby('order_date')['revenue'].sum().mean()
    top_cat = df.groupby('category')['revenue'].sum().idxmax()
    cust_count = df['customer'].nunique()
    
    kpi1.metric("Total Revenue", f"${total_rev/1000:,.1f}K", "+12.5%")
    kpi2.metric("Avg Order Value", f"${avg_order:,.0f}", "-2.1%")
    kpi3.metric("Market Leader", top_cat)
    kpi4.metric("Active Clients", cust_count, "+4")

    st.markdown("### 📊 Revenue & Market Dynamics")
    
    # Row 2: Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.caption("Sales Velocity Trend")
        trend_df = df.groupby(df['order_date'].dt.to_period('M'))['revenue'].sum().reset_index()
        trend_df['order_date'] = trend_df['order_date'].astype(str)
        fig_trend = px.area(trend_df, x='order_date', y='revenue', 
                           line_shape='spline', color_discrete_sequence=['#6366f1'])
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color="#e0e0e0", margin=dict(l=0, r=0, t=20, b=0), height=300,
            xaxis_title=None, yaxis_title=None
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with chart_col2:
        st.caption("Revenue Composition by Segment")
        cat_df = df.groupby('category')['revenue'].sum().reset_index()
        fig_pie = px.pie(cat_df, values='revenue', names='category', hole=.4,
                        color_discrete_sequence=px.colors.sequential.Plasma_r)
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color="#e0e0e0", margin=dict(l=0, r=0, t=20, b=0), height=300,
            showlegend=False
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Row 3: Exploratory Lab Integrated
    with st.expander("🔍 Advanced Exploratory Lab"):
        st.write("Deep-drill into specific sales architecture segments.")
        selected_cat = st.multiselect("Filter by Category", df['category'].unique())
        filtered_df = df[df['category'].isin(selected_cat)] if selected_cat else df

        fig_scatter = px.scatter(filtered_df, x='revenue', y='product_name', color='region',
                                size='revenue', hover_data=['customer'])
        fig_scatter.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Row 4: Recent Transactions
    st.markdown("### 📜 Recent High-Value Transactions")
    recent_df = df.sort_values(by='order_date', ascending=False).head(10)[['order_date', 'customer', 'product_name', 'revenue']]
    st.dataframe(recent_df, use_container_width=True, hide_index=True)

# ── Right Column: AI Sales Agent Chat ────────────────────────────────────────
with col_chat:
    st.markdown("""
    <div style="background: rgba(255,255,255,0.02); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 10px;">
        <h4 style="margin: 0; display: flex; align-items: center;">
            <span style="margin-right: 10px;">💬</span> AI Sales Agent
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat Input at the top
    query = st.chat_input("Query sales data...")
    if query:
        # User message immediately added to layout (visual feedback)
        st.session_state.history.insert(0, {"query": query, "response": "..."})
        st.rerun()

    # Handle actual query processing if the latest message is waiting for response
    if st.session_state.history and st.session_state.history[0]["response"] == "...":
        last_query = st.session_state.history[0]["query"]
        try:
            resp = httpx.post(f"{API_BASE_URL}/query", json={"query": last_query}, timeout=60)
            data = resp.json()
            st.session_state.history[0]["response"] = data["response"]
            st.rerun()
        except Exception as e:
            st.session_state.history[0]["response"] = f"Error: {e}"
            st.rerun()

    chat_container = st.container(height=500, border=False)
    
    with chat_container:
        for message in st.session_state.history:
            with st.chat_message("user"):
                st.markdown(f"<div style='font-size: 0.85rem;'>{message['query']}</div>", unsafe_allow_html=True)
            with st.chat_message("assistant"):
                st.markdown(f"<div style='font-size: 0.85rem;'>{message['response']}</div>", unsafe_allow_html=True)

    st.divider()
    
    # Mini stats at the bottom of chat
    st.markdown("#### ⚡ Quick Insights")
    best_cust = df.groupby('customer')['revenue'].sum().idxmax()
    st.info(f"🏆 Top Customer: **{best_cust}**")
    st.success(f"📍 Lead Region: **{df.groupby('region')['revenue'].count().idxmax()}**")

st.divider()
st.caption("© 2026 InsightPulse Systems • Premium Intelligence Dashboard")
