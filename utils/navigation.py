import streamlit as st


def init_navigation():
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    if "history" not in st.session_state:
        st.session_state.history = []


def go_to(page_name):
    current_page = st.session_state.get("page", "Home")

    if current_page != page_name:
        st.session_state.history.append(current_page)

    st.session_state.page = page_name
    st.rerun()


def go_back():
    if "history" in st.session_state and len(st.session_state.history) > 0:
        st.session_state.page = st.session_state.history.pop()
    else:
        st.session_state.page = "Home"

    st.rerun()


def go_home():
    current_page = st.session_state.get("page", "Home")

    if current_page != "Home":
        st.session_state.history.append(current_page)

    st.session_state.page = "Home"
    st.rerun()