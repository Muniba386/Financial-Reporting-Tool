import re

import streamlit as st
import pandas as pd
import altair as alt
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

# ---------------- Brand / Theme ----------------

NAVY = "#0B1F3A"
NAVY_LIGHT = "#16345C"
NAVY_SOFT = "#EEF2F8"
GOLD = "#B08D2E"
GOLD_LIGHT = "#D9B44A"
MUTED = "#6B7280"


def inject_custom_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        h1, h2, h3 {{
            font-family: 'Playfair Display', Georgia, serif !important;
            color: {NAVY} !important;
        }}

        [data-testid="stAppViewContainer"] {{
            background-color: #FBFBFC;
        }}

        /* ---- Sidebar ---- */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {NAVY} 0%, {NAVY_LIGHT} 100%);
        }}
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
            color: #E7ECF5 !important;
        }}
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
            background-color: #FFFFFF;
            border: 1px dashed rgba(255,255,255,0.35);
            border-radius: 10px;
        }}
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {{
            color: {NAVY} !important;
        }}
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {{
            background-color: {GOLD} !important;
            color: #FFFFFF !important;
            border: none !important;
        }}
        [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] {{
            color: {NAVY} !important;
            background-color: #FFFFFF;
            border-radius: 8px;
        }}
        [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] * {{
            color: {NAVY} !important;
        }}
        [data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,0.15);
        }}
        [data-testid="stSidebar"] [role="radiogroup"] label {{
            padding: 0.35rem 0.6rem;
            border-radius: 6px;
        }}
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {{
            background-color: rgba(255,255,255,0.08);
        }}

        /* ---- Buttons ---- */
        .stButton > button, .stDownloadButton > button {{
            background-color: {GOLD};
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.55rem 1.4rem;
            transition: background-color 0.15s ease;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            background-color: #96771F;
            color: #FFFFFF;
        }}

        /* ---- Metrics ---- */
        [data-testid="stMetricValue"] {{
            color: {NAVY};
            font-weight: 700;
        }}
        [data-testid="stMetricLabel"] {{
            color: {MUTED};
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-size: 0.78rem;
            font-weight: 600;
        }}

        /* ---- Bordered containers as cards ---- */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 12px !important;
            box-shadow: 0 1px 4px rgba(11,31,58,0.08);
        }}

        /* ---- Alerts ---- */
        [data-testid="stAlert"] {{
            border-radius: 10px;
        }}

        /* ---- Dataframes ---- */
        [data-testid="stDataFrame"] {{
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #E7EAF0;
        }}

        hr {{
            border-color: #E5E9F0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title, subtitle, icon="📊"):
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {NAVY} 0%, {NAVY_LIGHT} 100%);
                    padding: 2rem 2.4rem; border-radius: 14px; margin-bottom: 1.6rem;
                    box-shadow: 0 6px 20px rgba(11,31,58,0.22);">
          <div style="color:{GOLD_LIGHT}; font-size:0.8rem; letter-spacing:0.16em;
                      text-transform:uppercase; font-weight:700;">
            {icon} Financial Ratio Analysis Tool
          </div>
          <div style="color:#FFFFFF; font-family:'Playfair Display', Georgia, serif;
                      font-size:2.15rem; font-weight:700; margin-top:0.35rem; line-height:1.2;">
            {title}
          </div>
          <div style="color:#C3CCDC; font-size:1rem; margin-top:0.5rem;">
            {subtitle}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_bar_chart(data, color=GOLD, height=320):
    """Render a styled Altair bar chart from a single-column DataFrame
    whose index holds the category names (matches the shape previously
    passed to st.bar_chart throughout this app)."""
    df = data.reset_index()
    df.columns = ["Category", "Amount"]
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, size=54)
        .encode(
            x=alt.X("Category:N", sort=None, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Amount:Q", title="Amount (£)", axis=alt.Axis(format=",.0f")),
            color=alt.value(color),
            tooltip=[
                alt.Tooltip("Category:N", title="Item"),
                alt.Tooltip("Amount:Q", title="Amount", format=",.0f"),
            ],
        )
        .properties(height=height)
        .configure_axis(gridColor="#EEF1F5", domainColor="#D8DEE9", tickColor="#D8DEE9")
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, width="stretch")


inject_custom_css()

# ---------------- Read Financial Data (flexible upload) ----------------

from data_extraction import extract_financial_data, METRIC_LABELS

METRICS = list(METRIC_LABELS.keys())


def sync_company_data(prefix, uploaded_file, default_path, label):
    """
    Runs auto-detection only when the uploaded file actually changes (not
    on every rerun), and seeds st.session_state[f"{prefix}_values"] — a
    plain dict, not a widget-bound key — with the detected values.

    Using a plain dict (rather than reading widget keys directly) matters
    because Streamlit clears a widget's session_state entry whenever that
    widget isn't rendered in a given script run (e.g. after navigating
    away from the Home page). Storing values in an ordinary dict keeps
    them available on every page regardless of which widgets are visible.
    """
    if uploaded_file is not None:
        file_key = f"{uploaded_file.name}:{uploaded_file.size}"
        source, filename = uploaded_file, uploaded_file.name
    else:
        file_key = "__default__"
        source, filename = default_path, default_path

    state_key = f"{prefix}_file_key"
    if st.session_state.get(state_key) != file_key:
        values, meta = extract_financial_data(source, filename)
        st.session_state[state_key] = file_key
        st.session_state[f"{prefix}_meta"] = meta or {}
        st.session_state[f"{prefix}_extract_error"] = (meta or {}).get("error")
        st.session_state[f"{prefix}_values"] = {
            metric: float((values or {}).get(metric, 0.0)) for metric in METRICS
        }

    if f"{prefix}_values" not in st.session_state:
        st.session_state[f"{prefix}_values"] = {metric: 0.0 for metric in METRICS}


def company_values(prefix):
    return dict(st.session_state[f"{prefix}_values"])


def render_data_review(prefix, title):
    error = st.session_state.get(f"{prefix}_extract_error")
    if error:
        st.warning(f"⚠️ {error}")

    meta = st.session_state.get(f"{prefix}_meta", {})
    match_info = meta.get("match_info", {})
    if meta.get("detected_year"):
        other_years = [y for y in meta.get("available_years", []) if y != meta["detected_year"]]
        years_note = f" · detected year: **{meta['detected_year']}**"
        if other_years:
            years_note += f" (also found: {other_years} — edit figures below if you'd rather use a different year)"
        st.caption(f"Source column: **{meta.get('value_column', '?')}**{years_note}")

    values = st.session_state[f"{prefix}_values"]
    # Widget keys include the current file identity so that uploading a new
    # file creates fresh widgets with the newly-detected values. Without
    # this, Streamlit would keep showing each field's *previous* value —
    # passing a new `value=` to an existing widget key is ignored once
    # that key already has a stored value.
    file_key = st.session_state.get(f"{prefix}_file_key", "default")
    key_suffix = re.sub(r"[^a-zA-Z0-9_]", "_", str(file_key))

    cols = st.columns(2)
    for i, metric in enumerate(METRICS):
        with cols[i % 2]:
            new_val = st.number_input(
                METRIC_LABELS[metric],
                value=float(values.get(metric, 0.0)),
                key=f"widget_{prefix}_{metric}_{key_suffix}",
                step=1000.0,
                format="%.2f"
            )
            values[metric] = new_val
            info = match_info.get(metric)
            if info:
                st.caption(f"Matched \"{info['matched_label']}\" ({info['confidence']*100:.0f}% confidence)")
            else:
                st.caption("Not detected — enter manually")
    st.session_state[f"{prefix}_values"] = values


uploaded_file_a = st.sidebar.file_uploader(
    "📂 Upload Company A file",
    type=["xlsx", "xls", "csv", "pdf"],
    key="uploader_a"
)
uploaded_file_b = st.sidebar.file_uploader(
    "📂 Upload Company B file (optional)",
    type=["xlsx", "xls", "csv", "pdf"],
    key="uploader_b"
)

st.sidebar.caption(
    "Works with almost any financial statement — Excel, CSV, or a "
    "text-based PDF. Row order and exact account names don't need to "
    "match; figures are auto-detected and shown for review on the Home "
    "page before anything is calculated, so you can fix anything that "
    "wasn't picked up correctly."
)

sync_company_data("a", uploaded_file_a, "Financial_data.xlsx", "Company A")
sync_company_data("b", uploaded_file_b, "financial_data_company_b.xlsx", "Company B")

company_a = company_values("a")
company_b = company_values("b")

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

    BRAND_NAVY = colors.HexColor("#0B1F3A")
    BRAND_GOLD = colors.HexColor("#B08D2E")
    BRAND_SOFT = colors.HexColor("#F4F6FA")

    title_style = ParagraphStyle(
        "MyTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        alignment=1,
        textColor=BRAND_NAVY
    )

    styles["Title"].alignment = TA_LEFT
    styles["Title"].textColor = BRAND_NAVY
    styles["Heading1"].alignment = TA_LEFT
    styles["Heading1"].textColor = BRAND_NAVY
    styles["Heading2"].alignment = TA_LEFT
    styles["Heading2"].textColor = BRAND_NAVY

    story = []
    story.append(
        Paragraph(
            "<b>Financial Ratio Analysis Report</b>",
            title_style
        )
    )
    from reportlab.graphics.shapes import Drawing, Line

    line = Drawing(450, 10)
    gold_line = Line(0, 5, 450, 5)
    gold_line.strokeColor = BRAND_GOLD
    gold_line.strokeWidth = 2
    line.add(gold_line)

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

            The company generated revenue of £{revenue:,.0f} and achieved a net profit
            of £{net_profit:,.0f}. Liquidity, profitability and leverage ratios have
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
            f"<b>Revenue:</b> The company generated total revenue of £{revenue:,.0f} during the financial year, indicating the overall level of business activity.",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            f"<b>Gross Profit:</b> Gross profit amounted to £{gross_profit:,.0f}, demonstrating the company's ability to generate profit after direct production costs.",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            f"<b>Net Profit:</b> The company reported a net profit of £{net_profit:,.0f}, showing its profitability after all operating expenses, interest and taxes.",
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
        ["Revenue", f"{revenue:,.0f}"],
        ["Gross Profit", f"{gross_profit:,.0f}"],
        ["Net Profit", f"{net_profit:,.0f}"],
        ["Current Ratio", format_ratio(curr_ratio)],
        ["Debt to Equity", format_ratio(de_ratio)],
        ["Return on Equity", format_ratio(roe, suffix="%")]
    ]

    table = Table(table_data, colWidths=[220, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#D8DEE9")),
        ("BACKGROUND", (0, 1), (-1, -1), BRAND_SOFT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_SOFT]),
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
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#D8DEE9")),
        ("BACKGROUND", (0, 1), (-1, -1), BRAND_SOFT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_SOFT]),
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
    NAVY_HEX = "#0B1F3A"
    GOLD_HEX = "#B08D2E"

    plt.rcParams["font.family"] = "sans-serif"

    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.bar(
        ["Revenue", "Gross Profit", "Net Profit"],
        [revenue, gross_profit, net_profit],
        color=[NAVY_HEX, GOLD_HEX, "#5B7DA6"],
        width=0.55
    )
    ax1.set_title("Financial Performance", fontsize=13, fontweight="bold", color=NAVY_HEX)
    ax1.set_ylabel("Amount (£)")
    ax1.yaxis.set_major_formatter(money_formatter)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.grid(axis="y", color="#E5E9F0", linewidth=0.8, zorder=0)
    ax1.set_axisbelow(True)
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
        color=[NAVY_HEX, GOLD_HEX],
        width=0.45
    )
    ax2.set_title("Assets vs Liabilities", fontsize=13, fontweight="bold", color=NAVY_HEX)
    ax2.set_ylabel("Amount (£)")
    ax2.yaxis.set_major_formatter(money_formatter)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="y", color="#E5E9F0", linewidth=0.8, zorder=0)
    ax2.set_axisbelow(True)
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

    render_hero(
        "Welcome",
        "A polished, ratio-driven view of any company's financial statements — "
        "upload a file, review the detected figures, and generate a client-ready report.",
    )

    feature_cols = st.columns(5)
    features = [
        ("📈", "Liquidity", "Current ratio & short-term health"),
        ("💰", "Profitability", "Margins & earning power"),
        ("🏦", "Solvency", "Leverage & debt exposure"),
        ("📊", "Comparison", "Company A vs. Company B"),
        ("📄", "Reporting", "Boardroom-ready PDF export"),
    ]
    for col, (icon, label, desc) in zip(feature_cols, features):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"<div style='font-size:1.4rem;'>{icon}</div>"
                    f"<div style='font-weight:700; color:{NAVY}; margin-top:0.2rem;'>{label}</div>"
                    f"<div style='color:{MUTED}; font-size:0.82rem; margin-top:0.15rem;'>{desc}</div>",
                    unsafe_allow_html=True,
                )

    st.markdown(
        f"<div style='color:{MUTED}; font-size:0.85rem; margin-top:1.2rem;'>"
        f"Developed by <b style='color:{NAVY};'>Muniba Ashraf</b> · "
        f"BSc (Hons) Accounting &amp; Finance</div>",
        unsafe_allow_html=True,
    )

    st.divider()
    st.header("📥 Your Data")
    st.write(
        "These are the figures detected from your upload (or the sample data "
        "if nothing was uploaded). Everything below is editable — fix anything "
        "that wasn't picked up correctly before moving to the other pages."
    )

    st.subheader("Company A")
    with st.container(border=True):
        render_data_review("a", "Company A")

    with st.expander("Company B (used on the Company Comparison page)"):
        render_data_review("b", "Company B")

## ---------------- Ratio Analysis ----------------

elif page == "Ratio Analysis":

    render_hero(
        "Ratio Analysis Dashboard",
        "Liquidity, profitability and leverage at a glance, calculated from Company A's data.",
        icon="📈",
    )

    curr_ratio = current_ratio(current_assets, current_liabilities)
    gp_margin = gross_profit_margin(gross_profit, revenue)
    np_margin = net_profit_margin(net_profit, revenue)
    de_ratio = debt_to_equity(total_debt, equity)
    roe = return_on_equity(net_profit, equity)

    dashboard_metrics = [
        ("Liquidity", "Current Ratio", format_ratio(curr_ratio)),
        ("Profitability", "Gross Profit Margin", format_ratio(gp_margin, suffix="%")),
        ("Leverage", "Debt to Equity", format_ratio(de_ratio)),
        ("Returns", "Return on Equity", format_ratio(roe, suffix="%")),
    ]
    metric_cols = st.columns(4)
    for col, (tag, label, value) in zip(metric_cols, dashboard_metrics):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"<div style='color:{GOLD}; font-size:0.72rem; letter-spacing:0.08em; "
                    f"text-transform:uppercase; font-weight:700;'>{tag}</div>",
                    unsafe_allow_html=True,
                )
                st.metric(label, value)

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
    render_bar_chart(chart_data)

# ---------------- Company Comparison ----------------

elif page == "Company Comparison":

    render_hero(
        "Company Comparison",
        "Company A against Company B — raw figures and calculated ratios side by side.",
        icon="📊",
    )

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

    render_bar_chart(chart_df, color=NAVY_LIGHT)

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

    render_hero(
        "Financial Report",
        "Generate a polished, multi-page PDF — cover page, executive summary, "
        "ratio analysis and charts — ready to share.",
        icon="📄",
    )

    with st.container(border=True):
        st.markdown(
            f"<div style='font-weight:700; color:{NAVY}; font-size:1.05rem;'>"
            f"Financial Ratio Analysis Report</div>"
            f"<div style='color:{MUTED}; font-size:0.88rem; margin-top:0.25rem;'>"
            f"Includes an executive summary, recommendations, a detailed ratio "
            f"write-up, a summary table with interpretations, and two charts "
            f"(Revenue vs Profit, Assets vs Liabilities).</div>",
            unsafe_allow_html=True,
        )
        st.write("")

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
