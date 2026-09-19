import streamlit as st
import pandas as pd
from components.styles import load_css, render_header
from components.backend import check_backend, load_all_risks, load_sensor_data, short_diag

load_css()
check_backend()
render_header("Fleet Overview", "Detailed status of all aircraft")

try:
    all_risks = load_all_risks()
    sensor_df = load_sensor_data()
except Exception as e:
    st.error(f"⚠️ Failed to load backend data: {e}")
    st.stop()

st.markdown('<div class="section-header">Fleet Overview</div>', unsafe_allow_html=True)

sensor_lookup = sensor_df.set_index("asset_id")

table_rows = []
for r in all_risks:
    aid = r["asset_id"]
    cycles = int(sensor_lookup.loc[aid, "usage_cycles"]) if aid in sensor_lookup.index else 0
    table_rows.append({
        "Aircraft":         aid,
        "Status":           "READY ✓" if r["is_ready"] else "NON-READY ✗",
        "Risk Score":       r["risk_score"],
        "At-Risk Component": r["predicted_component_at_risk"].upper(),
        "Diagnosis":        short_diag(r["readiness_explanation"], 85),
        "Usage Cycles":     cycles,
    })

fleet_table_df = pd.DataFrame(table_rows)

st.dataframe(
    fleet_table_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Aircraft":         st.column_config.TextColumn("Aircraft", width="small"),
        "Status":           st.column_config.TextColumn("Status", width="small"),
        "Risk Score":       st.column_config.ProgressColumn(
                                "Risk Score", min_value=0, max_value=100,
                                format="%.1f", width="medium"),
        "At-Risk Component": st.column_config.TextColumn("At-Risk Component", width="small"),
        "Diagnosis":        st.column_config.TextColumn("Diagnosis", width="large"),
        "Usage Cycles":     st.column_config.NumberColumn("Usage Cycles", format="%d", width="small"),
    },
    height=450,
)
