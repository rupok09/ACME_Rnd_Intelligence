import streamlit as st

def show_pharmacokinetics():
    st.title("Pharmacokinetics")

    st.info("This module is under development.")

    st.markdown(
        """
        ### Planned Features

        - Generate IVIVC Level A templates
        - Upload dissolution profile raw matrices
        - Select critical excipient modifiers
        - Predict bioequivalence (BE) risk maps
        - Compare prototypes against RLD benchmarks
        - Export PK summary exposure reports
        """
    )