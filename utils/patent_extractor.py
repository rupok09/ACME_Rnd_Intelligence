import re
import pymupdf
import pandas as pd

from utils.excipient_functions import get_excipient_function


COMMON_EXCIPIENTS = [
    "microcrystalline cellulose",
    "mcc",
    "lactose",
    "mannitol",
    "hydroxypropyl cellulose",
    "hpc",
    "povidone",
    "pvp",
    "croscarmellose sodium",
    "crospovidone",
    "sodium starch glycolate",
    "magnesium stearate",
    "colloidal silicon dioxide",
    "silicon dioxide",
    "talc",
    "hypromellose",
    "hpmc",
    "polyethylene glycol",
    "peg 400",
    "titanium dioxide",
    "ferric oxide red",
    "hydrogenated castor oil",
]


def extract_pdf_text(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    pdf = pymupdf.open(stream=file_bytes, filetype="pdf")

    text = ""

    for page in pdf:
        text += page.get_text() + "\n"

    pdf.close()
    return text


def detect_patent_number(text):
    patterns = [
        r"US\s?\d{6,10}",
        r"WO\s?\d{4,10}",
        r"EP\s?\d{6,10}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)

    return "Uploaded Patent"


def split_examples(text):
    pattern = r"(Example\s+\d+)"
    parts = re.split(pattern, text, flags=re.IGNORECASE)

    examples = []

    for i in range(1, len(parts), 2):
        example_name = parts[i].strip()
        example_text = parts[i + 1][:3000] if i + 1 < len(parts) else ""

        examples.append(
            {
                "example": example_name,
                "text": example_text,
            }
        )

    return examples


def detect_dosage_form(text):
    text_lower = text.lower()

    dosage_forms = ["tablet", "capsule", "granule", "suspension", "solution", "pellet"]

    for dosage_form in dosage_forms:
        if dosage_form in text_lower:
            return dosage_form.title()

    return "Not Found"


def extract_amount_near_excipient(example_text, excipient):
    excipient_pattern = re.escape(excipient)
    pattern = rf"({excipient_pattern}).{{0,80}}?(\d+\.?\d*)\s?(mg|g|%|percent|parts)"

    match = re.search(pattern, example_text, flags=re.IGNORECASE)

    if not match:
        pattern_reverse = rf"(\d+\.?\d*)\s?(mg|g|%|percent|parts).{{0,80}}?({excipient_pattern})"
        match = re.search(pattern_reverse, example_text, flags=re.IGNORECASE)

    if match:
        if match.lastindex >= 3:
            amount = match.group(2) if match.group(2).lower() not in ["mg", "g", "%", "percent", "parts"] else match.group(1)
            unit = match.group(3) if match.group(3).lower() in ["mg", "g", "%", "percent", "parts"] else match.group(2)

            if unit.lower() in ["%", "percent"]:
                return "", f"{amount}%"

            return f"{amount} {unit}", ""

    return "", ""


def extract_patent_formulation_table(uploaded_file):
    text = extract_pdf_text(uploaded_file)
    patent_number = detect_patent_number(text)
    examples = split_examples(text)

    rows = []

    if not examples:
        examples = [{"example": "Example Not Detected", "text": text[:5000]}]

    for example in examples:
        example_name = example["example"]
        example_text = example["text"]
        dosage_form = detect_dosage_form(example_text)

        for excipient in COMMON_EXCIPIENTS:
            if excipient.lower() in example_text.lower():
                amount, percent = extract_amount_near_excipient(example_text, excipient)

                rows.append(
                    {
                        "Patent": patent_number,
                        "Example": example_name,
                        "Dosage Form": dosage_form,
                        "Excipient": excipient.title(),
                        "Amount": amount if amount else "Not Found",
                        "% w/w": percent if percent else "Not Found",
                        "Function": get_excipient_function(excipient),
                    }
                )

    if not rows:
        rows.append(
            {
                "Patent": patent_number,
                "Example": "Not Found",
                "Dosage Form": "Not Found",
                "Excipient": "No common excipient detected",
                "Amount": "Not Found",
                "% w/w": "Not Found",
                "Function": "Review manually",
            }
        )

    return pd.DataFrame(rows)