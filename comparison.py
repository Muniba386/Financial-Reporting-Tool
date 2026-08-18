import pandas as pd


data = pd.read_excel(
    "Financial_data.xlsx",
    sheet_name="comparison"
)


print(data)


for index, row in data.iterrows():

    company = row["Company"]
    profit = row["Net Profit"]

    print(company, "Net Profit:", profit)