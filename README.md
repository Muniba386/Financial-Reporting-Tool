# 📊 Financial Ratio Analysis Tool

An interactive Streamlit application that analyses a company's financial statements, calculates a full professional-scale set of liquidity, profitability, efficiency, leverage and returns ratios, compares two companies side by side, and generates a professional PDF report — built to combine practical Python skills with an Accounting & Finance background.

**Developed by Muniba Ashraf** — BSc (Hons) Accounting & Finance, First Class Honours, Liverpool John Moores University.

## Features

- **Ratio Analysis Dashboard** — five headline metrics (Current Ratio, Net Profit Margin, Inventory Turnover, Debt-to-Equity, Return on Equity), each with a plain-English interpretation (e.g. "Strong liquidity position"), plus a **Full Ratio Breakdown** covering all 21 ratios the tool calculates, grouped by category.
- **Company Comparison** — compares raw financial figures and the full ratio set for two companies side by side, category by category.
- **Financial Report (PDF)** — a polished, multi-page report with a cover page, executive summary, recommendations, a detailed ratio-by-ratio write-up, a Ratio Summary table with interpretations, a Full Ratio Breakdown table, two charts (Revenue vs Profit, Assets vs Liabilities), and — when a second company is uploaded — a comparison appendix with the full ratio set for both. Generated with ReportLab.
- **Upload almost any financial statement** — Excel (`.xlsx`/`.xls`), CSV, or a text-based PDF. Rows can be in any order, account names can be worded differently ("Turnover" instead of "Revenue", "Debtors" instead of "Accounts Receivable", etc.), and the year column can be named anything containing a 4-digit year (e.g. `2024`, `FY2025`). See "How file detection works" below.
- **Editable review step** — every detected figure is shown in an editable field on the Home page, grouped the way an accountant would read a set of statements (Income Statement / Current Assets & Liabilities / Other Balance Sheet), along with what it was matched from and how confident the match was, so you can fix anything the detector got wrong before calculating ratios or generating the report.
- **Friendly error handling** — if an uploaded file is missing rows, missing a year column, is a scanned (non-text) PDF, or is otherwise malformed, the app shows a clear message and lets you fill in the figures manually instead of crashing. Ratios that need a figure your statement doesn't report simply show **N/A** rather than a misleading number.

## Getting started

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

## How file detection works

The app looks for up to 15 line items in whatever file you upload. **8 core fields** (Revenue, Cost of Sales, Gross Profit, Net Profit, Current Assets, Current Liabilities, Total Debt, Equity) are what most basic financial statements report, and are needed for the 5 headline ratios. **7 optional fields** unlock the rest of the professional ratio set but aren't reported by every statement, so the app never treats their absence as a failed upload.

| Item | Optional? | Also recognised as |
|---|---|---|
| Revenue | | Total Revenue, Sales, Turnover, Net Sales, Sales Revenue |
| Cost of Sales | | Cost of Goods Sold, COGS, Cost of Revenue |
| Gross Profit | | Gross Income, Gross Margin |
| Operating Profit (EBIT) | ✓ | EBIT, Profit from Operations, Operating Income |
| Net Profit | | Net Income, Profit for the Year, Profit After Tax, Net Earnings |
| Interest Expense | ✓ | Finance Costs, Interest Payable |
| Inventory | ✓ | Inventories, Stock |
| Accounts Receivable | ✓ | Trade Receivables, Debtors |
| Cash & Cash Equivalents | ✓ | Cash and Bank, Cash at Bank |
| Current Assets | | Total Current Assets |
| Accounts Payable | ✓ | Trade Payables, Creditors |
| Current Liabilities | | Total Current Liabilities |
| Total Assets | ✓ | Total Assets Employed |
| Total Debt | | Total Liabilities, Total Borrowings, Long-term Debt |
| Equity | | Total Equity, Shareholders' Equity, Stockholders Equity, Net Assets |

Detection works like this:
1. **File type** — `.xlsx`/`.xls` and `.csv` are read directly; `.pdf` files have their tables extracted (text-based PDFs only — a scanned image PDF won't have a table to extract, and you'll be prompted to enter figures manually).
2. **Label column** — whichever column has the most text (not numbers) is treated as the line-item names.
3. **Year column** — the app looks for a column header containing a 4-digit year (e.g. `2025`, `FY2024`) and picks the most recent one. If no year is found, it falls back to whichever column has the most numeric values.
4. **Row matching** — each row's label is fuzzy-matched against the synonym list above to identify which of the 15 metrics it is. If Gross Profit isn't found but Revenue and Cost of Sales are, it's calculated automatically.
5. **Review** — on the Home page, every detected value is shown in an editable field, grouped by Income Statement / Current Assets & Liabilities / Other Balance Sheet, along with the row it was matched from and a confidence score, so you can correct anything before it feeds into the ratios or PDF report.

A warning only appears when the **core** fields can't be matched — a file missing only the optional ones (which is normal) won't be flagged. Ratios that need a missing optional figure simply show **N/A** instead of a number.

`Financial_data.xlsx` and `financial_data_company_b.xlsx` are the bundled sample files (Company A and Company B) used if you don't upload anything.

## Project structure

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit application (all pages + PDF report generation) |
| `data_extraction.py` | Flexible file parsing — detects line items and years in arbitrary Excel/CSV/PDF files |
| `ratios.py` | Ratio calculation functions (liquidity, profitability, efficiency, leverage, returns) |
| `analysis.py` | Plain-English interpretation of each headline ratio |
| `main.py`, `comparison.py`, `report.py` | Earlier command-line prototypes kept for reference |
| `Financial_data.xlsx`, `financial_data_company_b.xlsx` | Sample data for Company A and Company B |

## Ratios calculated

**Liquidity**
- **Current Ratio** = Current Assets ÷ Current Liabilities
- **Quick Ratio (Acid-Test)** = (Current Assets − Inventory) ÷ Current Liabilities
- **Cash Ratio** = Cash ÷ Current Liabilities
- **Working Capital** = Current Assets − Current Liabilities

**Profitability**
- **Gross Profit Margin** = Gross Profit ÷ Revenue × 100
- **Operating Profit Margin** = Operating Profit ÷ Revenue × 100
- **Net Profit Margin** = Net Profit ÷ Revenue × 100

**Efficiency**
- **Debtor (Receivables) Turnover** = Revenue ÷ Accounts Receivable
- **Debtor Days** = (Accounts Receivable ÷ Revenue) × 365
- **Inventory Turnover** = Cost of Sales ÷ Inventory
- **Inventory Days** = (Inventory ÷ Cost of Sales) × 365
- **Creditor (Payables) Turnover** = Cost of Sales ÷ Accounts Payable
- **Creditor Days** = (Accounts Payable ÷ Cost of Sales) × 365
- **Asset Turnover** = Revenue ÷ Total Assets

**Leverage**
- **Debt-to-Equity** = Total Debt ÷ Equity
- **Debt Ratio** = Total Debt ÷ Total Assets
- **Equity Ratio** = Equity ÷ Total Assets
- **Interest Coverage Ratio** = Operating Profit ÷ Interest Expense

**Returns**
- **Return on Equity** = Net Profit ÷ Equity × 100
- **Return on Assets** = Net Profit ÷ Total Assets × 100
- **Return on Capital Employed** = Operating Profit ÷ (Total Assets − Current Liabilities) × 100

## Roadmap / possible next steps

- Multi-year trend analysis (pick from all detected years, not just the most recent)
- Benchmarking against industry-average ratios
- OCR support for scanned (image-only) PDF statements
