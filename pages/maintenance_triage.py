import streamlit as st
import pandas as pd
from components.styles import load_css, render_header
from components.backend import (
    check_backend, 
    handle_get_maintenance_plan, 
    DEFAULT_AVAILABLE_CREWS, 
    DEFAULT_PARTS_INVENTORY
)

load_css()
check_backend()
render_header("Maintenance Triage", "Resource Planning & Optimization")

st.markdown('<div class="section-header">Maintenance Triage & Resource Planning</div>', unsafe_allow_html=True)

COMPONENTS = ["engine", "hydraulics", "fuel_system", "landing_gear", "avionics"]

with st.form("maintenance_form"):
    st.markdown("**Configure Available Resources**")
    fc1, fc2 = st.columns([1, 3])
    with fc1:
        crews = st.number_input(
            "Maintenance Crews", min_value=0, max_value=20,
            value=DEFAULT_AVAILABLE_CREWS, step=1,
            help="Number of available maintenance technician teams"
        )
    with fc2:
        st.markdown("Spare Parts Inventory per Component")
        p_cols = st.columns(len(COMPONENTS))
        parts = {}
        for col, comp in zip(p_cols, COMPONENTS):
            parts[comp] = col.number_input(
                comp.replace("_", " ").title(),
                min_value=0, max_value=20,
                value=DEFAULT_PARTS_INVENTORY.get(comp, 2),
                step=1,
            )

    submitted = st.form_submit_button("⚙️ Generate Maintenance Plan", use_container_width=True)

if submitted:
    if crews < 0:
        st.error("Crew count cannot be negative.")
    else:
        try:
            plan_result = handle_get_maintenance_plan(
                available_crews=int(crews),
                available_parts_per_component=parts,
            )
            if plan_result.get("status") != "success":
                st.error(f"Maintenance planner error: {plan_result.get('message', 'Unknown error')}")
            else:
                summary = plan_result["executive_summary"]
                metrics = plan_result["metrics"]
                schedule = plan_result["maintenance_schedule"]

                st.info(f"📋 **Executive Summary:** {summary}")

                m1, m2, m3 = st.columns(3)
                m1.metric("Requiring Maintenance", metrics["total_requiring_maintenance"])
                m2.metric("Scheduled",  metrics["scheduled_count"])
                m3.metric("Queued",     metrics["queued_count"])

                sched_items  = [r for r in schedule if r["status"] == "scheduled"]
                queued_items = [r for r in schedule if r["status"] == "queued"]

                if sched_items:
                    st.markdown(
                        "<p style='color:#22c55e;font-weight:700;font-size:0.9rem;"
                        "letter-spacing:0.06em;margin-top:1rem;'>✅ SCHEDULED — WORK ORDERS ASSIGNED</p>",
                        unsafe_allow_html=True)
                    sched_df = pd.DataFrame([{
                        "Priority": r["priority_rank"],
                        "Aircraft":  r["asset_id"],
                        "Component": r["predicted_component_at_risk"].upper(),
                        "Risk Score": r["risk_score"],
                        "Action":    r["reason"][:120] + "…" if len(r["reason"]) > 120 else r["reason"],
                    } for r in sched_items])
                    st.dataframe(sched_df, hide_index=True, use_container_width=True,
                                 column_config={
                                     "Risk Score": st.column_config.ProgressColumn(
                                         "Risk Score", min_value=0, max_value=100, format="%.1f"),
                                 })

                if queued_items:
                    st.markdown(
                        "<p style='color:#f59e0b;font-weight:700;font-size:0.9rem;"
                        "letter-spacing:0.06em;margin-top:1rem;'>⏳ QUEUED — AWAITING CREW / PARTS</p>",
                        unsafe_allow_html=True)
                    queued_df = pd.DataFrame([{
                        "Priority": r["priority_rank"],
                        "Aircraft":  r["asset_id"],
                        "Component": r["predicted_component_at_risk"].upper(),
                        "Risk Score": r["risk_score"],
                        "Bottleneck": r["reason"][:120] + "…" if len(r["reason"]) > 120 else r["reason"],
                    } for r in queued_items])
                    st.dataframe(queued_df, hide_index=True, use_container_width=True,
                                 column_config={
                                     "Risk Score": st.column_config.ProgressColumn(
                                         "Risk Score", min_value=0, max_value=100, format="%.1f"),
                                 })
        except Exception as e:
            st.error(f"⚠️ Maintenance plan generation failed: {e}")
