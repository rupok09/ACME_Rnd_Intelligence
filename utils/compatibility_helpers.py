import streamlit as st
import os

def apply_compatibility_theme():
    """Injects high-contrast enterprise styling blocks matching unified application standards."""
    st.markdown(
        """
        <style>
        /* Shared Dashboard Banner Design */
        .compat-banner {
            background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
            border: 1px solid #059669;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        .compat-title {
            color: #f8fafc;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .compat-subtitle {
            color: #a7f3d0;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        /* Direct Risk Badging */
        .risk-high {
            color: #ef4444;
            background-color: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.2);
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.8rem;
        }
        .risk-medium {
            color: #f59e0b;
            background-color: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.2);
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.8rem;
        }
        .risk-low {
            color: #10b981;
            background-color: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def check_compatibility_credentials():
    """Resolves session API keys and displays the dynamic onboarding setup wizard if vacant."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key and "gemini_api_key" in st.session_state:
        api_key = st.session_state.gemini_api_key

    if not api_key:
        st.markdown("### 🔒 System Workspace Verification")
        login_col1, login_col2 = st.columns([3, 2])
        
        with login_col1:
            with st.container(border=True):
                st.markdown("**Manual Verification**")
                st.caption("Paste your workspace passcode validation token to open communication paths.")
                default_input_val = st.session_state.get("compat_auto_key", "")
                user_token = st.text_input("Gemini Signature Register", type="password", placeholder="AIzaSy... or AQ...", value=default_input_val, key="compat_key_input")
                
                if st.button("Initialize Compatibility Node", use_container_width=True, type="primary"):
                    token_clean = user_token.strip()
                    if token_clean.startswith("AIzaSy") or token_clean.startswith("AQ"):
                        st.session_state.gemini_api_key = token_clean
                        st.toast("Compatibility prediction pipeline linked!", icon="🧩")
                        st.rerun()
                    else:
                        st.error("Invalid token format mapping. Please check your AI Studio key string.")
        
        with login_col2:
            with st.container(border=True):
                st.markdown("💡 **Automated Setup Wizard**")
                st.caption("Generate a signature map token instantly to initialize the interface framework.")
                st.markdown("[🌐 Launch Google AI Studio Launchpad](https://aistudio.google.com/)")
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                
                collected_paste = st.text_input("📋 Paste copied key stream directly here:", placeholder="Ctrl + V to dump here...", key="compat_wizard_input")
                if collected_paste:
                    clean_token = collected_paste.strip()
                    if "AIzaSy" in clean_token or clean_token.startswith("AQ"):
                        st.session_state.compat_auto_key = clean_token
                        st.session_state.gemini_api_key = clean_token
                        st.success("⚡ Token registered successfully! Reloading frame...")
                        st.rerun()
                    else:
                        st.warning("Tracking prefix missed. Verify your source clipboard maps.")
        return None
        
    return api_key