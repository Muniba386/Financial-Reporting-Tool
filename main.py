import pandas as pd
from analysis import (
    liquidity_analysis,
    profitability_analysis,
    debt_analysis
)

from report import print_report
from ratios import (
    current_ratio,
    gross_profit_margin,
    net_profit_margin,
    debt_to_equity,
    return_on_equity
)

data = pd.read_excel("Financial_data.xlsx")
# print(data)

revenue = data.loc[0,2025]
gross_profit = data.loc[2,2025]
net_profit = data.loc[3,2025]
current_assets = data.loc[4,2025]
current_liabilities = data.loc[5,2025]
total_debt = data.loc[6,2025]
equity = data.loc[7,2025]


print("Financial Ratio Analysis")
print("------------------------")

print("Current Ratio:",
      current_ratio(current_assets, current_liabilities))

print("Gross Profit Margin:",
      gross_profit_margin(gross_profit, revenue), "%")

print("Net Profit Margin:",
      net_profit_margin(net_profit, revenue), "%")

print("Debt to Equity:",
      debt_to_equity(total_debt, equity))

print("Return on Equity:",
      return_on_equity(net_profit, equity), "%")
print("\nFinancial Insights")
print("------------------")

print(liquidity_analysis(
    current_ratio(current_assets, current_liabilities)
))

print(profitability_analysis(
    net_profit_margin(net_profit, revenue)
))

print(debt_analysis(
    debt_to_equity(total_debt, equity)
))


print_report(
    "Company A",
    current_ratio(current_assets, current_liabilities),
    net_profit_margin(net_profit, revenue),
    debt_to_equity(total_debt, equity),
    return_on_equity(net_profit, equity)
)