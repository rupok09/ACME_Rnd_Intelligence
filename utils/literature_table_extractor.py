import re
import pandas as pd
import pdfplumber
import fitz  # PyMuPDF


EXCIPIENT_TERMS = [
    "microcrystalline cellulose", "mcc", "lactose", "lactose monohydrate",
    "mannitol", "crospovidone", "croscarmellose sodium",
    "sodium starch glycolate", "povidone", "polyvinylpyrrolidone",
    "hydroxypropyl cellulose", "hypromellose", "hpmc",
    "magnesium stearate", "sodium stearyl fumarate",
    "colloidal silicon dioxide", "silicon dioxide", "talc",
    "polyethylene glycol", "peg", "titanium dioxide",
    "stearic acid", "pregelatinized starch"
]

API_PROPERTY_PATTERNS = {
    "Melting Point": r"(melting point|m\.p\.|mp)\s*(?:is|of|:)?\s*([0-9]+(?:\.[0-9]+)?\s*(?:-|–|to)?\s*[0-9]*(?:\.[0-9]+)?\s*°?\s*C)",
    "Solubility": r"(solubility|soluble|sparingly soluble|practically insoluble)[^.]{0,180}",
    "pKa": r"(pka|pKa)\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)",
    "LogP / LogD": r"(logp|log p|logd|partition coefficient)\s*(?:is|=|:)?\s*([0-9.-]+)",
    "Polymorph": r"(polymorph|crystalline form|form [I|II|III|A|B])[^.]{0,160}",
    "Hygroscopicity": r"(hygroscopic|moisture uptake|water uptake)[^.]{0,160}",
    "Photostability": r"(photostability|light stability|light exposure)[^.]{0,160}",
    "Forced Degradation": r"(forced degradation|stress degradation|acid degradation|base degradation|oxidative degradation)[^.]{0,180}",
    "BCS Classification": r"(BCS class|biopharmaceutics classification)[^.]{0,160}",
}


def clean_text(value):
    if value is None:
        return ""
    return " ".join(str(value).replace("\n", " ").split()).strip()


def extract_text_by_page(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    pages = []

    for page_no, page in enumerate(doc, start=1):
        text = page.get_text("text")
        pages.append(
            {
                "Document": uploaded_file.name,
                "Page": page_no,
                "Text": text,
            }
        )

    doc.close()
    return pages


def extract_tables_by_page(uploaded_file):
    tables = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            page_tables = page.extract_tables()

            for table_no, table in enumerate(page_tables, start=1):
                if not table or len(table) < 2:
                    continue

                df = pd.DataFrame(table).fillna("")
                df = df.map(clean_text)

                # Use first row as header if useful
                first_row = df.iloc[0].tolist()
                if any(first_row):
                    df.columns = first_row
                    df = df.iloc[1:].reset_index(drop=True)

                df = df.loc[:, (df != "").any(axis=0)]

                if df.empty:
                    continue

                df.insert(0, "Document", uploaded_file.name)
                df.insert(1, "Page", page_no)
                df.insert(2, "Table No.", table_no)

                tables.append(df)

    if not tables:
        return pd.DataFrame()

    return pd.concat(tables, ignore_index=True)


def table_contains_excipient_or_formulation(df):
    text = " ".join(df.astype(str).values.flatten()).lower()

    formulation_words = [
        "example", "composition", "formulation", "tablet",
        "capsule", "ingredient", "amount", "mg", "%", "weight"
    ]

    if any(term in text for term in EXCIPIENT_TERMS):
        return True

    score = sum(1 for word in formulation_words if word in text)
    return score >= 2


def extract_patent_formulation_examples(uploaded_files):
    all_results = []

    for uploaded_file in uploaded_files:
        table_df = extract_tables_by_page(uploaded_file)

        if not table_df.empty:
            grouped_tables = []

            for _, group in table_df.groupby(["Document", "Page", "Table No."]):
                if table_contains_excipient_or_formulation(group):
                    grouped_tables.append(group)

            if grouped_tables:
                all_results.append(pd.concat(grouped_tables, ignore_index=True))

        # Fallback: text-based extraction
        text_rows = extract_formulation_from_text(uploaded_file)
        if not text_rows.empty:
            all_results.append(text_rows)

    if not all_results:
        return pd.DataFrame()

    return pd.concat(all_results, ignore_index=True)


def extract_formulation_from_text(uploaded_file):
    pages = extract_text_by_page(uploaded_file)
    rows = []

    for page in pages:
        text = page["Text"]
        lines = [clean_text(line) for line in text.splitlines()]
        lines = [line for line in lines if line]

        current_example = "Not detected"

        for line in lines:
            example_match = re.search(r"(example\s+\d+|formulation\s+\d+|composition\s+\d+)", line, re.I)
            if example_match:
                current_example = example_match.group(1).title()

            lower_line = line.lower()

            if not any(term in lower_line for term in EXCIPIENT_TERMS):
                continue

            amount_match = re.search(
                r"([0-9]+(?:\.[0-9]+)?)\s*(mg|g|mcg|µg|%|percent|parts|kg)",
                line,
                re.I
            )

            amount = amount_match.group(1) if amount_match else ""
            unit = amount_match.group(2) if amount_match else ""

            detected_excipient = ""

            for term in EXCIPIENT_TERMS:
                if term in lower_line:
                    detected_excipient = term.title()
                    break

            rows.append(
                {
                    "Document": uploaded_file.name,
                    "Page": page["Page"],
                    "Example / Section": current_example,
                    "Component / Excipient": detected_excipient,
                    "Amount": amount,
                    "Unit": unit,
                    "Source Text": line,
                }
            )

    return pd.DataFrame(rows)


def build_merged_excipient_table(formulation_df):
    if formulation_df is None or formulation_df.empty:
        return pd.DataFrame()

    rows = []

    for _, row in formulation_df.iterrows():
        row_text = " ".join([str(x) for x in row.values]).lower()

        for term in EXCIPIENT_TERMS:
            if term in row_text:
                rows.append(
                    {
                        "Document": row.get("Document", ""),
                        "Page": row.get("Page", ""),
                        "Excipient": term.title(),
                        "Evidence": " | ".join([str(x) for x in row.values if str(x).strip()]),
                    }
                )

    return pd.DataFrame(rows).drop_duplicates()


def extract_api_properties_from_pdf(uploaded_files):
    results = []

    for uploaded_file in uploaded_files:
        pages = extract_text_by_page(uploaded_file)

        for page in pages:
            text = clean_text(page["Text"])

            for prop, pattern in API_PROPERTY_PATTERNS.items():
                matches = re.finditer(pattern, text, re.I)

                for match in matches:
                    value = match.group(0)

                    results.append(
                        {
                            "Document": uploaded_file.name,
                            "Page": page["Page"],
                            "Property": prop,
                            "Extracted Value / Evidence": value,
                        }
                    )

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(results).drop_duplicates()