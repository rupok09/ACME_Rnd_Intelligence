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
    # FIXED: Hard check authentication profile matrix mapping first. Reject unverified connections.
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Access Denied. Please navigate to the Login portal module tab in the sidebar navigation stack to unlock system assets.")
        return None

    api_key = st.session_state.get("gemini_api_key", "")
    return api_key