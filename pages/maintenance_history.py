import streamlit as st
import pandas as pd
from components.styles import load_css, render_header
from components.backend import check_backend, load_all_risks, load_service_history

load_css()
check_backend()
render_header("Maintenance History", "Review past maintenance records")

try:
    all_risks = load_all_risks()
    service_df = load_service_history()
except Exception as e:
    st.error(f"⚠️ Failed to load backend data: {e}")
    st.stop()

st.markdown('<div class="section-header">Maintenance History</div>', unsafe_allow_html=True)

asset_ids_by_risk = [r["asset_id"] for r in all_risks]
selected_id = st.selectbox(
    "Select Aircraft for History Log",
    options=asset_ids_by_risk,
    help="Assets ordered by risk score (highest first)",
)

asset_service = service_df[service_df["asset_id"] == selected_id].copy()

if asset_service.empty:
    st.info("No service history records found for this asset.")
else:
    disp_service = asset_service[["date", "component", "issue_found", "action_taken"]].copy()
    disp_service["date"] = disp_service["date"].dt.strftime("%Y-%m-%d")
    disp_service.columns = ["Date", "Component", "Issue Found", "Action Taken"]
    st.dataframe(disp_service, hide_index=True, use_container_width=True)
