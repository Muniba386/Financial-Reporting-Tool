"""
Flexible financial data extraction.

Takes an uploaded file in almost any common shape — Excel/CSV with rows and
columns in a different order than expected, different account-name wording,
a different year column, or a table extracted from a PDF — and tries to
identify the 8 line items the app needs:

    revenue, cost_of_sales, gross_profit, net_profit,
    current_assets, current_liabilities, total_debt, equity

This is rule-based matching (name-synonym lookup + fuzzy string matching),
not an AI model reading the document, so it won't be perfect on every
possible layout. It's designed to get close on common formats and then let
the user review and correct the detected values before anything is
calculated — that review step is what makes it safe to rely on for
arbitrary files, not the auto-detection alone.
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
        "cost of sales and services"
    ],
    "gross_profit": [
        "gross profit", "gross income", "gross margin"
    ],
    "net_profit": [
        "net profit", "net income", "profit for the year",
        "profit after tax", "net earnings", "profit for the period",
        "profit attributable to owners", "net profit for the year",
        "profit/loss for the year"
    ],
    "current_assets": [
        "current assets", "total current assets"
    ],
    "current_liabilities": [
        "current liabilities", "total current liabilities"
    ],
    "total_debt": [
        "total debt", "total liabilities", "total borrowings",
        "borrowings", "long term debt", "long-term debt", "total loans",
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
    "net_profit": "Net Profit",
    "current_assets": "Current Assets",
    "current_liabilities": "Current Liabilities",
    "total_debt": "Total Debt",
    "equity": "Equity",
}

YEAR_PATTERN = re.compile(r"(19|20)\d{2}")

MATCH_THRESHOLD = 0.72


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


def match_rows_to_metrics(row_labels, threshold=MATCH_THRESHOLD):
    """
    Score every (row, metric) pair and greedily assign each metric to its
    single best-scoring, not-yet-used row. Returns {metric: (row_index, score)}.
    """
    candidates = []
    for idx, label in enumerate(row_labels):
        norm = normalize_label(label)
        if not norm:
            continue
        for metric, synonyms in METRIC_SYNONYMS.items():
            best_for_row_metric = max(_label_score(norm, syn) for syn in synonyms)
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


def _to_number(raw):
    if raw is None:
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

    assigned = match_rows_to_metrics(row_labels)

    values = {}
    match_info = {}
    for metric, (row_idx, score) in assigned.items():
        num_val = _to_number(df.iloc[row_idx][chosen_col])
        if num_val is not None:
            values[metric] = num_val
            match_info[metric] = {
                "matched_label": row_labels[row_idx],
                "confidence": round(score, 2),
            }

    if "gross_profit" not in values and "revenue" in values and "cost_of_sales" in values:
        values["gross_profit"] = values["revenue"] - values["cost_of_sales"]
        match_info["gross_profit"] = {
            "matched_label": "(calculated: Revenue − Cost of Sales)",
            "confidence": 1.0,
        }

    # A structurally valid file (we found a label column and a value
    # column) can still fail to match anything useful — e.g. a file that
    # simply isn't a financial statement. Rather than silently showing a
    # dashboard full of confident-looking zeroes, flag it so the app can
    # surface a clear warning instead of a false sense that it worked.
    total_metrics = len(METRIC_SYNONYMS)
    matched_count = len(values)
    warning = None
    if matched_count == 0:
        warning = (
            "We couldn't recognize any of the expected financial line items "
            "(Revenue, Net Profit, Current Assets, etc.) in this file. All "
            "figures have been left at 0 — please enter them manually below."
        )
    elif matched_count <= 3:
        warning = (
            f"Only {matched_count} of {total_metrics} expected line items were "
            f"recognized in this file. Please check the figures below and fill "
            f"in anything that's missing."
        )

    meta = {
        "label_column": str(label_col),
        "value_column": str(chosen_col),
        "detected_year": detected_year,
        "available_years": [y for _, y in year_cols],
        "match_info": match_info,
        "warning": warning,
    }
    return values, meta


def extract_from_pdf(file_obj):
    import pdfplumber

    tables_found = []
    try:
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                for table in (page.extract_tables() or []):
                    if table and len(table) > 1:
                        tables_found.append(table)
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

    best_values, best_meta, best_count = None, None, -1
    for table in tables_found:
        header, *rows = table
        try:
            columns = [h if h not in (None, "") else f"col{i}" for i, h in enumerate(header)]
            df = pd.DataFrame(rows, columns=columns)
        except Exception:
            continue
        values, meta = extract_from_dataframe(df)
        if values and len(values) > best_count:
            best_values, best_meta, best_count = values, meta, len(values)

    if best_values is None:
        return None, {
            "error": (
                "Found tables in this PDF but couldn't identify financial "
                "figures in them. Please use the review fields below to "
                "enter the figures manually."
            )
        }

    return best_values, best_meta


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
            df = pd.read_csv(source, header=0)
            return extract_from_dataframe(df)
        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(source)
            return extract_from_dataframe(df)
        else:
            return None, {"error": f"Unsupported file type: .{ext or '?'}. Please upload a .xlsx, .csv, or .pdf file."}
    except Exception as e:
        return None, {"error": f"Couldn't read this file: {e}"}
