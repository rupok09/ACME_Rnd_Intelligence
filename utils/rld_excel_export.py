from io import BytesIO
import pandas as pd


def create_rld_excel_report(
    rld_df=None,
    inactive_df=None,
    product_char_df=None,
    resources_df=None
):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        if rld_df is not None:
            rld_df.to_excel(writer, index=False, sheet_name="Orange Book")

        if inactive_df is not None:
            inactive_df.to_excel(writer, index=False, sheet_name="Inactive Ingredients")

        if product_char_df is not None:
            product_char_df.to_excel(writer, index=False, sheet_name="Product Characteristics")

        if resources_df is not None:
            resources_df.to_excel(writer, index=False, sheet_name="Resources")

    output.seek(0)
    return output