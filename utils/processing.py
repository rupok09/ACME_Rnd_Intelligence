import streamlit as st
import time


def show_processing(title):
    st.markdown("---")
    st.subheader(title)

    progress = st.progress(0)
    status = st.empty()

    steps = [
        "Initializing request...",
        "Reading document / preparing API query...",
        "Detecting API name...",
        "Connecting to PubChem...",
        "Searching trusted web sources...",
        "Validating collected data...",
        "Generating structured result table..."
    ]

    for i, step in enumerate(steps):
        status.info(step)
        progress.progress(int((i + 1) / len(steps) * 100))
        time.sleep(0.45)

    status.empty()