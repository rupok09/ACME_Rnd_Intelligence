import json
import os
import pandas as pd


DATABASE_PATH = os.path.join("utils", "excipient_database.json")


def load_excipient_database():
    if not os.path.exists(DATABASE_PATH):
        return {}

    with open(DATABASE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_name(name):
    return str(name).lower().strip()


def get_excipient_info(excipient_name):
    database = load_excipient_database()
    normalized_name = normalize_name(excipient_name)

    for key, value in database.items():
        if key in normalized_name or normalized_name in key:
            return value

    return {
        "Function": "Not available",
        "Category": "Not available",
        "Typical Range": "Not available",
        "Notes": "No local database match found."
    }


def build_excipient_intelligence_table(extracted_table_df):
    if extracted_table_df is None or extracted_table_df.empty:
        return pd.DataFrame(
            columns=["Excipient", "Function", "Category", "Typical Range", "Notes"]
        )

    possible_component_columns = [
        "Component",
        "Excipient",
        "Ingredient",
        "Ingredients",
        "Material",
        "Composition",
        "Name"
    ]

    component_column = None

    for column in extracted_table_df.columns:
        for possible_name in possible_component_columns:
            if possible_name.lower() in str(column).lower():
                component_column = column
                break

        if component_column:
            break

    if component_column is None:
        component_column = extracted_table_df.columns[0]

    excipients = []

    for value in extracted_table_df[component_column].dropna().unique():
        name = str(value).strip()

        if not name:
            continue

        lower_name = name.lower()

        api_words = ["api", "active", "drug substance", "clopidogrel", "paracetamol", "metformin"]
        if any(word in lower_name for word in api_words):
            continue

        info = get_excipient_info(name)

        excipients.append(
            {
                "Excipient": name,
                "Function": info["Function"],
                "Category": info["Category"],
                "Typical Range": info["Typical Range"],
                "Notes": info["Notes"],
            }
        )

    return pd.DataFrame(excipients).drop_duplicates()