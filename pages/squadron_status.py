import streamlit as st
from components.styles import load_css, render_header
from components.backend import check_backend, load_fleet_readiness, load_all_risks, load_sensor_data, load_service_history

load_css()
check_backend()
render_header("Squadron Status", "High-level fleet readiness metrics")

try:
    fleet_data = load_fleet_readiness()
    fleet_metrics = fleet_data["fleet_metrics"]
    all_risks = load_all_risks()
except Exception as e:
    st.error(f"⚠️ Failed to load backend data: {e}")
    st.stop()

critical_count = sum(1 for r in all_risks if r["risk_score"] >= 70)

st.markdown('<div class="section-header">Squadron Status</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Aircraft",   fleet_metrics["total_assets"])
k2.metric("Mission Ready",    fleet_metrics["mission_ready_count"],
          delta=f"+{fleet_metrics['mission_ready_count']} ready")
k3.metric("Non-Ready / Grounded", fleet_metrics["non_ready_count"],
          delta=f"-{fleet_metrics['non_ready_count']} grounded", delta_color="inverse")
k4.metric("Readiness Rate",   f"{fleet_metrics['readiness_rate_pct']}%")
k5.metric("Critical Risk (≥70)", critical_count,
          delta="action required" if critical_count > 0 else "none",
          delta_color="inverse" if critical_count > 0 else "normal")
