import streamlit as st


def load_css():
    st.markdown(
        """
        <style>

        /* ================= GLOBAL ================= */
        .stApp {
            background: #ffffff;
        }

        /* ================= SIDEBAR ================= */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #071b3a 0%, #020b1d 100%) !important;
            width: 295px !important;
        }

        section[data-testid="stSidebar"] * {
            color: white !important;
        }

        .sidebar-header {
            padding: 12px 4px 20px 4px;
            border-bottom: 1px solid rgba(255,255,255,0.12);
            margin-bottom: 18px;
        }

        .sidebar-logo {
            font-size: 25px;
            font-weight: 900;
            line-height: 1.15;
            color: #ffffff;
        }

        .sidebar-subtitle {
            font-size: 13px;
            color: #b9c6d2 !important;
            margin-top: 8px;
        }

        .sidebar-version {
            display: inline-block;
            margin-top: 12px;
            padding: 4px 10px;
            border-radius: 20px;
            background: rgba(0, 163, 255, 0.16);
            color: #8fd8ff !important;
            font-size: 12px;
            font-weight: 700;
        }

        .sidebar-card {
            margin-top: 24px;
            padding: 18px;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(255,255,255,0.055);
            font-size: 14px;
            line-height: 1.6;
        }

        .sidebar-user-card {
            margin-top: 16px;
            padding: 16px;
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(0,93,170,0.25), rgba(255,255,255,0.055));
            border: 1px solid rgba(255,255,255,0.10);
        }

        .user-label {
            font-size: 12px;
            color: #b9c6d2 !important;
        }

        .user-name {
            margin-top: 5px;
            font-size: 18px;
            font-weight: 900;
            color: #ffffff;
        }

        .user-role {
            margin-top: 4px;
            font-size: 13px;
            color: #b9c6d2 !important;
        }

        /* ================= BUTTONS ================= */
        div.stButton > button {
            background: linear-gradient(90deg, #005daa, #0077cc);
            color: white !important;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: 700;
            font-size: 15px;
            box-shadow: 0 8px 20px rgba(0,93,170,0.18);
        }

        div.stButton > button:hover {
            background: linear-gradient(90deg, #004b93, #005daa);
            color: white !important;
        }

        /* ================= HOME HEADER ================= */
        .home-brand-title {
            font-size: 34px;
            font-weight: 900;
            color: #08265c;
            margin-top: 18px;
        }

        .home-brand-subtitle {
            font-size: 15px;
            color: #005daa;
            font-style: italic;
            margin-top: 6px;
        }

        .home-top-menu {
            display: flex;
            gap: 32px;
            border-top: 1px solid #e5e7eb;
            padding-top: 18px;
            margin-top: 18px;
            margin-bottom: 28px;
            font-weight: 800;
            color: #0f172a;
            flex-wrap: wrap;
        }

        .active-menu {
            color: #005daa;
        }

        /* ================= HERO ================= */
        .home-hero {
            background: linear-gradient(90deg, #eaf6ff 0%, #d7ecff 55%, #b9dcff 100%);
            padding: 60px 45px;
            margin-bottom: 30px;
            border-radius: 0;
        }

        .home-hero-title {
            font-size: 46px;
            font-weight: 900;
            color: #071b3a;
            line-height: 1.15;
        }

        .home-hero-title span {
            color: #005daa;
        }

        .home-hero-text {
            font-size: 18px;
            color: #1f2937;
            max-width: 680px;
            line-height: 1.7;
            margin-top: 22px;
        }

        /* ================= HOME MODULE CARDS ================= */
        .home-card {
            background: white;
            padding: 32px 24px;
            border-radius: 18px;
            text-align: center;
            border: 1px solid #e5e7eb;
            box-shadow: 0 12px 30px rgba(15,23,42,0.08);
            min-height: 280px;
            margin-bottom: 14px;
            transition: all 0.25s ease;
        }

        .home-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 18px 40px rgba(15,23,42,0.12);
        }

        .home-card h3 {
            color: #08265c;
            font-weight: 900;
            font-size: 23px;
        }

        .home-card p {
            color: #374151;
            font-size: 15px;
            line-height: 1.6;
        }

        .home-icon {
            width: 85px;
            height: 85px;
            border-radius: 50%;
            color: white;
            font-size: 38px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 18px auto;
        }

        .home-icon.blue {
            background: #005daa;
        }

        .home-icon.green {
            background: #148a43;
        }

        .home-icon.purple {
            background: #5b3db8;
        }

        /* ================= API / COMMON PAGE CARDS ================= */
        .api-card {
            background: rgba(255,255,255,0.96);
            border: 1px solid #e5e7eb;
            border-radius: 20px;
            padding: 30px;
            min-height: 220px;
            box-shadow: 0 15px 40px rgba(15,23,42,0.08);
            margin-bottom: 18px;
        }

        .api-card-title {
            color: #005daa;
            font-size: 24px;
            font-weight: 850;
            margin-bottom: 14px;
        }

        .api-card-text {
            color: #0f172a;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 18px;
        }

        .upload-box {
            border: 2px dashed #005daa;
            border-radius: 16px;
            padding: 25px;
            text-align: center;
            background: #f2f8ff;
            margin-bottom: 15px;
        }

        /* ================= BOTTOM STRIP ================= */
        .bottom-strip {
            margin-top: 28px;
            background: linear-gradient(90deg, #004b93, #0067bd);
            color: white;
            padding: 25px;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            text-align: center;
            gap: 20px;
            font-size: 15px;
        }

        /* ================= FOOTER ================= */
        .footer {
            text-align: center;
            color: #64748b;
            margin-top: 35px;
            font-size: 13px;
        }

        /* ================= RESPONSIVE ================= */
        @media (max-width: 768px) {
            .home-brand-title {
                font-size: 24px;
            }

            .home-hero-title {
                font-size: 34px;
            }

            .home-top-menu {
                gap: 14px;
                font-size: 12px;
            }

            .bottom-strip {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        .result-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    margin-top: 16px;
}

.result-table th {
    background: #005daa;
    color: white;
    padding: 10px;
    text-align: left;
}

.result-table td {
    border: 1px solid #e5e7eb;
    padding: 10px;
    vertical-align: top;
}

.result-table tr:nth-child(even) {
    background: #f8fbff;
}

.result-table a {
    color: #005daa;
    font-weight: 700;
    text-decoration: none;
}

.result-table a:hover {
    text-decoration: underline;
}

        
.result-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    margin-top: 16px;
}

.result-table th {
    background: #005daa;
    color: white;
    padding: 10px;
    text-align: left;
}

.result-table td {
    border: 1px solid #e5e7eb;
    padding: 10px;
    vertical-align: top;
}

.result-table tr:nth-child(even) {
    background: #f8fbff;
}

.result-table a {
    color: #005daa;
    font-weight: 700;
    text-decoration: none;
}

.result-table a:hover {
    text-decoration: underline;
}

.result-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    margin-top: 16px;
}

.result-table th {
    background: #005daa;
    color: white;
    padding: 10px;
    text-align: left;
}

.result-table td {
    border: 1px solid #e5e7eb;
    padding: 10px;
    vertical-align: top;
}

.result-table tr:nth-child(even) {
    background: #f8fbff;
}

.result-table a {
    color: #005daa;
    font-weight: 700;
    text-decoration: none;
}

.result-table a:hover {
    text-decoration: underline;
}

.result-table img {
    max-width: 120px;
    height: auto;
}
        </style>
        """,
        unsafe_allow_html=True
    )