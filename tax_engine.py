#tax_engine.py
#Canadian progressive tax calculator - Fedral + Ontario 2026

FEDERAL_BRACKETS = [
    (58523, 0.14),
    (117045, 0.205),
    (181440, 0.26),
    (258482, 0.29),
    (float('inf'), 0.33)
]

ONTARIO_BRACKETS = [
    (53891, 0.0505),
    (107785, 0.0915),
    (150000, 0.1116),
    (220000, 0.1216),
    (float('inf'), 0.1316)
]

# Calculates which income falls under which bracket and upto which
def calculate_tax(income, brackets):
    tax = 0
    previous_limit = 0

    for limit, rate in brackets:
        if income <= previous_limit:
            break
        taxable_in_bracket = min(income, limit) - previous_limit
        tax += taxable_in_bracket * rate
        previous_limit = limit
    
    return round(tax, 2)

# Calculates combined taxable income of Federal and ontario taxes
def calculate_combined_tax(income):
    federal = calculate_tax(income, FEDERAL_BRACKETS)
    ontario = calculate_tax(income, ONTARIO_BRACKETS)
    total = federal + ontario
    effective_rate = round((total/income)*100, 2) if income > 0 else 0

    print (f"Income:           ${income:,.0f}")
    print (f"Federal tax:      ${federal:,.2f}")
    print (f"Ontario Tax:      ${ontario:,.2f}")
    print (f"Total Tax:        ${total:,.2f}")
    print (f"Effective rate:   {effective_rate}%")
    print (f"After-tax:        ${income - total:,.2f}")

# Test with David Chen's post-sale income scenario
if __name__ == "__main__":
    calculate_combined_tax(875000)