def current_ratio(current_assets, current_liabilities):
    if current_liabilities == 0:
        return None
    return current_assets / current_liabilities


def gross_profit_margin(gross_profit, revenue):
    if revenue == 0:
        return None
    return (gross_profit / revenue) * 100


def net_profit_margin(net_profit, revenue):
    if revenue == 0:
        return None
    return (net_profit / revenue) * 100


def debt_to_equity(total_debt, equity):
    if equity == 0:
        return None
    return total_debt / equity


def return_on_equity(net_profit, equity):
    if equity == 0:
        return None
    return (net_profit / equity) * 100


def format_ratio(value, decimals=2, suffix=""):
    """Format a ratio value for display, showing 'N/A' if it couldn't
    be calculated (e.g. division by zero)."""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}{suffix}"
