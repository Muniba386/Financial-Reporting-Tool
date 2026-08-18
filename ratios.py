# ---------------- Liquidity ----------------

def current_ratio(current_assets, current_liabilities):
    if current_liabilities == 0:
        return None
    return current_assets / current_liabilities


def quick_ratio(current_assets, inventory, current_liabilities):
    """Acid-test ratio — current assets excluding inventory, since stock
    can't always be turned into cash quickly enough to cover short-term
    liabilities."""
    if current_liabilities == 0:
        return None
    return (current_assets - inventory) / current_liabilities


def cash_ratio(cash, current_liabilities):
    if current_liabilities == 0:
        return None
    return cash / current_liabilities


def working_capital(current_assets, current_liabilities):
    """An absolute currency amount, not a ratio — always defined, no
    division involved."""
    return current_assets - current_liabilities


# ---------------- Profitability ----------------

def gross_profit_margin(gross_profit, revenue):
    if revenue == 0:
        return None
    return (gross_profit / revenue) * 100


def operating_profit_margin(operating_profit, revenue):
    if revenue == 0:
        return None
    return (operating_profit / revenue) * 100


def net_profit_margin(net_profit, revenue):
    if revenue == 0:
        return None
    return (net_profit / revenue) * 100


# ---------------- Efficiency ----------------

def debtor_turnover(revenue, accounts_receivable):
    """How many times a year receivables are collected, on average."""
    if accounts_receivable == 0:
        return None
    return revenue / accounts_receivable


def debtor_days(revenue, accounts_receivable):
    """Average number of days it takes to collect payment from customers."""
    if revenue == 0:
        return None
    return (accounts_receivable / revenue) * 365


def inventory_turnover(cost_of_sales, inventory):
    if inventory == 0:
        return None
    return cost_of_sales / inventory


def inventory_days(cost_of_sales, inventory):
    """Average number of days stock sits before being sold."""
    if cost_of_sales == 0:
        return None
    return (inventory / cost_of_sales) * 365


def creditor_turnover(cost_of_sales, accounts_payable):
    if accounts_payable == 0:
        return None
    return cost_of_sales / accounts_payable


def creditor_days(cost_of_sales, accounts_payable):
    """Average number of days taken to pay suppliers."""
    if cost_of_sales == 0:
        return None
    return (accounts_payable / cost_of_sales) * 365


def asset_turnover(revenue, total_assets):
    """How efficiently assets are being used to generate revenue."""
    if total_assets == 0:
        return None
    return revenue / total_assets


# ---------------- Leverage / Gearing ----------------

def debt_to_equity(total_debt, equity):
    if equity == 0:
        return None
    return total_debt / equity


def debt_ratio(total_debt, total_assets):
    """Proportion of assets financed by debt rather than equity."""
    if total_assets == 0:
        return None
    return total_debt / total_assets


def equity_ratio(equity, total_assets):
    """Proportion of assets financed by shareholders' equity."""
    if total_assets == 0:
        return None
    return equity / total_assets


def interest_coverage_ratio(operating_profit, interest_expense):
    """How many times over operating profit could cover the interest
    bill — a low number signals the company may struggle to service its
    debt."""
    if interest_expense == 0:
        return None
    return operating_profit / interest_expense


# ---------------- Returns ----------------

def return_on_equity(net_profit, equity):
    if equity == 0:
        return None
    return (net_profit / equity) * 100


def return_on_assets(net_profit, total_assets):
    if total_assets == 0:
        return None
    return (net_profit / total_assets) * 100


def return_on_capital_employed(operating_profit, total_assets, current_liabilities):
    """Return on the long-term capital actually invested in the
    business (total assets less short-term liabilities)."""
    capital_employed = total_assets - current_liabilities
    if capital_employed == 0:
        return None
    return (operating_profit / capital_employed) * 100


def format_ratio(value, decimals=2, suffix=""):
    """Format a ratio value for display, showing 'N/A' if it couldn't
    be calculated (e.g. division by zero)."""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}{suffix}"
