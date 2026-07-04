import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def calculate_pk_profiles(model_type, dosing_route, dose, volume_dist, k_elim, k_abs, infusion_time, total_time):
    """
    Mathematical PK engine mapping analytics for concentration-time distributions.
    """
    t = np.linspace(0, total_time, 400)
    concentrations = np.zeros_like(t)
    
    if model_type == "1-Compartment Model":
        if dosing_route == "IV Bolus":
            c0 = dose / volume_dist
            concentrations = c0 * np.exp(-k_elim * t)
            
        elif dosing_route == "IV Infusion":
            infusion_rate = dose / infusion_time
            cl = volume_dist * k_elim
            for i, time_point in enumerate(t):
                if time_point <= infusion_time:
                    concentrations[i] = (infusion_rate / cl) * (1 - np.exp(-k_elim * time_point))
                else:
                    c_at_end = (infusion_rate / cl) * (1 - np.exp(-k_elim * infusion_time))
                    concentrations[i] = c_at_end * np.exp(-k_elim * (time_point - infusion_time))
                    
        elif dosing_route == "Oral Absorption":
            if k_abs == k_elim:
                k_abs += 0.001
            scalar = (dose * k_abs) / (volume_dist * (k_abs - k_elim))
            concentrations = scalar * (np.exp(-k_elim * t) - np.exp(-k_abs * t))

    elif model_type == "2-Compartment Model":
        alpha = k_elim * 2.5
        beta = k_elim * 0.4
        if dosing_route == "Oral Absorption":
            ka_factor = k_abs if k_abs > 0 else 1.2
            scalar_a = (dose / volume_dist) * (ka_factor / (ka_factor - beta))
            concentrations = scalar_a * (np.exp(-beta * t) - np.exp(-alpha * t))
        else:
            amp_a = (dose / volume_dist) * 0.6
            amp_b = (dose / volume_dist) * 0.4
            concentrations = (amp_a * np.exp(-alpha * t)) + (amp_b * np.exp(-beta * t))

    return t, concentrations

def show_pharmacokinetics():
    st.markdown(
        """
        <div style="background-color: #0f172a; padding: 1.5rem 2rem; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 2rem;">
            <h2 style="color: #ffffff; margin: 0; font-size: 1.8rem;">🧬 Pharmacokinetics Simulation Matrix</h2>
            <p style="color: #94a3b8; margin: 0.5rem 0 0 0; font-size: 0.92rem;">
                Model systemic plasma profiles, validate formulation absorption vectors, and extract core kinetic exposure parameters.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    ctrl_col, plot_col = st.columns([1.1, 2.0], gap="large")

    with ctrl_col:
        st.subheader("⚙️ Simulation Settings")
        model_type = st.selectbox("Compartmental Configuration", ["1-Compartment Model", "2-Compartment Model"])
        dosing_route = st.radio("Dosing Administration Route", ["IV Bolus", "IV Infusion", "Oral Absorption"])
        
        st.markdown("---")
        st.subheader("🧪 Active Compound Variables")
        
        dose = st.number_input("Administered Dose (mg)", min_value=1.0, value=250.0, step=10.0)
        volume_dist = st.number_input("Volume of Distribution (Vd, L)", min_value=0.1, value=25.0, step=1.0)
        k_elim = st.number_input("Elimination Rate Constant (ke, hr⁻¹)", min_value=0.01, value=0.15, step=0.01)
        
        k_abs = 1.0
        infusion_time = 1.0
        
        if dosing_route == "Oral Absorption":
            k_abs = st.number_input("Absorption Rate Constant (ka, hr⁻¹)", min_value=0.05, value=0.80, step=0.05)
        elif dosing_route == "IV Infusion":
            infusion_time = st.number_input("Infusion Duration (Tinf, hr)", min_value=0.1, value=2.0, step=0.5)

        total_time = st.slider("Simulation Tracking Horizon (Hours)", min_value=12, max_value=72, value=24, step=4)

    t, conc = calculate_pk_profiles(model_type, dosing_route, dose, volume_dist, k_elim, k_abs, infusion_time, total_time)

    c_max = float(np.max(conc))
    t_max = float(t[np.argmax(conc)])
    
    # PATCHED: Safe version-agnostic check for trapezoidal area integration (Handles NumPy 2.0+)
    if hasattr(np, "trapezoid"):
        auc = float(np.trapezoid(conc, t))
    else:
        auc = float(np.trapz(conc, t))
        
    half_life = float(np.log(2) / k_elim)
    clearance = float(volume_dist * k_elim)

    with plot_col:
        st.subheader("📈 Plasma Concentration Time Profile")
        
        fig, ax = plt.subplots(figsize=(7, 4.2))
        ax.plot(t, conc, color="#3b82f6", linewidth=2.5, label="Plasma Concentration")
        ax.fill_between(t, conc, color="#3b82f6", alpha=0.1)
        
        ax.axvline(t_max, color="#ef4444", linestyle="--", alpha=0.5)
        ax.axhline(c_max, color="#ef4444", linestyle="--", alpha=0.5)
        
        ax.set_xlabel("Time (Hours)", fontsize=10, fontweight="bold")
        ax.set_ylabel("Concentration (mg/L)", fontsize=10, fontweight="bold")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_xlim(0, total_time)
        ax.set_ylim(0, max(conc) * 1.15 if max(conc) > 0 else 10)
        
        st.pyplot(fig)
        
        st.markdown("### 📊 Calculated Exposure Parameters")
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric(label="Peak Concentration (Cmax)", value=f"{c_max:.2f} mg/L")
            st.metric(label="Total Clearance (Cl)", value=f"{clearance:.2f} L/hr")
        with m_col2:
            st.metric(label="Time to Peak (Tmax)", value=f"{t_max:.2f} hr")
            st.metric(label="Half-Life (t1/2)", value=f"{half_life:.2f} hr")
        with m_col3:
            st.metric(label="Exposure Area (AUC 0-t)", value=f"{auc:.2f} mg*hr/L")
            
        export_df = pd.DataFrame({"Time (Hours)": t, "Concentration (mg/L)": conc})
        csv_buffer = export_df.to_csv(index=False).encode('utf-8')
        
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Export Computational Simulation CSV Dataset",
            data=csv_buffer,
            file_name="ACME_PK_Simulation.csv",
            mime="text/csv",
            use_container_width=True
        )