import streamlit as st
import pandas as pd

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
    st.title("🧪 API Characterization")
    st.write(
        "Search API records, select matching source records, choose required properties, "
        "and generate a source-linked characterization table."
    )

    st.markdown(
        """
        <div class="api-card">
            <div class="api-card-title">Step 1: Search API</div>
            <div class="api-card-text">
                Enter API name, salt form, CAS number, PubChem CID, or ChEMBL ID.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    api_name = st.text_input(
        "API / Compound Name",
        placeholder="e.g. Clarithromycin, Metformin HCl, Atorvastatin calcium",
        key="api_search_input"
    )

    if st.button("Find Matching Records", use_container_width=True):
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
                    # Unpack dataframe layer safely out of engine result payload dictionary
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

        # ==============================================================================
        # RDKit INTEGRATED STRUCTURAL INTELLIGENCE
        # ==============================================================================
        st.markdown("---")
        st.markdown("## 5. RDKit Structural Intelligence")

        smiles = None

        # 1. Primary Strategy: Agnostic Row Crawler across the compiled result DataFrame
        if result_df is not None and not result_df.empty:
            for index, row in result_df.iterrows():
                row_cells = [str(val).strip() for val in row.values]
                
                # Check if this specific row describes a SMILES entry
                if any("smiles" in cell.lower() for cell in row_cells):
                    for cell in row_cells:
                        # Clean up formatting, merged slashes, and spaces
                        clean_cell = cell.split("/")[0].strip()
                        clean_cell = "".join(clean_cell.split())
                        
                        # Identify the string by filtering out layout metadata labels
                        if len(clean_cell) > 10 and not any(x in clean_cell.lower() for x in ["smiles", "identity", "physicochemical", "found", "detected", "review", "missing"]):
                            # Salt-Stripper: Isolate the parent organic skeleton if counter-ions exist
                            if "." in clean_cell:
                                smiles = max(clean_cell.split("."), key=len)
                            else:
                                smiles = clean_cell
                            break
                if smiles:
                    break

        # 2. Secondary Strategy: Fallback to crawling raw session records if table parsing is skipped
        if not smiles:
            active_records = st.session_state.get("api_matching_records", [])
            target_keys = ["smiles", "canonicalsmiles", "canonical_smiles"]
            
            for rec in active_records:
                for raw_key, raw_val in rec.items():
                    normalized_key = str(raw_key).lower().replace("_", "").replace(" ", "")
                    if normalized_key in target_keys and raw_val:
                        raw_str = str(raw_val).split("/")[0].strip()
                        clean_str = "".join(raw_str.split())
                        
                        if "." in clean_str:
                            smiles = max(clean_str.split("."), key=len)
                        else:
                            smiles = clean_str
                        break
                if smiles:
                    break

        # 3. Execution Pipeline: Feed the verified, isolated parent string to the RDKit engine
        if smiles:
            current_api_name = st.session_state.get('current_api', 'API Molecule')
            with st.spinner("Running RDKit decomposition & hot-spot screening analysis..."):
                try:
                    rdkit_result = screen_molecule_degradation(current_api_name, smiles)

                    st.subheader("Structure")
                    if rdkit_result.get("image"):
                        st.image(rdkit_result["image"], width=450)

                    st.subheader("Molecular Properties")
                    st.dataframe(rdkit_result["properties"], use_container_width=True)

                    st.subheader("Functional Group Scan")
                    st.dataframe(rdkit_result["functional_groups"], use_container_width=True)

                    st.subheader("Predicted Degradation Products")
                    st.dataframe(rdkit_result["degradants"], use_container_width=True)
                except Exception as rdk_err:
                    st.error(f"RDKit Structural Subsystem Failure: {rdk_err}")
        else:
            st.info("Structure verification note: Canonical SMILES string field not discovered in selected data lineage logs to seed RDKit automation frameworks.")