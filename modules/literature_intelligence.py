import streamlit as st
import fitz  # PyMuPDF for optimized local browser text mining
import google.generativeai as genai
import os
import base64
import json
from dotenv import load_dotenv

# Load background credentials immediately on module invocation
load_dotenv()

# Task suitability model routing array hierarchy
MODEL_HIERARCHY = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

def apply_literature_theme():
    """Injects professional enterprise layout overrides mirroring the Gemini chat layout."""
    st.markdown(
        """
        <style>
        /* Document Banner Design */
        .lit-banner {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        .lit-title {
            color: #f8fafc;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .lit-subtitle {
            color: #94a3b8;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        /* GEMINI NATIVE CHAT LOOK & FEEL LAYOUT OVERRIDES */
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
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
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

        /* Native Secure Document Preview Wrapper Frame */
        .pdf-render-scroll-stage {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 25px;
            height: 600px;
            overflow-y: scroll;
            font-family: 'Courier New', Courier, monospace;
            white-space: pre-wrap;
            color: #000000 !important;
            font-size: 0.9rem;
            line-height: 1.5;
            box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def show_literature_intelligence():
    apply_literature_theme()

    st.markdown(
        """
        <div class="lit-banner">
            <div class="lit-title">Literature Reviewer</div>
            <div class="lit-subtitle">
                Extract hidden R&D insights across multiple raw research publications using advanced structured mining
                with direct compliance text-evidence trails.
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Access Denied. Please navigate to the Login portal module tab in the sidebar navigation stack to unlock system assets.")
        return

    api_key = st.session_state.gemini_api_key

    # --------------------------------------------------------------------------
    # SPLIT PANEL LAYOUT ENGINE: [ DOCUMENT SOURCE | REVIEW ASSISTANT ]
    # --------------------------------------------------------------------------
    panel_left, panel_right = st.columns([2, 3])

    with panel_left:
        st.markdown("### 📁 DOCUMENT SOURCE")
        uploaded_pdfs = st.file_uploader(
            "Upload research papers to start AI-powered review",
            type=["pdf"], accept_multiple_files=True, label_visibility="collapsed", key="lit_pdf_uploader"
        )

        if uploaded_pdfs:
            if "loaded_file_names" not in st.session_state:
                st.session_state.loaded_file_names = []
            
            current_names = [f.name for f in uploaded_pdfs]
            
            if current_names != st.session_state.loaded_file_names:
                st.session_state.extracted_doc_text = ""
                st.session_state.loaded_file_names = current_names
                st.session_state.suggested_questions = []
                st.session_state.chat_history_lit = []
                
                # Active dictionary cache mapping individual files to separated strings
                st.session_state.individual_docs_cache = {}
                
                with st.spinner("Processing local text extraction across files..."):
                    master_compiled_text = ""
                    for f in uploaded_pdfs:
                        try:
                            f.seek(0)
                            pdf_bytes = f.read()
                            if not pdf_bytes:
                                continue
                            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                            
                            file_specific_text = ""
                            master_compiled_text += f"\n\n==================================================\n"
                            master_compiled_text += f"START OF DOCUMENT: {f.name}\n"
                            master_compiled_text += f"==================================================\n"
                            
                            for page_num, page in enumerate(doc, start=1):
                                extracted_page = page.get_text()
                                file_specific_text += f"\n--- [PAGE {page_num}] ---\n{extracted_page}"
                                master_compiled_text += f"\n--- [{f.name} | PAGE {page_num}] ---\n{extracted_page}"
                            
                            # Cache the separated string map for individual tab selections
                            st.session_state.individual_docs_cache[f.name] = file_specific_text.strip()
                                
                        except Exception as parse_err:
                            st.error(f"Error parsing text footprint inside {f.name}: {parse_err}")
                    
                    st.session_state.extracted_doc_text = master_compiled_text.strip()

            with st.container(border=True):
                st.markdown(f"📚 **Loaded Context: {len(uploaded_pdfs)} Files Active**")
                for f in uploaded_pdfs:
                    file_size_mb = len(f.getvalue()) / (1024 * 1024)
                    st.markdown(f"📄 <span style='font-size:0.85rem;'>{f.name} ({file_size_mb:.2f} MB)</span>", unsafe_allow_html=True)
                
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                if st.button("Remove All Documents", use_container_width=True):
                    st.session_state.extracted_doc_text = ""
                    st.session_state.loaded_file_names = []
                    st.session_state.suggested_questions = []
                    st.session_state.chat_history_lit = []
                    st.session_state.individual_docs_cache = {}
                    st.rerun()
        else:
            st.session_state.extracted_doc_text = ""
            st.session_state.loaded_file_names = []
            st.session_state.suggested_questions = []
            st.session_state.chat_history_lit = []
            st.session_state.individual_docs_cache = {}
            st.markdown(
                """
                <div style="border: 2px dashed #334155; border-radius: 8px; padding: 3rem; text-align: center; color: #64748b;">
                    Drag & drop one or multiple PDF files here.<br>
                    <span style="font-size: 0.75rem;">Supported format: PDF documents only</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

    with panel_right:
        st.markdown("### 🤖 REVIEW ASSISTANT")
        
        if not uploaded_pdfs or not st.session_state.get("extracted_doc_text"):
            st.markdown(
                """
                <div style="text-align: center; padding: 5rem 2rem; color: #64748b;">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔍</div>
                    <strong>No Documents Active / Parsed</strong><br>
                    Upload one or more research papers on the left to initialize the AI Review Assistant workspace.
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.markdown(f"<p style='color: #3b82f6; font-size: 0.85rem; font-weight: 600;'>🟢 Active Multi-Context Matrix Locked ({len(uploaded_pdfs)} Papers)</p>", unsafe_allow_html=True)

            if "chat_history_lit" not in st.session_state:
                st.session_state.chat_history_lit = []

            # ------------------------------------------------------------------
            # TASK SUITABILITY ROUTING ENGINE (FOR CHIP QUESTIONS)
            # ------------------------------------------------------------------
            if not st.session_state.get("suggested_questions"):
                kw_prompt = (
                    f"Review the following text data and formulate 3 short analytical questions. "
                    f"Constraint: max 5 to 7 words total. JSON list of strings format.\n\n"
                    f"Text Snapshot:\n{st.session_state.extracted_doc_text[:12000]}"
                )
                for model_variant in MODEL_HIERARCHY:
                    try:
                        genai.configure(api_key=api_key)
                        kw_model = genai.GenerativeModel(model_variant)
                        kw_response = kw_model.generate_content(kw_prompt, generation_config={"response_mime_type": "application/json"})
                        st.session_state.suggested_questions = json.loads(kw_response.text)
                        break
                    except Exception:
                        continue
                
                if not st.session_state.get("suggested_questions"):
                    st.session_state.suggested_questions = [
                        "What solubility values are reported?",
                        "Show excipient compatibility observations.",
                        "Are stability profiles mentioned?"
                    ]

            tab_chat, tab_preview = st.tabs([
                "💬 AI Review Chat", "📄 Manual Document Viewers"
            ])

            clicked_query = None

            # --- TAB 1: AI REVIEW CHAT ---
            with tab_chat:
                chat_container = st.container(height=400, border=True)
                with chat_container:
                    if len(st.session_state.chat_history_lit) == 0:
                        st.markdown("<div style='text-align: center; color: #64748b; padding-top: 5rem;'>Context initialized successfully. Ask any specific question regarding this document below.</div>", unsafe_allow_html=True)
                    else:
                        for message in st.session_state.chat_history_lit:
                            if message["role"] == "user":
                                st.markdown(f'<div class="chat-row-user"><div class="chat-bubble-user">{message["text"]}</div></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="chat-row-ai"><div class="chat-body-ai">{message["text"]}</div></div><div class="gemini-turn-divider"></div>', unsafe_allow_html=True)

                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                st.markdown("<p style='font-size:0.8rem; font-weight:600; color:#64748b; margin-bottom:4px;'>🚀 QUICK EXPLORATION SUGGESTIONS</p>", unsafe_allow_html=True)
                chip_cols = st.columns(len(st.session_state.suggested_questions))
                for idx, question in enumerate(st.session_state.suggested_questions):
                    with chip_cols[idx]:
                        if st.button(question, key=f"chip_{idx}", use_container_width=True):
                            clicked_query = question

            user_query = st.chat_input("Cross-reference or ask questions about your uploaded documents...")
            active_input = user_query or clicked_query
            
            if active_input:
                st.session_state.chat_history_lit.append({"role": "user", "text": active_input})
                with st.spinner("Analyzing document references..."):
                    context_guided_prompt = (
                        f"You are a helpful and precise AI collaborator assisting a pharmaceutical formulation scientist.\n"
                        f"Answer the user's question accurately using this reference text data matrix:\n"
                        f"{st.session_state.extracted_doc_text[:35000]}\n\n"
                        f"User Query: {active_input}"
                    )
                    chat_success = False
                    for model_variant in MODEL_HIERARCHY:
                        try:
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel(model_variant)
                            response = model.generate_content(context_guided_prompt)
                            st.session_state.chat_history_lit.append({"role": "assistant", "text": response.text})
                            chat_success = True
                            st.rerun()
                            break
                        except Exception:
                            continue
                    if not chat_success:
                        st.error("⚠️ Token pipeline overtaxed across available models. Please paste an alternative key up top or wait for the quota window to clear.")

            # --- TAB 2: MANUAL DOCUMENT VIEWERS (BYPASSING BLOCKED IFRAMES) ---
            with tab_preview:
                target_doc_name = st.selectbox("Select document viewport to render:", current_names)
                if "individual_docs_cache" in st.session_state and target_doc_name in st.session_state.individual_docs_cache:
                    doc_raw_text = st.session_state.individual_docs_cache[target_doc_name]
                    
                    # Injects text data inside a secure, scrollable box wrapper (completely immune to Chrome blocking)
                    st.markdown(
                        f"""
                        <div class="pdf-render-scroll-stage">
{doc_raw_text}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                else:
                    st.info("Processing structured workspace rendering maps...")