import streamlit as st
import os

def apply_login_theme():
    """Injects professional enterprise authentication styling layers."""
    st.markdown(
        """
        <style>
        .login-container {
            max-width: 450px;
            margin: 4rem auto;
            padding: 2.5rem;
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-title {
            color: #0f172a;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .login-subtitle {
            color: #64748b;
            font-size: 0.88rem;
        }
        .status-authenticated {
            background-color: #f0fdf4;
            border: 1px solid #bbf7d0;
            color: #16a34a;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def show_login():
    apply_login_theme()

    # Initialize key state variables if not already present in session cache
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = ""
    if "employee_id" not in st.session_state:
        st.session_state.employee_id = ""

    # --------------------------------------------------------------------------
    # STATE A: ALREADY AUTHENTICATED SYSTEM VIEW
    # --------------------------------------------------------------------------
    if st.session_state.authenticated:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="login-header">
                <div class="login-title">🔐 Active Session Live</div>
                <div class="login-subtitle">ACME R&D Intelligence Token Matrix</div>
            </div>
            <div class="status-authenticated">
                🟢 Verified: Employee #{st.session_state.employee_id}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.info("Your API credential signature is safely locked into local environment memory. All active platform modules are unlocked.")
        
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        if st.button("Terminate Session (Logout)", use_container_width=True, type="primary"):
            st.session_state.authenticated = False
            st.session_state.gemini_api_key = ""
            st.session_state.employee_id = ""
            st.toast("Credentials purged successfully.", icon="🔒")
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # --------------------------------------------------------------------------
    # STATE B: AUTHENTICATION ACCESS PORTAL FORM
    # --------------------------------------------------------------------------
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="login-header">
            <div class="login-title">🔐 ACME R&D Gateway</div>
            <div class="login-subtitle">Secure single sign-on credential vault mapping system</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Input elements
    emp_id_input = st.text_input("Employee ID", placeholder="e.g., 41432")
    api_key_input = st.text_input("Password (Google AI Studio API Key)", type="password", placeholder="AIzaSy... or AQ...")

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    
    if st.button("Authenticate & Mount API Node", use_container_width=True):
        clean_emp_id = emp_id_input.strip()
        clean_api_key = api_key_input.strip()

        # Input verification gates
        if not clean_emp_id:
            st.error("⚠️ System requires a valid Employee ID to map terminal access signatures.")
            return
            
        if not clean_api_key:
            st.error("⚠️ System requires a secure Password string (API Key) to establish communication relays.")
            return

        # Validate token syntax signatures (supports basic AIzaSy and premium enterprise AQ format maps)
        if not (clean_api_key.startswith("AIzaSy") or clean_api_key.startswith("AQ")):
            st.error("⚠️ Invalid credential syntax structure. Verify your token entry and try again.")
            return

        # Committing tokens safely into runtime state memory caches
        st.session_state.authenticated = True
        st.session_state.employee_id = clean_emp_id
        st.session_state.gemini_api_key = clean_api_key
        
        st.toast(f"Welcome back, Employee {clean_emp_id}! Session mounted.", icon="🚀")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)