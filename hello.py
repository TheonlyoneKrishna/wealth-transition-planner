#hello.py
#Business sale calculator - connects to tax engine

from tax_engine import calculate_tax, FEDERAL_BRACKETS, ONTARIO_BRACKETS

def years_to_goal(current_age, goal_age):
    return goal_age-current_age

def future_value(present_value, annual_return, years):
    return present_value*(1+annual_return)**years

# Calculates the amount client will recieve after selling the business
def calculate_business_sale(proceeds, cost_base,lcge_available):
    gross_gain = proceeds - cost_base
    if lcge_available>0:
        taxable_gain = max(0,gross_gain - lcge_available)
    else:
        taxable_gain = gross_gain
    taxable_income = taxable_gain * 0.5
    
    return taxable_income

def future_value_contributions(annual_contribution, annual_return, years):
    return annual_contribution*(((1+annual_return)**years-1)/annual_return)

#Client Data
client_age = 45
proceeds = 3500000
expected_return = 0.06
cost_base = 500000
lcge_available = 1250000
annual_contribution = 18000

if __name__ == "__main__":
    # ── TEST DEFAULTS — not client values ──────────────────
    # These are illustrative inputs for standalone module testing only.
    # All client inputs flow through app.py in production.
    # ───────────────────────────────────────────────────────
    # Step 1: Calculate taxable income from business sale
    taxable_income = calculate_business_sale(proceeds, cost_base, lcge_available)

    #Step 2: Feed that into the real tax engine
    federal_tax = calculate_tax(taxable_income, FEDERAL_BRACKETS)
    ontario_tax = calculate_tax(taxable_income, ONTARIO_BRACKETS)
    total_tax = federal_tax + ontario_tax
    net_proceeds = proceeds - total_tax

    #Using the function
    years_left = years_to_goal(client_age, 60)
    future_contribution = future_value_contributions(annual_contribution, expected_return, years_left)
    future_portfolio = future_value(net_proceeds, expected_return,years_left)
    portfolio_at_retirement = future_contribution + future_portfolio



    print(f"Gross proceeds:            ${proceeds:,.0f}")
    print(f"Taxable income:            ${taxable_income:,.0f}")
    print(f"Total tax owing:           ${total_tax:,.2f}")
    print(f"Net proceeds after tax:    ${net_proceeds:,.2f}")
    print(f"Years to retirement:       {years_left}")
    print(f"Portfolio at retirement:   ${portfolio_at_retirement:,.2f}")

