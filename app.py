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

st.title("🇨🇦 Canadian Business Owner Wealth Transition Planner")
st.caption("Built for Ontario-based HNW clients | 2026 Tax Year | All calculations verified against CRA data")

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

# ── Section 1: Business Sale Summary ─────────────────────────
st.header(f"📋 Business Sale Analysis — {client_name}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Gross Proceeds", f"${proceeds:,.0f}")
col2.metric("Total Tax Owing", f"${total_tax:,.0f}")
col3.metric("Net After-Tax Proceeds", f"${net_proceeds:,.0f}")
col4.metric("LCGE Applied", "Yes ✅" if lcge_available else "No ❌")

col5, col6, col7 = st.columns(3)
col5.metric("Years to Retirement", f"{years_left} years")
col6.metric("Projected Portfolio at Retirement", f"${portfolio_start:,.0f}")
col7.metric("Effective Tax Rate on Sale", f"{round((total_tax/proceeds)*100,1)}%")

# ── Section 2: RRSP Meltdown ──────────────────────────────────
st.header("🏦 RRSP Meltdown Strategy")

rrsp_df = pd.DataFrame(rrsp_results)
final_tfsa = rrsp_df['tfsa_accumulated'].iloc[-1]
final_rrsp = rrsp_df['rrsp_balance'].iloc[-1]

final_non_reg = rrsp_df['non_reg_accumulated'].iloc[-1]
col8, col9, col9b = st.columns(3)
col8.metric("TFSA Accumulated (tax-free)", f"${final_tfsa:,.0f}")
col9.metric("Non-Registered Overflow", f"${final_non_reg:,.0f}")
col9b.metric("Remaining RRSP Balance", f"${final_rrsp:,.0f}")

fig_rrsp = go.Figure()
fig_rrsp.add_trace(go.Bar(
    x=rrsp_df['age'],
    y=rrsp_df['rrsp_balance'],
    name='RRSP Balance',
    marker_color='#e74c3c'
))
fig_rrsp.add_trace(go.Bar(
    x=rrsp_df['age'],
    y=rrsp_df['tfsa_accumulated'],
    name='TFSA Accumulated',
    marker_color='#27ae60'
))
fig_rrsp.add_trace(go.Bar(
    x=rrsp_df['age'],
    y=rrsp_df['non_reg_accumulated'],
    name='Non-Registered Overflow',
    marker_color='#2980b9'
))
fig_rrsp.update_layout(
    title="RRSP Drawdown vs TFSA Growth",
    barmode='group',
    xaxis_title="Age",
    yaxis_title="Balance ($)",
    height=400
)
st.plotly_chart(fig_rrsp, width='stretch')

# ── Section 3: CPP / OAS ──────────────────────────────────────
st.header("🏛️ CPP & OAS Summary")

col10, col11, col12 = st.columns(3)
col10.metric("Monthly CPP", f"${cpp_monthly:,.2f}", f"Starting age {cpp_start_age}")
col11.metric("Monthly OAS", f"${oas_monthly:,.2f}", f"Starting age {oas_start_age}")
col12.metric("Combined Annual Gov't Income", f"${cpp_annual + oas_annual:,.0f}")

# ── Section 4: Monte Carlo ────────────────────────────────────
st.header("📊 Monte Carlo Retirement Simulation")

success = mc_results['probability_of_success']
color   = "green" if success >= 90 else "orange" if success >= 75 else "red"

st.markdown(f"""
<h2 style='text-align:center; color:{color};'>
    Probability of Success: {success}%
</h2>
<p style='text-align:center;'>{mc_results['success_count']} of {mc_results['total_scenarios']} scenarios fully funded to age {life_expectancy}</p>
""", unsafe_allow_html=True)

years_axis = mc_results['years']
fig_mc = go.Figure()
fig_mc.add_trace(go.Scatter(x=years_axis, y=mc_results['percentiles']['p90'],
    fill=None, line=dict(color='rgba(39,174,96,0.3)'), name='90th percentile'))
fig_mc.add_trace(go.Scatter(x=years_axis, y=mc_results['percentiles']['p75'],
    fill='tonexty', line=dict(color='rgba(39,174,96,0.5)'), name='75th percentile'))
fig_mc.add_trace(go.Scatter(x=years_axis, y=mc_results['percentiles']['p50'],
    fill='tonexty', line=dict(color='#2c3e50', width=2), name='Median'))
fig_mc.add_trace(go.Scatter(x=years_axis, y=mc_results['percentiles']['p25'],
    fill='tonexty', line=dict(color='rgba(231,76,60,0.5)'), name='25th percentile'))
fig_mc.add_trace(go.Scatter(x=years_axis, y=mc_results['percentiles']['p10'],
    fill='tonexty', line=dict(color='rgba(231,76,60,0.3)'), name='10th percentile'))
fig_mc.update_layout(
    title=f"Portfolio Projection — 1,000 Scenarios",
    xaxis_title="Age",
    yaxis_title="Portfolio Value ($)",
    height=500
)
st.plotly_chart(fig_mc, width='stretch')

col13, col14, col15 = st.columns(3)
col13.metric("Median Portfolio at 90", f"${mc_results['percentiles']['p50'][-1]:,.0f}")
col14.metric("Best 10% at 90",         f"${mc_results['percentiles']['p90'][-1]:,.0f}")
col15.metric("Worst 10% at 90",        f"${mc_results['percentiles']['p10'][-1]:,.0f}")

rrsp_df    = pd.DataFrame(rrsp_results)
final_tfsa = rrsp_df['tfsa_accumulated'].iloc[-1]
final_rrsp = rrsp_df['rrsp_balance'].iloc[-1]
final_non_reg = rrsp_df['non_reg_accumulated'].iloc[-1]

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

# ── Section 4b: Lifetime Cash Flow Table + Stacked Net Worth ──
st.header("📅 Lifetime Financial Projection")
st.caption("5-year snapshots from today through life expectancy across all three buckets")

cf_df = pd.DataFrame(cashflow_rows)

# ── Stacked Net Worth Chart ───────────────────────────────────
fig_nw = go.Figure()
fig_nw.add_trace(go.Bar(
    x=cf_df['period'],
    y=cf_df['rrsp_balance'],
    name='RRSP / RRIF',
    marker_color='#e74c3c'
))
fig_nw.add_trace(go.Bar(
    x=cf_df['period'],
    y=cf_df['tfsa_balance'],
    name='TFSA (tax-free)',
    marker_color='#27ae60'
))
fig_nw.add_trace(go.Bar(
    x=cf_df['period'],
    y=cf_df['non_reg_balance'],
    name='Non-Registered',
    marker_color='#2980b9'
))
fig_nw.update_layout(
    title="Projected Net Worth by Bucket — Lifetime View",
    barmode='stack',
    xaxis_title="Period",
    yaxis_title="Balance ($)",
    height=500,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)
st.plotly_chart(fig_nw, width='stretch')

# ── Cash Flow Table ───────────────────────────────────────────
st.subheader("Period-by-Period Breakdown")

# Build display table
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

# ── Section 5: Estate Projection ─────────────────────────────
st.header("🏛️ Estate Projection at Death")

col16, col17, col18 = st.columns(3)
col16.metric("Gross Estate", f"${estate_results['gross_estate']:,.0f}")
col17.metric("Total Tax at Death", f"${estate_results['total_tax_at_death']:,.0f}")
col18.metric("Net Estate to Heirs", f"${estate_results['net_estate']:,.0f}")

col19, col20, col21 = st.columns(3)
col19.metric("Projected Portfolio", f"${estate_results['projected_portfolio']:,.0f}")
col20.metric("TFSA to Heirs (tax-free)", f"${estate_results['tfsa_to_heirs']:,.0f}")
col21.metric("Tax on RRSP at Death", f"${estate_results['rrsp_tax']:,.0f}")

# Estate breakdown chart
fig_estate = go.Figure(go.Pie(
    labels=[
        "Portfolio to Heirs (after tax)",
        "TFSA to Heirs (tax-free)",
        "RRSP Net to Heirs (after tax)",
        "Tax Paid at Death"
    ],
    values=[
        estate_results['projected_portfolio'] - estate_results['portfolio_tax'],
        estate_results['tfsa_to_heirs'],
        estate_results['rrsp_remaining'] - estate_results['rrsp_tax'],
        estate_results['total_tax_at_death']
    ],
    marker_colors=["#2980b9", "#27ae60", "#8e44ad", "#e74c3c"],
    hole=0.4
))
fig_estate.update_layout(
    title=f"Estate Composition at Age {life_expectancy} — What Goes Where",
    height=450
)
st.plotly_chart(fig_estate, width='stretch')
st.caption("This tool is for financial planning illustration purposes only. Not investment advice.")