import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Image,
    PageBreak,
    Spacer,
    KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from ratios import (
    current_ratio,
    gross_profit_margin,
    net_profit_margin,
    debt_to_equity,
    return_on_equity,
    format_ratio
)
from analysis import (
    liquidity_analysis,
    profitability_analysis,
    debt_analysis,
    gross_margin_analysis,
    roe_analysis
)


def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(
        550,
        20,
        f"Page {page_num}"
    )


st.set_page_config(
    page_title="Financial Ratio Analysis Tool",
    page_icon="📊",
    layout="wide"
)

# ---------------- Read Excel Data ----------------

REQUIRED_ROWS = [
    "Revenue", "Cost of Sales", "Gross Profit", "Net Profit",
    "Current Assets", "Current Liabilities", "Total Debt", "Equity"
]


def load_company_data(source, label):
    """
    Load a company's financial figures from an Excel file.

    Shows a friendly error message and stops the app instead of
    crashing with a raw traceback if the file is missing, unreadable,
    or doesn't have the expected rows/columns.
    """
    try:
        df = pd.read_excel(source)
    except Exception as e:
        st.error(
            f"⚠️ Couldn't read the Excel file for **{label}**. "
            f"Please make sure it's a valid .xlsx file in the expected format.\n\n"
            f"Details: {e}"
        )
        st.stop()

    if df.shape[0] < len(REQUIRED_ROWS):
        st.error(
            f"⚠️ The Excel file for **{label}** doesn't have enough rows.\n\n"
            f"Expected {len(REQUIRED_ROWS)} rows in this order: "
            f"{', '.join(REQUIRED_ROWS)}.\n\n"
            f"Found {df.shape[0]} row(s)."
        )
        st.stop()

    # Accept the year column whether pandas read it as an int (2025) or
    # a string ("2025") — depends on how the source file was saved.
    year_col = None
    for candidate in (2025, "2025"):
        if candidate in df.columns:
            year_col = candidate
            break

    if year_col is None:
        st.error(
            f"⚠️ The Excel file for **{label}** doesn't have a '2025' column.\n\n"
            f"Found columns: {list(df.columns)}"
        )
        st.stop()

    try:
        return {
            "revenue": df.loc[0, year_col],
            "gross_profit": df.loc[2, year_col],
            "net_profit": df.loc[3, year_col],
            "current_assets": df.loc[4, year_col],
            "current_liabilities": df.loc[5, year_col],
            "total_debt": df.loc[6, year_col],
            "equity": df.loc[7, year_col],
        }
    except Exception as e:
        st.error(
            f"⚠️ Couldn't read the expected values from the **{label}** file. "
            f"Details: {e}"
        )
        st.stop()


uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Excel File",
    type=["xlsx"]
)

st.sidebar.caption(
    "Expected format: 8 rows (Revenue, Cost of Sales, Gross Profit, Net "
    "Profit, Current Assets, Current Liabilities, Total Debt, Equity) "
    "with a '2025' column, same layout as Financial_data.xlsx."
)

if uploaded_file is not None:
    company_a = load_company_data(uploaded_file, "Company A (uploaded file)")
else:
    company_a = load_company_data("Financial_data.xlsx", "Company A")

company_b = load_company_data("financial_data_company_b.xlsx", "Company B")

# ---------- Company A ----------
revenue = company_a["revenue"]
gross_profit = company_a["gross_profit"]
net_profit = company_a["net_profit"]
current_assets = company_a["current_assets"]
current_liabilities = company_a["current_liabilities"]
total_debt = company_a["total_debt"]
equity = company_a["equity"]

# ---------- Company B ----------
revenue_b = company_b["revenue"]
gross_profit_b = company_b["gross_profit"]
net_profit_b = company_b["net_profit"]
current_assets_b = company_b["current_assets"]
current_liabilities_b = company_b["current_liabilities"]
total_debt_b = company_b["total_debt"]
equity_b = company_b["equity"]


def generate_pdf():

    doc = SimpleDocTemplate(
        "financial_report.pdf",
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    from reportlab.lib.styles import ParagraphStyle

    title_style = ParagraphStyle(
        "MyTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        alignment=1,
        textColor=colors.darkblue
    )

    styles["Title"].alignment = TA_LEFT
    styles["Heading1"].alignment = TA_LEFT
    styles["Heading2"].alignment = TA_LEFT

    story = []
    story.append(
        Paragraph(
            "<b>Financial Ratio Analysis Report</b>",
            title_style
        )
    )
    from reportlab.graphics.shapes import Drawing, Line

    line = Drawing(450, 10)
    line.add(Line(0, 5, 450, 5))

    story.append(line)
    story.append(Spacer(1, 25))
    story.append(Spacer(1, 80))

    story.append(
        Paragraph(
            "<b>Prepared by:</b> Muniba Ashraf\nBSc (Hons) Accounting & Finance",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            "<b>Report Period:</b> Financial Year 2025",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Date:</b> {datetime.now().strftime('%d %B %Y')}",
            styles["Normal"]
        )
    )

    story.append(PageBreak())

    story.append(
        Paragraph(
            "<b>Financial Ratio Analysis Report</b>",
            styles["Title"]
        )
    )
    story.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d %B %Y')}",
            styles["Normal"]
        )
    )
    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "<b>Executive Summary</b>",
            styles["Heading1"]
        )
    )

    story.append(
        Paragraph(
            f"""
            This report presents a financial analysis of the company's financial
            performance based on the 2025 financial statements.

            The company generated revenue of £{revenue:,} and achieved a net profit
            of £{net_profit:,}. Liquidity, profitability and leverage ratios have
            been calculated to evaluate the company's overall financial health and
            operational efficiency.
            """,
            styles["BodyText"]
        )
    )
    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "<b>Recommendations</b>",
            styles["Heading1"]
        )
    )

    story.append(
        Paragraph(
            """
            • Improve profitability by increasing operating efficiency.<br/>
            • Maintain the current liquidity ratio above 1.5.<br/>
            • Monitor debt levels to avoid excessive financial leverage.<br/>
            • Continue improving shareholder returns through sustainable growth strategies.
            """,
            styles["BodyText"]
        )
    )
    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "<b>Detailed Financial Analysis</b>",
            styles["Heading1"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Revenue:</b> The company generated total revenue of £{revenue:,} during the financial year, indicating the overall level of business activity.",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            f"<b>Gross Profit:</b> Gross profit amounted to £{gross_profit:,}, demonstrating the company's ability to generate profit after direct production costs.",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            f"<b>Net Profit:</b> The company reported a net profit of £{net_profit:,}, showing its profitability after all operating expenses, interest and taxes.",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 8))

    curr_ratio = current_ratio(current_assets, current_liabilities)
    de_ratio = debt_to_equity(total_debt, equity)
    roe = return_on_equity(net_profit, equity)
    gp_margin = gross_profit_margin(gross_profit, revenue)
    np_margin = net_profit_margin(net_profit, revenue)

    story.append(
        Paragraph(
            f"<b>Current Ratio ({format_ratio(curr_ratio)}):</b> A current ratio above 1 indicates that the company has sufficient current assets to meet its short-term liabilities, suggesting a satisfactory liquidity position.",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            f"<b>Debt-to-Equity Ratio ({format_ratio(de_ratio)}):</b> This ratio measures financial leverage. A value of {format_ratio(de_ratio)} indicates that the company uses a moderate level of debt financing relative to shareholders' equity.",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            f"<b>Return on Equity ({format_ratio(roe, suffix='%')}):</b> This ratio measures how effectively the company generates profit from shareholders' investment. A higher percentage indicates stronger financial performance.",
            styles["BodyText"]
        )
    )
    story.append(Spacer(1, 20))
    story.append(
        Paragraph(
            "<b>Financial Ratios</b>",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 10))
    table_data = [
        ["Metric", "Value"],
        ["Revenue", f"{revenue:,}"],
        ["Gross Profit", f"{gross_profit:,}"],
        ["Net Profit", f"{net_profit:,}"],
        ["Current Ratio", format_ratio(curr_ratio)],
        ["Debt to Equity", format_ratio(de_ratio)],
        ["Return on Equity", format_ratio(roe, suffix="%")]
    ]

    table = Table(table_data, colWidths=[220, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # ---------------- Ratio Summary & Interpretation ----------------

    ratio_summary_data = [
        ["Metric", "Value", "Interpretation"],
        ["Current Ratio", format_ratio(curr_ratio), liquidity_analysis(curr_ratio)],
        ["Gross Profit Margin", format_ratio(gp_margin, suffix="%"), gross_margin_analysis(gp_margin)],
        ["Net Profit Margin", format_ratio(np_margin, suffix="%"), profitability_analysis(np_margin)],
        ["Debt to Equity", format_ratio(de_ratio), debt_analysis(de_ratio)],
        ["Return on Equity", format_ratio(roe, suffix="%"), roe_analysis(roe)],
    ]

    ratio_summary_table = Table(
        ratio_summary_data,
        colWidths=[130, 70, 220]
    )
    ratio_summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ]))

    story.append(
        KeepTogether([
            Paragraph("<b>Ratio Summary & Interpretation</b>", styles["Heading2"]),
            Spacer(1, 10),
            ratio_summary_table
        ])
    )
    story.append(Spacer(1, 20))

    # ---------------- Charts ----------------

    money_formatter = FuncFormatter(lambda x, pos: f"£{x:,.0f}")

    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.bar(
        ["Revenue", "Gross Profit", "Net Profit"],
        [revenue, gross_profit, net_profit]
    )
    ax1.set_title("Financial Performance")
    ax1.set_ylabel("Amount (£)")
    ax1.yaxis.set_major_formatter(money_formatter)
    fig1.tight_layout()
    fig1.savefig("chart.png", dpi=300)
    plt.close(fig1)

    story.append(
        KeepTogether([
            Paragraph("<b>Revenue vs Profit</b>", styles["Heading2"]),
            Spacer(1, 8),
            Image("chart.png", width=350, height=250)
        ])
    )
    story.append(Spacer(1, 20))

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar(
        ["Current Assets", "Current Liabilities"],
        [current_assets, current_liabilities],
        color=["#2E7D32", "#C62828"]
    )
    ax2.set_title("Assets vs Liabilities")
    ax2.set_ylabel("Amount (£)")
    ax2.yaxis.set_major_formatter(money_formatter)
    fig2.tight_layout()
    fig2.savefig("chart2.png", dpi=300)
    plt.close(fig2)

    story.append(
        KeepTogether([
            Paragraph("<b>Assets vs Liabilities</b>", styles["Heading2"]),
            Spacer(1, 8),
            Image("chart2.png", width=350, height=250)
        ])
    )
    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "<b>Conclusion</b>",
            styles["Heading1"]
        )
    )

    story.append(
        Paragraph(
            f"""
            The financial analysis indicates that the company maintained a stable
            financial position during 2025. Liquidity remained satisfactory with a
            Current Ratio of {format_ratio(curr_ratio)},
            while the Debt-to-Equity Ratio of {format_ratio(de_ratio)}
            shows moderate financial leverage. The company generated a Return on Equity
            of {format_ratio(roe, suffix='%')}, indicating effective use
            of shareholders' investment. Overall, the company demonstrates healthy
            financial performance and operational efficiency.
            """,
            styles["BodyText"]
        )
    )
    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )


# ---------------- Sidebar ----------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a page",
    [
        "Home",
        "Ratio Analysis",
        "Company Comparison",
        "Financial Report"
    ]
)

# ---------------- Home ----------------

if page == "Home":

    st.title("📊 Financial Ratio Analysis Tool")

    st.markdown("""
## Welcome!

This application performs:

- 📈 Liquidity Analysis
- 💰 Profitability Analysis
- 🏦 Solvency Analysis
- 📊 Company Comparison
- 📄 Financial Report Generation

---

Developed by **Muniba Ashraf**
""")

## ---------------- Ratio Analysis ----------------

elif page == "Ratio Analysis":

    st.title("📈 Ratio Analysis Dashboard")

    curr_ratio = current_ratio(current_assets, current_liabilities)
    gp_margin = gross_profit_margin(gross_profit, revenue)
    np_margin = net_profit_margin(net_profit, revenue)
    de_ratio = debt_to_equity(total_debt, equity)
    roe = return_on_equity(net_profit, equity)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Current Ratio",
            format_ratio(curr_ratio)
        )

        st.metric(
            "Gross Profit Margin",
            format_ratio(gp_margin, suffix="%")
        )

    with col2:
        st.metric(
            "Debt to Equity",
            format_ratio(de_ratio)
        )

        st.metric(
            "Return on Equity",
            format_ratio(roe, suffix="%")
        )

    st.divider()

    st.subheader("📋 Financial Insights")

    st.success(liquidity_analysis(curr_ratio))

    st.info(profitability_analysis(np_margin))

    st.warning(debt_analysis(de_ratio))

    st.divider()

    st.subheader("📊 Financial Performance")

    chart_option = st.selectbox(
        "Choose a chart",
        [
            "Revenue vs Profit",
            "Assets vs Liabilities",
            "Debt vs Equity"
        ]
    )

    if chart_option == "Revenue vs Profit":

        chart_data = pd.DataFrame(
            {
                "Amount": [
                    revenue,
                    gross_profit,
                    net_profit
                ]
            },
            index=[
                "Revenue",
                "Gross Profit",
                "Net Profit"
            ]
        )

    elif chart_option == "Assets vs Liabilities":

        chart_data = pd.DataFrame(
            {
                "Amount": [
                    current_assets,
                    current_liabilities
                ]
            },
            index=[
                "Current Assets",
                "Current Liabilities"
            ]
        )

    elif chart_option == "Debt vs Equity":

        chart_data = pd.DataFrame(
            {
                "Amount": [
                    total_debt,
                    equity
                ]
            },
            index=[
                "Total Debt",
                "Equity"
            ]
        )

    # Show the chart for ALL options
    st.bar_chart(chart_data)

# ---------------- Company Comparison ----------------

elif page == "Company Comparison":

    st.title("📊 Company Comparison")

    comparison_df = pd.DataFrame({
        "Company A": [
            revenue,
            gross_profit,
            net_profit,
            current_assets,
            current_liabilities,
            total_debt,
            equity
        ],
        "Company B": [
            revenue_b,
            gross_profit_b,
            net_profit_b,
            current_assets_b,
            current_liabilities_b,
            total_debt_b,
            equity_b
        ]
    },
        index=[
            "Revenue",
            "Gross Profit",
            "Net Profit",
            "Current Assets",
            "Current Liabilities",
            "Total Debt",
            "Equity"
    ])

    st.subheader("Financial Comparison")
    st.dataframe(comparison_df, width="stretch")

    st.subheader("Comparison Chart")

    chart_metric = st.selectbox(
        "Select Metric",
        comparison_df.index
    )

    chart_df = pd.DataFrame(
        {
            "Amount": comparison_df.loc[chart_metric]
        }
    )

    st.bar_chart(chart_df)

    # ---------------- Ratio Comparison ----------------

    st.divider()
    st.subheader("📐 Ratio Comparison")

    ratio_comparison_df = pd.DataFrame({
        "Company A": [
            format_ratio(current_ratio(current_assets, current_liabilities)),
            format_ratio(gross_profit_margin(gross_profit, revenue), suffix="%"),
            format_ratio(net_profit_margin(net_profit, revenue), suffix="%"),
            format_ratio(debt_to_equity(total_debt, equity)),
            format_ratio(return_on_equity(net_profit, equity), suffix="%"),
        ],
        "Company B": [
            format_ratio(current_ratio(current_assets_b, current_liabilities_b)),
            format_ratio(gross_profit_margin(gross_profit_b, revenue_b), suffix="%"),
            format_ratio(net_profit_margin(net_profit_b, revenue_b), suffix="%"),
            format_ratio(debt_to_equity(total_debt_b, equity_b)),
            format_ratio(return_on_equity(net_profit_b, equity_b), suffix="%"),
        ]
    }, index=[
        "Current Ratio",
        "Gross Profit Margin",
        "Net Profit Margin",
        "Debt to Equity",
        "Return on Equity"
    ])

    st.dataframe(ratio_comparison_df, width="stretch")
    st.caption(
        "Ratios use different scales (multiples vs. percentages), so they're "
        "shown as a table rather than a single chart to avoid a misleading comparison."
    )

    # ---------------- Financial Report ----------------

elif page == "Financial Report":

    st.title("📄 Financial Report")

    if st.button("Generate PDF Report"):

        with st.spinner("Generating PDF report..."):
            generate_pdf()

        with open("financial_report.pdf", "rb") as pdf_file:

            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_file,
                file_name="financial_report.pdf",
                mime="application/pdf"
            )

        st.success("✅ Report generated successfully!")
