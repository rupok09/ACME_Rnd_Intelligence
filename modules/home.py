import streamlit as st
from utils.navigation import go_to

def show_home():
    # 1. READ INNER SYSTEM NAV CODES
    # Looks for a change in page status sent by our flat text items
    if "nav_redirect_bridge" in st.session_state and st.session_state.nav_redirect_bridge:
        destination = st.session_state.nav_redirect_bridge
        del st.session_state["nav_redirect_bridge"]
        go_to(destination)

    # --------------------------------------------------------------------------
    # 2. PREMIUM CSS OVERRIDE FOR TRUE HORIZONTAL LINK ALIGNMENT
    # --------------------------------------------------------------------------
    st.markdown(
        """
        <style>
        .navbar-horizontal-row {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 28px !important;
            width: 100% !important;
            padding: 8px 0px !important;
            margin-bottom: 2px !important;
        }
        
        .navbar-text-item {
            color: #64748b !important;
            font-size: 0.94rem !important;
            font-weight: 500 !important;
            text-decoration: none !important;
            border-bottom: 2px solid transparent !important;
            padding-bottom: 4px !important;
            white-space: nowrap !important;
            cursor: pointer !important;
            transition: color 0.15s ease-in-out;
        }
        
        .navbar-text-item:hover {
            color: #0f172a !important;
        }
        
        .navbar-text-item.active-current-tab {
            color: #3b82f6 !important;
            font-weight: 700 !important;
            border-bottom: 2px solid #3b82f6 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------------------------
    # 3. INTERACTIVE TEXT NAV LINER ROW (Guaranteed Single-Tab Routing)
    # --------------------------------------------------------------------------
    # Using parent frame state modification forces the current Streamlit app layer
    # to reload cleanly without opening duplicate tabs or breaking the back button.
    st.markdown(
        """
        <div class="navbar-horizontal-row">
            <span onclick="window.parent.postMessage({type: 'streamlit:set_component_value', value: 'Home'}, '*')" class="navbar-text-item active-current-tab">Home</span>
            <span onclick="window.parent.postMessage({type: 'streamlit:set_component_value', value: 'Literature Review'}, '*')" class="navbar-text-item">Literature Review</span>
            <span onclick="window.parent.postMessage({type: 'streamlit:set_component_value', value: 'API Characterization'}, '*')" class="navbar-text-item">API Characterization</span>
            <span onclick="window.parent.postMessage({type: 'streamlit:set_component_value', value: 'RLD Information'}, '*')" class="navbar-text-item">RLD Information</span>
            <span onclick="window.parent.postMessage({type: 'streamlit:set_component_value', value: 'Drug-Excipient Compatibility'}, '*')" class="navbar-text-item">Drug-Excipient Compatibility</span>
            <span onclick="window.parent.postMessage({type: 'streamlit:set_component_value', value: 'Pharmacokinetics'}, '*')" class="navbar-text-item">Pharmacokinetics</span>
            <span onclick="window.parent.postMessage({type: 'streamlit:set_component_value', value: 'DOE Optimization'}, '*')" class="navbar-text-item">DOE Optimization</span>
            <span onclick="window.parent.postMessage({type: 'streamlit:set_component_value', value: 'AI Assistant'}, '*')" class="navbar-text-item">AI Assistant</span>
        </div>
        <hr style="margin-top: 4px; margin-bottom: 25px; border: 0; border-top: 1px solid #e2e8f0;">
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------------------------
    # HERO BANNER CANVAS
    # --------------------------------------------------------------------------
    st.markdown(
        """
        <div class="home-hero" style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 3rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 2rem;">
            <div class="home-hero-title" style="color: #ffffff; font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem; line-height: 1.2;">
                Advancing Health<br>
                Through <span style="color: #38bdf8;">Research & Innovation</span>
            </div>
            <div class="home-hero-text" style="color: #94a3b8; font-size: 1.05rem; max-width: 800px; line-height: 1.6;">
                The ACME Laboratories Ltd. is committed to delivering high-quality pharmaceutical
                solutions through science, collaboration, innovation, and engineering excellence.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ================= ROW 1: MODULES 1, 2, 3 =================
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="home-card">
                <div class="home-icon green">📚</div>
                <h3>Literature Review</h3>
                <p>Upload downloaded PDFs, extract text, review literature, and summarize key findings.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Literature Review", use_container_width=True, key="home_btn_lit"):
            go_to("Literature Review")

    with col2:
        st.markdown(
            """
            <div class="home-card">
                <div class="home-icon blue">🧪</div>
                <h3>API Characterization</h3>
                <p>Search API physicochemical properties from trusted web sources.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open API Characterization", use_container_width=True, key="home_btn_api"):
            go_to("API Characterization")

    with col3:
        st.markdown(
            """
            <div class="home-card">
                <div class="home-icon purple">📋</div>
                <h3>RLD Information</h3>
                <p>Collect reference listed drug and regulatory information for development decisions.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open RLD Information", use_container_width=True, key="home_btn_rld"):
            go_to("RLD Information")

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # ================= ROW 2: MODULES 4, 5, 6 =================
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(
            """
            <div class="home-card">
                <div class="home-icon purple">🧩</div>
                <h3>Drug-Excipient Compatibility</h3>
                <p>Assess possible drug-excipient interactions and product stability risks.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Compatibility", use_container_width=True, key="home_btn_compat"):
            go_to("Drug-Excipient Compatibility")

    with col5:
        st.markdown(
            """
            <div class="home-card">
                <div class="home-icon green">🧬</div>
                <h3>Pharmacokinetics</h3>
                <p>Model systemic absorption vectors, half-life parameters, and clearance simulations.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Pharmacokinetics", use_container_width=True, key="home_btn_pk"):
            go_to("Pharmacokinetics")

    with col6:
        st.markdown(
            """
            <div class="home-card">
                <div class="home-icon blue">📊</div>
                <h3>DOE Optimization</h3>
                <p>Design experiments, analyze responses, rank trials, and identify the best formulation.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open DOE Optimization", use_container_width=True, key="home_btn_doe"):
            go_to("DOE Optimization")

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    # ================= ROW 3: POSITION 7 (AI ASSISTANT) =================
    st.markdown(
        """
        <style>
        .home-assistant-banner {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            border: 1px solid #3b82f6;
            border-radius: 12px;
            padding: 1.5rem 2rem;
            margin-bottom: 1rem;
        }
        .assistant-title-row {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #f8fafc;
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .assistant-desc-text {
            color: #94a3b8;
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 0.5rem;
        }
        </style>
        <div class="home-assistant-banner">
            <div class="assistant-title-row">🤖 AI Assistant Workspace</div>
            <div class="assistant-desc-text">
                Initialize conversational cross-module intelligence pipelines powered by Google Gemini. 
                Cross-reference physicochemical properties against active patent literature data arrays instantly.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_space, col_ai_btn = st.columns([3, 1])
    with col_ai_btn:
        if st.button("Launch AI Assistant Portal", use_container_width=True, type="primary", key="home_btn_ai"):
            go_to("AI Assistant")

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="bottom-strip">
            <div><b>Quality</b><br>Our Commitment</div>
            <div><b>Innovation</b><br>Driven by Science</div>
            <div><b>Collaboration</b><br>Stronger Together</div>
            <div><b>Excellence</b><br>In Everything We Do</div>
        </div>
        """,
        unsafe_allow_html=True
    )