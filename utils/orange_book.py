import os
import re
import pandas as pd
from urllib.parse import quote_plus


PRODUCTS_PATH = os.path.join("data", "orange_book", "products.txt")


def clean_search_text(text):
    text = str(text).upper()
    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    text = " ".join(text.split())
    return text


def get_orange_book_search_url(api_name):
    return "https://www.accessdata.fda.gov/scripts/cder/ob/index.cfm"


def search_orange_book(api_name):
    reference_url = get_orange_book_search_url(api_name)

    try:
        df = pd.read_csv(
            PRODUCTS_PATH,
            sep="~",
            dtype=str,
            encoding="latin1"
        ).fillna("")

        df.columns = [col.strip() for col in df.columns]

        search_text = clean_search_text(api_name)

        df["SEARCH_INGREDIENT"] = df["Ingredient"].apply(clean_search_text)
        df["SEARCH_TRADE"] = df["Trade_Name"].apply(clean_search_text)

        matched_df = df[
            df["SEARCH_INGREDIENT"].str.contains(search_text, na=False)
            | df["SEARCH_TRADE"].str.contains(search_text, na=False)
        ]

        return matched_df, reference_url

    except Exception as error:
        print("Orange Book local search error:", error)
        return pd.DataFrame(), reference_url


def filter_rld_rows(df):
    if df is None or df.empty:
        return pd.DataFrame()

    rld_df = df[df["RLD"].astype(str).str.upper().str.contains("YES|RLD", na=False)]

    if not rld_df.empty:
        return rld_df

    return df.head(20)


def prepare_orange_book_display(df, reference_url):
    if df is None or df.empty:
        return pd.DataFrame(
            [{
                "Active Ingredient": "Not Found",
                "Proprietary Name": "Not Found",
                "Appl. No.": "Not Found",
                "Dosage Form": "Not Found",
                "Route": "Not Found",
                "Strength": "Not Found",
                "TE Code": "Not Found",
                "RLD": "Not Found",
                "RS": "Not Found",
                "Applicant Holder": "Not Found",
                "Reference": reference_url,
            }]
        )

    output_df = pd.DataFrame()

    output_df["Active Ingredient"] = df["Ingredient"]
    output_df["Proprietary Name"] = df["Trade_Name"]
    output_df["Appl. No."] = df["Appl_Type"] + df["Appl_No"]
    output_df["Dosage Form"] = df["DF;Route"].str.split(";").str[0]
    output_df["Route"] = df["DF;Route"].str.split(";").str[-1]
    output_df["Strength"] = df["Strength"]
    output_df["TE Code"] = df["TE_Code"]
    output_df["RLD"] = df["RLD"]
    output_df["RS"] = df["RS"]
    output_df["Applicant Holder"] = df["Applicant_Full_Name"]
    output_df["Reference"] = reference_url

    return output_df