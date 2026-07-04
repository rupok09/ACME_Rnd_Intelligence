from io import BytesIO
import pandas as pd
import re


def remove_html_tags(text):
    if not isinstance(text, str):
        return text

    text = re.sub(r'<img[^>]*>', '[Structure Image]', text)
    text = re.sub(r'<a[^>]*>', '', text)
    text = text.replace("</a>", "")

    return text


def create_excel_report(df):
    clean_df = df.copy()

    for column in clean_df.columns:
        clean_df[column] = clean_df[column].apply(remove_html_tags)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        clean_df.to_excel(writer, index=False, sheet_name="API Characterization")

    output.seek(0)
    return output