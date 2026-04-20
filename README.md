# 🇨🇦 Canadian Business Owner Wealth Transition Planner

A comprehensive, interactive financial planning application built for Ontario-based high-net-worth business owners navigating a business sale and retirement transition.

Built with Python and Streamlit. All calculations verified against 2026 CRA data.

**Live Demo:** [Launch App](https://your-app-url.streamlit.app) ← we'll update this after deployment

---

## What This Tool Does

Most financial planning tools model retirement in isolation. This application models the complete wealth transition - from business sale through retirement to estate - as one integrated picture.

A business owner selling their company faces a cascade of interconnected decisions: How much tax will the sale trigger? How do I use my Lifetime Capital Gains Exemption? When should I start drawing down my RRSP before CPP and OAS arrive? At what age should I start CPP to maximize lifetime income? What does my estate look like at death after all taxes?

This tool answers all of those questions simultaneously, with every assumption visible and adjustable in real time.

---

## Modules

### 1. Business Sale Analysis
- Calculates gross capital gain from business sale
- Applies Lifetime Capital Gains Exemption (LCGE) - dynamic input up to $1,250,000
- Computes Federal + Ontario tax on the taxable gain using 2026 progressive brackets
- Projects net after-tax proceeds to retirement using future value calculations
- Models RRSP and TFSA contributions compounding over the pre-retirement period

### 2. RRSP Meltdown Strategy
- Models systematic RRSP drawdown during low-income retirement years (age 60–71)
- Targets annual income to fill lower tax brackets before CPP/OAS begin
- Tracks CRA-compliant TFSA contribution room dynamically (current room + future annual limits)
- Splits after-tax withdrawals between TFSA (tax-free) and non-registered overflow
- Visualizes three-bucket strategy: RRSP declining, TFSA filling, non-registered growing

### 3. CPP & OAS Optimizer
- Models CPP monthly benefit at every start age from 60–70
- Calculates actuarial adjustments: -0.6%/month before 65, +0.7%/month after 65
- Computes breakeven age for early vs. delayed CPP start
- Checks OAS clawback exposure based on total retirement income
- Uses 2026 verified maximums: CPP $1,507.65/month, OAS $742.31/month

### 4. Monte Carlo Retirement Simulation
- Runs 1,000 retirement scenarios with randomized annual returns and inflation
- Models sequence-of-returns risk across 30+ year retirement horizons
- Outputs probability of success — percentage of scenarios fully funded to life expectancy
- Displays fan chart showing 10th, 25th, 50th, 75th, and 90th percentile portfolio paths
- Integrates CPP/OAS income timing into each scenario

### 5. Estate Projection
- Projects portfolio value from retirement to death
- Models tax at death: income tax on remaining RRSP/RRIF, capital gains on non-registered
- Shows TFSA passing tax-free to beneficiaries
- Donut chart showing estate composition — what goes to heirs vs. CRA

---

## Tech Stack

- **Python 3.14** — core calculation engine
- **Streamlit** — interactive web interface
- **Plotly** — charts and visualizations
- **Pandas / NumPy** — data manipulation and Monte Carlo simulation
- **All Canadian tax data verified against CRA 2026 published rates**

---

## How to Run Locally

```bash
git clone https://github.com/TheonlyoneKrishna/wealth-transition-planner.git
cd wealth-transition-planner
pip install -r requirements.txt
streamlit run app.py
```

---

## Key Assumptions & Data Sources

- Federal and Ontario tax brackets: 2026 CRA published rates
- CPP maximum at 65: $1,507.65/month (Government of Canada, January 2026)
- OAS maximum at 65: $742.31/month (Government of Canada, Q1 2026)
- OAS clawback threshold: $95,323 net income (2026)
- TFSA cumulative room: $109,000 (eligible since 2009) + $7,000/year going forward
- LCGE limit: $1,250,000 for qualified small business corporation shares
- Monte Carlo: normal distribution of returns, mean 6%, std 12%, inflation mean 2.5%

---

## Important Disclaimer

This tool is for financial planning illustration purposes only. It does not constitute investment, tax, or legal advice. All projections are hypothetical. Consult a qualified financial advisor before making any financial decisions.

---

*Built by Krishna Patel | Financial Planning Student, Seneca Polytechnic
