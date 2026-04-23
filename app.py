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

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Wealth Transition Planner",
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
<h1>Canadian Business Owner<br>Wealth Transition Planner</h1>
<p style='color:#8BA3C7; font-size:0.85rem; letter-spacing:0.05em; margin-top:-8px;'>
    ONTARIO · 2026 TAX YEAR · CRA VERIFIED
</p>
<hr>
""", unsafe_allow_html=True)

# ── Sidebar: Client Inputs ────────────────────────────────────
st.sidebar.header("Client Profile")

client_name = st.sidebar.text_input("Client Name", value="David Chen")
client_age  = st.sidebar.slider("Current Age", 35, 65, 45)

st.sidebar.subheader("Business Details")
proceeds           = st.sidebar.number_input("Business Sale Proceeds ($)", value=3500000, step=50000)
cost_base          = st.sidebar.number_input("Adjusted Cost Base ($)", value=500000, step=10000)
lcge_available     = st.sidebar.number_input(
    "Remaining LCGE Room ($)", 
    value = 1250000,
    min_value = 0,
    max_value = 1250000,
    step = 50000)

st.sidebar.subheader("Retirement Assumptions")
retirement_age   = st.sidebar.slider("Target Retirement Age", 55, 70, 60)
life_expectancy  = st.sidebar.slider("Life Expectancy", 75, 100, 90)
annual_spending  = st.sidebar.number_input("Annual Retirement Spending ($)", value=120000, step=5000)
mean_return      = st.sidebar.slider("Expected Portfolio Return (%)", 3.0, 10.0, 6.0) / 100
cpp_start_age    = st.sidebar.slider("CPP Start Age", 60, 70, 70)
oas_start_age    = st.sidebar.slider("OAS Start Age", 65, 70, 65)

st.sidebar.subheader("Current Portfolio Balances")
rrsp_balance_today  = st.sidebar.number_input("Current RRSP Balance ($)", value=800000, step=10000)
tfsa_balance_today  = st.sidebar.number_input("Current TFSA Balance ($)", value=0, step=1000)
current_tfsa_room   = st.sidebar.number_input("Current TFSA Room Available ($)", value=109000, min_value=0, max_value=500000, step=1000)

st.sidebar.subheader("Annual Contributions (Pre-Retirement)")
annual_rrsp_contrib = st.sidebar.number_input("Annual RRSP Contribution ($)", value=18000, step=1000)
annual_tfsa_contrib = st.sidebar.number_input("Annual TFSA Contribution ($)", value=7000, step=500)
employment_income   = st.sidebar.number_input("Annual Employment Income ($)", value=80000, step=5000)

st.sidebar.subheader("Market Assumptions")
std_return          = st.sidebar.slider("Portfolio Volatility / Std Dev (%)", 5.0, 20.0, 12.0) / 100
mean_inflation      = st.sidebar.slider("Expected Inflation (%)", 1.0, 5.0, 2.5) / 100
std_inflation       = st.sidebar.slider("Inflation Volatility (%)", 0.5, 3.0, 1.0) / 100

# ── Run All Calculations ──────────────────────────────────────

# Step 1: Business sale tax calculation
taxable_income  = calculate_business_sale(proceeds, cost_base, lcge_available, 0)
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
    current_tfsa_room=current_tfsa_room,
    tfsa_balance_today=tfsa_balance_today,
)

# Step 4: Extract retirement-age balances from cashflow engine
# These feed into meltdown, Monte Carlo, and estate modules
retirement_row      = next(r for r in cashflow_rows if r['phase'] == 'retirement')
rrsp_at_retirement  = retirement_row['rrsp_balance']
tfsa_at_retirement  = retirement_row['tfsa_balance']
non_reg_at_retirement = retirement_row['non_reg_balance']
portfolio_start     = rrsp_at_retirement + tfsa_at_retirement + non_reg_at_retirement

# Step 5: RRSP meltdown — uses cashflow-derived RRSP balance at retirement
# target_income = top of 2nd federal bracket (fill lower brackets deliberately)
rrsp_results = rrsp_meltdown(
    rrsp_balance=rrsp_at_retirement,
    start_age=retirement_age,
    end_age=71,
    other_income=30000,
    annual_return=mean_return,
    target_income=117045,
    current_tfsa_room=current_tfsa_room,
    years_to_retirement=(71 - client_age),
    annual_new_tfsa_room=7000
)

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
rrsp_df       = pd.DataFrame(rrsp_results)
final_tfsa    = rrsp_df['tfsa_accumulated'].iloc[-1]
final_rrsp    = rrsp_df['rrsp_balance'].iloc[-1]
final_non_reg = rrsp_df['non_reg_accumulated'].iloc[-1]

# Step 8: Estate projection — uses cashflow-derived balances
estate_results = calculate_estate(
    portfolio_value=non_reg_at_retirement,
    rrsp_remaining=final_rrsp,
    tfsa_value=tfsa_at_retirement + final_tfsa,
    death_age=life_expectancy,
    retirement_age=retirement_age,
    annual_return=mean_return,
    annual_spending=annual_spending,
    cpp_annual=cpp_annual,
    oas_annual=oas_annual
)

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Overview",
    "📅 Lifetime Projection", 
    "🏦 Retirement Strategy",
    "📊 Monte Carlo",
    "🏛️ Estate Planning",
    "⚖️ Scenario Comparison"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
with tab1:
    st.header(f"Business Sale Analysis — {client_name}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gross Proceeds", f"${proceeds:,.0f}")
    col2.metric("Total Tax Owing", f"${total_tax:,.0f}")
    col3.metric("Net After-Tax Proceeds", f"${net_proceeds:,.0f}")
    col4.metric("LCGE Applied", f"${lcge_available:,.0f}")

    col5, col6, col7 = st.columns(3)
    col5.metric("Years to Retirement", f"{years_left} years")
    col6.metric("Projected Portfolio at Retirement", f"${portfolio_start:,.0f}")
    col7.metric("Effective Tax Rate on Sale", f"{round((total_tax/proceeds)*100,1)}%")

    st.markdown("<hr>", unsafe_allow_html=True)
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

# ══════════════════════════════════════════════════════════════
# TAB 2 — LIFETIME PROJECTION
# ══════════════════════════════════════════════════════════════
with tab2:
    st.header("Lifetime Financial Projection")
    st.caption("5-year snapshots from today through life expectancy across all three buckets")

    cf_df = pd.DataFrame(cashflow_rows)

    fig_nw = go.Figure()
    fig_nw.add_trace(go.Bar(x=cf_df['period'], y=cf_df['rrsp_balance'],
        name='RRSP / RRIF', marker_color='#e74c3c'))
    fig_nw.add_trace(go.Bar(x=cf_df['period'], y=cf_df['tfsa_balance'],
        name='TFSA (tax-free)', marker_color='#2DD4A0'))
    fig_nw.add_trace(go.Bar(x=cf_df['period'], y=cf_df['non_reg_balance'],
        name='Non-Registered', marker_color='#C9A84C'))
    fig_nw.update_layout(
        title="Projected Net Worth by Bucket — Lifetime View",
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

    st.subheader("Period-by-Period Breakdown")
    display_rows = []
    for r in cashflow_rows:
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
        })
    display_df = pd.DataFrame(display_rows)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — RETIREMENT STRATEGY
# ══════════════════════════════════════════════════════════════
with tab3:
    st.header("RRSP Meltdown Strategy")

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
# TAB 4 — MONTE CARLO
# ══════════════════════════════════════════════════════════════
with tab4:
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
# TAB 5 — ESTATE PLANNING
# ══════════════════════════════════════════════════════════════
with tab5:
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
# TAB 6 — SCENARIO COMPARISON
# ══════════════════════════════════════════════════════════════
with tab6:
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