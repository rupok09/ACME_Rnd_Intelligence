import os
os.environ["RDK_BUILD_HEADLESS"] = "True"
import matplotlib
matplotlib.use("Agg")

import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
import requests
from rdkit import Chem
from rdkit.Chem import Draw

# ==========================================================================
# INLINED UTILITY CORE MECHANICS
# ==========================================================================
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
        
        /* Custom Clean Layout Headers matching Vercel UI */
        .section-header {
            color: #475569;
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 15px;
            margin-bottom: 0.75rem;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def check_compatibility_credentials():
    """Resolves session API keys and displays the dynamic onboarding setup wizard if vacant."""
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Access Denied. Please navigate to the Login portal module tab in the sidebar navigation stack to unlock system assets.")
        return None

    api_key = st.session_state.get("gemini_api_key", "")
    return api_key

# ==========================================================================
# MOLECULAR GRAPHICS & SEARCH INFRASTRUCTURE
# ==========================================================================
def get_smiles_from_pubchem(api_name):
    """Fetches canonical SMILES strings with optimized name sanitization for pharmaceutical salts."""
    try:
        clean_name = api_name.lower()
        for salt in [" bisulfate", " besylate", " hydrochloride", " hcl", " maleate", " sodium", " calcium", " fumarate"]:
            clean_name = clean_name.replace(salt, "")
        clean_name = clean_name.strip()

        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/v1/compound/name/{requests.utils.quote(clean_name)}/property/CanonicalSMILES/JSON"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data["PropertyTable"]["Properties"][0]["CanonicalSMILES"]
    except Exception:
        pass
    return None

def render_molecule_svg(smiles):
    """Generates an explicit SVG string of the chemical structure using RDKit."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            drawer = Draw.MolDraw2DSVG(240, 160)
            drawer.DrawMolecule(mol)
            drawer.FinishDrawing()
            return drawer.GetDrawingText()
    except Exception:
        pass
    return None

# ==========================================================================
# INTERFACE VIEW RENDERER PORTAL
# ==========================================================================
def show_drug_excipient_compatibility():
    apply_compatibility_theme()

    st.markdown(
        """
        <div class="compat-banner">
            <div class="compat-title">Drug-Excipient Compatibility Platform</div>
            <div class="compat-subtitle">
                Automated binary interaction predictive modeling engine. Screen custom excipient blend matrices 
                against active compound functional groups to predict stability and degradation risks.
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

    api_key = check_compatibility_credentials()
    if not api_key:
        return  

    genai.configure(api_key=api_key)

    # --------------------------------------------------------------------------
    # 1. SCREENING PARAMETERS (TOP SECTION)
    # --------------------------------------------------------------------------
    st.markdown("### 🎛️ SCREENING PARAMETERS")
    
    with st.container(border=True):
        col_param1, col_param2 = st.columns(2)
        with col_param1:
            target_api = st.text_input("Active Pharmaceutical Ingredient (API)", placeholder="e.g., Clopidogrel Bisulfate, Aspirin")
        
        with col_param2:
            comprehensive_excipients = [
                "Microcrystalline Cellulose (MCC) PH-101",
                "Microcrystalline Cellulose (MCC) PH-102",
                "Lactose Monohydrate (Fine Powder)",
                "Spray-Dried Lactose",
                "Anhydrous Lactose",
                "Mannitol (Pearlitol SD200)",
                "Dibasic Calcium Phosphate Anhydrous",
                "Dibasic Calcium Phosphate Dihydrate",
                "Isomalt",
                "Sorbitol",
                "Sucrose",
                "Povidone K30 (PVP K30)",
                "Povidone K90 (PVP K90)",
                "Copovidone (VA64)",
                "Hydroxypropyl Cellulose (HPC-LF)",
                "Hydroxypropyl Methylcellulose (HPMC E5)",
                "Pregelatinized Starch (Starch 1500)",
                "Crosspovidone (Polyplasdone XL)",
                "Sodium Starch Glycolate (Primojel)",
                "Croscarmellose Sodium (Ac-Di-Sol)",
                "Low-Substituted Hydroxypropyl Cellulose (L-HPC)",
                "Corn Starch",
                "Magnesium Stearate (Vegetable Grade)",
                "Stearic Acid",
                "Sodium Stearyl Fumarate (PRUV)",
                "Talc (Purified)",
                "Colloidal Silicon Dioxide (Aerosil 200)",
                "Hydrogenated Vegetable Oil",
                "Glyceryl Behenate",
                "Hydroxypropyl Methylcellulose (HPMC K100M CR)",
                "Hydroxypropyl Methylcellulose (HPMC K4M CR)",
                "Ethylcellulose",
                "Eudragit L100-55",
                "Eudragit S100",
                "Eudragit RL/RS PO",
                "Polyethylene Oxide (PEO)",
                "Sodium Lauryl Sulfate (SLS)",
                "Poloxamer 407",
                "Polysorbate 80 (Tween 80)",
                "Citric Acid Anhydrous",
                "Sodium Bicarbonate",
                "Calcium Carbonate"
            ]
            selected_excipients = st.multiselect("Select Excipients to Screen", options=comprehensive_excipients)
            
        trigger_prediction = st.button("Run Compatibility Screening Profile", use_container_width=True, type="primary")

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 2. COMPUTATIONAL ANALYSIS RESULTS (FULL WIDTH BOTTOM SECTION)
    # --------------------------------------------------------------------------
    st.markdown("### 🔬 COMPUTATIONAL ANALYSIS RESULTS")
    
    if trigger_prediction:
        if not target_api.strip():
            st.warning("⚠️ Please provide a valid Active Pharmaceutical Ingredient (API) target identity name.")
            return
        
        with st.spinner("Executing structural functional-group mechanistic queries..."):
            try:
                smiles = get_smiles_from_pubchem(target_api)
                molecule_svg = render_molecule_svg(smiles) if smiles else None
                
                model = genai.GenerativeModel("gemini-2.5-flash")
                analysis_prompt = (
                    f"You are an advanced computational chemistry platform specializing in pharmaceutical formulation risk assessment.\n"
                    f"Analyze the combination of API: '{target_api}' and Excipients: {selected_excipients}.\n\n"
                    f"Generate your output as a single valid JSON object containing exactly these keys:\n"
                    f"1. 'drug_profile': {{ 'chemical_class': '...', 'molecular_weight': '...', 'key_functional_groups': ['...'] }}\n"
                    f"2. 'recommended_risk': 'High' or 'Medium' or 'Low'\n"
                    f"3. 'excipient_profile': {{ 'cas_number': '...', 'formula': '...', 'synonyms': '...', 'category': '...' }}\n"
                    f"4. 'identified_evidence': An array of objects matching literary assays: [{{ 'study_type': '...', 'compatibility': '...', 'source': '...', 'details': '...' }}]\n"
                    f"5. 'rule_based_evidence': An array of objects detailing functional liabilities: [{{ 'drug_group': '...', 'formula': '...', 'excipient_group': '...', 'reaction_type': '...', 'description': '...' }}]\n\n"
                    f"CRITICAL RULES: Text details should contain full complete evidence lines sentences. Do NOT include HTML markdown tags."
                )
                
                response = model.generate_content(
                    analysis_prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                st.session_state.compat_structured_results = json.loads(response.text)
                st.session_state.active_screen_api = target_api
                st.session_state.active_molecule_svg = molecule_svg
                
            except Exception as err:
                err_msg = str(err)
                if "429" in err_msg or "quota" in err_msg.lower():
                    st.error("⚠️ **API Rate Limit Exceeded (Error 429)**: The workspace is experiencing high request volume. Please wait roughly 30–60 seconds before executing your next analytical run.")
                else:
                    st.error(f"Inference Engine Failed: {err_msg}")

    if "compat_structured_results" in st.session_state and st.session_state.get("compat_structured_results"):
        data = st.session_state.compat_structured_results
        svg_data = st.session_state.get("active_molecule_svg", None)
        
        tab_info, tab_evidence, tab_rules = st.tabs([
            "Formulation information", 
            "Identified evidence", 
            "Rule-based evidence"
        ])
        
        # --- TAB 1: FORMULATION INFORMATION ---
        with tab_info:
            col_drug, col_excipient = st.columns(2)
            
            with col_drug:
                st.markdown('<div class="section-header">Drug Profile</div>', unsafe_allow_html=True)
                with st.container(border=True):
                    dp = data.get("drug_profile", {})
                    
                    img_col, data_col = st.columns([2, 3])
                    with img_col:
                        if svg_data:
                            st.markdown(f'<div style="text-align:center; background-color:white; padding:5px; border-radius:6px; border:1px solid #e2e8f0;">{svg_data}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="height:100px; background-color:#f8fafc; display:flex; align-items:center; justify-content:center; border-radius:6px; border:1px dashed #cbd5e1; font-size:0.75rem; color:#64748b; text-align:center; padding:5px;">Structure Pending API Window</div>', unsafe_allow_html=True)
                    
                    with data_col:
                        st.markdown(f"**Name:** <span style='font-size:0.85rem; color:#1e293b;'>{st.session_state.active_screen_api.upper()}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Molecular Species:** <span style='font-size:0.85rem; color:#64748b;'>{dp.get('chemical_class', 'N/A')}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Molecular Weight:** <span style='font-size:0.85rem; color:#64748b;'>{dp.get('molecular_weight', 'N/A')}</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"<p style='margin-top:10px; font-size:0.8rem; color:#475569;'><b>Detected Functional Groups:</b> {', '.join(dp.get('key_functional_groups', []))}</p>", unsafe_allow_html=True)

            with col_excipient:
                st.markdown('<div class="section-header">Excipient Profile</div>', unsafe_allow_html=True)
                with st.container(border=True):
                    ep = data.get("excipient_profile", {})
                    primary_excipient = selected_excipients[0] if selected_excipients else "No Excipient Selected"
                    
                    st.markdown(f"**Excipient:** <span style='float:right; font-size:0.85rem; font-weight:600;'>{primary_excipient}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Excipient CAS:** <span style='float:right; font-size:0.85rem; color:#64748b;'>{ep.get('cas_number', 'N/A')}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Excipient Formula:** <span style='float:right; font-size:0.85rem; color:#64748b;'>{ep.get('formula', 'N/A')}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Excipient Synonyms:** <span style='display:block; font-size:0.8rem; color:#64748b; text-align:right; margin-top:2px;'>{ep.get('synonyms', 'N/A')}</span>", unsafe_allow_html=True)
                    
                    st.markdown("<hr style='margin:8px 0;'>", unsafe_allow_html=True)
                    st.markdown(f"**Category:** <span style='float:right; font-size:0.85rem; color:#059669; font-weight:600;'>{ep.get('category', 'Formulation Agent')}</span>", unsafe_allow_html=True)

            st.markdown('<div class="section-header">Risk Levels</div>', unsafe_allow_html=True)
            
            risk_level = data.get("recommended_risk", "Low")
            if risk_level == "High":
                risk_badge = '<span style="background-color:#fef2f2; color:#dc2626; padding:4px 12px; border-radius:20px; font-weight:700; font-size:0.85rem; border:1px solid #fecaca;">High risk</span>'
            elif risk_level == "Medium":
                risk_badge = '<span style="background-color:#fffbeb; color:#d97706; padding:4px 12px; border-radius:20px; font-weight:700; font-size:0.85rem; border:1px solid #fef3c7;">Medium risk</span>'
            else:
                risk_badge = '<span style="background-color:#f0fdf4; color:#16a34a; padding:4px 12px; border-radius:20px; font-weight:700; font-size:0.85rem; border:1px solid #bbf7d0;">Low risk</span>'
            
            with st.container(border=True):
                r_c1, r_c2 = st.columns(2)
                with r_c1:
                    st.markdown(f"**Identified risk:** &nbsp; {risk_badge}", unsafe_allow_html=True)
                with r_c2:
                    st.markdown(f"**Rule-based risk:** &nbsp; {risk_badge}", unsafe_allow_html=True)

        # --- TAB 2: IDENTIFIED EVIDENCE ---
        with tab_evidence:
            st.markdown('<div class="section-header">Identified Evidence</div>', unsafe_allow_html=True)
            evidence_list = data.get("identified_evidence", [])
            
            if evidence_list:
                table_rows = []
                for ev in evidence_list:
                    comp_status = ev.get('compatibility', 'Stable')
                    if 'stable' in comp_status.lower():
                        badge = '<span style="background-color:#f0fdf4; color:#16a34a; padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:600;">Stable / No Interaction</span>'
                    else:
                        badge = '<span style="background-color:#fef2f2; color:#dc2626; padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:600;">Interaction Detected</span>'
                        
                    table_rows.append({
                        "STUDY TYPE": f"<b>{ev.get('study_type', 'N/A')}</b>",
                        "COMPATIBILITY": badge,
                        "SOURCE REFERENCE": f"<span style='color:#475569; font-size:0.8rem;'>{ev.get('source', 'N/A')}</span>",
                        "SCIENTIFIC DETAILS": f"<span style='color:#334155; font-size:0.8rem;'>{ev.get('details', 'N/A')}</span>"
                    })
                
                df = pd.DataFrame(table_rows)
                st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
            else:
                st.info("No explicit binary literature exceptions matched against active criteria records.")

        # --- TAB 3: RULE-BASED EVIDENCE ---
        with tab_rules:
            st.markdown('<div class="section-header">Rule-Based Evidence</div>', unsafe_allow_html=True)
            rules_list = data.get("rule_based_evidence", [])
            
            if rules_list:
                rule_rows = []
                for rule in rules_list:
                    rx_type = f"<span style='color:#b91c1c; font-weight:600;'>{rule.get('reaction_type', 'N/A')}</span>"
                    rule_rows.append({
                        "DRUG RISK GROUP": f"<b>{rule.get('drug_group', 'N/A')}</b>",
                        "GROUP FORMULA": f"<code>{rule.get('formula', 'N/A')}</code>",
                        "EXCIPIENT RISK GROUP": f"<b>{rule.get('excipient_group', 'N/A')}</b>",
                        "REACTION TYPE": rx_type,
                        "INTERACTION DESCRIPTION": f"<span style='color:#334155; font-size:0.8rem;'>{rule.get('description', 'N/A')}</span>"
                    })
                
                df_rules = pd.DataFrame(rule_rows)
                st.write(df_rules.to_html(escape=False, index=False), unsafe_allow_html=True)
            else:
                st.info("No mechanical functional-group liabilities flagged for this formulation composition matrix.")
    else:
        if not trigger_prediction:
            st.markdown(
                """
                <div style="text-align: center; padding: 6rem 2rem; color: #64748b; border: 2px dashed #e2e8f0; border-radius: 8px;">
                    <strong>Awaiting Data Validation...</strong><br>
                    Execute an analytical query stream above to compile report arrays.
                </div>
                """, 
                unsafe_allow_html=True
            )