#rrsp_module.py
# RRSP meltdown strategy modeler

from tax_engine import calculate_tax,FEDERAL_BRACKETS,ONTARIO_BRACKETS

# Calculates the meltdown from withdrawals in low income years
# respects annual TFSA contribution room limits
def rrsp_meltdown(
        rrsp_balance,
        start_age,
        end_age,
        other_income,
        annual_return,
        target_income,
        current_tfsa_room,
        years_to_retirement,
        annual_new_tfsa_room=7000
):
    # Dynamically calculate TFSA room available at retirement
    tfsa_room_at_retirement = current_tfsa_room + (years_to_retirement * annual_new_tfsa_room)
    remaining_tfsa_room = tfsa_room_at_retirement

    results = []
    tfsa_accumulated = 0
    non_reg_accumulated = 0
    current_balance = rrsp_balance
    remaining_tfsa_room = tfsa_room_at_retirement

    for age in range(start_age, end_age + 1):
        # How much RRSP room is left before hitting target income
        rrsp_withdrawal = max(0, target_income - other_income)

        # Don't withdraw more than the balance
        rrsp_withdrawal = min(rrsp_withdrawal, current_balance)

        # Total income this year
        total_income = other_income + rrsp_withdrawal

        # Tax on total income
        federal_tax = calculate_tax(total_income, FEDERAL_BRACKETS)
        ontario_tax = calculate_tax(total_income, ONTARIO_BRACKETS)
        total_tax = federal_tax + ontario_tax

        # Tax on just other income
        base_federal = calculate_tax(other_income, FEDERAL_BRACKETS)
        base_ontario = calculate_tax(other_income, ONTARIO_BRACKETS)
        base_tax = base_ontario + base_federal

        # Marginal tax paid on the RRSP withdrawal specifically
        tax_on_withdrawal = total_tax - base_tax
        after_tax_withdrawal = rrsp_withdrawal - tax_on_withdrawal

        # Split after-tax withdrawal between TFSA and non-registered
        tfsa_contribution = min(after_tax_withdrawal, remaining_tfsa_room)
        non_reg_contribution = after_tax_withdrawal - tfsa_contribution

        tfsa_accumulated += tfsa_contribution
        non_reg_accumulated += non_reg_contribution

        # Add new TFSA room for next year
        remaining_tfsa_room = remaining_tfsa_room - tfsa_contribution + annual_new_tfsa_room

        # RRSP balance grows then we subtract withdrawal
        current_balance = (current_balance * (1 + annual_return)) - rrsp_withdrawal

        results.append({
            'age': age,
            'rrsp_withdrawal': round(rrsp_withdrawal, 2),
            'total_income': round(total_income, 2),
            'total_tax': round(total_tax, 2),
            'after_tax_withdrawal': round(after_tax_withdrawal, 2),
            'tfsa_contribution': round(tfsa_contribution, 2),
            'non_reg_contribution': round(non_reg_contribution, 2),
            'tfsa_accumulated': round(tfsa_accumulated, 2),
            'non_reg_accumulated': round(non_reg_accumulated, 2),
            'remaining_tfsa_room': round(remaining_tfsa_room, 2),
            'rrsp_balance': round(max(0, current_balance), 2)
        })

    return results

def print_meltdown_result(results):
    print(f"{'Age':<6}{'RRSP W/D':<14}{'Tax Paid':<14}{'TFSA':<14}{'Non-Reg':<14}{'TFSA Room Left':<18}{'RRSP Bal'}")
    print("-" * 95)
    for r in results:
        print(f"{r['age']:<6}${r['rrsp_withdrawal']:>10,.0f}  ${r['total_tax']:>10,.0f}  ${r['tfsa_accumulated']:>10,.0f}  ${r['non_reg_accumulated']:>10,.0f}  ${r['remaining_tfsa_room']:>13,.0f}  ${r['rrsp_balance']:>10,.0f}")

if __name__ == "__main__":
    results = rrsp_meltdown(
        rrsp_balance=800000,
        start_age=60,
        end_age=71,
        other_income=30000,
        annual_return=0.06,
        target_income=117000,
        current_tfsa_room=109000,
        years_to_retirement=15,
        annual_new_tfsa_room=7000
    )
    print_meltdown_result(results)