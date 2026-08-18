def print_report(company, current_ratio, net_margin, debt_equity, roe):

    print("=" * 50)
    print(f"Financial Report: {company}")
    print("=" * 50)

    print(f"Current Ratio       : {current_ratio:.2f}")
    print(f"Net Profit Margin   : {net_margin:.2f}%")
    print(f"Debt-to-Equity      : {debt_equity:.2f}")
    print(f"Return on Equity    : {roe:.2f}%")

    print("=" * 50)