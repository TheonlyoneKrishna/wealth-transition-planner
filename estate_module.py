# estate_module.py
# Estate projection - models tax at death and net estate value

from tax_engine import calculate_tax, FEDERAL_BRACKETS, ONTARIO_BRACKETS

def calculate_estate(
    portfolio_value,
    rrsp_remaining,
    tfsa_value,
    death_age,
    retirement_age,
    annual_return,
    annual_spending,
    cpp_annual,
    oas_annual
):
    # Project portfolio from retirement to death
    years_in_retirement = death_age - retirement_age
    
    # Simplified projection - average annual growth minus spending
    # net of government income
    net_annual_withdrawal = max(0, annual_spending - cpp_annual - oas_annual)
    
    projected_portfolio = portfolio_value
    for year in range(years_in_retirement):
        projected_portfolio = projected_portfolio * (1 + annual_return) - net_annual_withdrawal
        projected_portfolio = max(0, projected_portfolio)
    
    # RRSP/RRIF at death - fully taxable as income
    rrsp_tax = calculate_tax(rrsp_remaining, FEDERAL_BRACKETS) + \
               calculate_tax(rrsp_remaining, ONTARIO_BRACKETS)
    rrsp_net = rrsp_remaining - rrsp_tax

    # Non-registered portfolio - assume 50% is accrued capital gains
    # 50% inclusion rate on deemed disposition
    assumed_gain = projected_portfolio * 0.5
    portfolio_tax = calculate_tax(assumed_gain * 0.5, FEDERAL_BRACKETS) + \
                    calculate_tax(assumed_gain * 0.5, ONTARIO_BRACKETS)
    portfolio_net = projected_portfolio - portfolio_tax

    # TFSA passes tax-free
    # Project TFSA to death age
    years_tfsa_growth = death_age - retirement_age
    projected_tfsa = tfsa_value * (1 + annual_return) ** years_tfsa_growth

    # Total estate
    gross_estate = projected_portfolio + rrsp_remaining + projected_tfsa
    total_tax = rrsp_tax + portfolio_tax
    net_estate = portfolio_net + rrsp_net + projected_tfsa

    return {
        'death_age': death_age,
        'projected_portfolio': round(projected_portfolio, 0),
        'projected_tfsa': round(projected_tfsa, 0),
        'rrsp_remaining': round(rrsp_remaining, 0),
        'rrsp_tax': round(rrsp_tax, 0),
        'portfolio_tax': round(portfolio_tax, 0),
        'total_tax_at_death': round(total_tax, 0),
        'gross_estate': round(gross_estate, 0),
        'net_estate': round(net_estate, 0),
        'tfsa_to_heirs': round(projected_tfsa, 0)
    }

if __name__ == "__main__":
    result = calculate_estate(
        portfolio_value=7920673,
        rrsp_remaining=142072,
        tfsa_value=766234,
        death_age=85,
        retirement_age=60,
        annual_return=0.06,
        annual_spending=120000,
        cpp_annual=25690,
        oas_annual=8908
    )

    print(f"\nEstate Projection at Age {result['death_age']}")
    print("=" * 50)
    print(f"Projected portfolio:     ${result['projected_portfolio']:>15,.0f}")
    print(f"Projected TFSA:          ${result['projected_tfsa']:>15,.0f}")
    print(f"Remaining RRSP:          ${result['rrsp_remaining']:>15,.0f}")
    print(f"Gross estate:            ${result['gross_estate']:>15,.0f}")
    print("-" * 50)
    print(f"Tax on RRSP at death:    ${result['rrsp_tax']:>15,.0f}")
    print(f"Tax on portfolio gains:  ${result['portfolio_tax']:>15,.0f}")
    print(f"Total tax at death:      ${result['total_tax_at_death']:>15,.0f}")
    print("-" * 50)
    print(f"Net estate to heirs:     ${result['net_estate']:>15,.0f}")
    print(f"  of which TFSA:         ${result['tfsa_to_heirs']:>15,.0f} (tax-free)")