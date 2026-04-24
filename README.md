# 🇨🇦 Canadian Wealth Transition Planner

An interactive, advisor-ready financial planning application for Canadian high-net-worth clients. Models the complete wealth lifecycle - from business sale through retirement to estate — in one integrated tool.

**Live Demo:** [Launch App](https://wealth-transition-planner-c2kot39re4uanmzsfqrpzj.streamlit.app) · **GitHub:** [TheonlyoneKrishna](https://github.com/TheonlyoneKrishna/wealth-transition-planner)

---

## What This Tool Does

Most financial planning tools model retirement in isolation. This application integrates every major Canadian wealth planning decision into one live, interactive dashboard — with every assumption visible and adjustable in real time.

Supports both business owner clients (with LCGE and business sale modeling) and employed professionals (portfolio-only planning). Multi-client save/load functionality allows advisors to maintain a book of business directly within the app.

---

## Six Integrated Modules

### 1. Business Sale Analysis
Models the full tax impact of a business sale - gross capital gain, Lifetime Capital Gains Exemption (LCGE up to $1.25M), Federal + Ontario progressive tax on the taxable gain, and net after-tax proceeds flowing into the portfolio. Non-business clients see a bucket-by-bucket growth projection instead.

### 2. Lifetime Cash Flow Engine
The core of the application. Runs year-by-year from today through life expectancy across all three buckets (RRSP, TFSA, Non-Registered), producing 5-year period snapshots with full income, withdrawal, tax, and balance detail. All other modules receive their starting values from this engine - eliminating isolated calculations.

### 3. RRSP Meltdown Strategy
Models systematic RRSP drawdown during low-income retirement years, targeting the top of the second federal bracket to minimize lifetime tax. Tracks CRA-compliant TFSA contribution room dynamically - current room plus annual accumulation - splitting after-tax withdrawals between TFSA (tax-free) and non-registered overflow. Visualizes the three-bucket strategy year by year from retirement to age 71.

### 4. CPP & OAS Optimizer
Models CPP monthly benefit at every start age from 60–70 using CRA actuarial adjustment rates (-0.6%/month before 65, +0.7%/month after 65). Calculates breakeven age for every early VS delayed comparison. Checks OAS clawback exposure based on projected total retirement income. Uses 2026 verified maximums: CPP $1,507.65/month, OAS $742.31/month.

### 5. Monte Carlo Retirement Simulation
Runs 1,000 retirement scenarios with randomized annual returns (normal distribution) and inflation, capturing sequence-of-returns risk across 30+ year horizons. Outputs probability of success and a fan chart showing 10th, 25th, 50th, 75th, and 90th percentile portfolio paths. All three market assumption inputs (return, volatility, inflation) are user-configurable.

### 6. Estate Projection
Projects portfolio value from retirement to death, modeling tax at death on RRSP/RRIF balance (fully taxable as income) and capital gains on non-registered portfolio (50% accrued gain assumption, 50% inclusion rate). TFSA passes tax-free to beneficiaries. Donut chart shows estate composition - what goes to heirs VS CRA.

---

## Additional Features

- **Scenario Comparison tab** - run a full alternate scenario (different retirement age, return, or spending) alongside the base plan. Overlay Monte Carlo fan charts for direct visual comparison. Quick-select presets: Early Retirement, Conservative Market, Aggressive Growth, Higher Spending.
- **Multi-client support** - save and load client profiles as JSON files. Advisor can maintain a full book of business and switch between clients with one click.
- **Non-business client mode** - checkbox removes business sale inputs entirely and replaces the overview with a bucket-by-bucket growth comparison (today vs. at retirement).
- **TFSA lump sum contribution** - models one-time use of accumulated unused contribution room, separate from annual contributions.
- **Dynamic age ranges** - all age inputs accept values from 18 to 85+ to support any client life stage.

---

## Tech Stack

- **Python 3.14** — core calculation engine across six modules
- **Streamlit** — interactive web interface with tab navigation
- **Plotly** — all charts (stacked bars, fan charts, donut, grouped bars)
- **Pandas / NumPy** — data manipulation and Monte Carlo simulation
- **JSON** — client profile persistence (no database required)
- **All Canadian tax data verified against 2026 CRA published rates**

---

## How to Run Locally

```bash
git clone https://github.com/TheonlyoneKrishna/wealth-transition-planner.git
cd wealth-transition-planner
pip install -r requirements.txt
streamlit run app.py
```

---

## Data Sources & Key Assumptions

| Item | Value | Source |
|------|-------|--------|
| Federal bottom rate | 14% | CRA 2026 |
| Federal top rate | 33% (above $258,482) | CRA 2026 |
| Ontario top rate | 13.16% (above $220,000) | CRA 2026 |
| CPP maximum at 65 | $1,507.65/month | Government of Canada, Jan 2026 |
| OAS maximum at 65 | $742.31/month | Government of Canada, Q1 2026 |
| OAS clawback threshold | $95,323 net income | CRA 2026 |
| LCGE limit | $1,250,000 | CRA 2026 (QSBC shares) |
| TFSA cumulative room | $109,000 + $7,000/year | CRA 2026 |
| RRIF minimum factors | Ages 65–95 per CRA table | CRA 2026 |
| Monte Carlo returns | Normal distribution, configurable mean/std | User input |

---

## Project Structure

---

## Disclaimer

This tool is for financial planning illustration purposes only. It does not constitute investment, tax, or legal advice. All projections are hypothetical. Consult a qualified financial advisor before making any financial decisions.

---

*Krishna Patel | Financial Planning Student, Seneca Polytechnic | CSC Certified*
*[LinkedIn](https://www.linkedin.com/in/krishna-patel-7b1984344) · [Live App](https://wealth-transition-planner-c2kot39re4uanmzsfqrpzj.streamlit.app)*