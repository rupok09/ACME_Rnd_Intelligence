import streamlit as st
import pandas as pd
from urllib.parse import quote_plus
import requests
import base64

from utils.orange_book import (
    search_orange_book,
    filter_rld_rows,
    prepare_orange_book_display,
)

from utils.dailymed import (
    search_dailymed_labels,
    extract_dailymed_label_tables,
)

from utils.dailymed_pdf_reader import (
    extract_inactive_ingredients,
    extract_product_characteristics,
)

from utils.rld_excel_export import create_rld_excel_report


def make_link_table(df, link_columns):
    display_df = df.copy()

    for column in link_columns:
        if column in display_df.columns:
            display_df[column] = display_df[column].apply(
                lambda x: f'<a href="{x}" target="_blank">Open</a>'
                if isinstance(x, str) and x.startswith("http")
                else x
            )

    html = display_df.to_html(
        escape=False,
        index=False,
        classes="result-table"
    )

    st.markdown(html, unsafe_allow_html=True)


def show_rld_information():
    st.title("RLD Information")

    st.write(
        "Search FDA Orange Book, select the RLD product, then collect DailyMed label information "
        "and extract inactive ingredients/product characteristics."
    )

    # ===================== STEP 1: ORANGE BOOK =====================
    api_name = st.text_input(
        label="API / Product Name",
        placeholder="e.g. Clopidogrel Bisulfate"
    )

    if st.button("Search RLD / RS Product", use_container_width=True):

        if not api_name.strip():
            st.warning("Please enter API / Product name first.")
            return

        with st.spinner("Searching FDA Orange Book local data..."):
            raw_df, reference_url = search_orange_book(api_name.strip())
            rld_df = filter_rld_rows(raw_df)
            display_df = prepare_orange_book_display(rld_df, reference_url)

        st.session_state.rld_api_name = api_name.strip()
        st.session_state.orange_book_raw_df = raw_df
        st.session_state.orange_book_display_df = display_df
        st.session_state.orange_book_reference = reference_url

        st.success("FDA Orange Book search completed.")

    orange_book_display_df = st.session_state.get("orange_book_display_df", None)
    reference_url = st.session_state.get("orange_book_reference", None)

    selected_orange_book_record = None

    if orange_book_display_df is not None:
        st.markdown("### Orange Book RLD Result")

        if reference_url:
            st.link_button(
                "Open FDA Orange Book Search Result",
                reference_url,
                use_container_width=True
            )

        make_link_table(orange_book_display_df, ["Reference"])

        if not orange_book_display_df.empty:
            options = []

            for index, row in orange_book_display_df.iterrows():
                option = (
                    f"{row['Proprietary Name']} | "
                    f"{row['Active Ingredient']} | "
                    f"{row['Strength']} | "
                    f"{row['Applicant Holder']}"
                )
                options.append(option)

            selected_option = st.selectbox(
                "Select RLD / Reference Product Record",
                options
            )

            selected_index = options.index(selected_option)
            selected_orange_book_record = orange_book_display_df.iloc[selected_index].to_dict()
            st.session_state.selected_orange_book_record = selected_orange_book_record

        with st.expander("View raw Orange Book table"):
            raw_df = st.session_state.get("orange_book_raw_df", pd.DataFrame())

            if raw_df is not None and not raw_df.empty:
                st.dataframe(raw_df, use_container_width=True)
            else:
                st.info("No raw Orange Book table extracted.")

    # ===================== STEP 2: DAILYMED =====================

    selected_record = st.session_state.get("selected_orange_book_record", None)

    default_query = ""

    if selected_record:
        brand = selected_record.get("Proprietary Name", "")
        ingredient = selected_record.get("Active Ingredient", "")

        if brand and brand != "Not Found":
            default_query = brand
        else:
            default_query = ingredient
    else:
        default_query = st.session_state.get("rld_api_name", "")

    dailymed_query = st.text_input(
        label="RLD / RS Name",
        value=default_query,
        placeholder="e.g. PLAVIX"
    )

    if st.button("Search DailyMed Label Info", use_container_width=True):

        if not dailymed_query.strip():
            st.warning("Please enter DailyMed search query.")
            return

        with st.spinner("Searching DailyMed labels..."):
            labels = search_dailymed_labels(dailymed_query.strip())

        st.session_state.dailymed_labels = labels

        if labels:
            st.success("DailyMed labels found.")
        else:
            st.error("No DailyMed labels found.")

    labels = st.session_state.get("dailymed_labels", [])

    selected_label = None

    if labels:
        label_options = [
            f"{label['title']} | SETID: {label['setid']}"
            for label in labels
        ]

        selected_label_text = st.selectbox(
            "Select DailyMed Label",
            label_options
        )

        selected_label = labels[label_options.index(selected_label_text)]
        st.session_state.selected_dailymed_label = selected_label

        # FIXED: Fetch remote PDF bytes via backend stream and parse to standard base64 inline frame context
        st.markdown("#### 📄 Drug Label Document Preview")
        try:
            pdf_url = selected_label["pdf_link"]
            with st.spinner("Downloading and processing secure label preview stream..."):
                response = requests.get(pdf_url, timeout=10)
                if response.status_code == 200:
                    base64_pdf = base64.b64encode(response.content).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                else:
                    st.error(f"Failed to pull content structure from portal endpoint (Status Code: {response.status_code})")
        except Exception as preview_err:
            st.error(f"Unable to render local base64 document frame data: {preview_err}")
            
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        st.link_button(
            "🔗 Open Official DailyMed Label Portal Context",
            selected_label["label_link"],
            use_container_width=True
        )

# ===================== OUTPUTS =====================

inactive_df = st.session_state.get("inactive_df", None)
product_char_df = st.session_state.get("product_char_df", None)
resources_df = st.session_state.get("resources_df", None)
orange_book_df = st.session_state.get("orange_book_display_df", None)

if inactive_df is not None:
    st.markdown("### Inactive Ingredients")
    st.dataframe(inactive_df, use_container_width=True)

if product_char_df is not None:
    st.markdown("### Product Characteristics")
    st.dataframe(product_char_df, use_container_width=True)

if resources_df is not None:
    st.markdown("### Resources")
    make_link_table(resources_df, ["Reference"])