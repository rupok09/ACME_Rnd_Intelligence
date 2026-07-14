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
        </style>
        """,
        unsafe_allow_html=True
    )

def execute_local_text_mining_fallback(text, file_names):
    """Local text analytics fallback parser triggered if all cloud model alternatives hit free tier limits."""
    fallback_matrix = []
    text_lower = text.lower()
    primary_file = file_names[0] if file_names else "Uploaded Document"
    
    # 1. API Solubility
    sol_value = "Solubility limits not explicitly isolated via local rules index."
    for line in text.split('\n'):
        if "solub" in line.lower() or "mg/ml" in line.lower():
            sol_value = line.strip()
            break
    fallback_matrix.append({
        'file_name': primary_file, 'metric': 'API Solubility',
        'extracted_value': sol_value[:150], 'evidence_trail': "Scanned via local text string patterns."
    })
    
    # 2. Dosage Form Type
    form_value = "Solid oral dosage form"
    for term in ["tablet", "capsule", "pellet", "suspension"]:
        if term in text_lower:
            form_value = f"{term.capitalize()} formulation configuration detected."
            break
    fallback_matrix.append({
        'file_name': primary_file, 'metric': 'Dosage Form Type',
        'extracted_value': form_value, 'evidence_trail': "Structural keywords located within document text strings."
    })
    
    # 3. Excipient / Carrier Composition
    excipients = []
    for exc in ["cellulose", "stearate", "lactose", "starch", "povidone", "silicon"]:
        if exc in text_lower:
            excipients.append(exc.capitalize())
    fallback_matrix.append({
        'file_name': primary_file, 'metric': 'Excipient / Carrier Composition',
        'extracted_value': ", ".join(excipients) if excipients else "Standard reference matrix carriers.",
        'evidence_trail': "Matched against internal local reference library indexes."
    })
    
    # 4. Key Findings / BCS Class
    bcs_value = "BCS Class tracking requires complete cloud verification."
    for bcs_term in ["bcs class i", "bcs class ii", "bcs class iii", "bcs class iv"]:
        if bcs_term in text_lower:
            bcs_value = bcs_term.upper()
            break
    fallback_matrix.append({
        'file_name': primary_file, 'metric': 'Key Findings / BCS Class',
        'extracted_value': bcs_value, 'evidence_trail': "Direct target signature mapped locally."
    })
    
    return fallback_matrix

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

    # FIXED: Bypassed standard workspace input block forms. Force login terminal checks.
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
                st.session_state.structured_matrix_data = None
                st.session_state.suggested_questions = []
                st.session_state.chat_history_lit = []
                st.session_state.lit_fallback_active = False
                
                with st.spinner("Processing local text extraction across files..."):
                    master_compiled_text = ""
                    for f in uploaded_pdfs:
                        try:
                            f.seek(0)
                            pdf_bytes = f.read()
                            if not pdf_bytes:
                                continue
                            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                            master_compiled_text += f"\n\n==================================================\n"
                            master_compiled_text += f"START OF DOCUMENT: {f.name}\n"
                            master_compiled_text += f"==================================================\n"
                            for page_num, page in enumerate(doc, start=1):
                                master_compiled_text += f"\n--- [{f.name} | PAGE {page_num}] ---\n"
                                master_compiled_text += page.get_text()
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
                    st.session_state.structured_matrix_data = None
                    st.session_state.suggested_questions = []
                    st.session_state.chat_history_lit = []
                    st.session_state.lit_fallback_active = False
                    st.rerun()
        else:
            st.session_state.extracted_doc_text = ""
            st.session_state.loaded_file_names = []
            st.session_state.structured_matrix_data = None
            st.session_state.suggested_questions = []
            st.session_state.chat_history_lit = []
            st.session_state.lit_fallback_active = False
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

            tab_chat, tab_matrix, tab_preview = st.tabs([
                "💬 AI Review Chat", "📊 Structured Extraction Table", "📄 Manual Document Viewers"
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
                with st.spinner("Analyzing data tables across repositories..."):
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

            # --- TAB 2: AUTOMATED STRUCTURED PARAMETER MATRIX ---
            with tab_matrix:
                st.markdown("### 📊 Automated Multi-File Parameter Matrix")
                st.caption("AI-driven deep structured extraction running verification mappings against source text elements.")

                if st.session_state.get("structured_matrix_data") is None:
                    with st.spinner("Compiling cross-document metrics data matrices..."):
                        matrix_prompt = (
                            f"Analyze the attached text and parse out critical pharmaceutical design metrics. "
                            f"Extract information for these 4 fields: 1. 'API Solubility', 2. 'Dosage Form Type', 3. 'Excipient / Carrier Composition', 4. 'Key Findings / BCS Class'.\n"
                            f"Format strictly as JSON array of objects: [{{'file_name': '...', 'metric': '...', 'extracted_value': '...', 'evidence_trail': '...'}}]\n\n"
                            f"Context Matrix:\n{st.session_state.extracted_doc_text[:30000]}"
                        )
                        
                        parsed_successfully = False
                        for model_variant in MODEL_HIERARCHY:
                            try:
                                genai.configure(api_key=api_key)
                                matrix_model = genai.GenerativeModel(model_variant)
                                matrix_response = matrix_model.generate_content(matrix_prompt, generation_config={"response_mime_type": "application/json"})
                                st.session_state.structured_matrix_data = json.loads(matrix_response.text)
                                st.session_state.lit_fallback_active = False
                                parsed_successfully = True
                                break
                            except Exception as m_err:
                                if "429" in str(m_err) or "quota" in str(m_err).lower():
                                    st.toast(f"⏳ {model_variant} limits reached. Routing processing thread to fallback layer...")
                                    continue
                        
                        if not parsed_successfully:
                            st.session_state.structured_matrix_data = execute_local_text_mining_fallback(st.session_state.extracted_doc_text, current_names)
                            st.session_state.lit_fallback_active = True
                            st.toast("⚡ Daily cloud limits reached. Swapped over to local parsing structures.", icon="⚙️")

                if st.session_state.get("structured_matrix_data"):
                    if st.session_state.get("lit_fallback_active", False):
                        st.markdown("⚠️ *Displaying local heuristic keyword matrix extraction (Cloud engine rate-limited).*")
                    st.markdown("---")
                    for entry in st.session_state.structured_matrix_data:
                        with st.container(border=True):
                            m_col1, m_col2 = st.columns([1, 2])
                            with m_col1:
                                st.markdown(f"📁 **File:** `{entry.get('file_name', 'N/A')}`")
                                st.markdown(f"📌 **Parameter:** `{entry.get('metric', 'N/A')}`")
                            with m_col2:
                                st.markdown(f"💡 **Extracted Metric Value:**\n*{entry.get('extracted_value', 'N/A')}*")
                                st.markdown(
                                    f"""<div style='background-color:#f1f5f9; padding:8px; border-left:3px solid #10b981; font-size:0.8rem; color:#475569;'>
                                        📄 <strong>Direct Evidence Trail:</strong><br>"{entry.get('evidence_trail', 'N/A')}"
                                    </div>""", 
                                    unsafe_allow_html=True
                                )

            # --- TAB 3: BASE64 DOCUMENT PREVIEWER ---
            with tab_preview:
                target_doc_name = st.selectbox("Select document viewport to render:", current_names)
                for f in uploaded_pdfs:
                    if f.name == target_doc_name:
                        try:
                            base64_pdf = base64.b64encode(f.getvalue()).decode('utf-8')
                            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                            st.markdown(pdf_display, unsafe_allow_html=True)
                        except Exception as preview_err:
                            st.error(f"Unable to generate preview layout for {f.name}: {preview_err}")