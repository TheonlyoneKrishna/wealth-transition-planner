# monte_carlo.py
# Monte Carlo retirement simulation - 1,000 scenarios

import numpy as np
from tax_engine import calculate_tax, FEDERAL_BRACKETS, ONTARIO_BRACKETS

# Simulation parameters
NUM_SCENARIOS = 1000


# Runs monte calro with 1000 scenarios gives the complete picture with percentile and success rate
def run_monte_carlo(
    portfolio_value,
    annual_spending,
    cpp_annual,
    oas_annual,
    cpp_start_age,
    oas_start_age,
    retirement_age,
    life_expectancy,
    mean_return,
    std_return,
    mean_inflation,
    std_inflation
):
    np.random.seed(42)  # makes results reproducible
    years = life_expectancy - retirement_age
    success_count = 0
    all_portfolios = []

    for scenario in range(NUM_SCENARIOS):
        # Generate random returns and inflation for every year
        annual_returns = np.random.normal(mean_return, std_return, years)
        annual_inflations = np.random.normal(mean_inflation, std_inflation, years)

        balance = portfolio_value
        portfolio_path = [balance]
        failed = False

        for year in range(years):
            current_age = retirement_age + year

            # Income this year
            cpp_income = cpp_annual if current_age >= cpp_start_age else 0
            oas_income = oas_annual if current_age >= oas_start_age else 0
            government_income = cpp_income + oas_income

            # RRIF mandatory minimum withdrawal (age 71+)
            RRIF_FACTORS = {
                    71: 0.0528, 72: 0.0540, 73: 0.0553, 74: 0.0567,
                    75: 0.0582, 76: 0.0598, 77: 0.0617, 78: 0.0636,
                    79: 0.0658, 80: 0.0682, 81: 0.0708, 82: 0.0738,
                    83: 0.0771, 84: 0.0808, 85: 0.0851, 86: 0.0899,
                    87: 0.0955, 88: 0.1021, 89: 0.1099, 90: 0.1192,
                    95: 0.2000
                }
            rrif_withdrawal = 0
            if current_age >= 71 and balance > 0:
                    factor = RRIF_FACTORS.get(min(current_age, 95), 0.20)
                    rrif_withdrawal = balance * factor

            # Adjust spending for cumulative inflation
            inflation_factor = np.prod(1 + annual_inflations[:year+1])
            real_spending = annual_spending * inflation_factor

            # Net withdrawal needed from portfolio
            net_withdrawal = max(0, real_spending - government_income)

            # Tax on government income
            taxable_income = government_income + rrif_withdrawal
            if taxable_income > 0:
                tax = calculate_tax(taxable_income, FEDERAL_BRACKETS) + \
                    calculate_tax(taxable_income, ONTARIO_BRACKETS)
                net_withdrawal += tax
            else:
                tax=0

            net_withdrawal = max(0, net_withdrawal +tax - rrif_withdrawal)  # RRIF already withdrawn

            # Portfolio grows then we withdraw
            balance = balance * (1 + annual_returns[year]) - net_withdrawal

            if balance <= 0:
                failed = True
                balance = 0
                portfolio_path.append(0)
                break

            portfolio_path.append(round(balance, 2))
           
            
        if not failed:
            success_count += 1

        all_portfolios.append(portfolio_path)

    probability_of_success = round((success_count / NUM_SCENARIOS) * 100, 1)

    # Calculate percentile paths for visualization later
    max_len = max(len(p) for p in all_portfolios)
    padded = [p + [0] * (max_len - len(p)) for p in all_portfolios]
    portfolios_array = np.array(padded)

    percentiles = {
        'p10': np.percentile(portfolios_array, 10, axis=0).tolist(),
        'p25': np.percentile(portfolios_array, 25, axis=0).tolist(),
        'p50': np.percentile(portfolios_array, 50, axis=0).tolist(),
        'p75': np.percentile(portfolios_array, 75, axis=0).tolist(),
        'p90': np.percentile(portfolios_array, 90, axis=0).tolist(),
    }

    return {
        'probability_of_success': probability_of_success,
        'success_count': success_count,
        'total_scenarios': NUM_SCENARIOS,
        'percentiles': percentiles,
        'years': list(range(retirement_age, retirement_age + max_len))
    }

if __name__ == "__main__":
    # ── TEST DEFAULTS — not client values ──────────────────
    # These are illustrative inputs for standalone module testing only.
    # All client inputs flow through app.py in production.
    # ───────────────────────────────────────────────────────
    results = run_monte_carlo(
        portfolio_value=3130199,
        annual_spending=120000,
        cpp_annual=25690,
        oas_annual=8908,
        cpp_start_age=70,
        oas_start_age=65,
        retirement_age=60,
        life_expectancy=90,
        mean_return=0.06,
        std_return=0.12,
        mean_inflation=0.025,
        std_inflation=0.01
    )

    print(f"Monte Carlo Results — {results['total_scenarios']} scenarios")
    print(f"Retirement age:        60")
    print(f"Life expectancy:       90")
    print(f"Annual spending:       $120,000")
    print(f"Starting portfolio:    $3,130,199")
    print("=" * 45)
    print(f"Probability of success: {results['probability_of_success']}%")
    print(f"Scenarios succeeded:    {results['success_count']}/{results['total_scenarios']}")
    print(f"\nMedian portfolio at 90: ${results['percentiles']['p50'][-1]:,.0f}")
    print(f"Best 10% at 90:         ${results['percentiles']['p90'][-1]:,.0f}")
    print(f"Worst 10% at 90:        ${results['percentiles']['p10'][-1]:,.0f}")