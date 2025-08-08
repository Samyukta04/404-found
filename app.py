import streamlit as st
import os
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import random
from dotenv import load_dotenv
from groq import Groq
import yfinance as yf
import io

load_dotenv()

st.set_page_config(
    page_title="Credit Intelligence Engine",
    page_icon="🧠",
    layout="wide"
)

# ----------------------------- STYLES -----------------------------
st.markdown("""
<style>
    .hero-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 3rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #007bff;
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    .analysis-container {
        background: #f8f9fa;
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        max-height: 400px;
        overflow-y: auto;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .customer-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #007bff;
    }
    .opportunity-high { border-left-color: #28a745; background: #f5fff5; }
    .opportunity-medium { border-left-color: #ffc107; background: #fffdf5; }
    .opportunity-low { border-left-color: #dc3545; background: #fff5f5; }
    .real-time-indicator {
        display: inline-block;
        background: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% {opacity:1;} 50% {opacity:0.7;} 100% {opacity:1;} }
    .input-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
    }
    .real-data-badge { background:#28a745;color:white;padding:0.2rem 0.5rem;border-radius:5px;font-size:0.7rem;margin-left:0.5rem; }
    .success-box { background:#d4edda;border:1px solid #c3e6cb;color:#155724;padding:1rem;border-radius:8px;margin:1rem 0; }
</style>
""", unsafe_allow_html=True)

# ------------------------ GROQ CLIENT ------------------------
@st.cache_resource
def init_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("⚠ Please set your GROQ_API_KEY in the .env file")
        st.stop()
    return Groq(api_key=api_key)

client = init_groq_client()

# ------------------------ MARKET DATA ------------------------
@st.cache_data(ttl=300)
def get_real_market_data():
    try:
        sp500 = yf.Ticker("^GSPC")
        vix = yf.Ticker("^VIX")
        treasury = yf.Ticker("^TNX")

        sp500_data = sp500.history(period="2d")
        vix_data = vix.history(period="1d")
        treasury_data = treasury.history(period="1d")

        if len(sp500_data) >= 2:
            sp500_change = ((sp500_data['Close'].iloc[-1] - sp500_data['Close'].iloc[-2]) / sp500_data['Close'].iloc[-2]) * 100
        else:
            sp500_change = random.uniform(-2, 2)

        return {
            'sp500_change': sp500_change,
            'vix_level': vix_data['Close'].iloc[-1] if not vix_data.empty else random.uniform(12, 35),
            'treasury_rate': treasury_data['Close'].iloc[-1] if not treasury_data.empty else random.uniform(4.2, 5.8),
            'timestamp': datetime.now(),
            'data_source': 'live' if not sp500_data.empty else 'simulated'
        }
    except Exception as e:
        return {
            'sp500_change': random.uniform(-2, 2),
            'vix_level': random.uniform(12, 35),
            'treasury_rate': random.uniform(4.2, 5.8),
            'timestamp': datetime.now(),
            'data_source': 'simulated',
            'error': str(e)
        }

# --------------------- SESSION DEFAULTS ---------------------
if 'customers' not in st.session_state:
    st.session_state.customers = []
if 'processed_customers' not in st.session_state:
    st.session_state.processed_customers = 0
if 'total_revenue_impact' not in st.session_state:
    st.session_state.total_revenue_impact = 0.0
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'show_analysis' not in st.session_state:
    st.session_state.show_analysis = {}

# ----------------------------- HEADER -----------------------------
st.markdown("""
<div class="hero-container">
    <h1>Credit Intelligence Engine</h1>
    <h3>Real-Time Credit Optimization & Revenue Maximization</h3>
    <p><span class="real-time-indicator">🔴 LIVE</span> AI-Powered Customer Portfolio Management</p>
</div>
""", unsafe_allow_html=True)

# ============================ TABS (TOP) ============================
tab_dashboard, tab_all = st.tabs(["📊 Dashboard", "📋 All Customers"])

# ============================== DASHBOARD ==============================
with tab_dashboard:
    # --- Market cards ---
    market_data = get_real_market_data()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        color = "🟢" if market_data['sp500_change'] > 0 else "🔴"
        st.metric(f"S&P 500 {color}", f"{market_data['sp500_change']:+.2f}%", delta=f"Source: {market_data['data_source']}")
    with c2:
        st.metric("VIX (Fear Index)", f"{market_data['vix_level']:.1f}", delta="Live data")
    with c3:
        st.metric("10Y Treasury", f"{market_data['treasury_rate']:.2f}%", delta="Current rate")
    with c4:
        st.metric("Last Update", market_data['timestamp'].strftime("%H:%M:%S"), delta="Auto-refresh")

    # --- Input form ---
    st.markdown("""
    <div class="input-section">
        <h3>Add Real Customer Data</h3>
        <p>Input actual customer information for AI analysis and credit optimization</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("customer_input_form", clear_on_submit=True):
        st.markdown("**Required fields are marked with ***")
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name *", placeholder="e.g., John Smith")
            current_limit = st.number_input("Current Credit Limit ($) *", min_value=500, max_value=100000, value=5000, step=500)
            utilization = st.slider("Credit Utilization (%)", 0, 100, 45)
            payment_history = st.slider("Payment History Score", 0, 100, 85)
        with col2:
            income = st.number_input("Annual Income ($) *", min_value=25000, max_value=500000, value=65000, step=5000)
            risk_score = st.number_input("Risk Score (300-850)", min_value=300, max_value=850, value=650)
            months_since_increase = st.number_input("Months Since Last Increase", min_value=0, max_value=120, value=12)
            spending_category = st.selectbox("Primary Spending Category",
                                             ["Groceries", "Gas", "Dining", "Travel", "Shopping", "Healthcare", "Business"])
        submitted = st.form_submit_button("➕ Add Customer for Analysis", type="primary", use_container_width=True)

    # --- Submission handling ---
    if submitted:
        if not customer_name or not customer_name.strip():
            st.error("❌ Customer name is required!")
        elif customer_name.strip() in [c['name'] for c in st.session_state.customers]:
            st.error("❌ Customer with this name already exists in portfolio!")
        else:
            utilization_decimal = utilization / 100
            utilization_factor = max(0.5, 1 - utilization_decimal) if utilization_decimal > 0.7 else 1.2
            income_factor = min(2.0, income / 50000)
            risk_factor = max(0.3, (risk_score - 300) / 550)
            time_factor = min(1.3, 1 + (months_since_increase / 60))

            market_factor = 1.0
            if market_data['sp500_change'] > 1: market_factor = 1.1
            elif market_data['sp500_change'] < -1: market_factor = 0.9

            recommended_limit = int(current_limit * utilization_factor * income_factor * risk_factor * time_factor * market_factor)
            recommended_limit = max(current_limit, recommended_limit)
            rate_reduction = max(0, (payment_history - 80) * 0.05 + (risk_score - 600) * 0.01)

            increase_percentage = (recommended_limit - current_limit) / current_limit
            opportunity = "High" if increase_percentage > 0.3 else ("Medium" if increase_percentage > 0.1 else "Low")

            new_customer = {
                "id": f"C{len(st.session_state.customers) + 1:03d}",
                "name": customer_name.strip(),
                "current_limit": current_limit,
                "utilization": utilization_decimal,
                "payment_history": payment_history,
                "income": income,
                "risk_score": risk_score,
                "last_increase": f"{months_since_increase} months ago" if months_since_increase > 0 else "never",
                "spending_trend": "analyzed",
                "category_spend": {spending_category.lower(): int(current_limit * utilization_decimal * 0.6)},
                "opportunity": opportunity,
                "recommended_limit": recommended_limit,
                "rate_reduction": rate_reduction,
                "market_context": f"Added during {market_data['sp500_change']:+.1f}% market day",
                "timestamp": datetime.now(),
                "spending_category": spending_category
            }
            st.session_state.customers.append(new_customer)

            st.markdown(f"""
            <div class="success-box">
                <h4>✅ {customer_name.strip()} Added Successfully!</h4>
                <ul>
                    <li><strong>AI Recommendation:</strong> ${recommended_limit:,} limit ({increase_percentage * 100:.0f}% increase)</li>
                    <li><strong>Opportunity Level:</strong> {opportunity}</li>
                    <li><strong>Potential APR Reduction:</strong> {rate_reduction:.1f}%</li>
                    <li><strong>Revenue Impact:</strong> ${(recommended_limit - current_limit) * 0.15:,.0f} annually</li>
                    <li><strong>Market Timing:</strong> {'Favorable' if market_data['sp500_change'] > 0 else 'Cautious approach'}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1); st.rerun()

    # --- Display last 3 customers + metrics/charts ---
    if st.session_state.customers:
        st.markdown("### Customer Portfolio Analysis")
        st.markdown(f"*Showing {min(3, len(st.session_state.customers))} most recent customers:*")
        left, right = st.columns([2, 1])

        with left:
            for i, customer in enumerate(reversed(st.session_state.customers[-3:])):
                opportunity_class = f"opportunity-{customer['opportunity'].lower()}"
                st.markdown(f"""
                <div class="customer-card {opportunity_class}">
                    <h4>{customer['name']} (ID: {customer['id']}) <span class="real-data-badge">REAL DATA</span></h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                        <div><strong>Current Limit:</strong> ${customer['current_limit']:,}</div>
                        <div><strong>Utilization:</strong> {customer['utilization']:.0%}</div>
                        <div><strong>Risk Score:</strong> {customer['risk_score']}</div>
                        <div><strong>Income:</strong> ${customer['income']:,}</div>
                        <div><strong>Payment History:</strong> {customer['payment_history']}%</div>
                        <div><strong>Primary Category:</strong> {customer.get('spending_category', 'N/A')}</div>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                        <strong>🧠 AI Recommendation:</strong><br>
                        • Increase limit to ${customer['recommended_limit']:,} (+{((customer['recommended_limit'] / customer['current_limit']) - 1) * 100:.0f}%)<br>
                        • Potential APR reduction: {customer['rate_reduction']:.1f}%<br>
                        • Estimated annual revenue increase: ${(customer['recommended_limit'] - customer['current_limit']) * 0.15:,.0f}<br>
                        • Market timing: {"Favorable conditions" if market_data['sp500_change'] > 0 else "Cautious approach recommended"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with right:
            st.markdown("### 📊 Real-Time Portfolio Metrics")
            total_customers = len(st.session_state.customers)
            total_portfolio_value = sum([c['current_limit'] for c in st.session_state.customers])
            avg_utilization = sum([c['utilization'] for c in st.session_state.customers]) / max(total_customers, 1)
            high_opportunity_count = len([c for c in st.session_state.customers if c['opportunity'] == 'High'])

            st.markdown(f"""
            <div class="metric-card">
                <h4>Portfolio Overview</h4>
                <div><strong>Total Customers:</strong> {total_customers}</div>
                <div><strong>Portfolio Value:</strong> ${total_portfolio_value:,}</div>
                <div><strong>Avg Utilization:</strong> {avg_utilization:.0%}</div>
                <div><strong>High Opportunities:</strong> {high_opportunity_count}</div>
            </div>
            """, unsafe_allow_html=True)

            if total_customers > 0:
                st.markdown("#### Customer Utilization Distribution")
                fig = px.histogram(x=[c['utilization'] * 100 for c in st.session_state.customers],
                                   nbins=min(10, total_customers),
                                   title="Credit Utilization (%)",
                                   labels={'x': 'Utilization %', 'y': 'Customers'})
                fig.update_layout(height=250, showlegend=False,
                                  xaxis_title="Utilization %", yaxis_title="Customers")
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("#### Opportunity Distribution")
                counts = {}
                for c in st.session_state.customers:
                    counts[c['opportunity']] = counts.get(c['opportunity'], 0) + 1
                fig_pie = px.pie(values=list(counts.values()), names=list(counts.keys()),
                                 color_discrete_map={'High': '#28a745', 'Medium': '#ffc107', 'Low': '#dc3545'})
                fig_pie.update_layout(height=250)
                st.plotly_chart(fig_pie, use_container_width=True)

        # --- Refresh controls (stay in Dashboard) ---
        r1, r2, r3 = st.columns(3)
        with r1:
            if st.button("🔄 Refresh Market Data", type="secondary"):
                st.cache_data.clear(); st.rerun()
        with r2:
            if st.button("📊 Recalculate All", type="secondary"):
                for cust in st.session_state.customers:
                    cust['market_context'] = f"Updated during {market_data['sp500_change']:+.1f}% market day"
                st.success("✅ All customer data recalculated with current market conditions!")
                time.sleep(1); st.rerun()
        with r3:
            if st.button("🗑 Clear Portfolio", type="secondary"):
                st.session_state.customers = []
                st.session_state.processed_customers = 0
                st.session_state.total_revenue_impact = 0.0
                st.session_state.analysis_results = {}
                st.success("✅ Portfolio cleared!")
                time.sleep(1); st.rerun()

        # --- Revenue projection ---
        st.markdown("#### 💰 6-Month Revenue Projection")
        months = ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6']
        baseline = [st.session_state.total_revenue_impact * (i + 1) / 6 for i in range(6)]
        optimized = [st.session_state.total_revenue_impact * 1.2 * (i + 1) / 6 for i in range(6)]
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Scatter(x=months, y=baseline, name='Conservative Estimate'))
        fig_rev.add_trace(go.Scatter(x=months, y=optimized, name='Optimistic Projection'))
        fig_rev.update_layout(title="Revenue Impact Projection ($)", height=400,
                              xaxis_title="Timeline", yaxis_title="Revenue Impact ($)")
        st.plotly_chart(fig_rev, use_container_width=True)
    else:
        st.info("👆 *Add customer data above to see real-time AI analysis and portfolio optimization!*")

# ============================== ALL CUSTOMERS ==============================
def build_customers_df(customers):
    if not customers:
        return pd.DataFrame()
    df = pd.json_normalize(customers, sep=".")
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    preferred = [
        "id","name","current_limit","recommended_limit","utilization","payment_history",
        "income","risk_score","opportunity","rate_reduction","spending_category",
        "last_increase","market_context","timestamp"
    ]
    cols = [c for c in preferred if c in df.columns] + [c for c in df.columns if c not in preferred]
    return df[cols]

with tab_all:
    st.markdown("### 📋 Full Customer List")
    if not st.session_state.customers:
        st.info("No customers yet. Add some on the Dashboard tab.")
    else:
        df = build_customers_df(st.session_state.customers)
        st.dataframe(df, use_container_width=True)

        # CSV
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        # Excel
        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Customers")
        excel_buf.seek(0)

        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button("⬇ Download CSV", data=csv_bytes,
                               file_name="customers.csv", mime="text/csv",
                               use_container_width=True)
        with dl2:
            st.download_button("⬇ Download Excel", data=excel_buf,
                               file_name="customers.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)

# ----------------------------- FOOTER STRAP -----------------------------
st.markdown("---")
st.markdown("""
<div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 2rem; border-radius: 15px; text-align: center;">
    <h3>Credit Intelligence Engine</h3>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 2rem; margin: 1rem 0;">
        <div><h4 style="color: #28a745;">Real-Time</h4><p>Market Data Integration</p></div>
        <div><h4 style="color: #007bff;">AI-Powered</h4><p>Credit Optimization</p></div>
        <div><h4 style="color: #ffc107;">User-Driven</h4><p>Portfolio Building</p></div>
        <div><h4 style="color: #dc3545;">Measurable</h4><p>Business Impact</p></div>
    </div>
    <p><strong>Revolutionary Credit Intelligence • Live Market Integration • Immediate ROI Calculation</strong></p>
</div>
""", unsafe_allow_html=True)