import re
import pandas as pd
import pymupdf

from utils.excipient_functions import get_excipient_function


def extract_pdf_text(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    pdf = pymupdf.open(stream=file_bytes, filetype="pdf")

    text = ""

    for page in pdf:
        text += page.get_text() + "\n"

    pdf.close()
    return text


def clean_line(line):
    return " ".join(str(line).split()).strip()


def extract_section(text, start_keyword, end_keywords):
    lines = [clean_line(line) for line in text.splitlines()]
    lines = [line for line in lines if line]

    start_index = None

    for i, line in enumerate(lines):
        if start_keyword.lower() in line.lower():
            start_index = i
            break

    if start_index is None:
        return []

    section_lines = []

    for line in lines[start_index + 1:]:
        lower_line = line.lower()

        if any(end.lower() in lower_line for end in end_keywords):
            break

        section_lines.append(line)

    return section_lines


def extract_inactive_ingredients(uploaded_file):
    text = extract_pdf_text(uploaded_file)

    section_lines = extract_section(
        text,
        "Inactive Ingredients",
        [
            "Product Characteristics",
            "Packaging",
            "Marketing Information",
            "Principal Display Panel",
            "Labeler",
        ],
    )

    ingredients = []

    skip_words = [
        "ingredient name",
        "strength",
        "inactive ingredients",
        "active ingredient",
    ]

    for line in section_lines:
        lower_line = line.lower()

        if any(word in lower_line for word in skip_words):
            continue

        if len(line) < 2:
            continue

        # Try to catch strength if present
        strength_match = re.search(r"(\d+\.?\d*\s?(mg|g|mcg|%|percent))", line, re.IGNORECASE)

        if strength_match:
            strength = strength_match.group(1)
            ingredient = line.replace(strength, "").strip(" -:|")
        else:
            strength = "—"
            ingredient = line.strip(" -:|")

        if ingredient and ingredient.lower() not in ["nan", "none"]:
            ingredients.append(
                {
                    "Ingredient Name": ingredient,
                    "Strength": strength,
                    "Function": get_excipient_function(ingredient),
                }
            )

    if not ingredients:
        ingredients.append(
            {
                "Ingredient Name": "Not Found",
                "Strength": "—",
                "Function": "—",
            }
        )

    return pd.DataFrame(ingredients)


def extract_product_characteristics(uploaded_file):
    text = extract_pdf_text(uploaded_file)

    section_lines = extract_section(
        text,
        "Product Characteristics",
        [
            "Packaging",
            "Marketing Information",
            "Inactive Ingredients",
            "Labeler",
        ],
    )

    characteristics = {
        "Color": "Not Found",
        "Shape": "Not Found",
        "Score": "Not Found",
        "Size": "Not Found",
        "Imprint Code": "Not Found",
    }

    joined_text = " ".join(section_lines)

    patterns = {
        "Color": r"Color\s+([A-Za-z]+)",
        "Shape": r"Shape\s+([A-Za-z]+)",
        "Score": r"Score\s+([A-Za-z ]+?)(?=Shape|Size|Imprint|$)",
        "Size": r"Size\s+([0-9.]+\s?mm)",
        "Imprint Code": r"Imprint Code\s+([A-Za-z0-9 ;/-]+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, joined_text, re.IGNORECASE)

        if match:
            characteristics[key] = clean_line(match.group(1))

    rows = []

    for key, value in characteristics.items():
        rows.append(
            {
                "Characteristic": key,
                "Value": value,
            }
        )

    return pd.DataFrame(rows)