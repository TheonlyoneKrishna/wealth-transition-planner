# cpp_oas_module.py
# CPP and OAS optimizer - finds breakeven and optimal start age

from tax_engine import calculate_tax, FEDERAL_BRACKETS, ONTARIO_BRACKETS

# 2026 verified maximiums (Government of Canada)
CPP_MAX_AGE_65 = 1507.65  # monthly
OAS_MAX_AGE_65 = 742.31   # monthly (ages 65-74)
OAS_CLAWBACK_THRESHOLD = 95323  # annual income where clawback begins

# calculates the gain/loss in monthly CPP pymt according to start age
def calculate_cap_monthly(cpp_at_65, start_age):
    if start_age < 65:
        reduction = (65 - start_age) * 12 * 0.006
        return round(cpp_at_65 * (1-reduction),2)
    elif start_age > 65:
        increase = (start_age - 65) * 12 * 0.007
        return round(cpp_at_65 * (1+increase),2)
    return round(cpp_at_65,2)

# Calculates the gain in montly OAS pymt according to start year
def calculate_oas_monthly(oas_at_65, start_age):
    if start_age >65:
        increase = (start_age - 65) * 12 * 0.006
        return round(oas_at_65 *(1+increase),2)
    return round(oas_at_65,2)

# Calculates how many months are late/early, and gives breakeven age accordingly 
def calculate_breakdown(cpp_at_65, early_age, late_age):
    early_month = calculate_cap_monthly(cpp_at_65, early_age)
    late_monthly = calculate_cap_monthly( cpp_at_65, late_age)

    months_early = (late_age - early_age)*12
    total_early = 0
    total_late = 0
    breakeven_age = None

    for month in range(1,1201):  #model 100 years max
        total_early += early_month
        if month > months_early:
            total_late += late_monthly

        if total_late >= total_early and breakeven_age is None:
            breakeven_age = late_age + (month - months_early)/12
        
    return {
        'early_age': early_age,
        'late_age': late_age,
        'early_monthly': early_month,
        'late_monthly': late_monthly,
        'breakeven_age': round(breakeven_age,1) if breakeven_age else None
    }

# A complete summary of CPP/OAS
def cpp_oas_summary(cpp_at_65, other_retirement_income, client_name="Client"):
    print(f"\nCPP/OAS Optimization Summary for {client_name}")
    print("=" * 60)
    print(f"\nCPP at age 65: ${cpp_at_65:,.2f}/monthly")
    print(f"\n{'Start Age':<12}{'Monthly CPP':<18}{'Annual CPP'}")
    print("-" * 45)
    for age in [60,61,62,63,64,65,66,67,68,69,70]:
        monthly = calculate_cap_monthly(cpp_at_65, age)
        annual = monthly * 12
        print(f"{age:<12}${monthly:>10,.2f}   ${annual:>10,.2f}")
    
    print(f"\nBreakeven Analysis (vs starting at 65):")
    print("-" * 45)
    for early_age in [60, 63]:
        result = calculate_breakdown(cpp_at_65, early_age, 65)
        print(F"Start at {early_age} vs 65: breakeven at age {result['breakeven_age']}")

    for late_age in [67,70]:
        result = calculate_breakdown(cpp_at_65, 65, late_age)
        print(F"Start at 65 vs {late_age}: breakeven at age {result['breakeven_age']}")

# Checks If there is any Clawback
    print(f"\nOAS Clawback Check:")
    print("-" * 45)
    oas_annual = OAS_MAX_AGE_65 * 12
    total_income = other_retirement_income + oas_annual
    if total_income > OAS_CLAWBACK_THRESHOLD:
        clawback = (total_income - OAS_CLAWBACK_THRESHOLD)*0.15
        print(f"Other income:      ${other_retirement_income:,.0f}")
        print(f"OAS income:        ${oas_annual:,.0f}")
        print(f"Total income:      ${total_income:,.0f}")
        print(f"Clawback amount:  ${clawback:,.2f}")
        print(f"Net OAS received:  ${oas_annual - clawback:,.2f}/year")
    else:
        print(f"No clawback - income ${total_income:,.0f} below threshold")

if __name__ == "__main__":
    cpp_oas_summary(
        cpp_at_65 = CPP_MAX_AGE_65,
        other_retirement_income = 60000
    )
