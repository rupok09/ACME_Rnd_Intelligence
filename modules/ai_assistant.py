import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load master background configurations
load_dotenv()

def apply_assistant_theme():
    """Injects layout styling matching the unified high-contrast chat skin."""
    st.markdown(
        """
        <style>
        /* Shared Dashboard Banner Design */
        .assist-banner {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            border: 1px solid #3b82f6;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        .assist-title {
            color: #f8fafc;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .assist-subtitle {
            color: #cbd5e1;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        /* GEMINI WORKSPACE ROW CONTAINERS */
        .chat-row-user {
            width: 100% !important;
            display: flex !important;
            justify-content: flex-end !important;
            margin-bottom: 1.5rem !important;
            padding: 0 0.5rem !important;
        }
        
        .chat-bubble-user {
            background-color: #2e3c51 !important; 
            color: #f1f5f9 !important;
            padding: 0.85rem 1.25rem !important;
            border-radius: 18px 18px 4px 18px !important; 
            max-width: 80% !important;
            font-size: 0.95rem !important;
            line-height: 1.5 !important;
        }
        
        .chat-row-ai {
            width: 100% !important;
            display: flex !important;
            justify-content: flex-start !important;
            margin-bottom: 1.5rem !important;
            padding: 1rem !important;
            background-color: #f8fafc !important; 
            border-radius: 8px !important;
            border: 1px solid #e2e8f0 !important;
        }
        
        .chat-body-ai {
            color: #0f172a !important; 
            width: 100% !important;
            font-size: 0.95rem !important;
            line-height: 1.6 !important;
        }
        
        .gemini-turn-divider {
            border-bottom: 1px solid #e2e8f0;
            margin: 1.5rem 0;
            width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def show_ai_assistant():
    apply_assistant_theme()

    # --------------------------------------------------------------------------
    # HEADER BANNER CANVAS
    # --------------------------------------------------------------------------
    st.markdown(
        """
        <div class="assist-banner">
            <div class="assist-title">🤖 AI Assistant Command Center</div>
            <div class="assist-subtitle">
                Centralized generative intelligence console. Troubleshoot stability issues, cross-analyze 
                excipient properties, or draft formulation strategies directly with Gemini.
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # --------------------------------------------------------------------------
    # CREDENTIAL RESOLUTION GATEWAY & WIZARD
    # --------------------------------------------------------------------------
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key and "gemini_api_key" in st.session_state:
        api_key = st.session_state.gemini_api_key

    # If no key is found, show the setup wizard
    if not api_key:
        st.markdown("### 🔒 System Workspace Verification")
        login_col1, login_col2 = st.columns([3, 2])
        
        with login_col1:
            with st.container(border=True):
                st.markdown("**Manual Verification**")
                st.caption("Paste your workspace passcode validation token to open communication paths.")
                
                default_input_val = st.session_state.get("assistant_auto_key", "")
                user_token = st.text_input("Gemini Signature Register", type="password", placeholder="AIzaSy... or AQ....", value=default_input_val)
                
                if st.button("Initialize Assistant Node", use_container_width=True, type="primary"):
                    token_clean = user_token.strip()
                    # FIXED LOGIC: Accept both traditional AIzaSy strings and your direct AQ enterprise tokens
                    if token_clean.startswith("AIzaSy") or token_clean.startswith("AQ"):
                        st.session_state.gemini_api_key = token_clean
                        st.toast("Assistant link established!", icon="🤖")
                        st.rerun()
                    else:
                        st.error("Invalid token format mapping. Please ensure your key is copied cleanly from AI Studio.")
        
        with login_col2:
            with st.container(border=True):
                st.markdown("💡 **Automated Setup Wizard**")
                st.caption("Generate a signature map token instantly to initialize the interface framework.")
                st.markdown("[🌐 Launch Google AI Studio Launchpad](https://aistudio.google.com/)")
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                
                collected_paste = st.text_input("📋 Paste copied key stream directly here:", placeholder="Ctrl + V to dump here...")
                if collected_paste:
                    clean_token = collected_paste.strip()
                    if "AIzaSy" in clean_token or clean_token.startswith("AQ"):
                        st.session_state.assistant_auto_key = clean_token
                        st.session_state.gemini_api_key = clean_token
                        st.success("⚡ Token registered successfully! Reloading frame...")
                        st.rerun()
                    else:
                        st.warning("Tracking prefix missed. Verify your source clipboard maps.")
        return

    # Initialize client engine configuration silently
    genai.configure(api_key=api_key)

    # --------------------------------------------------------------------------
    # ACTIVE INTERACTIVE CHAT GRAPHIC GRID
    # --------------------------------------------------------------------------
    panel_left, panel_right = st.columns([3, 1])

    # Gather background cross-module states dynamically to enrich assistant understanding
    active_literature = st.session_state.get("extracted_doc_text", "")
    active_api = st.session_state.get("active_api_profile", None)

    with panel_right:
        st.markdown("### ⚙ guide SYSTEM")
        with st.container(border=True):
            st.markdown("**Active Environment**")
            st.code("gemini-2.5-flash", language="text")
            
            st.markdown("---")
            st.markdown("**Cross-Module Memory Context**")
            
            if active_literature:
                st.markdown("🟢 `Literature Sync Enabled`")
            else:
                st.markdown("⚪ `Literature Vault Vacant`")
                
            if active_api:
                st.markdown(f"🟢 `API Target Sync: {active_api.get('name', 'Unknown')}`")
            else:
                st.markdown("⚪ `No Active API Selected`")
            
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            if st.button("Clear Chat History", use_container_width=True, type="secondary"):
                st.session_state.chat_history_global = []
                st.rerun()

    with panel_left:
        st.markdown("### 💬 CONVERSATION WORKSPACE")
        
        if "chat_history_global" not in st.session_state:
            st.session_state.chat_history_global = []

        chat_container = st.container(height=400, border=True)
        with chat_container:
            if len(st.session_state.chat_history_global) == 0:
                st.markdown(
                    """
                    <div style='text-align: center; color: #64748b; padding-top: 8rem;'>
                        Hello Rupok! I am your central R&D Assistant node. How can I help you cross-reference your 
                        formulation datasets or resolve chemical anomalies today?
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                for message in st.session_state.chat_history_global:
                    if message["role"] == "user":
                        st.markdown(f'<div class="chat-row-user"><div class="chat-bubble-user">{message["text"]}</div></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-row-ai"><div class="chat-body-ai">{message["text"]}</div></div><div class="gemini-turn-divider"></div>', unsafe_allow_html=True)

        # Chat input element
        user_query = st.chat_input("Ask a cross-module formulation question...")
        if user_query:
            st.session_state.chat_history_global.append({"role": "user", "text": user_query})
            
            with st.spinner("Processing formulation parameters..."):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    
                    system_system_prompt = (
                        "You are Gemini, a highly advanced pharmaceutical development AI assistant working in the "
                        "ACME Laboratories R&D division. Your user is an executive formulation scientist. Answer all questions "
                        "with strict scientific accuracy, detailing structural mechanisms, compatibility logic, or physical "
                        "chemistry rules whenever applicable."
                    )
                    
                    if active_literature:
                        system_system_prompt += f"\n\n[LITERATURE MEMORY] Use the following extracted paper text parameters if helpful: {active_literature[:20000]}"
                    if active_api:
                        system_system_prompt += f"\n\n[API MOLECULE MEMORY] Use the following active profile parameters if helpful: {active_api}"
                    
                    compiled_messages = [f"System instruction: {system_system_prompt}\n"]
                    for msg in st.session_state.chat_history_global:
                        role_title = "User" if msg["role"] == "user" else "Assistant"
                        compiled_messages.append(f"{role_title}: {msg['text']}\n")
                    
                    compiled_prompt_block = "".join(compiled_messages)
                    response = model.generate_content(compiled_prompt_block)
                    
                    st.session_state.chat_history_global.append({"role": "assistant", "text": response.text})
                    st.rerun()
                except Exception as err:
                    st.error(f"Error communicating with processing cluster parameters: {err}")