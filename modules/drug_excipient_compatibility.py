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

# Import the clean theme and verification modules from your utilities path
from utils.compatibility_helpers import apply_compatibility_theme, check_compatibility_credentials

def get_smiles_from_pubchem(api_name):
    """Fetches canonical SMILES strings with optimized name sanitization for pharmaceutical salts."""
    try:
        # Sanitize common salt extensions to optimize parent molecule lookup rates
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
            drawer = Draw.MolDraw2DSVG(300, 200)
            drawer.DrawMolecule(mol)
            drawer.FinishDrawing()
            return drawer.GetDrawingText()
    except Exception:
        pass
    return None

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
    # CORE INTERFACE FORM LAYOUT
    # --------------------------------------------------------------------------
    panel_left, panel_right = st.columns([2, 3])

    with panel_left:
        st.markdown("### 🎛️ SCREENING PARAMETERS")
        
        with st.container(border=True):
            target_api = st.text_input("Active Pharmaceutical Ingredient (API)", placeholder="e.g., Clopidogrel Bisulfate, Aspirin")
            
            # Expanded and categorized industrial excipient matrix options
            comprehensive_excipients = [
                # --- Diluents / Fillers ---
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
                
                # --- Binders ---
                "Povidone K30 (PVP K30)",
                "Povidone K90 (PVP K90)",
                "Copovidone (VA64)",
                "Hydroxypropyl Cellulose (HPC-LF)",
                "Hydroxypropyl Methylcellulose (HPMC E5)",
                "Pregelatinized Starch (Starch 1500)",
                
                # --- Disintegrants ---
                "Crosspovidone (Polyplasdone XL)",
                "Sodium Starch Glycolate (Primojel)",
                "Croscarmellose Sodium (Ac-Di-Sol)",
                "Low-Substituted Hydroxypropyl Cellulose (L-HPC)",
                "Corn Starch",
                
                # --- Lubricants / Glidants ---
                "Magnesium Stearate (Vegetable Grade)",
                "Stearic Acid",
                "Sodium Stearyl Fumarate (PRUV)",
                "Talc (Purified)",
                "Colloidal Silicon Dioxide (Aerosil 200)",
                "Hydrogenated Vegetable Oil",
                "Glyceryl Behenate",
                
                # --- Polymers / Coating Agents / Functional Matrix ---
                "Hydroxypropyl Methylcellulose (HPMC K100M CR)",
                "Hydroxypropyl Methylcellulose (HPMC K4M CR)",
                "Ethylcellulose",
                "Eudragit L100-55",
                "Eudragit S100",
                "Eudragit RL/RS PO",
                "Polyethylene Oxide (PEO)",
                
                # --- Surfactants / Solubilizers / Miscellaneous ---
                "Sodium Lauryl Sulfate (SLS)",
                "Poloxamer 407",
                "Polysorbate 80 (Tween 80)",
                "Citric Acid Anhydrous",
                "Sodium Bicarbonate",
                "Calcium Carbonate"
            ]
            
            selected_excipients = st.multiselect(
                "Select Excipients to Screen",
                options=comprehensive_excipients,
            )
            
            # Expanded Solid Oral Dosage Form Options
            expanded_dosage_forms = [
                "Immediate-Release Tablet (Film-Coated)",
                "Immediate-Release Tablet (Uncoated)",
                "Hard Gelatin Capsule",
                "Hydroxymethylcellulose (HPMC) Capsule",
                "Sustained-Release Hydrophilic Matrix Tablet",
                "Extended-Release Lipophilic Matrix Tablet",
                "Enteric-Coated (Delayed-Release) Tablet",
                "Enteric-Coated Pellet Capsule",
                "Orodispersible Tablet (ODT)",
                "Chewable Tablet",
                "Effervescent Tablet",
                "Bilayer Tablet (Fixed-Dose Combination)",
                "Mini-Tablets in Capsule"
            ]
            
            dosage_form = st.selectbox("Intended Dosage Form", options=expanded_dosage_forms)
            
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            trigger_prediction = st.button("Run Compatibility Screening Profile", use_container_width=True, type="primary")

    # --------------------------------------------------------------------------
    # RIGHT SIDE: ADVANCED REPORT VIEWER STAGE (WITH EXPLICIT 429 HANDLING)
    # --------------------------------------------------------------------------
    with panel_right:
        st.markdown("### 🔬 COMPUTATIONAL ANALYSIS RESULTS")
        
        if trigger_prediction:
            if not target_api.strip():
                st.warning("⚠️ Please provide a valid Active Pharmaceutical Ingredient (API) target identity name.")
                return
            
            with st.spinner("Executing structural functional-group mechanistic queries..."):
                try:
                    # 1. Fetch structure maps using the sanitized utility function
                    smiles = get_smiles_from_pubchem(target_api)
                    molecule_svg = render_molecule_svg(smiles) if smiles else None
                    
                    # 2. Query Gemini analysis model
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    analysis_prompt = (
                        f"You are an advanced computational chemistry platform specializing in pharmaceutical formulation risk assessment.\n"
                        f"Analyze the combination of API: '{target_api}' and Excipients: {selected_excipients} for a '{dosage_form}' configuration.\n\n"
                        f"Generate your output as a single valid JSON object containing exactly these keys:\n"
                        f"1. 'drug_profile': {{ 'chemical_class': '...', 'molecular_weight': '...', 'key_functional_groups': ['...'] }}\n"
                        f"2. 'recommended_risk': 'High' or 'Medium' or 'Low'\n"
                        f"3. 'identified_evidence': An array of objects, each with: [{{ 'drug_name': '...', 'excipient_name': '...', 'reaction_type': '...', 'details': '...' }}]\n"
                        f"4. 'rule_based_evidence': An array of objects detailing functional liabilities: "
                        f"[{{ 'drug_risk_group': '...', 'drug_group_formula': '...', 'excipient_risk_group': '...', 'reaction_type': '...', 'interaction_description': '...' }}]\n\n"
                        f"CRITICAL RULES: Do NOT output HTML code like <span> tags inside any text field. Return raw, clean text titles only."
                    )
                    
                    response = model.generate_content(
                        analysis_prompt,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    
                    # Store variables in session context upon validation success
                    st.session_state.compat_structured_results = json.loads(response.text)
                    st.session_state.active_screen_api = target_api
                    st.session_state.active_molecule_svg = molecule_svg
                    
                except Exception as err:
                    # Intercept API limit overloads and replace with clear user alerts
                    err_msg = str(err)
                    if "429" in err_msg or "quota" in err_msg.lower():
                        st.error("⚠️ **API Rate Limit Exceeded (Error 429)**: The workspace is experiencing high request volume. Please wait roughly 30–60 seconds before executing your next analytical run.")
                    else:
                        st.error(f"Inference Engine Failed: {err_msg}")

        # Render layout sections if session cache memory is populated
        if "compat_structured_results" in st.session_state and st.session_state.get("compat_structured_results"):
            data = st.session_state.compat_structured_results
            svg_data = st.session_state.get("active_molecule_svg", None)
            
            tab_info, tab_evidence, tab_rules = st.tabs([
                "📄 Formulation Information", 
                "🔗 Identified Evidence", 
                "📋 Rule-Based Evidence"
            ])
            
            # --- TAB 1: FORMULATION INFORMATION ---
            with tab_info:
                st.markdown("#### 💊 Target Profiling Components")
                prof_col1, prof_col2 = st.columns([4, 3])
                
                with prof_col1:
                    with st.container(border=True):
                        st.markdown("**Drug Profile Summary**")
                        dp = data.get("drug_profile", {})
                        
                        text_side, img_side = st.columns([3, 2])
                        with text_side:
                            st.markdown(f"**Name:** `{st.session_state.active_screen_api.upper()}`")
                            st.markdown(f"**Species/Class:**\n{dp.get('chemical_class', 'N/A')}")
                            st.markdown(f"**Molecular Weight:**\n{dp.get('molecular_weight', 'N/A')}")
                        
                        with img_side:
                            if svg_data:
                                st.markdown(f'<div style="text-align:center; background-color:white; padding:5px; border-radius:4px;">{svg_data}</div>', unsafe_allow_html=True)
                            else:
                                st.caption("⚠️ Structure match pending next successful API tracking window.")
                                
                        st.markdown(f"**Detected Groups:** {', '.join(dp.get('key_functional_groups', []))}")
                
                with prof_col2:
                    with st.container(border=True):
                        st.markdown("**Selected Blend Profile**")
                        st.markdown(f"**Dosage Form Layout:** {dosage_form}")
                        st.markdown("**Excipient Roster:**")
                        for ex in selected_excipients:
                            st.markdown(f"- <span style='font-size:0.85rem;'>{ex}</span>", unsafe_allow_html=True)
                
                st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
                
                risk_level = data.get("recommended_risk", "Low")
                if risk_level == "High":
                    badge_style = "background-color: #fef2f2; border: 1px solid #fecaca; color: #dc2626;"
                elif risk_level == "Medium":
                    badge_style = "background-color: #fffbeb; border: 1px solid #fef3c7; color: #d97706;"
                else:
                    badge_style = "background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #16a34a;"
                    
                st.markdown(
                    f"""
                    <div style="padding: 1rem; border-radius: 8px; {badge_style} font-weight: 700; text-align: center; font-size: 1.1rem;">
                        ⚠️ OVERALL RECOMMENDED MATRIX RISK: {risk_level.upper()} RISK
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

            # --- TAB 2: IDENTIFIED EVIDENCE ---
            with tab_evidence:
                st.markdown("#### 🔗 Direct Binary Interaction Cross-References")
                evidence_list = data.get("identified_evidence", [])
                if evidence_list:
                    for ev in evidence_list:
                        with st.container(border=True):
                            ev_left, ev_right = st.columns([1, 2])
                            with ev_left:
                                st.markdown(f"🧪 **Excipient:** `{ev.get('excipient_name', 'N/A')}`")
                                st.markdown(f"💥 **Reaction:** <span style='color:#dc2626; font-weight:600;'>{ev.get('reaction_type', 'N/A')}</span>", unsafe_allow_html=True)
                            with ev_right:
                                st.markdown(f"📝 **Evidence Mapping & Details:**\n<span style='font-size:0.88rem; color:#334155;'>{ev.get('details', 'N/A')}</span>", unsafe_allow_html=True)
                else:
                    st.info("No explicit binary literature exceptions matched against active criteria records.")

            # --- TAB 3: RULE-BASED EVIDENCE ---
            with tab_rules:
                st.markdown("#### 📋 Structural Group Mechanistic Rule Checks")
                rules_list = data.get("rule_based_evidence", [])
                for rule in rules_list:
                    with st.container(border=True):
                        r_col1, r_col2 = st.columns([1, 2])
                        with r_col1:
                            st.markdown(f"🧬 **Drug Group:** `{rule.get('drug_risk_group', 'N/A')}`")
                            st.markdown(f"🧪 **Formula:** `{rule.get('drug_group_formula', 'N/A')}`")
                            st.markdown(f"🧱 **Excipient Variable:** `{rule.get('excipient_risk_group', 'N/A')}`")
                        with r_col2:
                            st.markdown(f"💥 **Reaction Type:** <span style='color:#b91c1c; font-weight:600; background-color:#fef2f2; padding:4px 8px; border-radius:4px;'>{rule.get('reaction_type', 'N/A')}</span>", unsafe_allow_html=True)
                            st.markdown(f"<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
                            st.markdown(f"📝 **Interaction Description:**\n<span style='font-size:0.88rem; color:#334155; line-height:1.5;'>{rule.get('interaction_description', 'N/A')}</span>", unsafe_allow_html=True)
        else:
            if not trigger_prediction:
                st.markdown(
                    """
                    <div style="text-align: center; padding: 8rem 2rem; color: #64748b; border: 2px dashed #e2e8f0; border-radius: 8px;">
                        <strong>Awaiting Data Validation...</strong><br>
                        Execute an analytical query stream above to compile report arrays.
                    </div>
                    """, 
                    unsafe_allow_html=True
                )