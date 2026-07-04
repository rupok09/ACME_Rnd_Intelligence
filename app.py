import streamlit as st

# Crucial: Page configuration must be the absolute first Streamlit command executed
st.set_page_config(
    page_title="ACME R&D Intelligence",
    page_icon="🧪",
    layout="wide"
)

import traceback

# Helper to safely create a module view with isolated error catching
def safe_import_module(module_path, function_name):
    try:
        mod = __import__(module_path, fromlist=[function_name])
        return getattr(mod, function_name)
    except Exception as e:
        error_msg = traceback.format_exc()
        def fallback_view():
            st.error(f"❌ Failed to load module: `{module_path}`")
            with st.expander("🔍 View Technical Dependency & Compilation Logs", expanded=True):
                st.code(error_msg, language="python")
        return fallback_view

# Load global CSS parameters and navigation utils
from styles.custom_css import load_css
from utils.navigation import (
    init_navigation,
    go_to,
    go_back,
    go_home
)

# Load global CSS parameters and initialize session state navigation matrices
load_css()
init_navigation()

# SINGLE-TAB ROUTER INTERCEPTOR: Routes custom text navbar clicks cleanly inside the same window frame
if "nav" in st.query_params:
    st.session_state.page = st.query_params["nav"]
    st.query_params.clear()

# Lazy-loaded safe feature module mappings
show_home = safe_import_module("modules.home", "show_home")
show_literature_intelligence = safe_import_module("modules.literature_intelligence", "show_literature_intelligence")
show_api_characterization = safe_import_module("modules.api_characterization", "show_api_characterization")
show_rld_information = safe_import_module("modules.rld_information", "show_rld_information")
show_drug_excipient_compatibility = safe_import_module("modules.drug_excipient_compatibility", "show_drug_excipient_compatibility")
show_pharmacokinetics = safe_import_module("modules.pharmacokinetics", "show_pharmacokinetics")
show_doe_optimization = safe_import_module("modules.doe_optimization", "show_doe_optimization")
show_ai_assistant = safe_import_module("modules.ai_assistant", "show_ai_assistant")
show_login = safe_import_module("modules.login", "show_login")


# ================= TOP BAR =================
top_back, top_title, top_login = st.columns([1, 5, 1])

with top_back:
    if st.button("← Back", use_container_width=True, key="top_bar_back"):
        go_back()

with top_title:
    st.markdown(
        "<div class='top-app-title'>ACME R&D Intelligence</div>",
        unsafe_allow_html=True
    )

with top_login:
    if st.button("👤 Login", use_container_width=True, key="top_bar_login"):
        go_to("Login")


# ================= SIDEBAR =================
with st.sidebar:
    # 1. FIXED LOGO CORNER NODE: Side-by-side branding panel block
    logo_side_col, title_side_col = st.columns([1, 3])
    with logo_side_col:
        # Fallback handling for logo image asset visualization
        try:
            st.image("assets/acme_logo.png", width=55)
        except Exception:
            st.markdown("### 🧪")
            
    with title_side_col:
        st.markdown(
            """
            <div style="margin-top: -2px;">
                <div style="color: #f8fafc; font-size: 1.1rem; font-weight: 700; line-height: 1.2;">ACME Laboratories Ltd.</div>
                <div style="color: #94a3b8; font-size: 0.72rem; margin-top: 2px;">For Health • Vigour • Happiness</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown(
        """
        <div style="border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 15px; margin-top: 5px;">
            <span style="font-size: 0.75rem; font-weight: 600; color: #38bdf8; letter-spacing: 0.5px; text-transform: uppercase;">
                Research & Development Hub
            </span>
            <span style="float: right; font-size: 0.7rem; color: #64748b; font-family: monospace;">v1.0.0</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Sequential Left-Hand Sidebar Module Quick Links Actions
    if st.button("⌂ Home", use_container_width=True, key="side_nav_home"):
        go_home()

    if st.button("📚 Literature Review", use_container_width=True, key="side_nav_lit"):
        go_to("Literature Review")

    if st.button("🧪 API Characterization", use_container_width=True, key="side_nav_api"):
        go_to("API Characterization")

    if st.button("📋 RLD Information", use_container_width=True, key="side_nav_rld"):
        go_to("RLD Information")

    if st.button("🧩 Drug-Excipient Compatibility", use_container_width=True, key="side_nav_compat"):
        go_to("Drug-Excipient Compatibility")

    if st.button("🧬 Pharmacokinetics", use_container_width=True, key="side_nav_pk"):
        go_to("Pharmacokinetics")

    if st.button("📊 DOE Optimization", use_container_width=True, key="side_nav_doe"):
        go_to("DOE Optimization")

    if st.button("🤖 AI Assistant", use_container_width=True, key="side_nav_ai"):
        go_to("AI Assistant")

    st.markdown(
        """
        <div class="sidebar-card" style="margin-top: 15px;">
            <b>R&D Intelligence Hub</b><br><br>
            A modular AI platform for literature review, API characterization, 
            RLD information, compatibility assessment, pharmacokinetics simulation,
            DOE optimization, and conversational AI assistance.
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------------------
    # DYNAMIC SIDEBAR USER CAPTURE PROFILE GRID
    # ------------------------------------------------------------------------------
    st.markdown("---")

    if st.session_state.get("authenticated", False):
        current_user_display = f"ID: {st.session_state.get('employee_id', '41432')}"
        current_role_display = "Authorized Scientist"
    else:
        current_user_display = "Guest Terminal"
        current_role_display = "Awaiting Authentication"

    with st.container(border=True):
        st.markdown("<small style='color: #64748b; font-weight: 600;'>CURRENT USER</small>", unsafe_allow_html=True)
        st.markdown(f"#### 👤 {current_user_display}")
        st.markdown(f"<span style='font-size: 0.85rem; color: #38bdf8;'>⚙️ {current_role_display}</span>", unsafe_allow_html=True)


# ================= PAGE ROUTER =================
page = st.session_state.page

if page == "Home":
    show_home()

elif page == "Literature Review":
    show_literature_intelligence()

elif page == "API Characterization":
    show_api_characterization()

elif page == "RLD Information":
    show_rld_information()

elif page == "Drug-Excipient Compatibility":
    show_drug_excipient_compatibility()

elif page == "Microstructural Layer":
    show_drug_excipient_compatibility()

elif page == "Pharmacokinetics":
    show_pharmacokinetics()

elif page == "DOE Optimization":
    show_doe_optimization()

elif page == "AI Assistant":
    show_ai_assistant()

elif page == "Login":
    show_login()

else:
    go_home()


# ================= FOOTER =================
st.markdown(
    """
    <div class="footer">
        ©2026 ACME Laboratories Ltd. — Research & Development Division.
    </div>
    """,
    unsafe_allow_html=True
)