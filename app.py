# app.py
# Canadian Business Owner Wealth Transition Planner
# Main Streamlit application

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from estate_module import calculate_estate
from tax_engine import calculate_tax, FEDERAL_BRACKETS, ONTARIO_BRACKETS
from hello import calculate_business_sale, future_value, years_to_goal, future_value_contributions
from rrsp_module import rrsp_meltdown
from cpp_oas_module import calculate_cap_monthly, calculate_oas_monthly, CPP_MAX_AGE_65, OAS_MAX_AGE_65
from monte_carlo import run_monte_carlo
from cashflow_module import run_cashflow
from client_manager import get_saved_clients, save_client, load_client, delete_client

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Canadian Wealth Transition Planner",
    page_icon="💼",
    layout="wide"
)

# ── Custom CSS Theme ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root variables ── */
:root {
    --navy:      #0B1426;
    --navy-mid:  #112240;
    --navy-card: #1A2F4A;
    --gold:      #C9A84C;
    --gold-light:#E8C97A;
    --white:     #F0F4FF;
    --muted:     #8BA3C7;
    --success:   #2DD4A0;
    --danger:    #FF6B6B;
    --border:    rgba(201,168,76,0.2);
}

/* ── Global background ── */
.stApp {
    background: linear-gradient(135deg, #0B1426 0%, #0D1B35 50%, #0B1426 100%);
    font-family: 'DM Sans', sans-serif;
    color: var(--white);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--navy-mid) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label {
    color: var(--muted) !important;
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-weight: 500;
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--gold) !important;
    font-family: 'Playfair Display', serif;
    font-size: 0.9rem;
    letter-spacing: 0.08em;
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
    margin-top: 20px;
}

/* ── Main title ── */
h1 {
    font-family: 'Playfair Display', serif !important;
    color: var(--white) !important;
    font-size: 2.2rem !important;
    letter-spacing: -0.02em;
    border-bottom: 2px solid var(--gold);
    padding-bottom: 12px;
    margin-bottom: 4px !important;
}

/* ── Section headers ── */
h2 {
    font-family: 'Playfair Display', serif !important;
    color: var(--gold-light) !important;
    font-size: 1.4rem !important;
    letter-spacing: 0.01em;
    margin-top: 2rem !important;
}

h3 {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--muted) !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 600;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--navy-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px !important;
    transition: border-color 0.2s ease;
}
[data-testid="stMetric"]:hover {
    border-color: var(--gold);
}
[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 500;
}
[data-testid="stMetricValue"] {
    color: var(--white) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.7rem !important;
    font-weight: 600;
    letter-spacing: -0.02em;
}
[data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
}

/* ── Caption ── */
.stCaption {
    color: var(--muted) !important;
    font-size: 0.75rem;
    letter-spacing: 0.04em;
}

/* ── Plotly chart backgrounds ── */
.js-plotly-plot {
    border-radius: 12px;
    border: 1px solid var(--border);
    overflow: hidden;
}

/* ── Dataframe table ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

/* ── Number inputs & sliders ── */
[data-testid="stNumberInput"] input {
    background: var(--navy) !important;
    border: 1px solid var(--border) !important;
    color: var(--white) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: var(--gold) !important;
}

/* ── Dividers ── */
hr {
    border-color: var(--border) !important;
    margin: 1.5rem 0;
}

/* ── Success/warning probability colors ── */
.success-text { color: var(--success); }
.warning-text { color: #F4A261; }
.danger-text  { color: var(--danger); }

/* ── Gold accent line before each section ── */
h2::before {
    content: '';
    display: block;
    width: 40px;
    height: 3px;
    background: var(--gold);
    margin-bottom: 8px;
    border-radius: 2px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1>Canadian Wealth<br>Transition Planner</h1>
<p style='color:#8BA3C7; font-size:0.85rem; letter-spacing:0.05em; margin-top:-8px;'>
    ONTARIO · 2026 TAX YEAR · CRA VERIFIED
</p>
<hr>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────
# These hold the current values across Streamlit reruns
# Only set once on first load — never overwrite user's live inputs
defaults = {
    "client_name":        "New Client",
    "client_age":         45,
    "proceeds":           0,
    "cost_base":          0,
    "lcge_available":     0,
    "retirement_age":     60,
    "life_expectancy":    90,
    "annual_spending":    80000,
    "mean_return":        6.0,
    "cpp_start_age":      65,
    "oas_start_age":      65,
    "rrsp_balance_today": 0,
    "tfsa_balance_today": 0,
    "tfsa_lump_sum":      0,
    "has_business":       True,
    "non_reg_balance_today":  0,
    "current_tfsa_room":  109000,
    "annual_rrsp_contrib":18000,
    "annual_tfsa_contrib":7000,
    "employment_income":  80000,
    "std_return":         12.0,
    "mean_inflation":     2.5,
    "std_inflation":      1.0,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Sidebar: Client Manager ───────────────────────────────────
st.sidebar.markdown("### Client Manager")

saved_clients = get_saved_clients()
selected_client = st.sidebar.selectbox(
    "Saved Clients",
    options=["— select a client —"] + saved_clients,
    key="selected_client"
)

cm1, cm2, cm3, cm4 = st.sidebar.columns(4)

if cm1.button("Load", use_container_width=True):
    if selected_client != "— select a client —":
        data = load_client(selected_client)
        if data:
            for key, val in data.items():
                st.session_state[key] = val
            st.sidebar.success(f"Loaded {selected_client}")
        else:
            st.sidebar.error("Client file not found")
    else:
        st.sidebar.warning("Select a client first")

if cm2.button("Save", use_container_width=True):
    if st.session_state["client_name"].strip() == "" or st.session_state["client_name"] == "New Client":
        st.sidebar.warning("Enter a client name first")
    else:
        save_data = {k: st.session_state[k] for k in defaults.keys()}
        save_client(st.session_state["client_name"], save_data)
        st.sidebar.success(f"Saved {st.session_state['client_name']}")

if cm3.button("New", use_container_width=True):
    for key, val in defaults.items():
        st.session_state[key] = val
    st.sidebar.success("Ready for new client")

if cm4.button("Del", use_container_width=True):
    if selected_client != "— select a client —":
        delete_client(selected_client)
        st.sidebar.success(f"Deleted {selected_client}")
    else:
        st.sidebar.warning("Select a client to delete")

st.sidebar.markdown("---")

# ── Sidebar: Client Inputs ────────────────────────────────────
st.sidebar.header("Client Profile")

client_name = st.sidebar.text_input("Client Name",
    value=st.session_state["client_name"],
    key="client_name")
client_age = st.sidebar.slider("Current Age", 18, 85,
    value=st.session_state["client_age"],
    key="client_age")

st.sidebar.subheader("Business Details")
has_business = st.sidebar.checkbox("Client has a business sale",
    value=st.session_state.get("has_business", True),
    key="has_business")

if has_business:
    proceeds = st.sidebar.number_input("Business Sale Proceeds ($)",
        value=st.session_state["proceeds"], step=50000, min_value=0,
        key="proceeds")
    cost_base = st.sidebar.number_input("Adjusted Cost Base ($)",
        value=st.session_state["cost_base"], step=10000, min_value=0,
        key="cost_base")
    lcge_available = st.sidebar.number_input("Remaining LCGE Room ($)",
        value=st.session_state["lcge_available"],
        min_value=0, max_value=1250000, step=50000,
        key="lcge_available")
else:
    proceeds      = 0
    cost_base     = 0
    lcge_available = 0

st.sidebar.subheader("Retirement Assumptions")
retirement_age = st.sidebar.slider("Target Retirement Age", 18, 85,
    value=st.session_state["retirement_age"],
    key="retirement_age")
life_expectancy = st.sidebar.slider("Life Expectancy", 1, 110,
    value=st.session_state["life_expectancy"],
    key="life_expectancy")
annual_spending = st.sidebar.number_input("Annual Retirement Spending ($)",
    value=st.session_state["annual_spending"], step=5000, min_value=0,
    key="annual_spending")
mean_return = st.sidebar.slider("Expected Portfolio Return (%)", 3.0, 10.0,
    value=st.session_state["mean_return"],
    key="mean_return") / 100
cpp_start_age = st.sidebar.slider("CPP Start Age", 60, 70,
    value=st.session_state["cpp_start_age"],
    key="cpp_start_age")
oas_start_age = st.sidebar.slider("OAS Start Age", 65, 70,
    value=st.session_state["oas_start_age"],
    key="oas_start_age")

st.sidebar.subheader("Current Portfolio Balances")
rrsp_balance_today = st.sidebar.number_input("Current RRSP Balance ($)",
    value=st.session_state["rrsp_balance_today"], step=10000, min_value=0,
    key="rrsp_balance_today")
tfsa_balance_today = st.sidebar.number_input("Current TFSA Balance ($)",
    value=st.session_state["tfsa_balance_today"], step=1000, min_value=0,
    key="tfsa_balance_today")
non_reg_balance_today = st.sidebar.number_input("Current Non-Registered Balance ($)",
    value=st.session_state.get("non_reg_balance_today",0), step=5000, min_value=0,
    key="non_reg_balance_today")
current_tfsa_room = st.sidebar.number_input("Current TFSA Room Available ($)",
    value=st.session_state["current_tfsa_room"],
    min_value=0, max_value=500000, step=1000,
    key="current_tfsa_room")
tfsa_room_for_lump = max(1, int(st.session_state["current_tfsa_room"]))
tfsa_lump_sum_default = min(st.session_state.get("tfsa_lump_sum", 0), tfsa_room_for_lump)

tfsa_lump_sum = st.sidebar.number_input("TFSA Lump Sum Contribution Today ($)",
    value=tfsa_lump_sum_default,
    min_value=0,
    max_value=tfsa_room_for_lump,
    step=1000,
    key="tfsa_lump_sum",
    help="One-time contribution using exisiting unused room - applied immediately today")

st.sidebar.subheader("Annual Contributions (Pre-Retirement)")
annual_rrsp_contrib = st.sidebar.number_input("Annual RRSP Contribution ($)",
    value=st.session_state["annual_rrsp_contrib"], step=1000, min_value=0,
    key="annual_rrsp_contrib")
annual_tfsa_contrib = st.sidebar.number_input("Annual TFSA Contribution ($)",
    value=st.session_state["annual_tfsa_contrib"], step=500, min_value=0,
    key="annual_tfsa_contrib")
employment_income = st.sidebar.number_input("Annual Employment Income ($)",
    value=st.session_state["employment_income"], step=5000, min_value=0,
    key="employment_income")

st.sidebar.subheader("Market Assumptions")
std_return = st.sidebar.slider("Portfolio Volatility / Std Dev (%)", 5.0, 20.0,
    value=st.session_state["std_return"],
    key="std_return") / 100
mean_inflation = st.sidebar.slider("Expected Inflation (%)", 1.0, 5.0,
    value=st.session_state["mean_inflation"],
    key="mean_inflation") / 100
std_inflation = st.sidebar.slider("Inflation Volatility (%)", 0.5, 3.0,
    value=st.session_state["std_inflation"],
    key="std_inflation") / 100
st.sidebar.subheader("Inflation Display")
show_real = st.sidebar.checkbox(
    "Show inflation-adjusted (real) values",
    value=False,
    help="Adjusts all future dollar amounts to today's purchasing power using expected inflation rate"
)

# ── Run All Calculations ──────────────────────────────────────

# Step 1: Business sale tax calculation
taxable_income  = calculate_business_sale(proceeds, cost_base, lcge_available)
federal_tax     = calculate_tax(taxable_income, FEDERAL_BRACKETS)
ontario_tax     = calculate_tax(taxable_income, ONTARIO_BRACKETS)
total_tax       = federal_tax + ontario_tax
net_proceeds    = proceeds - total_tax
years_left      = years_to_goal(client_age, retirement_age)

# Step 2: CPP / OAS amounts at chosen start ages
cpp_monthly     = calculate_cap_monthly(CPP_MAX_AGE_65, cpp_start_age)
oas_monthly     = calculate_oas_monthly(OAS_MAX_AGE_65, oas_start_age)
cpp_annual      = cpp_monthly * 12
oas_annual      = oas_monthly * 12

# Step 3: Cashflow engine — source of truth for all bucket balances
# Runs year-by-year from today through death across all three buckets
# Apply TFSA lump sum — added to balance today, reduces available room
effective_tfsa_balance = tfsa_balance_today + tfsa_lump_sum
effective_tfsa_room    = max(0, current_tfsa_room - tfsa_lump_sum)

cashflow_rows = run_cashflow(
    client_age=client_age,
    retirement_age=retirement_age,
    life_expectancy=life_expectancy,
    employment_income=employment_income,
    annual_rrsp_contrib=annual_rrsp_contrib,
    annual_tfsa_contrib=annual_tfsa_contrib,
    mean_return=mean_return,
    net_proceeds=net_proceeds,
    rrsp_balance_today=rrsp_balance_today,
    cpp_annual=cpp_annual,
    oas_annual=oas_annual,
    cpp_start_age=cpp_start_age,
    oas_start_age=oas_start_age,
    annual_spending=annual_spending,
    current_tfsa_room=effective_tfsa_room,
    tfsa_balance_today=effective_tfsa_balance,
    non_reg_balance_today=non_reg_balance_today,
)

# Step 4: Extract retirement-age balances from cashflow engine
# These feed into meltdown, Monte Carlo, and estate modules
pre_retirement_rows = [r for r in cashflow_rows if r['phase'] == 'pre-retirement']
last_pre_ret        = pre_retirement_rows[-1]
rrsp_at_retirement    = last_pre_ret['rrsp_balance']
tfsa_at_retirement    = last_pre_ret['tfsa_balance']
non_reg_at_retirement = last_pre_ret['non_reg_balance']
portfolio_start       = rrsp_at_retirement + tfsa_at_retirement + non_reg_at_retirement
import streamlit as st

# Step 5: RRSP meltdown — uses cashflow-derived RRSP balance at retirement
# Dynamic meltdown target — one bracket above employment income
if employment_income < 58523:
    meltdown_target = 58523
elif employment_income < 117045:
    meltdown_target = 117045
else:
    meltdown_target = 117045

# Other income during meltdown = only gov benefits that have started by retirement
meltdown_other_income = 0
if cpp_start_age <= retirement_age:
    meltdown_other_income += cpp_annual
if oas_start_age <= retirement_age:
    meltdown_other_income += oas_annual

if retirement_age <= 71:
    rrsp_results = rrsp_meltdown(
        rrsp_balance=rrsp_at_retirement,
        start_age=retirement_age,
        end_age=71,
        other_income=meltdown_other_income,
        annual_return=mean_return,
        target_income=meltdown_target,
        current_tfsa_room=effective_tfsa_room,
        years_to_retirement=(71 - client_age),
        annual_new_tfsa_room=7000
    )
else:
    rrsp_results = []

if rrsp_results:
    rrsp_df       = pd.DataFrame(rrsp_results)
    final_tfsa    = rrsp_df['tfsa_accumulated'].iloc[-1]
    final_rrsp    = rrsp_df['rrsp_balance'].iloc[-1]
    final_non_reg = rrsp_df['non_reg_accumulated'].iloc[-1]
else:
    rrsp_df       = pd.DataFrame()
    final_tfsa    = 0
    final_rrsp    = rrsp_at_retirement
    final_non_reg = 0

# Step 6: Monte Carlo — uses total portfolio at retirement
mc_results = run_monte_carlo(
    portfolio_value=portfolio_start,
    annual_spending=annual_spending,
    cpp_annual=cpp_annual,
    oas_annual=oas_annual,
    cpp_start_age=cpp_start_age,
    oas_start_age=oas_start_age,
    retirement_age=retirement_age,
    life_expectancy=life_expectancy,
    mean_return=mean_return,
    std_return=std_return,
    mean_inflation=mean_inflation,
    std_inflation=std_inflation
)

# Step 7: RRSP meltdown summary variables
if rrsp_results:
    rrsp_df       = pd.DataFrame(rrsp_results)
    final_tfsa    = rrsp_df['tfsa_accumulated'].iloc[-1]
    final_rrsp    = rrsp_df['rrsp_balance'].iloc[-1]
    final_non_reg = rrsp_df['non_reg_accumulated'].iloc[-1]
else:
    rrsp_df       = pd.DataFrame()
    final_tfsa    = 0
    final_rrsp    = rrsp_at_retirement
    final_non_reg = 0

# Step 8: Estate projection — uses cashflow-derived balances
last_cf_row = cashflow_rows[-1]

estate_results = calculate_estate(
    portfolio_value=last_cf_row['non_reg_balance'],
    rrsp_remaining=last_cf_row['rrsp_balance'],
    tfsa_value=last_cf_row['tfsa_balance'],
    death_age=life_expectancy,
    retirement_age=retirement_age,
    annual_return=mean_return,
    annual_spending=annual_spending,
    cpp_annual=cpp_annual,
    oas_annual=oas_annual
)

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📋 Overview",
    "📅 Lifetime Projection", 
    "🏦 Retirement Strategy",
    "📈 CPP & OAS",
    "📊 Monte Carlo",
    "🏛️ Estate Planning",
    "⚖️ Scenario Comparison"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
with tab1:
    st.header(f"{'Business Sale Analysis' if has_business else 'Financial Overview'} — {client_name}")

    if has_business:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Gross Proceeds", f"${proceeds:,.0f}")
        col2.metric("Total Tax Owing", f"${total_tax:,.0f}")
        col3.metric("Net After-Tax Proceeds", f"${net_proceeds:,.0f}")
        col4.metric("LCGE Applied", f"${lcge_available:,.0f}")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Employment Income (Annual)", f"${employment_income:,.0f}")
        col2.metric("Projected Portfolio at Retirement", f"${portfolio_start:,.0f}")
        col3.metric("Years to Retirement", f"{years_left} years")

    if has_business:
        col5, col6, col7 = st.columns(3)
        col5.metric("Years to Retirement", f"{years_left} years")
        col6.metric("Projected Portfolio at Retirement", f"${portfolio_start:,.0f}")
        effective_tax_rate = round((total_tax / proceeds) * 100, 1) if proceeds > 0 else 0
        col7.metric("Effective Tax Rate on Sale", f"{effective_tax_rate}%")

    st.markdown("<hr>", unsafe_allow_html=True)

    if has_business:
        st.subheader("Where Does the Money Go?")
        fig_overview = go.Figure()
        fig_overview.add_trace(go.Bar(
            x=["Business Sale Proceeds", "Tax Owing (CRA)", "Net After-Tax Proceeds", "Portfolio at Retirement"],
            y=[proceeds, total_tax, net_proceeds, portfolio_start],
            marker_color=["#C9A84C", "#FF6B6B", "#2DD4A0", "#C9A84C"],
            text=[f"${proceeds:,.0f}", f"${total_tax:,.0f}", f"${net_proceeds:,.0f}", f"${portfolio_start:,.0f}"],
            textposition="outside",
            textfont=dict(color="#F0F4FF", size=12)
        ))
        fig_overview.update_layout(
            title="From Business Sale to Retirement Portfolio",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#F0F4FF',
            height=450,
            showlegend=False,
            yaxis=dict(tickformat="$,.0f", gridcolor="rgba(201,168,76,0.1)"),
            bargap=0.4
        )
        st.plotly_chart(fig_overview, width='stretch')
   
    else:
        st.subheader("Portfolio Growth Projection")
        st.caption("No business sale - portfolio built entirely from employment income and contributions")

        total_today = rrsp_balance_today + tfsa_balance_today + non_reg_balance_today

        categories = ['RRSP / RRIF', 'TFSA', 'Non-Registered', 'Total Portfolio']
        today_values      = [rrsp_balance_today, tfsa_balance_today, non_reg_balance_today, total_today]
        retirement_values = [rrsp_at_retirement, tfsa_at_retirement, non_reg_at_retirement, portfolio_start]

        fig_overview = go.Figure()

        fig_overview.add_trace(go.Bar(
            name='Today',
            x=categories,
            y=today_values,
            marker_color='rgba(139,163,199,0.7)',
            text=[f"${v:,.0f}" for v in today_values],
            textposition='outside',
            textfont=dict(color='#F0F4FF', size=11),
            width=0.35
        ))

        fig_overview.add_trace(go.Bar(
            name='At Retirement',
            x=categories,
            y=retirement_values,
            marker_color=['#e74c3c', '#2DD4A0', '#C9A84C', '#4A90D9'],
            text=[f"${v:,.0f}" for v in retirement_values],
            textposition='outside',
            textfont=dict(color='#F0F4FF', size=11),
            width=0.35
        ))

        fig_overview.update_layout(
            title=f"Portfolio Today vs At Retirement (Age {retirement_age}) — By Bucket",
            barmode='group',
            bargroupgap=0.15,
            bargap=0.3,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#F0F4FF',
            height=500,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            yaxis=dict(
                tickformat='$,.0f',
                gridcolor='rgba(201,168,76,0.1)'
            ),
            xaxis=dict(
                tickfont=dict(size=13)
            )
        )
        st.plotly_chart(fig_overview, width='stretch')

# ══════════════════════════════════════════════════════════════
# TAB 2 — LIFETIME PROJECTION
# ══════════════════════════════════════════════════════════════
with tab2:
    st.header("Lifetime Financial Projection")
    st.caption("5-year snapshots from today through life expectancy across all three buckets")

    cf_df = pd.DataFrame(cashflow_rows)

    # Build inflation adjustment factors per period
    # Each period is 5 years — cumulative inflation compounds
    if show_real:
        inflation_factors = []
        cumulative_years = 0
        for r in cashflow_rows:
            # Extract years in this period from the period label
            period_years = 5  # all periods are 5 years
            cumulative_years += period_years
            factor = (1 + mean_inflation) ** cumulative_years
            inflation_factors.append(factor)

        cf_df['rrsp_balance_display']    = cf_df['rrsp_balance']    / inflation_factors
        cf_df['tfsa_balance_display']    = cf_df['tfsa_balance']    / inflation_factors
        cf_df['non_reg_balance_display'] = cf_df['non_reg_balance'] / inflation_factors
        cf_df['total_net_worth_display'] = cf_df['total_net_worth'] / inflation_factors
        display_label = f"Real Values (today's $, {mean_inflation*100:.1f}% inflation)"
    else:
        cf_df['rrsp_balance_display']    = cf_df['rrsp_balance']
        cf_df['tfsa_balance_display']    = cf_df['tfsa_balance']
        cf_df['non_reg_balance_display'] = cf_df['non_reg_balance']
        cf_df['total_net_worth_display'] = cf_df['total_net_worth']
        display_label = "Nominal Values"

    fig_nw = go.Figure()
    fig_nw.add_trace(go.Bar(x=cf_df['period'], y=cf_df['rrsp_balance_display'],
        name='RRSP / RRIF', marker_color='#e74c3c'))
    fig_nw.add_trace(go.Bar(x=cf_df['period'], y=cf_df['tfsa_balance_display'],
        name='TFSA (tax-free)', marker_color='#2DD4A0'))
    fig_nw.add_trace(go.Bar(x=cf_df['period'], y=cf_df['non_reg_balance_display'],
        name='Non-Registered', marker_color='#C9A84C'))
    fig_nw.update_layout(
        title=f"Projected Net Worth by Bucket — {display_label}",
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#F0F4FF',
        xaxis_title="Period",
        yaxis_title="Balance ($)",
        height=500,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    st.plotly_chart(fig_nw, width='stretch')

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Effective Tax Rate — Lifetime View")
    st.caption("Tax paid as a percentage of total income each period")

    tax_rate_rows = []
    for r in cashflow_rows:
        # Calculate total income for this period
        total_income = (
            r['employment_income'] +
            r['cpp_income'] +
            r['oas_income'] +
            r['rrsp_withdrawal']
        )
        # Non-reg withdrawal: only taxable portion (25% as per cashflow assumption)
        total_income += r['non_reg_withdrawal'] * 0.25

        effective_rate = round((r['tax_owing'] / total_income) * 100, 1) if total_income > 0 else 0

        tax_rate_rows.append({
            'period':         r['period'],
            'phase':          r['phase'],
            'effective_rate': effective_rate,
            'tax_owing':      r['tax_owing'],
            'total_income':   round(total_income)
        })

    tax_df = pd.DataFrame(tax_rate_rows)

    fig_tax = go.Figure()

    # Shade background by phase
    retirement_periods = tax_df[tax_df['phase'] == 'retirement']['period'].tolist()
    if retirement_periods:
        fig_tax.add_vrect(
            x0=retirement_periods[0],
            x1=retirement_periods[-1],
            fillcolor='rgba(201,168,76,0.05)',
            layer='below',
            line_width=0
        )

    # Effective rate line
    fig_tax.add_trace(go.Scatter(
        x=tax_df['period'],
        y=tax_df['effective_rate'],
        mode='lines+markers',
        name='Effective Tax Rate',
        line=dict(color='#C9A84C', width=2.5),
        marker=dict(size=7),
        hovertemplate='%{x}<br>Effective Rate: %{y}%<br><extra></extra>'
    ))

    # Zero line reference
    fig_tax.add_hline(
        y=0,
        line_dash='dot',
        line_color='rgba(139,163,199,0.3)'
    )

    # Annotate retirement start
    if retirement_periods:
        fig_tax.add_annotation(
            x=retirement_periods[0],
            y=tax_df[tax_df['phase'] == 'retirement']['effective_rate'].iloc[0],
            text="Retirement →",
            showarrow=True,
            arrowhead=2,
            arrowcolor='#8BA3C7',
            font=dict(color='#8BA3C7', size=11),
            ax=60,
            ay=-30
        )

    fig_tax.update_layout(
        title='Effective Tax Rate by Period',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#F0F4FF',
        height=400,
        xaxis_title='Period',
        yaxis=dict(
            title='Effective Rate (%)',
            ticksuffix='%',
            gridcolor='rgba(201,168,76,0.1)'
        ),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    st.plotly_chart(fig_tax, width='stretch')

    st.subheader("Period-by-Period Breakdown")
    display_rows = []
    for i,r in enumerate(cashflow_rows):
        display_rows.append({
            'Period':           r['period'],
            'Phase':            r['phase'].replace('-', ' ').title(),
            'Employment ($)':   f"${r['employment_income']:,}" if r['employment_income'] > 0 else '—',
            'CPP ($)':          f"${r['cpp_income']:,}" if r['cpp_income'] > 0 else '—',
            'OAS ($)':          f"${r['oas_income']:,}" if r['oas_income'] > 0 else '—',
            'RRSP W/D ($)':     f"${r['rrsp_withdrawal']:,}" if r['rrsp_withdrawal'] > 0 else '—',
            'Non-Reg W/D ($)':  f"${r['non_reg_withdrawal']:,}" if r['non_reg_withdrawal'] > 0 else '—',
            'TFSA W/D ($)':     f"${r['tfsa_withdrawal']:,}" if r['tfsa_withdrawal'] > 0 else '—',
            'Tax Owing ($)':    f"${r['tax_owing']:,}",
            'RRSP Bal ($)':     f"${r['rrsp_balance']:,}",
            'TFSA Bal ($)':     f"${r['tfsa_balance']:,}",
            'Non-Reg Bal ($)':  f"${r['non_reg_balance']:,}",
            'Net Worth ($)':    f"${r['total_net_worth']:,}",
            'Real Net Worth ($)':  f"${round(r['total_net_worth'] / inflation_factors[i]):,}" if show_real else "—",
        })
    display_df = pd.DataFrame(display_rows)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — RETIREMENT STRATEGY
# ══════════════════════════════════════════════════════════════
with tab3:
    st.header("RRSP Meltdown Strategy")

    if rrsp_df.empty:
        st.info("No RRSP meltdown window available — retirement starts after age 71. "
                "RRIF mandatory withdrawals apply immediately.")
    else:

        final_non_reg = rrsp_df['non_reg_accumulated'].iloc[-1]
        col8, col9, col9b = st.columns(3)
        col8.metric("TFSA Accumulated (tax-free)", f"${final_tfsa:,.0f}")
        col9.metric("Non-Registered Overflow", f"${final_non_reg:,.0f}")
        col9b.metric("Remaining RRSP Balance", f"${final_rrsp:,.0f}")

        fig_rrsp = go.Figure()
        fig_rrsp.add_trace(go.Bar(x=rrsp_df['age'], y=rrsp_df['rrsp_balance'],
            name='RRSP Balance', marker_color='#e74c3c'))
        fig_rrsp.add_trace(go.Bar(x=rrsp_df['age'], y=rrsp_df['tfsa_accumulated'],
            name='TFSA Accumulated', marker_color='#2DD4A0'))
        fig_rrsp.add_trace(go.Bar(x=rrsp_df['age'], y=rrsp_df['non_reg_accumulated'],
            name='Non-Registered Overflow', marker_color='#C9A84C'))
        fig_rrsp.update_layout(
            title="RRSP Drawdown vs TFSA Growth",
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#F0F4FF',
            xaxis_title="Age",
            yaxis_title="Balance ($)",
            height=400
        )
        st.plotly_chart(fig_rrsp, width='stretch')

        st.markdown("<hr>", unsafe_allow_html=True)
        st.header("CPP & OAS Summary")

        col10, col11, col12 = st.columns(3)
        col10.metric("Monthly CPP", f"${cpp_monthly:,.2f}", f"Starting age {cpp_start_age}")
        col11.metric("Monthly OAS", f"${oas_monthly:,.2f}", f"Starting age {oas_start_age}")
        col12.metric("Combined Annual Gov't Income", f"${cpp_annual + oas_annual:,.0f}")
        
# ══════════════════════════════════════════════════════════════
# TAB 4 — CPP & OAS
# ══════════════════════════════════════════════════════════════
with tab4:
    st.header("CPP & OAS Optimizer")

    from cpp_oas_module import calculate_breakdown

    # OAS clawback calculation — runs before tabs render
    OAS_CLAWBACK_THRESHOLD = 95323
    OAS_FULL_CLAWBACK = 154906

    # OAS clawback uses net world income — all taxable sources
    # In retirement year 1: CPP + OAS + RRIF minimum (if 71+) + non-reg taxable portion
    rrif_income = 0
    if retirement_age >= 71 and rrsp_at_retirement > 0:
        rrif_income = rrsp_at_retirement * 0.0528

    # Non-reg: 25% of balance assumed taxable (50% gain, 50% inclusion rate)
    non_reg_taxable = non_reg_at_retirement * 0.25 if non_reg_at_retirement > 0 else 0

    # RRSP meltdown withdrawal if pre-71
    meltdown_income = 0
    if retirement_age < 71 and rrsp_at_retirement > 0:
        meltdown_income = max(0, meltdown_target - meltdown_other_income)

    estimated_retirement_income = (
        cpp_annual +
        oas_annual +
        rrif_income +
        non_reg_taxable +
        meltdown_income
    )

    if estimated_retirement_income > OAS_FULL_CLAWBACK:
        net_oas = 0
    elif estimated_retirement_income > OAS_CLAWBACK_THRESHOLD:
        clawback_amount = (estimated_retirement_income - OAS_CLAWBACK_THRESHOLD) * 0.15
        clawback_amount = min(clawback_amount, oas_annual)
        net_oas = max(0, oas_annual - clawback_amount)
    else:
        net_oas = oas_annual

    col10, col11, col12 = st.columns(3)
    col10.metric("Monthly CPP", f"${cpp_monthly:,.2f}", f"Starting age {cpp_start_age}")
    col11.metric("Monthly OAS", f"${oas_monthly:,.2f}", f"Starting age {oas_start_age}")
    col12.metric("Combined Annual Gov't Income", f"${cpp_annual + oas_annual:,.0f}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("CPP Start Age Comparison")
    st.caption("Monthly benefit and breakeven age vs chosen start age across all options 60–70")

    cpp_rows = []
    for age in range(60, 71):
        monthly = calculate_cap_monthly(CPP_MAX_AGE_65, age)
        annual  = monthly * 12

        if age < cpp_start_age:
            bd = calculate_breakdown(CPP_MAX_AGE_65, age, cpp_start_age)
            breakeven_note = f"Age {bd['breakeven_age']}" if bd['breakeven_age'] else "Never"
            vs_label = f"vs chosen age {cpp_start_age}"
        elif age > cpp_start_age:
            bd = calculate_breakdown(CPP_MAX_AGE_65, cpp_start_age, age)
            breakeven_note = f"Age {bd['breakeven_age']}" if bd['breakeven_age'] else "Never"
            vs_label = f"vs chosen age {cpp_start_age}"
        else:
            breakeven_note = "— (chosen age)"
            vs_label = ""

        cpp_rows.append({
            'Start Age':       age,
            'Monthly CPP ($)': f"${monthly:,.2f}",
            'Annual CPP ($)':  f"${annual:,.0f}",
            'Breakeven':       breakeven_note,
            'Comparison':      vs_label
        })
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("OAS Clawback Analysis")

    if estimated_retirement_income > OAS_FULL_CLAWBACK:
        st.markdown(
            f"""<div style='background-color: rgba(255,107,107,0.15); 
            border: 1px solid #FF6B6B; border-radius: 8px; padding: 16px; color: #FF6B6B;'>
            🚨 <strong>Full OAS Clawback</strong> — Estimated retirement income of 
            <strong>${estimated_retirement_income:,.0f}</strong> exceeds the full clawback 
            threshold of <strong>${OAS_FULL_CLAWBACK:,.0f}</strong>. 
            Client receives <strong>$0</strong> in OAS benefits.
            </div>""",
            unsafe_allow_html=True
        )

    elif estimated_retirement_income > OAS_CLAWBACK_THRESHOLD:
        clawback_display = min((estimated_retirement_income - OAS_CLAWBACK_THRESHOLD) * 0.15, oas_annual)
        st.markdown(
            f"""<div style='background-color: rgba(244,162,97,0.15); 
            border: 1px solid #F4A261; border-radius: 8px; padding: 16px; color: #F4A261;'>
            ⚠️ <strong>Partial OAS Clawback</strong> — Estimated retirement income of 
            <strong>${estimated_retirement_income:,.0f}</strong> exceeds the 
            <strong>${OAS_CLAWBACK_THRESHOLD:,.0f}</strong> threshold. 
            Estimated clawback: <strong>${clawback_display:,.0f}/year</strong>. 
            Net OAS received: <strong>${net_oas:,.0f}/year</strong>.
            </div>""",
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            f"""<div style='background-color: rgba(45,212,160,0.15); 
            border: 1px solid #2DD4A0; border-radius: 8px; padding: 16px; color: #2DD4A0;'>
            ✅ <strong>No OAS Clawback</strong> — Estimated retirement income of 
            <strong>${estimated_retirement_income:,.0f}</strong> is below the 
            <strong>${OAS_CLAWBACK_THRESHOLD:,.0f}</strong> threshold. 
            Full OAS of <strong>${oas_annual:,.0f}/year</strong> retained.
            </div>""",
            unsafe_allow_html=True
        )

    col_oas1, col_oas2, col_oas3 = st.columns(3)
    col_oas1.metric("Estimated Retirement Income", f"${estimated_retirement_income:,.0f}")
    col_oas2.metric("OAS Clawback Threshold", f"${OAS_CLAWBACK_THRESHOLD:,.0f}")
    col_oas3.metric("Net OAS After Clawback", f"${net_oas:,.0f}")

    cpp_table = pd.DataFrame(cpp_rows)

    def highlight_chosen(row):
        if str(row['Start Age']) == str(cpp_start_age):
            return ['background-color: rgba(201,168,76,0.2)'] * len(row)
        return [''] * len(row)

    st.dataframe(
        cpp_table.style.apply(highlight_chosen, axis=1),
        use_container_width=True,
        hide_index=True
    )

    if cpp_start_age < 70:
        bd_vs_70 = calculate_breakdown(CPP_MAX_AGE_65, cpp_start_age, 70)
        if bd_vs_70['breakeven_age'] and bd_vs_70['breakeven_age'] < life_expectancy:
            st.warning(f"⚠️ Delaying CPP to age 70 breaks even at age {bd_vs_70['breakeven_age']}. "
                      f"Given life expectancy of {life_expectancy}, delaying would yield "
                      f"${(bd_vs_70['late_monthly'] - bd_vs_70['early_monthly']) * 12 * (life_expectancy - bd_vs_70['breakeven_age']):,.0f} "
                      f"more in total CPP income.")
        else:
            st.info(f"At life expectancy {life_expectancy}, delaying CPP to 70 does not break even.")

# ══════════════════════════════════════════════════════════════
# TAB 5 — MONTE CARLO
# ══════════════════════════════════════════════════════════════
with tab5:
    st.header("Monte Carlo Retirement Simulation")

    success = mc_results['probability_of_success']
    color = "#2DD4A0" if success >= 90 else "#F4A261" if success >= 75 else "#FF6B6B"

    st.markdown(f"""
    <div style='text-align:center; padding:30px 0;'>
        <div style='font-family:"Playfair Display",serif; font-size:3.5rem; color:{color}; font-weight:700; line-height:1;'>
            {success}%
        </div>
        <div style='color:#8BA3C7; font-size:0.85rem; letter-spacing:0.1em; text-transform:uppercase; margin-top:8px;'>
            Probability of Success
        </div>
        <div style='color:#8BA3C7; font-size:0.8rem; margin-top:4px;'>
            {mc_results['success_count']} of {mc_results['total_scenarios']} scenarios fully funded to age {life_expectancy}
        </div>
    </div>
    """, unsafe_allow_html=True)

    years_axis = mc_results['years']
    fig_mc = go.Figure()
    fig_mc.add_trace(go.Scatter(x=years_axis, y=mc_results['percentiles']['p90'],
        fill=None, line=dict(color='rgba(45,212,160,0.3)'), name='90th percentile'))
    fig_mc.add_trace(go.Scatter(x=years_axis, y=mc_results['percentiles']['p75'],
        fill='tonexty', line=dict(color='rgba(45,212,160,0.5)'), name='75th percentile'))
    fig_mc.add_trace(go.Scatter(x=years_axis, y=mc_results['percentiles']['p50'],
        fill='tonexty', line=dict(color='#C9A84C', width=2), name='Median'))
    fig_mc.add_trace(go.Scatter(x=years_axis, y=mc_results['percentiles']['p25'],
        fill='tonexty', line=dict(color='rgba(255,107,107,0.5)'), name='25th percentile'))
    fig_mc.add_trace(go.Scatter(x=years_axis, y=mc_results['percentiles']['p10'],
        fill='tonexty', line=dict(color='rgba(255,107,107,0.3)'), name='10th percentile'))
    fig_mc.update_layout(
        title=f"Portfolio Projection — 1,000 Scenarios",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#F0F4FF',
        xaxis_title="Age",
        yaxis_title="Portfolio Value ($)",
        height=500
    )
    st.plotly_chart(fig_mc, width='stretch')

    col13, col14, col15 = st.columns(3)
    col13.metric("Median Portfolio at Death", f"${mc_results['percentiles']['p50'][-1]:,.0f}")
    col14.metric("Best 10% at Death", f"${mc_results['percentiles']['p90'][-1]:,.0f}")
    col15.metric("Worst 10% at Death", f"${mc_results['percentiles']['p10'][-1]:,.0f}")

# ══════════════════════════════════════════════════════════════
# TAB 6 — ESTATE PLANNING
# ══════════════════════════════════════════════════════════════
with tab6:
    st.header(f"Estate Projection at Death — Age {life_expectancy}")

    col16, col17, col18 = st.columns(3)
    col16.metric("Gross Estate", f"${estate_results['gross_estate']:,.0f}")
    col17.metric("Total Tax at Death", f"${estate_results['total_tax_at_death']:,.0f}")
    col18.metric("Net Estate to Heirs", f"${estate_results['net_estate']:,.0f}")

    col19, col20, col21 = st.columns(3)
    col19.metric("Projected Portfolio", f"${estate_results['projected_portfolio']:,.0f}")
    col20.metric("TFSA to Heirs (tax-free)", f"${estate_results['tfsa_to_heirs']:,.0f}")
    col21.metric("Tax on RRSP at Death", f"${estate_results['rrsp_tax']:,.0f}")

    fig_estate = go.Figure(go.Pie(
        labels=["Portfolio to Heirs (after tax)", "TFSA to Heirs (tax-free)",
                "RRSP Net to Heirs (after tax)", "Tax Paid at Death"],
        values=[
            estate_results['projected_portfolio'] - estate_results['portfolio_tax'],
            estate_results['tfsa_to_heirs'],
            estate_results['rrsp_remaining'] - estate_results['rrsp_tax'],
            estate_results['total_tax_at_death']
        ],
        marker_colors=["#2980b9", "#2DD4A0", "#8e44ad", "#FF6B6B"],
        hole=0.4
    ))
    fig_estate.update_layout(
        title=f"Estate Composition at Age {life_expectancy} — What Goes Where",
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#F0F4FF',
        height=450
    )
    st.plotly_chart(fig_estate, width='stretch')

# ══════════════════════════════════════════════════════════════
# TAB 7 — SCENARIO COMPARISON
# ══════════════════════════════════════════════════════════════
with tab7:
    st.header("Scenario Comparison")
    st.caption("Compare your base plan against an alternate set of assumptions")

    # Quick-select buttons
    st.subheader("Quick Scenarios")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    scenario_preset = None
    if col_s1.button("🕐 Early Retirement"):
        scenario_preset = "early"
    if col_s2.button("📉 Conservative Market"):
        scenario_preset = "conservative"
    if col_s3.button("📈 Aggressive Growth"):
        scenario_preset = "aggressive"
    if col_s4.button("💸 Higher Spending"):
        scenario_preset = "spending"

    # Scenario inputs
    st.subheader("Custom Scenario Inputs")
    sc1, sc2, sc3 = st.columns(3)

    default_ret = retirement_age - 5 if scenario_preset == "early" else retirement_age
    default_ret_return = 0.04 if scenario_preset == "conservative" else (0.08 if scenario_preset == "aggressive" else mean_return)
    default_spending = annual_spending * 1.25 if scenario_preset == "spending" else annual_spending

    s_retirement_age  = sc1.slider("Scenario Retirement Age", 50, 70, default_ret)
    s_mean_return     = sc2.slider("Scenario Portfolio Return (%)", 2.0, 12.0, round(default_ret_return*100,1)) / 100
    s_annual_spending = sc3.number_input("Scenario Annual Spending ($)", value=int(default_spending), step=5000)

    # Run scenario calculations
    s_years_left = years_to_goal(client_age, s_retirement_age)

    s_cashflow_rows = run_cashflow(
        client_age=client_age,
        retirement_age=s_retirement_age,
        life_expectancy=life_expectancy,
        employment_income=employment_income,
        annual_rrsp_contrib=annual_rrsp_contrib,
        annual_tfsa_contrib=annual_tfsa_contrib,
        mean_return=s_mean_return,
        net_proceeds=net_proceeds,
        rrsp_balance_today=rrsp_balance_today,
        cpp_annual=cpp_annual,
        oas_annual=oas_annual,
        cpp_start_age=cpp_start_age,
        oas_start_age=oas_start_age,
        annual_spending=s_annual_spending,
        current_tfsa_room=current_tfsa_room,
        tfsa_balance_today=tfsa_balance_today,
    )

    s_retirement_row = next(r for r in s_cashflow_rows if r['phase'] == 'retirement')
    s_portfolio_start = s_retirement_row['rrsp_balance'] + s_retirement_row['tfsa_balance'] + s_retirement_row['non_reg_balance']

    s_mc_results = run_monte_carlo(
        portfolio_value=s_portfolio_start,
        annual_spending=s_annual_spending,
        cpp_annual=cpp_annual,
        oas_annual=oas_annual,
        cpp_start_age=cpp_start_age,
        oas_start_age=oas_start_age,
        retirement_age=s_retirement_age,
        life_expectancy=life_expectancy,
        mean_return=s_mean_return,
        std_return=std_return,
        mean_inflation=mean_inflation,
        std_inflation=std_inflation
    )

    # Side-by-side comparison
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Side-by-Side Results")

    b1, b2, b3 = st.columns(3)
    b1.metric("Base — Portfolio at Retirement", f"${portfolio_start:,.0f}")
    b2.metric("Scenario — Portfolio at Retirement", f"${s_portfolio_start:,.0f}",
        delta=f"${s_portfolio_start - portfolio_start:,.0f}")
    b3.metric("Difference", f"${abs(s_portfolio_start - portfolio_start):,.0f}",
        delta="Scenario better" if s_portfolio_start > portfolio_start else "Base better")

    b4, b5, b6 = st.columns(3)
    b4.metric("Base — Success Rate", f"{mc_results['probability_of_success']}%")
    b5.metric("Scenario — Success Rate", f"{s_mc_results['probability_of_success']}%",
        delta=f"{round(s_mc_results['probability_of_success'] - mc_results['probability_of_success'],1)}%")
    b6.metric("Base Retirement Age", f"{retirement_age}",
        delta=f"Scenario: {s_retirement_age}")

    # Overlay Monte Carlo chart
    s_years_axis = s_mc_results['years']
    fig_compare = go.Figure()

    # Base plan median
    fig_compare.add_trace(go.Scatter(
        x=years_axis, y=mc_results['percentiles']['p50'],
        line=dict(color='#C9A84C', width=2.5, dash='solid'),
        name='Base — Median'
    ))
    fig_compare.add_trace(go.Scatter(
        x=years_axis, y=mc_results['percentiles']['p10'],
        fill=None, line=dict(color='rgba(201,168,76,0.0)'), name='Base — 10th pct',
        showlegend=False
    ))
    fig_compare.add_trace(go.Scatter(
        x=years_axis, y=mc_results['percentiles']['p90'],
        fill='tonexty', line=dict(color='rgba(201,168,76,0.0)'), name='Base — Range',
        fillcolor='rgba(201,168,76,0.15)'
    ))

    # Scenario median
    fig_compare.add_trace(go.Scatter(
        x=s_years_axis, y=s_mc_results['percentiles']['p50'],
        line=dict(color='#2DD4A0', width=2.5, dash='solid'),
        name='Scenario — Median'
    ))
    fig_compare.add_trace(go.Scatter(
        x=s_years_axis, y=s_mc_results['percentiles']['p10'],
        fill=None, line=dict(color='rgba(45,212,160,0.0)'), name='Scenario — 10th pct',
        showlegend=False
    ))
    fig_compare.add_trace(go.Scatter(
        x=s_years_axis, y=s_mc_results['percentiles']['p90'],
        fill='tonexty', line=dict(color='rgba(45,212,160,0.0)'), name='Scenario — Range',
        fillcolor='rgba(45,212,160,0.15)'
    ))

    fig_compare.update_layout(
        title="Base Plan vs Scenario — Portfolio Projection Overlay",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#F0F4FF',
        xaxis_title="Age",
        yaxis_title="Portfolio Value ($)",
        height=500
    )
    st.plotly_chart(fig_compare, width='stretch')

st.caption("This tool is for financial planning illustration purposes only. Not investment advice.")