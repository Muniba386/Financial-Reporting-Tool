# 📊 Financial Ratio Analysis Tool

An interactive Streamlit application that analyses a company's financial statements, calculates key liquidity, profitability and leverage ratios, compares two companies side by side, and generates a professional PDF report — built to combine practical Python skills with an Accounting & Finance background.

**Developed by Muniba Ashraf** — BSc (Hons) Accounting & Finance, First Class Honours, Liverpool John Moores University.

## Features

- **Ratio Analysis Dashboard** — Current Ratio, Gross Profit Margin, Net Profit Margin, Debt-to-Equity, and Return on Equity, each with a plain-English interpretation (e.g. "Strong liquidity position").
- **Company Comparison** — compares raw financial figures and computed ratios for two companies side by side.
- **Financial Report (PDF)** — a polished, multi-page report with a cover page, executive summary, recommendations, a detailed ratio-by-ratio write-up, a Ratio Summary table with interpretations, two charts (Revenue vs Profit, Assets vs Liabilities), and a conclusion — generated with ReportLab.
- **Upload almost any financial statement** — Excel (`.xlsx`/`.xls`), CSV, or a text-based PDF. Rows can be in any order, account names can be worded differently ("Turnover" instead of "Revenue", "Shareholders' Equity" instead of "Equity", etc.), and the year column can be named anything containing a 4-digit year (e.g. `2024`, `FY2025`). See "How file detection works" below.
- **Editable review step** — every detected figure is shown in an editable field on the Home page, along with what it was matched from and how confident the match was, so you can fix anything the detector got wrong before calculating ratios or generating the report.
- **Friendly error handling** — if an uploaded file is missing rows, missing a year column, is a scanned (non-text) PDF, or is otherwise malformed, the app shows a clear message and lets you fill in the figures manually instead of crashing.

## Getting started

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

## How file detection works

The app looks for these 8 line items in whatever file you upload:

| Item | Also recognised as |
|---|---|
| Revenue | Total Revenue, Sales, Turnover, Net Sales, Sales Revenue |
| Cost of Sales | Cost of Goods Sold, COGS, Cost of Revenue |
| Gross Profit | Gross Income, Gross Margin |
| Net Profit | Net Income, Profit for the Year, Profit After Tax, Net Earnings |
| Current Assets | Total Current Assets |
| Current Liabilities | Total Current Liabilities |
| Total Debt | Total Liabilities, Total Borrowings, Long-term Debt |
| Equity | Total Equity, Shareholders' Equity, Stockholders Equity, Net Assets |

Detection works like this:
1. **File type** — `.xlsx`/`.xls` and `.csv` are read directly; `.pdf` files have their tables extracted (text-based PDFs only — a scanned image PDF won't have a table to extract, and you'll be prompted to enter figures manually).
2. **Label column** — whichever column has the most text (not numbers) is treated as the line-item names.
3. **Year column** — the app looks for a column header containing a 4-digit year (e.g. `2025`, `FY2024`) and picks the most recent one. If no year is found, it falls back to whichever column has the most numeric values.
4. **Row matching** — each row's label is fuzzy-matched against the synonym list above to identify which of the 8 metrics it is. If Gross Profit isn't found but Revenue and Cost of Sales are, it's calculated automatically.
5. **Review** — on the Home page, every detected value is shown in an editable field along with the row it was matched from and a confidence score, so you can correct anything before it feeds into the ratios or PDF report.

If a file doesn't match well (unusual wording, a currency symbol the parser doesn't recognise, etc.), the fields will just show 0.00 or a low-confidence match — simply type in the correct figures and everything downstream (ratios, charts, PDF) will use your edited values.

`Financial_data.xlsx` and `financial_data_company_b.xlsx` are the bundled sample files (Company A and Company B) used if you don't upload anything.

## Project structure

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit application (all pages + PDF report generation) |
| `data_extraction.py` | Flexible file parsing — detects line items and years in arbitrary Excel/CSV/PDF files |
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

- Multi-year trend analysis (pick from all detected years, not just the most recent)
- Benchmarking against industry-average ratios
- OCR support for scanned (image-only) PDF statements
