"""
Plain-English interpretation of each ratio.

Every "headline" function (liquidity_analysis, profitability_analysis, etc.)
returns a (headline, detail, severity) 3-tuple:
  - headline: a short banded label ("Comfortable liquidity position")
  - detail: a hedged, one-sentence interpretation that states the actual
    number's real-world meaning ("£1.71 of current assets for every £1 of
    current liabilities") without declaring the company flatly "good" or
    "bad" — a ratio in isolation doesn't establish that; industry norms and
    the trend over time matter too, so the wording says so rather than
    implying a verdict.
  - severity: one of "good", "medium", "bad", "unavailable" — the caller
    (the Streamlit app / PDF report) uses it to choose how the message is
    displayed, so the colour on screen always matches what the message is
    actually saying instead of being fixed to whichever ratio happens to
    sit in which slot.

interpret_ratio() below covers the full 18-ratio set (including ones with
no dedicated headline function above) with a shorter emoji-badge + one-line
read — used for the per-row captions in the "Full Ratio Breakdown" table,
where a full paragraph per ratio would be too dense.
"""


def liquidity_analysis(current_ratio, currency="£"):
    if current_ratio is None:
        return "Current ratio unavailable", "Current liabilities are zero, so this ratio can't be calculated.", "unavailable"

    if current_ratio >= 1.5:
        return (
            "Comfortable liquidity position",
            f"The company holds {currency}{current_ratio:.2f} of current assets for every {currency}1 of "
            f"current liabilities. This suggests a reasonably comfortable short-term "
            f"liquidity position, though interpretation should still consider industry "
            f"norms and the trend over recent periods.",
            "good",
        )
    elif current_ratio >= 1:
        return (
            "Adequate liquidity position",
            f"Current assets exceed current liabilities ({currency}{current_ratio:.2f} to {currency}1), but "
            f"the margin is modest. This is generally considered adequate rather than "
            f"strong — worth watching alongside the trend over time.",
            "medium",
        )
    else:
        return (
            "Liquidity position warrants attention",
            f"Current liabilities exceed current assets ({currency}{current_ratio:.2f} of current "
            f"assets for every {currency}1 of current liabilities), which can point to short-term "
            f"cash-flow pressure. That said, a ratio below 1 isn't unusual in some "
            f"industries with fast inventory or cash cycles.",
            "bad",
        )


def profitability_analysis(net_profit_margin, currency="£"):
    if net_profit_margin is None:
        return "Net profit margin unavailable", "Revenue is zero, so this margin can't be calculated.", "unavailable"

    if net_profit_margin >= 20:
        return (
            "Strong net profit margin",
            f"For every {currency}100 of revenue, roughly {currency}{net_profit_margin:.0f} is retained as "
            f"net profit after all costs. This is a strong margin by most general "
            f"standards, although what counts as strong varies considerably by sector.",
            "good",
        )
    elif net_profit_margin >= 10:
        return (
            "Sound net profit margin",
            f"Roughly {currency}{net_profit_margin:.0f} of every {currency}100 of revenue is retained as "
            f"net profit — a reasonable margin, best read alongside industry peers and "
            f"the company's own trend over time.",
            "medium",
        )
    else:
        return (
            "Net profit margin below typical benchmarks",
            f"Only around {currency}{net_profit_margin:.0f} of every {currency}100 of revenue is retained "
            f"as net profit. This may reflect higher costs, pricing pressure, or simply "
            f"a lower-margin sector — worth comparing against industry peers rather than "
            f"reading in isolation.",
            "bad",
        )


def debt_analysis(debt_equity, currency="£"):
    if debt_equity is None:
        return "Debt-to-equity unavailable", "Equity is zero, so this ratio can't be calculated.", "unavailable"

    if debt_equity < 1:
        return (
            "Conservative leverage",
            f"Total debt is {currency}{debt_equity:.2f} for every {currency}1 of equity, meaning the "
            f"company relies more on shareholder funding than borrowing. This generally "
            f"points to lower financial risk, though the appropriate level of leverage "
            f"varies considerably by industry and growth stage.",
            "good",
        )
    elif debt_equity < 2:
        return (
            "Moderate leverage",
            f"Debt stands at {currency}{debt_equity:.2f} for every {currency}1 of equity — a moderate "
            f"level of financial risk that's worth monitoring as the business grows, "
            f"particularly against sector norms.",
            "medium",
        )
    else:
        return (
            "Elevated leverage",
            f"Debt is {currency}{debt_equity:.2f} for every {currency}1 of equity, indicating a heavier "
            f"reliance on debt financing. This increases financial risk, particularly if "
            f"profits or interest rates move unfavourably — though capital-intensive "
            f"industries often operate with materially higher gearing as a matter of "
            f"course.",
            "bad",
        )


def gross_margin_analysis(gross_profit_margin, currency="£"):
    if gross_profit_margin is None:
        return "Gross profit margin unavailable", "Revenue is zero, so this margin can't be calculated.", "unavailable"

    if gross_profit_margin >= 50:
        return (
            "Strong gross margin",
            f"About {currency}{gross_profit_margin:.0f} of every {currency}100 of revenue remains after "
            f"direct production/service costs. A high gross margin generally leaves more "
            f"room to cover overheads, though typical margins differ substantially "
            f"between industries.",
            "good",
        )
    elif gross_profit_margin >= 30:
        return (
            "Healthy gross margin",
            f"About {currency}{gross_profit_margin:.0f} of every {currency}100 of revenue remains after "
            f"direct costs — a reasonable margin, best judged against sector norms.",
            "medium",
        )
    else:
        return (
            "Gross margin below typical benchmarks",
            f"Only around {currency}{gross_profit_margin:.0f} of every {currency}100 of revenue remains "
            f"after direct costs. This can reflect pricing, input costs, or a "
            f"lower-margin business model — context from the sector matters here.",
            "bad",
        )


def roe_analysis(roe, currency="£"):
    if roe is None:
        return "Return on equity unavailable", "Equity is zero, so this ratio can't be calculated.", "unavailable"

    if roe >= 20:
        return (
            "Strong shareholder returns",
            f"For every {currency}100 of shareholders' equity, roughly {currency}{roe:.0f} of profit was "
            f"generated over the period. This is a strong return by general standards, "
            f"though it should be weighed against the level of risk and leverage taken "
            f"on to achieve it.",
            "good",
        )
    elif roe >= 10:
        return (
            "Moderate shareholder returns",
            f"Roughly {currency}{roe:.0f} of profit was generated for every {currency}100 of shareholders' "
            f"equity — a moderate return, best compared against similar companies in the "
            f"same sector.",
            "medium",
        )
    else:
        return (
            "Shareholder returns below typical benchmarks",
            f"Only around {currency}{roe:.0f} of profit was generated for every {currency}100 of "
            f"shareholders' equity. This may reflect the business's stage, sector, or "
            f"current performance — worth reading alongside profitability and leverage "
            f"together rather than in isolation.",
            "bad",
        )


def efficiency_analysis(inventory_turnover):
    """Headline interpretation for the Efficiency category, based on how
    many times a year inventory is sold and replaced. Rule-of-thumb bands
    like the other headline metrics — actual "good" turnover varies a lot
    by industry, so this is a general guide, not a fixed standard."""
    if inventory_turnover is None:
        return (
            "Inventory turnover unavailable",
            "Needs Cost of Sales and Inventory, which weren't both provided.",
            "unavailable",
        )

    if inventory_turnover >= 8:
        return (
            "Fast-moving inventory",
            f"Inventory turns over roughly {inventory_turnover:.1f} times a year, "
            f"suggesting efficient stock management — though very high turnover in some "
            f"sectors can also reflect thin buffer stock, so it's worth reading alongside "
            f"the trend.",
            "good",
        )
    elif inventory_turnover >= 4:
        return (
            "Moderate inventory turnover",
            f"Inventory turns over roughly {inventory_turnover:.1f} times a year — a "
            f"moderate pace, best judged against typical turnover for the sector.",
            "medium",
        )
    else:
        return (
            "Slow-moving inventory",
            f"Inventory turns over roughly {inventory_turnover:.1f} times a year, which "
            f"can indicate overstocking or softer sales — although some industries "
            f"(e.g. capital goods) normally carry slower-turning stock as a matter of "
            f"course.",
            "bad",
        )


# ---------------------------------------------------------------------
# Lightweight per-row interpretation for the Full Ratio Breakdown table
# ---------------------------------------------------------------------
#
# One line, not a paragraph — a table of 18 ratios needs a scannable badge
# and short read, not the fuller narrative the 5 headline cards above give.
# Each entry: (thresholds, emoji, short-phrase, severity), evaluated in
# order; "higher_is_better" flips whether we walk the bands from the top
# (ratio/turnover-style metrics) or the bottom (leverage/"days" metrics
# where a smaller number is generally the less risky one). Metrics with no
# generally-agreed direction (e.g. creditor days, where taking longer to
# pay suppliers is a cash-flow choice, not simply "worse") get a neutral,
# purely descriptive read instead of a good/bad banding.

RATIO_BANDS = {
    "current_ratio": (True, [(1.5, "🟢", "Comfortable liquidity"), (1.0, "🟡", "Adequate liquidity"), (0, "🔴", "Liquidity may be tight")]),
    "quick_ratio": (True, [(1.0, "🟢", "Comfortable without relying on stock"), (0.7, "🟡", "Adequate, limited buffer"), (0, "🔴", "Relies heavily on inventory/short-term assets")]),
    "cash_ratio": (True, [(0.5, "🟢", "Strong cash buffer"), (0.2, "🟡", "Modest cash buffer"), (0, "🔴", "Thin cash buffer")]),
    "gross_profit_margin": (True, [(50, "🟢", "Strong gross margin"), (30, "🟡", "Reasonable gross margin"), (0, "🔴", "Below typical gross margins")]),
    "operating_profit_margin": (True, [(15, "🟢", "Strong operating margin"), (8, "🟡", "Reasonable operating margin"), (0, "🔴", "Below typical operating margins")]),
    "net_profit_margin": (True, [(20, "🟢", "Strong net margin"), (10, "🟡", "Reasonable net margin"), (0, "🔴", "Below typical net margins")]),
    "inventory_turnover": (True, [(8, "🟢", "Fast-moving inventory"), (4, "🟡", "Moderate turnover"), (0, "🔴", "Slow-moving inventory")]),
    "debtor_turnover": (True, [(8, "🟢", "Collects receivables quickly"), (4, "🟡", "Moderate collection pace"), (0, "🔴", "Slow to collect receivables")]),
    "asset_turnover": (True, [(1.0, "🟢", "Efficient asset use"), (0.5, "🟡", "Moderate asset use"), (0, "🔴", "Assets generating relatively little revenue")]),
    "return_on_equity": (True, [(20, "🟢", "Strong return to shareholders"), (10, "🟡", "Moderate return to shareholders"), (0, "🔴", "Below typical shareholder returns")]),
    "return_on_assets": (True, [(10, "🟢", "Strong return on assets"), (5, "🟡", "Moderate return on assets"), (0, "🔴", "Below typical returns on assets")]),
    "return_on_capital_employed": (True, [(15, "🟢", "Strong return on capital employed"), (8, "🟡", "Moderate return on capital employed"), (0, "🔴", "Below typical returns on capital employed")]),
    "interest_coverage_ratio": (True, [(5, "🟢", "Comfortable interest cover"), (2, "🟡", "Adequate interest cover"), (0, "🔴", "Thin interest cover")]),
    "debt_to_equity": (False, [(0.5, "🟢", "Conservative leverage"), (1.5, "🟡", "Moderate leverage"), (999999, "🔴", "Elevated leverage")]),
    "debt_ratio": (False, [(0.3, "🟢", "Low reliance on debt financing"), (0.6, "🟡", "Moderate reliance on debt financing"), (999999, "🔴", "High reliance on debt financing")]),
    "debtor_days": (False, [(30, "🟢", "Collects payment quickly"), (60, "🟡", "Typical collection period"), (999999, "🟡", "Longer collection period")]),
}

# Metrics deliberately given a neutral, non-judgemental read rather than a
# good/bad band — "better" isn't well-defined for these without knowing the
# company's working-capital strategy or capital structure by design (e.g.
# equity ratio is simply the mirror of debt ratio, and creditor days /
# inventory days reflect a policy choice as much as a performance signal).
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
    # something "stable" — avoids a trend arrow flipping on noise like
    # 1.700 vs 1.703.
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
    (per RATIO_BANDS), None if it's context-dependent (see NEUTRAL_METRICS)
    — used by the user-defined benchmark comparison to phrase "above
    benchmark" as favourable or unfavourable rather than just "different"."""
    if metric_key in NEUTRAL_METRICS or metric_key not in RATIO_BANDS:
        return None
    return RATIO_BANDS[metric_key][0]


def interpret_ratio(metric_key, value):
    """Returns (emoji, short_phrase, severity) for the Full Ratio Breakdown
    table. metric_key matches the keys used in ratios.py / compute_ratio_set
    (e.g. "current_ratio", "debt_to_equity"). Falls back to a neutral,
    no-judgement read for anything not explicitly banded above, so every
    row gets *something* rather than only a subset looking interpreted."""
    if value is None:
        return "⚪", "Not enough data to calculate", "unavailable"

    if metric_key in NEUTRAL_METRICS or metric_key not in RATIO_BANDS:
        return "⚪", "Context-dependent — compare against prior periods or sector norms", "info"

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
