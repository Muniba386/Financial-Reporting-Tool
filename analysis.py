"""
Plain-English interpretation of each ratio.

Every function returns a (message, severity) tuple rather than a bare
string. `severity` is one of "good", "medium", "bad", "unavailable" — the
caller (the Streamlit app) uses it to choose how the message is displayed
(a green success box, a blue info box, and so on), so the colour on screen
always matches what the message is actually saying instead of being fixed
to whichever ratio happens to sit in which slot.
"""


def liquidity_analysis(current_ratio):

    if current_ratio is None:
        return "Current ratio unavailable: current liabilities are zero", "unavailable"

    if current_ratio >= 1.5:
        return "Strong liquidity position", "good"

    elif current_ratio >= 1:
        return "Acceptable liquidity position", "medium"

    else:
        return "Liquidity risk: company may struggle to pay short-term debts", "bad"



def profitability_analysis(net_profit_margin):

    if net_profit_margin is None:
        return "Net profit margin unavailable: revenue is zero", "unavailable"

    if net_profit_margin >= 20:
        return "Excellent profitability", "good"

    elif net_profit_margin >= 10:
        return "Good profitability", "medium"

    else:
        return "Low profitability", "bad"



def debt_analysis(debt_equity):

    if debt_equity is None:
        return "Debt-to-equity unavailable: equity is zero", "unavailable"

    if debt_equity < 1:
        return "Low financial risk", "good"

    elif debt_equity < 2:
        return "Moderate financial risk", "medium"

    else:
        return "High dependence on debt", "bad"



def gross_margin_analysis(gross_profit_margin):

    if gross_profit_margin is None:
        return "Gross profit margin unavailable: revenue is zero", "unavailable"

    if gross_profit_margin >= 50:
        return "Strong gross margin", "good"

    elif gross_profit_margin >= 30:
        return "Healthy gross margin", "medium"

    else:
        return "Low gross margin", "bad"



def roe_analysis(roe):

    if roe is None:
        return "Return on equity unavailable: equity is zero", "unavailable"

    if roe >= 20:
        return "Strong shareholder returns", "good"

    elif roe >= 10:
        return "Moderate shareholder returns", "medium"

    else:
        return "Weak shareholder returns", "bad"
