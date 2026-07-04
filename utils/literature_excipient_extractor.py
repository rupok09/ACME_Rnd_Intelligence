import re
import pandas as pd
import pdfplumber
import fitz


EXCIPIENT_TERMS = [
    "inactive ingredients",
    "ingredients",
    "ingredient",
    "excipients",
    "microcrystalline cellulose",
    "cellulose",
    "mcc",
    "lactose",
    "lactose monohydrate",
    "mannitol",
    "crospovidone",
    "croscarmellose sodium",
    "sodium starch glycolate",
    "povidone",
    "polyvinylpyrrolidone",
    "hydroxypropyl cellulose",
    "low substituted hydroxypropyl cellulose",
    "low substituted hpc",
    "hypromellose",
    "hpmc",
    "magnesium stearate",
    "sodium stearyl fumarate",
    "colloidal silicon dioxide",
    "silicon dioxide",
    "talc",
    "polyethylene glycol",
    "peg",
    "titanium dioxide",
    "stearic acid",
    "pregelatinized starch",
    "hydrogenated castor oil",
    "glyceryl behenate",
    "opadry",
]


GENERIC_TERMS = [
    "ingredient",
    "ingredients",
    "inactive ingredients",
    "excipients",
]


def clean_text(value):
    if value is None:
        return ""
    return " ".join(str(value).replace("\n", " ").split()).strip()


def make_unique_columns(columns):
    seen = {}
    new_columns = []

    for i, col in enumerate(columns):
        col = clean_text(col) or f"Column_{i + 1}"

        if col in seen:
            seen[col] += 1
            col = f"{col}_{seen[col]}"
        else:
            seen[col] = 0

        new_columns.append(col)

    return new_columns


def safe_concat(dataframes):
    cleaned = []

    for df in dataframes:
        if df is not None and not df.empty:
            df = df.copy()
            df.columns = make_unique_columns(df.columns)
            cleaned.append(df.reset_index(drop=True))

    if not cleaned:
        return pd.DataFrame()

    return pd.concat(cleaned, ignore_index=True, sort=False)


def row_contains_excipient(text):
    text = str(text).lower()
    return any(term in text for term in EXCIPIENT_TERMS)


def detect_excipient(text):
    lower_text = str(text).lower()

    matched_terms = []

    for term in EXCIPIENT_TERMS:
        if term in lower_text and term not in GENERIC_TERMS:
            matched_terms.append(term.title())

    return matched_terms


def detect_example(text):
    match = re.search(
        r"(example\s+\d+|example\s+[a-z]|formulation\s+\d+|composition\s+\d+|table\s+\d+)",
        str(text),
        re.IGNORECASE,
    )
    return match.group(1).title() if match else "Not detected"


def extract_amount_unit(text):
    text = str(text)

    match = re.search(
        r"([0-9]+(?:\.[0-9]+)?(?:\s*[-–]\s*[0-9]+(?:\.[0-9]+)?)?)\s*(mg|g|mcg|µg|%|percent|parts|kg|%w/w|% w/w)",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1), match.group(2)

    return "", ""


def extract_exact_pdf_tables(uploaded_file):
    extracted_tables = []

    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page_no, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()

                for table_no, table in enumerate(tables, start=1):
                    if not table or len(table) < 2:
                        continue

                    df = pd.DataFrame(table).fillna("")
                    df = df.map(clean_text)

                    first_row = df.iloc[0].tolist()

                    if any(first_row):
                        df.columns = make_unique_columns(first_row)
                        df = df.iloc[1:].reset_index(drop=True)
                    else:
                        df.columns = make_unique_columns(df.columns)

                    df = df.loc[:, (df != "").any(axis=0)]

                    if df.empty:
                        continue

                    table_text = " ".join(df.astype(str).values.flatten()).lower()

                    if not row_contains_excipient(table_text):
                        continue

                    df.insert(0, "Document", uploaded_file.name)
                    df.insert(1, "Page", page_no)
                    df.insert(2, "Table No.", table_no)

                    extracted_tables.append(df)

    except Exception as error:
        print("PDF table extraction error:", error)

    return safe_concat(extracted_tables)


def split_into_paragraphs(page_text):
    page_text = str(page_text)

    paragraphs = re.split(r"\n\s*\n", page_text)

    clean_paragraphs = []

    for paragraph in paragraphs:
        paragraph = clean_text(paragraph)

        if len(paragraph) >= 30:
            clean_paragraphs.append(paragraph)

    return clean_paragraphs


def extract_context_windows(page_text, window_size=2):
    lines = page_text.splitlines()
    clean_lines = [clean_text(line) for line in lines if clean_text(line)]

    contexts = []

    for i, line in enumerate(clean_lines):
        if not row_contains_excipient(line):
            continue

        start = max(0, i - window_size)
        end = min(len(clean_lines), i + window_size + 1)

        context = " ".join(clean_lines[start:end])
        context = clean_text(context)

        if len(context) >= 20:
            contexts.append(context)

    return contexts


def extract_exact_excipient_lines(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    rows = []

    for page_no, page in enumerate(doc, start=1):
        page_text = page.get_text("text") or ""

        paragraphs = split_into_paragraphs(page_text)

        page_contexts = []

        if paragraphs:
            for paragraph in paragraphs:
                if row_contains_excipient(paragraph):
                    page_contexts.append(paragraph)

        if not page_contexts:
            page_contexts = extract_context_windows(page_text, window_size=2)

        for context in page_contexts:
            matched_excipients = detect_excipient(context)

            if not matched_excipients:
                continue

            amount, unit = extract_amount_unit(context)

            rows.append(
                {
                    "Document": uploaded_file.name,
                    "Page": page_no,
                    "Example / Section": detect_example(context),
                    "Exact Line / Paragraph": context,
                    "Detected Excipient(s)": "; ".join(matched_excipients),
                    "Amount": amount,
                    "Unit": unit,
                    "Extraction Type": "Text Paragraph / Context",
                }
            )

    doc.close()

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).drop_duplicates()


def extract_patent_formulation_examples(uploaded_files):
    all_tables = []

    for uploaded_file in uploaded_files:
        exact_table_df = extract_exact_pdf_tables(uploaded_file)
        exact_line_df = extract_exact_excipient_lines(uploaded_file)

        if not exact_table_df.empty:
            exact_table_df["Extraction Type"] = "Exact PDF Table"
            all_tables.append(exact_table_df)

        if not exact_line_df.empty:
            all_tables.append(exact_line_df)

    return safe_concat(all_tables)


def build_merged_excipient_table(formulation_df):
    if formulation_df is None or formulation_df.empty:
        return pd.DataFrame()

    rows = []

    for _, row in formulation_df.iterrows():

        evidence = ""

        if "Exact Line / Paragraph" in formulation_df.columns:
            evidence = row.get("Exact Line / Paragraph", "")

        if not evidence and "Exact Line" in formulation_df.columns:
            evidence = row.get("Exact Line", "")

        if not evidence and "Source Text" in formulation_df.columns:
            evidence = row.get("Source Text", "")

        if not evidence:
            evidence_parts = []

            for value in row.values:
                if pd.isna(value):
                    continue

                text_value = str(value).strip()

                if text_value and text_value.lower() != "none":
                    evidence_parts.append(text_value)

            evidence = " | ".join(evidence_parts)

        evidence = str(evidence)
        lower_evidence = evidence.lower()

        for term in EXCIPIENT_TERMS:
            if term in lower_evidence and term not in GENERIC_TERMS:
                rows.append(
                    {
                        "Document": row.get("Document", ""),
                        "Page": row.get("Page", ""),
                        "Excipient": term.title(),
                        "Amount": row.get("Amount", ""),
                        "Unit": row.get("Unit", ""),
                        "Evidence": evidence,
                    }
                )

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).drop_duplicates()