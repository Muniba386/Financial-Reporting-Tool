"""
Flexible financial data extraction.

Takes an uploaded file in almost any common shape — Excel/CSV with rows and
columns in a different order than expected, different account-name wording,
a different year column, a table extracted from a PDF, or a full
professional statement spread across several sheets/pages (a separate
Income Statement and Balance Sheet, as real annual reports and Companies
House filings almost always are) — and tries to identify the 15 line items
the app understands:

    revenue, cost_of_sales, gross_profit, operating_profit, net_profit,
    interest_expense, inventory, accounts_receivable, cash, current_assets,
    accounts_payable, current_liabilities, total_assets, total_debt, equity

This is rule-based matching (name-synonym lookup + fuzzy string matching),
not an AI model reading the document, so it won't be perfect on every
possible layout. It's designed to get close on common formats — including
multi-sheet workbooks and multi-page PDFs — and then let the user review
and correct the detected values before anything is calculated. That review
step is what makes it safe to rely on for arbitrary files, not the
auto-detection alone.
"""

import re
import difflib

import pandas as pd

METRIC_SYNONYMS = {
    "revenue": [
        "revenue", "total revenue", "sales", "turnover", "net sales",
        "total sales", "sales revenue", "income from operations"
    ],
    "cost_of_sales": [
        "cost of sales", "cost of goods sold", "cogs", "cost of revenue",
        "cost of sales and services", "total cost of revenue",
        "total cost of sales"
    ],
    "gross_profit": [
        "gross profit", "gross income", "gross margin"
    ],
    "operating_profit": [
        "operating profit", "ebit", "profit from operations",
        "operating income", "earnings before interest and tax",
        "operating profit for the year"
    ],
    "net_profit": [
        "net profit", "net income", "profit for the year",
        "profit after tax", "net earnings", "profit for the period",
        "profit attributable to owners", "net profit for the year",
        "profit/loss for the year"
    ],
    "interest_expense": [
        "interest expense", "finance costs", "finance cost",
        "interest payable", "finance expense", "interest paid"
    ],
    "inventory": [
        "inventory", "inventories", "stock", "closing stock", "stocks"
    ],
    "accounts_receivable": [
        "accounts receivable", "trade receivables", "debtors",
        "trade debtors", "receivables", "trade and other receivables"
    ],
    "cash": [
        "cash", "cash and cash equivalents", "cash and bank",
        "cash at bank", "bank and cash", "cash at bank and in hand"
    ],
    "current_assets": [
        "current assets", "total current assets"
    ],
    "accounts_payable": [
        "accounts payable", "trade payables", "creditors",
        "trade creditors", "payables", "trade and other payables"
    ],
    "current_liabilities": [
        "current liabilities", "total current liabilities"
    ],
    "total_assets": [
        "total assets", "total assets employed"
    ],
    "total_debt": [
        "total debt", "total liabilities", "total borrowings",
        "borrowings", "long term debt", "long-term debt", "total loans",
        "long term loans", "long-term loans", "loans", "bank loans",
        "total liabilities and debt"
    ],
    "equity": [
        "equity", "total equity", "shareholders equity",
        "shareholders' equity", "stockholders equity", "net assets",
        "total shareholders funds", "shareholders funds",
        "total equity attributable to owners"
    ],
}

METRIC_LABELS = {
    "revenue": "Revenue",
    "cost_of_sales": "Cost of Sales",
    "gross_profit": "Gross Profit",
    "operating_profit": "Operating Profit (EBIT)",
    "net_profit": "Net Profit",
    "interest_expense": "Interest Expense",
    "inventory": "Inventory",
    "accounts_receivable": "Accounts Receivable (Debtors)",
    "cash": "Cash & Cash Equivalents",
    "current_assets": "Current Assets",
    "accounts_payable": "Accounts Payable (Creditors)",
    "current_liabilities": "Current Liabilities",
    "total_assets": "Total Assets",
    "total_debt": "Total Debt",
    "equity": "Equity",
}

# Fields that many simpler financial statements won't report at all
# (operating profit, interest expense, inventory, receivables, payables,
# total assets are common omissions from a basic P&L/balance sheet
# extract). Left at 0 with a clear "optional" note in the review UI
# instead of being treated as a matching failure — a file missing only
# these shouldn't trigger the "we couldn't recognize this file" warning.
OPTIONAL_METRICS = {
    "operating_profit", "interest_expense", "inventory",
    "accounts_receivable", "cash", "accounts_payable", "total_assets",
}

YEAR_PATTERN = re.compile(r"(19|20)\d{2}")

MATCH_THRESHOLD = 0.72

# How many rows from the top of a sheet/CSV to scan when looking for the
# real header row (see find_header_row). Professional statements commonly
# have a company-name title, a statement-name subtitle, a date-range line
# and a blank spacer row before the actual "FY2024 / FY2025 / FY2026E"
# column headers — comfortably within this window.
HEADER_SCAN_ROWS = 15


def normalize_label(value):
    text = str(value).lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _label_score(norm_label, synonym):
    syn_norm = normalize_label(synonym)
    if not norm_label or not syn_norm:
        return 0.0
    if norm_label == syn_norm:
        return 1.0
    if syn_norm in norm_label or norm_label in syn_norm:
        return 0.9
    return difflib.SequenceMatcher(None, norm_label, syn_norm).ratio()


def match_rows_to_metrics(row_labels, has_value, threshold=MATCH_THRESHOLD):
    """
    Score every (row, metric) pair and greedily assign each metric to its
    single best-scoring, not-yet-used row. Returns {metric: (row_index, score)}.

    has_value: a list parallel to row_labels — True where that row actually
    has a usable number in the column we're about to read from, False
    otherwise. Rows without a value are excluded from candidacy entirely.
    This matters because real statements are full of bare section headers
    that read exactly like the metric we want ("Revenue", "Current Assets",
    "Stockholders' Equity") sitting just above the actual total line
    ("Total revenue", "Total current assets", "Total stockholders'
    equity") — without this filter, a blank header can win the text-match
    tie-break and then get permanently assigned to that metric with a
    None value, silently blocking the real total line from ever being
    matched at all.
    """
    candidates = []
    for idx, label in enumerate(row_labels):
        if not has_value[idx]:
            continue
        norm = normalize_label(label)
        if not norm:
            continue
        for metric, synonyms in METRIC_SYNONYMS.items():
            best_for_row_metric = max(_label_score(norm, syn) for syn in synonyms)
            # Small tie-break nudge toward "Total X" lines over component
            # sub-lines with similar wording (e.g. "Total revenue" over
            # "Product revenue" / "Service revenue", "Total current
            # assets" over a component like "Inventory") — a real
            # statement's grand-total line is almost always what a ratio
            # calculation wants, not one piece of it.
            if norm.startswith("total "):
                best_for_row_metric += 0.03
            if best_for_row_metric >= threshold:
                candidates.append((best_for_row_metric, idx, metric))

    candidates.sort(key=lambda c: -c[0])

    used_rows = set()
    used_metrics = set()
    assigned = {}
    for score, idx, metric in candidates:
        if idx in used_rows or metric in used_metrics:
            continue
        used_rows.add(idx)
        used_metrics.add(metric)
        assigned[metric] = (idx, score)

    return assigned


def detect_year_columns(columns):
    """Return [(original_column, year_int), ...] sorted most-recent first."""
    found = []
    for col in columns:
        match = YEAR_PATTERN.search(str(col))
        if match:
            found.append((col, int(match.group(0))))
    found.sort(key=lambda c: -c[1])
    return found


def find_header_row(raw_rows, max_scan=HEADER_SCAN_ROWS):
    """
    raw_rows: a list of rows (no header assumed — row 0 is just whatever
    the first row of the sheet/CSV happens to be) as returned by e.g.
    pd.read_excel(..., header=None).values.tolist().

    Real financial statements almost always have a company name, a
    statement title, and a "For the year ended ..." line above the actual
    column-header row — blindly treating row 0 as the header (pandas'
    default) misreads all of that as data and leaves the real "FY2024 /
    FY2025 / FY2026E" row buried as an ordinary line item, which is why
    year-column detection was failing on well-formatted professional
    statements. This scans the first few rows for the one with the most
    year-like cells ("FY2024", "2024", "Dec-2024", "2024 (£)") — the
    strongest, most common signal for a statement's real header row — and
    returns its 0-based index. Falls back to 0 (pandas' own default) if no
    row in the scan window has any year-like cell at all, so already-clean
    files (e.g. a plain "Item, 2024" CSV) behave exactly as before.
    """
    best_idx, best_hits = 0, 0
    for i, row in enumerate(raw_rows[:max_scan]):
        hits = 0
        for v in row:
            if v is None:
                continue
            text = str(v).strip()
            if not text or text.lower() == "nan":
                continue
            if YEAR_PATTERN.search(text):
                hits += 1
        if hits > best_hits:
            best_hits = hits
            best_idx = i
    return best_idx


def reframe_with_header(raw_df, header_row):
    """Re-slice a header=None DataFrame so row `header_row` becomes the
    column headers and everything after it becomes the data — the same
    shape pd.read_excel(..., header=N) would produce, but computed after
    the fact once find_header_row has located the real header row."""
    header_values = raw_df.iloc[header_row].tolist()
    df = raw_df.iloc[header_row + 1:].copy()
    cleaned_cols = []
    for i, c in enumerate(header_values):
        if c is None or (isinstance(c, float) and pd.isna(c)) or str(c).strip() == "":
            cleaned_cols.append(f"col{i}")
        else:
            cleaned_cols.append(c)
    df.columns = cleaned_cols
    return df.reset_index(drop=True)


def _to_number(raw):
    if raw is None:
        return None
    # pandas represents a blank cell as float('nan'), not None — and
    # nan IS an instance of float, so without this check a blank cell
    # was silently treated as "the number nan" instead of "no value
    # here", which let bare section-header rows (blank in every year
    # column) pass the has_value filter in match_rows_to_metrics and
    # win a metric with a NaN result instead of being correctly skipped
    # in favour of the row with the real total.
    if isinstance(raw, float) and pd.isna(raw):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    text = str(raw).strip()
    if not text:
        return None
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    text = re.sub(r"[£$€,\s]", "", text)
    try:
        value = float(text)
    except ValueError:
        return None
    return -value if negative else value


def _finalize_meta(meta, values):
    """Fill in meta["warning"] based on how many of the 8 CORE fields (not
    all 15 — most real statements never report inventory, receivables/
    payables, interest expense, or total assets at all) ended up matched.
    Shared by the single-table path and the multi-sheet/multi-table merge
    path so both apply the exact same warning threshold to the final,
    combined set of values rather than to any one sheet/table in
    isolation."""
    core_metrics = [m for m in METRIC_SYNONYMS if m not in OPTIONAL_METRICS]
    total_core = len(core_metrics)
    matched_core_count = sum(1 for m in core_metrics if m in values)
    warning = None
    if matched_core_count == 0:
        warning = (
            "We couldn't recognize any of the expected financial line items "
            "(Revenue, Net Profit, Current Assets, etc.) in this file. All "
            "figures have been left at 0 — please enter them manually below."
        )
    elif matched_core_count <= 3:
        warning = (
            f"Only {matched_core_count} of {total_core} core line items were "
            f"recognized in this file. Please check the figures below and fill "
            f"in anything that's missing."
        )
    meta["warning"] = warning
    return meta


def _merge_extractions(results):
    """results: [(source_label, (values, meta)), ...] — one entry per
    sheet (Excel) or table (PDF). Merges them into one combined result
    rather than picking a single "best" source, because a real statement
    routinely spreads Income Statement and Balance Sheet line items across
    separate sheets/pages that don't overlap — picking only the
    single highest-scoring source would silently discard everything the
    other one found. Where the same metric is matched in more than one
    source, the higher-confidence match wins."""
    combined_values = {}
    combined_match_info = {}
    sources_used = []
    label_col_display = value_col_display = detected_year = None
    available_years = []

    for label, (values, meta) in results:
        if not values:
            continue
        sources_used.append(label)
        if label_col_display is None:
            label_col_display = meta.get("label_column")
            value_col_display = meta.get("value_column")
            detected_year = meta.get("detected_year")
            available_years = meta.get("available_years", [])
        for metric, val in values.items():
            new_conf = meta.get("match_info", {}).get(metric, {}).get("confidence", 0)
            existing_conf = combined_match_info.get(metric, {}).get("confidence", -1)
            if metric not in combined_values or new_conf > existing_conf:
                combined_values[metric] = val
                combined_match_info[metric] = meta["match_info"][metric]

    meta = {
        "label_column": label_col_display,
        "value_column": value_col_display,
        "detected_year": detected_year,
        "available_years": available_years,
        "match_info": combined_match_info,
        "sources_combined": sources_used,
    }
    return combined_values, meta


def extract_from_dataframe(df, preferred_year=None):
    """
    df: a DataFrame where one column holds row/line-item labels (auto-detected)
    and other columns hold yearly figures. Returns (values, meta).
    values: {metric: float}
    meta: details about what was matched, for a transparent review UI.
    """
    if df is None or df.shape[0] == 0 or df.shape[1] < 2:
        return None, {"error": "This file doesn't look like a financial statement table (not enough rows/columns)."}

    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")
    if df.shape[1] < 2:
        return None, {"error": "Couldn't find both a label column and a value column in this file."}

    # Identify the label column: whichever column has the most non-numeric text
    label_col = df.columns[0]
    best_non_numeric = -1
    for col in df.columns:
        non_numeric = sum(
            1 for v in df[col]
            if isinstance(v, str) and _to_number(v) is None and v.strip()
        )
        if non_numeric > best_non_numeric:
            best_non_numeric = non_numeric
            label_col = col

    row_labels = df[label_col].astype(str).tolist()
    other_cols = [c for c in df.columns if c != label_col]

    year_cols = detect_year_columns(other_cols)

    chosen_col = None
    detected_year = None
    if year_cols:
        if preferred_year is not None:
            match = next((c for c, y in year_cols if y == preferred_year), None)
            chosen_col = match if match is not None else year_cols[0][0]
            detected_year = preferred_year if match is not None else year_cols[0][1]
        else:
            chosen_col, detected_year = year_cols[0]
    else:
        # No year-labelled column found — fall back to the column with the
        # most numeric-looking values.
        best_numeric_count, best_col = -1, None
        for col in other_cols:
            numeric_count = sum(1 for v in df[col] if _to_number(v) is not None)
            if numeric_count > best_numeric_count:
                best_numeric_count = numeric_count
                best_col = col
        chosen_col = best_col

    if chosen_col is None:
        return None, {"error": "Couldn't find a column of figures to read values from."}

    has_value = [_to_number(df.iloc[i][chosen_col]) is not None for i in range(len(row_labels))]
    assigned = match_rows_to_metrics(row_labels, has_value)

    values = {}
    match_info = {}
    for metric, (row_idx, score) in assigned.items():
        num_val = _to_number(df.iloc[row_idx][chosen_col])
        if num_val is not None:
            values[metric] = num_val
            match_info[metric] = {
                "matched_label": row_labels[row_idx],
                # The "total "-prefix tie-break in match_rows_to_metrics can
                # push a score slightly past 1.0 (e.g. an exact match that
                # also gets the bonus) — fine for internal ranking, but
                # "103% confidence" reads oddly in the review UI, so it's
                # capped here purely for display.
                "confidence": round(min(score, 1.0), 2),
            }

    if "gross_profit" not in values and "revenue" in values and "cost_of_sales" in values:
        values["gross_profit"] = values["revenue"] - values["cost_of_sales"]
        match_info["gross_profit"] = {
            "matched_label": "(calculated: Revenue − Cost of Sales)",
            "confidence": 1.0,
        }

    # A structurally valid table (we found a label column and a value
    # column) can still fail to match anything useful — e.g. a table that
    # simply isn't a financial statement. Rather than silently showing a
    # dashboard full of confident-looking zeroes, flag it so the app can
    # surface a clear warning instead of a false sense that it worked.
    meta = {
        "label_column": str(label_col),
        "value_column": str(chosen_col),
        "detected_year": detected_year,
        "available_years": [y for _, y in year_cols],
        "match_info": match_info,
    }
    _finalize_meta(meta, values)
    return values, meta


def extract_from_excel(source):
    """Reads every sheet in the workbook (not just the first), auto-
    detecting each sheet's real header row independently, and merges
    whatever each sheet matches into one combined result — the layout a
    professional statement almost always uses is a separate Income
    Statement sheet and Balance Sheet sheet, each with its own header row
    position and its own set of year columns, neither of which is a
    complete statement on its own."""
    try:
        all_raw = pd.read_excel(source, sheet_name=None, header=None)
    except Exception as e:
        return None, {"error": f"Couldn't read this Excel file: {e}"}

    results = []
    preferred_year = None
    for sheet_name, raw_df in all_raw.items():
        if raw_df is None or raw_df.shape[0] == 0:
            continue
        header_row = find_header_row(raw_df.values.tolist())
        df = reframe_with_header(raw_df, header_row)
        values, meta = extract_from_dataframe(df, preferred_year=preferred_year)
        if values and preferred_year is None and meta.get("detected_year"):
            # Bias every subsequent sheet toward the same fiscal year the
            # first successfully-matched sheet used, so a workbook whose
            # sheets don't all offer identical year columns (e.g. the P&L
            # covers 3 years but the balance sheet only 2) still reads
            # consistently from the same year wherever that year exists.
            preferred_year = meta["detected_year"]
        results.append((sheet_name, (values, meta)))

    combined_values, combined_meta = _merge_extractions(results)
    if not combined_values:
        return None, {
            "error": (
                "Couldn't recognize any financial line items in this "
                "workbook (checked every sheet). Please use the review "
                "fields below to enter the figures manually."
            )
        }
    _finalize_meta(combined_meta, combined_values)
    return combined_values, combined_meta


def extract_from_pdf(file_obj):
    import pdfplumber

    tables_found = []
    try:
        with pdfplumber.open(file_obj) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                for t_idx, table in enumerate(page.extract_tables() or []):
                    if table and len(table) > 1:
                        tables_found.append((f"page {page_num}", table))
    except Exception as e:
        return None, {"error": f"Couldn't open this PDF: {e}"}

    if not tables_found:
        return None, {
            "error": (
                "No tables could be found in this PDF (it may be a scanned "
                "image rather than a text-based document). Please use the "
                "review fields below to enter the figures manually."
            )
        }

    # Merged across every table found (not just the single best-matching
    # one) — a multi-page professional statement typically has the Income
    # Statement and Balance Sheet as separate tables on separate pages,
    # each contributing different line items rather than one page being a
    # strictly "better" read of the whole document.
    results = []
    preferred_year = None
    for label, table in tables_found:
        header, *rows = table
        try:
            columns = [h if h not in (None, "") else f"col{i}" for i, h in enumerate(header)]
            df = pd.DataFrame(rows, columns=columns)
        except Exception:
            continue
        values, meta = extract_from_dataframe(df, preferred_year=preferred_year)
        if values and preferred_year is None and meta.get("detected_year"):
            preferred_year = meta["detected_year"]
        results.append((label, (values, meta)))

    combined_values, combined_meta = _merge_extractions(results)
    if not combined_values:
        return None, {
            "error": (
                "Found tables in this PDF but couldn't identify financial "
                "figures in them. Please use the review fields below to "
                "enter the figures manually."
            )
        }
    _finalize_meta(combined_meta, combined_values)
    return combined_values, combined_meta


def extract_financial_data(source, filename=None):
    """
    source: a file path (str) or a file-like object (e.g. from
            st.file_uploader). filename is used to detect the file type
            when source is a file-like object.
    Returns (values, meta) — values is None on failure, with meta["error"]
    explaining why.
    """
    name = filename or getattr(source, "name", None) or str(source)
    ext = str(name).lower().rsplit(".", 1)[-1] if "." in str(name) else ""

    try:
        if ext == "pdf":
            return extract_from_pdf(source)
        elif ext == "csv":
            raw = pd.read_csv(source, header=None)
            header_row = find_header_row(raw.values.tolist())
            df = reframe_with_header(raw, header_row)
            return extract_from_dataframe(df)
        elif ext in ("xlsx", "xls"):
            return extract_from_excel(source)
        else:
            return None, {"error": f"Unsupported file type: .{ext or '?'}. Please upload a .xlsx, .csv, or .pdf file."}
    except Exception as e:
        return None, {"error": f"Couldn't read this file: {e}"}
