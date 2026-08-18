# 📊 Financial Ratio Analysis Tool

An interactive Streamlit application that analyses a company's financial statements, calculates key liquidity, profitability and leverage ratios, compares two companies side by side, and generates a professional PDF report — built to combine practical Python skills with an Accounting & Finance background.

**Developed by Muniba Ashraf** — BSc (Hons) Accounting & Finance, First Class Honours, Liverpool John Moores University.

## Features

- **Ratio Analysis Dashboard** — Current Ratio, Gross Profit Margin, Net Profit Margin, Debt-to-Equity, and Return on Equity, each with a plain-English interpretation (e.g. "Strong liquidity position").
- **Company Comparison** — compares raw financial figures and computed ratios for two companies side by side.
- **Financial Report (PDF)** — a polished, multi-page report with a cover page, executive summary, recommendations, a detailed ratio-by-ratio write-up, a Ratio Summary table with interpretations, two charts (Revenue vs Profit, Assets vs Liabilities), and a conclusion — generated with ReportLab.
- **Upload your own data** — swap in any company's figures via the sidebar Excel uploader, as long as it follows the expected format below.
- **Friendly error handling** — if an uploaded file is missing rows, missing the expected year column, or otherwise malformed, the app shows a clear message instead of crashing.

## Getting started

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

## Expected Excel format

`Financial_data.xlsx` (and any file you upload) should have 8 rows, in this order, with a `2025` column:

| Item | 2025 |
|---|---|
| Revenue | ... |
| Cost of Sales | ... |
| Gross Profit | ... |
| Net Profit | ... |
| Current Assets | ... |
| Current Liabilities | ... |
| Total Debt | ... |
| Equity | ... |

`financial_data_company_b.xlsx` provides the second company shown in the Company Comparison page.

## Project structure

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit application (all pages + PDF report generation) |
| `ratios.py` | Ratio calculation functions (current ratio, margins, D/E, ROE) |
| `analysis.py` | Plain-English interpretation of each ratio |
| `main.py`, `comparison.py`, `report.py` | Earlier command-line prototypes kept for reference |
| `Financial_data.xlsx`, `financial_data_company_b.xlsx` | Sample data for Company A and Company B |

## Ratios calculated

- **Current Ratio** = Current Assets ÷ Current Liabilities
- **Gross Profit Margin** = Gross Profit ÷ Revenue × 100
- **Net Profit Margin** = Net Profit ÷ Revenue × 100
- **Debt-to-Equity** = Total Debt ÷ Equity
- **Return on Equity** = Net Profit ÷ Equity × 100

## Roadmap / possible next steps

- Multi-year trend analysis (the data already has a 2024 column ready to use)
- Benchmarking against industry-average ratios
- Editable inputs directly in the UI, without needing an Excel file
- Deploy to Streamlit Community Cloud for a live demo link
