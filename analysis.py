"""
Financial interpretation of each ratio, written in the register of a
professional financial analysis report rather than plain conversational
English.

Every "headline" function (liquidity_analysis, profitability_analysis, etc.)
returns a (headline, detail, severity) 3-tuple:
  - headline: a short banded label ("Sound Liquidity Position")
  - detail: a hedged, one-sentence interpretation that states the actual
    number's real-world meaning ("£1.71 of current assets for every £1 of
    current liabilities") without declaring the company flatly "good" or
    "bad". A ratio in isolation does not establish that; industry norms and
    the trend over time matter too, so the wording says so rather than
    implying a verdict.
  - severity: one of "good", "medium", "bad", "unavailable". The caller
    (the Streamlit app / PDF report) uses it to choose how the message is
    displayed, so the colour on screen always matches what the message is
    actually saying instead of being fixed to whichever ratio happens to
    sit in which slot.

interpret_ratio() below covers the full 18-ratio set (including ones with
no dedicated headline function above) with a shorter emoji-badge and
one-line read, used for the per-row captions in the "Full Ratio Breakdown"
table, where a full paragraph per ratio would be too dense.
"""


def liquidity_analysis(current_ratio, currency="£"):
    if current_ratio is None:
        return (
            "Current Ratio Not Calculable",
            "Current liabilities are recorded as zero, so this ratio cannot be calculated.",
            "unavailable",
        )

    if current_ratio >= 1.5:
        return (
            "Sound Liquidity Position",
            f"The current ratio of {current_ratio:.2f} indicates that the company holds "
            f"{currency}{current_ratio:.2f} of current assets for every {currency}1.00 of "
            f"current liabilities. This suggests the company is well placed to meet its "
            f"short-term obligations as they fall due, although the position should still "
            f"be considered alongside sector norms and the trend across recent reporting "
            f"periods.",
            "good",
        )
    elif current_ratio >= 1:
        return (
            "Adequate Liquidity Position",
            f"Current assets exceed current liabilities ({currency}{current_ratio:.2f} to "
            f"{currency}1.00), although the margin of safety is modest. This level is "
            f"generally regarded as adequate rather than strong, and would benefit from "
            f"being monitored over subsequent reporting periods.",
            "medium",
        )
    else:
        return (
            "Liquidity Position Requires Attention",
            f"Current liabilities exceed current assets ({currency}{current_ratio:.2f} of "
            f"current assets for every {currency}1.00 of current liabilities), which may "
            f"indicate pressure on short-term cash flow. A ratio below 1.00 is not unusual "
            f"in sectors with rapid inventory turnover or advance customer payment, so this "
            f"finding should be read in that context.",
            "bad",
        )


def profitability_analysis(net_profit_margin, currency="£"):
    if net_profit_margin is None:
        return (
            "Net Profit Margin Not Calculable",
            "Revenue is recorded as zero, so this margin cannot be calculated.",
            "unavailable",
        )

    if net_profit_margin >= 20:
        return (
            "Strong Net Profit Margin",
            f"A net profit margin of {net_profit_margin:.1f}% indicates that, for every "
            f"{currency}100 of revenue, approximately {currency}{net_profit_margin:.0f} is "
            f"retained as profit after all operating costs, finance costs and taxation. "
            f"This is a strong margin by general standards, although what constitutes a "
            f"strong margin varies considerably between sectors.",
            "good",
        )
    elif net_profit_margin >= 10:
        return (
            "Satisfactory Net Profit Margin",
            f"A net profit margin of {net_profit_margin:.1f}% indicates that approximately "
            f"{currency}{net_profit_margin:.0f} of every {currency}100 of revenue is "
            f"retained as profit. This is a satisfactory margin, best assessed against "
            f"comparable companies in the same sector and the company's own trend over time.",
            "medium",
        )
    else:
        return (
            "Net Profit Margin Below Sector Norms",
            f"A net profit margin of {net_profit_margin:.1f}% indicates that only around "
            f"{currency}{net_profit_margin:.0f} of every {currency}100 of revenue is "
            f"retained as profit. This may reflect the cost structure, pricing policy or "
            f"nature of the sector, and is best assessed by comparison with industry peers "
            f"rather than in isolation.",
            "bad",
        )


def debt_analysis(debt_equity, currency="£"):
    if debt_equity is None:
        return (
            "Gearing Not Calculable",
            "Shareholders' equity is recorded as zero, so this ratio cannot be calculated.",
            "unavailable",
        )

    if debt_equity < 1:
        return (
            "Conservative Gearing",
            f"The gearing (debt-to-equity) ratio of {debt_equity:.2f} indicates "
            f"{currency}{debt_equity:.2f} of total debt for every {currency}1.00 of "
            f"shareholders' equity, meaning the company relies more heavily on shareholder "
            f"funding than on borrowing. This is generally associated with lower financial "
            f"risk, although the appropriate level of gearing varies by sector and stage of "
            f"growth.",
            "good",
        )
    elif debt_equity < 2:
        return (
            "Moderate Gearing",
            f"The gearing (debt-to-equity) ratio stands at {debt_equity:.2f}, representing "
            f"{currency}{debt_equity:.2f} of debt for every {currency}1.00 of equity. This "
            f"is a moderate level of financial risk that warrants monitoring as the company "
            f"grows, particularly with reference to sector norms.",
            "medium",
        )
    else:
        return (
            "Elevated Gearing",
            f"The gearing (debt-to-equity) ratio of {debt_equity:.2f} indicates a "
            f"comparatively heavy reliance on debt financing relative to shareholders' "
            f"equity. This increases financial risk, particularly should profitability or "
            f"interest rates move unfavourably, although capital-intensive sectors often "
            f"operate with materially higher gearing as standard practice.",
            "bad",
        )


def gross_margin_analysis(gross_profit_margin, currency="£"):
    if gross_profit_margin is None:
        return (
            "Gross Profit Margin Not Calculable",
            "Revenue is recorded as zero, so this margin cannot be calculated.",
            "unavailable",
        )

    if gross_profit_margin >= 50:
        return (
            "Strong Gross Margin",
            f"A gross profit margin of {gross_profit_margin:.1f}% indicates that "
            f"approximately {currency}{gross_profit_margin:.0f} of every {currency}100 of "
            f"revenue remains after direct production and service costs. A high gross "
            f"margin generally provides greater capacity to absorb overheads, although "
            f"typical margins differ substantially between industries.",
            "good",
        )
    elif gross_profit_margin >= 30:
        return (
            "Satisfactory Gross Margin",
            f"A gross profit margin of {gross_profit_margin:.1f}% indicates that "
            f"approximately {currency}{gross_profit_margin:.0f} of every {currency}100 of "
            f"revenue remains after direct costs. This is a satisfactory margin, best "
            f"assessed against sector norms.",
            "medium",
        )
    else:
        return (
            "Gross Margin Below Sector Norms",
            f"A gross profit margin of {gross_profit_margin:.1f}% indicates that only "
            f"around {currency}{gross_profit_margin:.0f} of every {currency}100 of revenue "
            f"remains after direct costs. This can reflect pricing policy, input costs, or "
            f"the nature of the business model, and sector context should be taken into "
            f"account when assessing it.",
            "bad",
        )


def roe_analysis(roe, currency="£"):
    if roe is None:
        return (
            "Return on Equity Not Calculable",
            "Shareholders' equity is recorded as zero, so this ratio cannot be calculated.",
            "unavailable",
        )

    if roe >= 20:
        return (
            "Strong Return on Equity",
            f"A return on equity of {roe:.1f}% indicates that, for every {currency}100 of "
            f"shareholders' equity, approximately {currency}{roe:.0f} of profit was "
            f"generated over the period. This is a strong return by general standards, "
            f"although it should be weighed against the level of risk and gearing employed "
            f"to achieve it.",
            "good",
        )
    elif roe >= 10:
        return (
            "Moderate Return on Equity",
            f"A return on equity of {roe:.1f}% indicates that approximately "
            f"{currency}{roe:.0f} of profit was generated for every {currency}100 of "
            f"shareholders' equity. This is a moderate return, best compared against "
            f"similar companies operating in the same sector.",
            "medium",
        )
    else:
        return (
            "Return on Equity Below Sector Norms",
            f"A return on equity of {roe:.1f}% indicates that only around "
            f"{currency}{roe:.0f} of profit was generated for every {currency}100 of "
            f"shareholders' equity. This may reflect the company's stage, sector or current "
            f"performance, and is best read alongside profitability and gearing rather than "
            f"in isolation.",
            "bad",
        )


def efficiency_analysis(inventory_turnover):
    """Headline interpretation for the Efficiency category, based on how
    many times a year inventory is sold and replaced. Rule-of-thumb bands
    like the other headline metrics; actual "good" turnover varies
    considerably by industry, so this is a general guide, not a fixed
    standard."""
    if inventory_turnover is None:
        return (
            "Inventory Turnover Not Calculable",
            "This ratio requires both Cost of Sales and Inventory, and one or both were "
            "not provided.",
            "unavailable",
        )

    if inventory_turnover >= 8:
        return (
            "Efficient Inventory Management",
            f"Inventory turns over approximately {inventory_turnover:.1f} times per year, "
            f"suggesting efficient stock management. A very high turnover in some sectors "
            f"can also reflect thin buffer stock, so this figure is best read alongside the "
            f"trend over recent periods.",
            "good",
        )
    elif inventory_turnover >= 4:
        return (
            "Moderate Inventory Turnover",
            f"Inventory turns over approximately {inventory_turnover:.1f} times per year, "
            f"a moderate pace best judged against typical turnover for the sector.",
            "medium",
        )
    else:
        return (
            "Slow-Moving Inventory",
            f"Inventory turns over approximately {inventory_turnover:.1f} times per year, "
            f"which can indicate overstocking or softer sales. Certain industries, such as "
            f"capital goods, normally carry slower-turning stock as standard practice.",
            "bad",
        )


# ---------------------------------------------------------------------
# Lightweight per-row interpretation for the Full Ratio Breakdown table
# ---------------------------------------------------------------------
#
# One line, not a paragraph. A table of 18 ratios needs a scannable badge
# and short read, not the fuller narrative the headline functions above
# give. Each entry: (thresholds, emoji, short-phrase, severity), evaluated
# in order; "higher_is_better" flips whether we walk the bands from the top
# (ratio/turnover-style metrics) or the bottom (gearing/"days" metrics
# where a smaller number is generally the less risky one). Metrics with no
# generally-agreed direction (e.g. creditor days, where taking longer to
# pay suppliers is a cash-flow policy choice, not simply "worse") get a
# neutral, purely descriptive read instead of a good/bad banding.

RATIO_BANDS = {
    "current_ratio": (True, [(1.5, "🟢", "Sound liquidity"), (1.0, "🟡", "Adequate liquidity"), (0, "🔴", "Liquidity may be constrained")]),
    "quick_ratio": (True, [(1.0, "🟢", "Sound position independent of stock"), (0.7, "🟡", "Adequate, limited buffer"), (0, "🔴", "Relies heavily on inventory realisation")]),
    "cash_ratio": (True, [(0.5, "🟢", "Strong cash buffer"), (0.2, "🟡", "Modest cash buffer"), (0, "🔴", "Thin cash buffer")]),
    "gross_profit_margin": (True, [(50, "🟢", "Strong gross margin"), (30, "🟡", "Satisfactory gross margin"), (0, "🔴", "Below typical gross margins")]),
    "operating_profit_margin": (True, [(15, "🟢", "Strong operating margin"), (8, "🟡", "Satisfactory operating margin"), (0, "🔴", "Below typical operating margins")]),
    "net_profit_margin": (True, [(20, "🟢", "Strong net margin"), (10, "🟡", "Satisfactory net margin"), (0, "🔴", "Below typical net margins")]),
    "inventory_turnover": (True, [(8, "🟢", "Efficient inventory management"), (4, "🟡", "Moderate turnover"), (0, "🔴", "Slow-moving inventory")]),
    "debtor_turnover": (True, [(8, "🟢", "Collects receivables promptly"), (4, "🟡", "Moderate collection pace"), (0, "🔴", "Slow to collect receivables")]),
    "asset_turnover": (True, [(1.0, "🟢", "Efficient asset utilisation"), (0.5, "🟡", "Moderate asset utilisation"), (0, "🔴", "Assets generating comparatively little revenue")]),
    "return_on_equity": (True, [(20, "🟢", "Strong return to shareholders"), (10, "🟡", "Moderate return to shareholders"), (0, "🔴", "Below typical shareholder returns")]),
    "return_on_assets": (True, [(10, "🟢", "Strong return on assets"), (5, "🟡", "Moderate return on assets"), (0, "🔴", "Below typical returns on assets")]),
    "return_on_capital_employed": (True, [(15, "🟢", "Strong return on capital employed"), (8, "🟡", "Moderate return on capital employed"), (0, "🔴", "Below typical returns on capital employed")]),
    "interest_coverage_ratio": (True, [(5, "🟢", "Comfortable interest cover"), (2, "🟡", "Adequate interest cover"), (0, "🔴", "Thin interest cover")]),
    "debt_to_equity": (False, [(1.0, "🟢", "Conservative gearing"), (2.0, "🟡", "Moderate gearing"), (999999, "🔴", "Elevated gearing")]),
    "debt_ratio": (False, [(0.3, "🟢", "Low reliance on debt financing"), (0.6, "🟡", "Moderate reliance on debt financing"), (999999, "🔴", "High reliance on debt financing")]),
    "debtor_days": (False, [(30, "🟢", "Prompt collection period"), (60, "🟡", "Typical collection period"), (999999, "🔴", "Extended collection period")]),
}

# Metrics deliberately given a neutral, non-judgemental read rather than a
# good/bad band. "Better" is not well-defined for these without knowing the
# company's working-capital strategy or capital structure by design (for
# example, the equity ratio is simply the mirror of the debt ratio, and
# creditor days / inventory days reflect a policy choice as much as a
# performance signal).
NEUTRAL_METRICS = {
    "working_capital", "equity_ratio", "inventory_days", "creditor_turnover", "creditor_days",
}


def ratio_direction(metric_key, first_value, last_value):
    """For the multi-year trend view: compares a ratio's earliest vs most
    recent available value and returns (arrow, label, severity). Uses the
    same higher-is-better convention as RATIO_BANDS where one is defined
    (e.g. net profit margin rising is "Improving"); for metrics with no
    generally-agreed direction (working capital's absolute size, creditor
    days reflecting a payment-terms choice, etc.) it reports a neutral
    "Increased/Decreased" rather than implying better-or-worse. Returns
    None if either value is missing, so the caller can show "N/A"."""
    if first_value is None or last_value is None:
        return None

    delta = last_value - first_value
    # A small relative (or, near zero, absolute) tolerance before calling
    # something "stable", to avoid a trend arrow flipping on noise like
    # 1.700 versus 1.703.
    tolerance = max(abs(first_value) * 0.02, 0.01)
    if abs(delta) <= tolerance:
        return "➡️", "Stable", "info"

    rising = delta > 0
    if metric_key in NEUTRAL_METRICS or metric_key not in RATIO_BANDS:
        return ("↑", "Increased", "info") if rising else ("↓", "Decreased", "info")

    higher_is_better, _bands = RATIO_BANDS[metric_key]
    improving = rising if higher_is_better else not rising
    return ("📈", "Improving", "good") if improving else ("📉", "Declining", "bad")


def is_higher_better(metric_key):
    """True/False if this ratio has a generally-agreed "better" direction
    (per RATIO_BANDS), None if it is context-dependent (see
    NEUTRAL_METRICS). Used by the user-defined benchmark comparison to
    phrase "above benchmark" as favourable or unfavourable rather than
    just "different"."""
    if metric_key in NEUTRAL_METRICS or metric_key not in RATIO_BANDS:
        return None
    return RATIO_BANDS[metric_key][0]


def interpret_ratio(metric_key, value):
    """Returns (emoji, short_phrase, severity) for the Full Ratio Breakdown
    table. metric_key matches the keys used in ratios.py / compute_ratio_set
    (e.g. "current_ratio", "debt_to_equity"). Falls back to a neutral,
    no-judgement read for anything not explicitly banded above, so every
    row gets something rather than only a subset looking interpreted."""
    if value is None:
        return "⚪", "Not enough data to calculate", "unavailable"

    if metric_key in NEUTRAL_METRICS or metric_key not in RATIO_BANDS:
        return "⚪", "Context-dependent: compare against prior periods or sector norms", "info"

    higher_is_better, bands = RATIO_BANDS[metric_key]
    if higher_is_better:
        for threshold, emoji, phrase in bands:
            if value >= threshold:
                return emoji, phrase, {"🟢": "good", "🟡": "medium", "🔴": "bad"}[emoji]
        return bands[-1][1], bands[-1][2], "bad"
    else:
        for threshold, emoji, phrase in bands:
            if value <= threshold:
                return emoji, phrase, {"🟢": "good", "🟡": "medium", "🔴": "bad"}[emoji]
        return bands[-1][1], bands[-1][2], "bad"
