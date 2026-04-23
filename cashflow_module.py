# cashflow_module.py
# Year-by-year cash flow engine — pre-retirement and retirement periods
# Shows 5-year increment snapshots from current age to death
# All balances track three buckets: RRSP, TFSA, Non-Registered

from tax_engine import calculate_tax, FEDERAL_BRACKETS, ONTARIO_BRACKETS

ANNUAL_TFSA_ROOM = 7000 # CRS annual TFSA contribution limit

# CRA 2026 RRIF minimum withdrawal factors (verified)
RRIF_FACTORS = {
    65: 0.0400, 66: 0.0417, 67: 0.0435, 68: 0.0455, 69: 0.0476,
    70: 0.0500, 71: 0.0528, 72: 0.0540, 73: 0.0553, 74: 0.0567,
    75: 0.0582, 76: 0.0598, 77: 0.0617, 78: 0.0636, 79: 0.0658,
    80: 0.0682, 81: 0.0708, 82: 0.0738, 83: 0.0771, 84: 0.0808,
    85: 0.0851, 86: 0.0899, 87: 0.0955, 88: 0.1021, 89: 0.1099,
    90: 0.1192, 91: 0.1306, 92: 0.1449, 93: 0.1634, 94: 0.1879,
    95: 0.2000
}

def run_cashflow(
    client_age,           # current age today
    retirement_age,       # age client stops working
    life_expectancy,      # age to model to
    employment_income,    # annual employment income pre-retirement
    annual_rrsp_contrib,  # annual RRSP contribution pre-retirement
    annual_tfsa_contrib,  # annual TFSA contribution pre-retirement
    mean_return,          # expected annual portfolio return (decimal)
    net_proceeds,         # after-tax business sale proceeds (non-reg at start)
    rrsp_balance_today,   # RRSP balance TODAY (not at retirement)
    cpp_annual,           # annual CPP at chosen start age
    oas_annual,           # annual OAS at chosen start age
    cpp_start_age,        # age CPP begins
    oas_start_age,        # age OAS begins
    annual_spending,      # annual retirement spending target
    current_tfsa_room,    # TFSA contribution room available today
    tfsa_balance_today,   # TFSA balance TODAY
    non_reg_balance_today=0 #existing non-reg balance TODAY (separate from proceeds)
):
    rows = []

    # ── Starting balances (TODAY) ────────────────────────────
    non_reg  = net_proceeds + non_reg_balance_today
    rrsp     = rrsp_balance_today
    tfsa     = tfsa_balance_today
    tfsa_room = current_tfsa_room

    # ── PRE-RETIREMENT ───────────────────────────────────────
    # Each loop iteration = one 5-year period from client_age to retirement_age
    age = client_age
    while age < retirement_age:
        period_end = min(age + 5, retirement_age)
        years = period_end - age

        period_employment  = employment_income * years
        period_rrsp_contrib = 0
        period_tfsa_contrib = 0
        period_tax         = 0

        for y in range(years):
            # RRSP deduction reduces taxable employment income
            taxable = max(0, employment_income - annual_rrsp_contrib)
            fed = calculate_tax(taxable, FEDERAL_BRACKETS)
            ont = calculate_tax(taxable, ONTARIO_BRACKETS)
            period_tax += fed + ont

            # RRSP grows with contribution + return
            rrsp = (rrsp + annual_rrsp_contrib) * (1 + mean_return)
            period_rrsp_contrib += annual_rrsp_contrib

            # TFSA grows with contribution (capped at room) + return
            tfsa_contrib_this_year = min(annual_tfsa_contrib, tfsa_room)
            tfsa = (tfsa + tfsa_contrib_this_year) * (1 + mean_return)
            tfsa_room = max(0, tfsa_room - tfsa_contrib_this_year) + ANNUAL_TFSA_ROOM
            period_tfsa_contrib += tfsa_contrib_this_year

            # Non-reg grows on investment return only (no withdrawals pre-retirement)
            non_reg = non_reg * (1 + mean_return)

        total_net_worth = rrsp + tfsa + non_reg

        rows.append({
            'period':            f"Age {age}–{period_end}",
            'phase':             'pre-retirement',
            'employment_income': round(period_employment),
            'rrsp_contrib':      round(period_rrsp_contrib),
            'tfsa_contrib':      round(period_tfsa_contrib),
            'tax_owing':         round(period_tax),
            'cpp_income':        0,
            'oas_income':        0,
            'rrsp_withdrawal':   0,
            'non_reg_withdrawal':0,
            'tfsa_withdrawal':   0,
            'rrsp_balance':      round(rrsp),
            'tfsa_balance':      round(tfsa),
            'non_reg_balance':   round(non_reg),
            'total_net_worth':   round(total_net_worth)
        })

        age = period_end

    # ── RETIREMENT ───────────────────────────────────────────
    # Each loop iteration = one 5-year period from retirement_age to life_expectancy
    # Guard: if life_expectancy <= retirement_age, add one terminal row and return
    if life_expectancy <= retirement_age:
        rows.append({
            'period':            f"Age {retirement_age}",
            'phase':             'retirement',
            'employment_income': 0,
            'rrsp_contrib':      0,
            'tfsa_contrib':      0,
            'tax_owing':         0,
            'cpp_income':        0,
            'oas_income':        0,
            'rrsp_withdrawal':   0,
            'non_reg_withdrawal':0,
            'tfsa_withdrawal':   0,
            'rrsp_balance':      round(rrsp),
            'tfsa_balance':      round(tfsa),
            'non_reg_balance':   round(non_reg),
            'total_net_worth':   round(rrsp + tfsa + non_reg)
        })
        return rows

    age = retirement_age
    while age < life_expectancy:
        period_end = min(age + 5, life_expectancy)
        years = period_end - age

        period_cpp       = 0
        period_oas       = 0
        period_rrsp_w    = 0
        period_non_reg_w = 0
        period_tfsa_w    = 0
        period_tax       = 0

        for y in range(years):
            current_age = age + y

            # ── Government income ────────────────────────────
            cpp_this_year = cpp_annual if current_age >= cpp_start_age else 0
            oas_this_year = oas_annual if current_age >= oas_start_age else 0

            # OAS clawback: 15 cents clawed back per dollar above $95,323
            # Check against total income approximation (will refine with actual income below)
            if oas_this_year > 0:
                approx_total = cpp_this_year + oas_this_year
                if approx_total > 95323:
                    clawback = (approx_total - 95323) * 0.15
                    oas_this_year = max(0, oas_this_year - clawback)

            gov_income = cpp_this_year + oas_this_year

            # ── RRIF mandatory withdrawal (age 71+) ─────────
            # RRSP converts to RRIF at 71; mandatory minimum withdrawals begin
            rrif_min = 0
            if current_age >= 71 and rrsp > 0:
                factor = RRIF_FACTORS.get(min(current_age, 95), 0.20)
                rrif_min = rrsp * factor

            rrsp_withdrawal = rrif_min  # only mandatory minimum — meltdown handled separately

            # ── Spending gap calculation ─────────────────────
            # How much still needs to come from investable assets?
            gap = max(0, annual_spending - gov_income - rrsp_withdrawal)

            # Withdrawal hierarchy: non-reg first (tax advantaged vs RRSP),
            # TFSA last (let it compound tax-free as long as possible)
            non_reg_w = min(gap, non_reg)
            remaining_gap = gap - non_reg_w
            tfsa_w = min(remaining_gap, tfsa) if remaining_gap > 0 else 0

            # ── Tax calculation ──────────────────────────────
            # Taxable income = government benefits + RRSP/RRIF withdrawal
            # + capital gain portion of non-reg withdrawal
            # Non-reg: assume 50% of balance is accrued gain, 50% inclusion rate
            # → taxable gain = non_reg_w × 0.50 × 0.50 = non_reg_w × 0.25
            # This matches estate_module.py assumption and is conservative/defensible
            non_reg_taxable_portion = non_reg_w * 0.25
            taxable_income = gov_income + rrsp_withdrawal + non_reg_taxable_portion

            fed = calculate_tax(taxable_income, FEDERAL_BRACKETS)
            ont = calculate_tax(taxable_income, ONTARIO_BRACKETS)
            period_tax += fed + ont

            # ── Update balances (grow then withdraw, order matters) ──
            rrsp    = max(0, (rrsp    - rrsp_withdrawal) * (1 + mean_return))
            non_reg = max(0, (non_reg - non_reg_w)       * (1 + mean_return))
            # TFSA: add annual $7,000 new room contribution + growth - withdrawal
            tfsa    = max(0, (tfsa - tfsa_w + ANNUAL_TFSA_ROOM)      * (1 + mean_return))

            # Accumulate period totals
            period_cpp       += cpp_this_year
            period_oas       += oas_this_year
            period_rrsp_w    += rrsp_withdrawal
            period_non_reg_w += non_reg_w
            period_tfsa_w    += tfsa_w

        total_net_worth = rrsp + tfsa + non_reg

        rows.append({
            'period':            f"Age {age}–{period_end}",
            'phase':             'retirement',
            'employment_income': 0,
            'rrsp_contrib':      0,
            'tfsa_contrib':      0,
            'tax_owing':         round(period_tax),
            'cpp_income':        round(period_cpp),
            'oas_income':        round(period_oas),
            'rrsp_withdrawal':   round(period_rrsp_w),
            'non_reg_withdrawal':round(period_non_reg_w),
            'tfsa_withdrawal':   round(period_tfsa_w),
            'rrsp_balance':      round(rrsp),
            'tfsa_balance':      round(tfsa),
            'non_reg_balance':   round(non_reg),
            'total_net_worth':   round(total_net_worth)
        })

        age = period_end

    return rows


if __name__ == "__main__":
    rows = run_cashflow(
        client_age=45,
        retirement_age=60,
        life_expectancy=90,
        employment_income=80000,
        annual_rrsp_contrib=18000,
        annual_tfsa_contrib=7000,
        mean_return=0.06,
        net_proceeds=3130200,
        rrsp_balance_today=800000,   # renamed from rrsp_balance_now — TODAY's balance
        cpp_annual=25690,
        oas_annual=8908,
        cpp_start_age=70,
        oas_start_age=65,
        annual_spending=120000,
        current_tfsa_room=109000,
        tfsa_balance_today=0,        # renamed from tfsa_balance_now — TODAY's balance
    )

    print(f"\n{'Period':<12} {'Phase':<15} {'Employment':>12} {'RRSP W/D':>11} {'Non-Reg W/D':>12} {'CPP':>10} {'OAS':>10} {'Tax':>10}")
    print(f"{'':12} {'':15} {'RRSP Bal':>12} {'TFSA Bal':>11} {'Non-Reg':>12} {'Net Worth':>10}")
    print("─" * 100)
    for r in rows:
        print(f"{r['period']:<12} {r['phase']:<15} "
              f"Emp:${r['employment_income']:>10,}  RRSP-W:${r['rrsp_withdrawal']:>9,}  "
              f"NR-W:${r['non_reg_withdrawal']:>9,}  CPP:${r['cpp_income']:>8,}  "
              f"OAS:${r['oas_income']:>7,}  Tax:${r['tax_owing']:>9,}")
        print(f"{'':12} {'':15} "
              f"RRSP:${r['rrsp_balance']:>10,}  TFSA:${r['tfsa_balance']:>10,}  "
              f"NR:${r['non_reg_balance']:>11,}  NW:${r['total_net_worth']:>11,}")
        print()