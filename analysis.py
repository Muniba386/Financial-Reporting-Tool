def liquidity_analysis(current_ratio):

    if current_ratio is None:
        return "Current ratio unavailable: current liabilities are zero"

    if current_ratio >= 1.5:
        return "Strong liquidity position"

    elif current_ratio >= 1:
        return "Acceptable liquidity position"

    else:
        return "Liquidity risk: company may struggle to pay short-term debts"



def profitability_analysis(net_profit_margin):

    if net_profit_margin is None:
        return "Net profit margin unavailable: revenue is zero"

    if net_profit_margin >= 20:
        return "Excellent profitability"

    elif net_profit_margin >= 10:
        return "Good profitability"

    else:
        return "Low profitability"



def debt_analysis(debt_equity):

    if debt_equity is None:
        return "Debt-to-equity unavailable: equity is zero"

    if debt_equity < 1:
        return "Low financial risk"

    elif debt_equity < 2:
        return "Moderate financial risk"

    else:
        return "High dependence on debt"



def gross_margin_analysis(gross_profit_margin):

    if gross_profit_margin is None:
        return "Gross profit margin unavailable: revenue is zero"

    if gross_profit_margin >= 50:
        return "Strong gross margin"

    elif gross_profit_margin >= 30:
        return "Healthy gross margin"

    else:
        return "Low gross margin"



def roe_analysis(roe):

    if roe is None:
        return "Return on equity unavailable: equity is zero"

    if roe >= 20:
        return "Strong shareholder returns"

    elif roe >= 10:
        return "Moderate shareholder returns"

    else:
        return "Weak shareholder returns"
