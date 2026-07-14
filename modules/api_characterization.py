import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.api_properties import PROPERTY_GROUPS
from utils.api_characterization_engine import (
    find_matching_records,
    run_api_characterization
)
from utils.excel_export import create_excel_report
from utils.rdkit_degradation_engine import screen_molecule_degradation


def render_html_table(df):
    html = df.to_html(
        escape=False,
        index=False,
        classes="result-table"
    )
    st.markdown(html, unsafe_allow_html=True)


def record_key(record):
    return f"{record['source']} | {record['record_name']} | {record['record_id']}"


def show_record_preview(record):
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

    with col1:
        if record.get("structure_url"):
            st.image(record["structure_url"], width=90)
        else:
            st.write("—")

    with col2:
        st.write(f"**{record['source']}**")
        st.write(record["record_name"])
        st.caption(record["record_id"])

    with col3:
        st.write(f"Formula: `{record.get('formula', '—')}`")
        st.write(f"MW: `{record.get('molecular_weight', '—')}`")

    with col4:
        if record.get("link"):
            st.link_button("Open", record["link"])
        else:
            st.write("—")


def show_api_characterization():
    st.title("API Characterization")
    st.write(
        "Search API records, select matching source records, choose required properties, "
        "and generate a source-linked characterization table."
    )

    api_name = st.text_input(
        "API / Compound Name",
        placeholder="e.g. Clarithromycin, Metformin HCl, Atorvastatin calcium",
        key="api_search_input"
    )

    if st.button("Search API", use_container_width=True):
        if not api_name.strip():
            st.warning("Please enter an API name first.")
            return

        with st.spinner("Searching PubChem, ChEMBL and DrugBank..."):
            records = find_matching_records(api_name.strip())

        st.session_state.api_matching_records = records
        st.session_state.current_api = api_name.strip()
        st.session_state.api_result_df = None

        if len(records) == 0:
            st.error("No matching records found from available sources.")
            return

    records = st.session_state.get("api_matching_records", [])

    if records:
        st.markdown("### Step 2: Select Matching Source Record(s)")
        selected_records = []

        for index, record in enumerate(records):
            st.markdown("---")
            selected = st.checkbox(
                f"Select {record['source']} record: {record['record_name']} ({record['record_id']})",
                value=True if record["source"] in ["PubChem", "ChEMBL"] else False,
                key=f"record_select_{index}_{record_key(record)}"
            )

            show_record_preview(record)
            if selected:
                selected_records.append(record)

        st.info("Default mode: selected records will be merged into one result table.")
        st.markdown("### Step 3: Select Required Properties")

        selected_properties = []
        default_selected = [
            "API Name", "Structure", "PubChem CID", "ChEMBL ID", "CAS Number",
            "Molecular Formula", "Molecular Weight", "IUPAC Name", "Canonical SMILES",
            "pKa", "LogP / LogD"
        ]

        for category, properties in PROPERTY_GROUPS.items():
            expanded = category in ["Identity", "Physicochemical"]
            with st.expander(category, expanded=expanded):
                cols = st.columns(2)
                for index, property_name in enumerate(properties):
                    with cols[index % 2]:
                        checked = st.checkbox(
                            property_name,
                            value=property_name in default_selected,
                            key=f"api_property_{category}_{property_name}"
                        )
                        if checked:
                            selected_properties.append(property_name)

        st.markdown("### Step 4: Characterize API")
        if st.button("Characterize API", use_container_width=True):
            if len(selected_records) == 0:
                st.warning("Please select at least one source record.")
                return
            if len(selected_properties) == 0:
                st.warning("Please select at least one property.")
                return

            with st.spinner("Merging selected source records and building characterization table..."):
                try:
                    characterization_payload = run_api_characterization(
                        selected_properties=selected_properties,
                        selected_records=selected_records
                    )
                    
                    if isinstance(characterization_payload, dict):
                        st.session_state.api_result_df = characterization_payload.get("properties")
                    else:
                        st.session_state.api_result_df = characterization_payload
                        
                    st.success("API characterization completed.")
                except Exception as e:
                    st.error(f"Error compiling characterization table: {e}")
                    return

    result_df = st.session_state.get("api_result_df", None)

    if result_df is not None:
        st.markdown("### API Characterization Results")
        render_html_table(result_df)

        excel_file = create_excel_report(result_df)
        st.download_button(
            label="Download Excel Report",
            data=excel_file,
            file_name=f"{st.session_state.get('current_api', 'API')}_API_Characterization.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )