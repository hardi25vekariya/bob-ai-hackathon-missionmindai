import streamlit as st
import pandas as pd
from components.styles import load_css, render_header
from components.backend import (
    check_backend, 
    handle_get_fleet_readiness, 
    handle_get_asset_risk, 
    handle_get_maintenance_plan
)

load_css()
check_backend()
render_header("BOB COPILOT", "AI-powered mission intelligence")

st.markdown('<div class="section-header">Bob Copilot</div>', unsafe_allow_html=True)

st.markdown(
    '<p class="bob-header">BOB COPILOT</p>'
    '<p style="color:#94a3b8;font-size:0.85rem;margin-top:0.2rem;">'
    'IBM Bob answers these queries using live MCP tools — zero hallucination, 100% data-grounded</p>',
    unsafe_allow_html=True,
)

bob_left, bob_right = st.columns(2)

EXAMPLE_QUERIES = [
    ("Which aircraft are currently non-ready?",
     "get_fleet_readiness", "Fleet readiness overview with NON-READY flags"),
    ("Why is Tail-108 non-ready? Give me the full diagnostic.",
     "get_asset_risk", "Asset-level risk score + sensor breach breakdown"),
    ("Which aircraft has the highest failure risk right now?",
     "get_asset_risk", "Ranked risk list — top result is highest risk"),
    ("What should we repair first with 3 crews and 2 engine spares?",
     "get_maintenance_plan", "Greedy triage schedule under crew & parts constraints"),
    ("Which jets are queued because of spare-part shortages?",
     "get_maintenance_plan", "Maintenance schedule with bottleneck details"),
]

with bob_left:
    st.markdown("**Example Queries for IBM Bob**")
    for q, tool, _ in EXAMPLE_QUERIES:
        st.markdown(
            f'<div class="bob-card"><em>"{q}"</em></div>',
            unsafe_allow_html=True,
        )

with bob_right:
    st.markdown("**MCP Tool Routing**")
    mcp_rows = [{
        "Query Topic":    desc,
        "MCP Tool":       tool,
    } for _, tool, desc in EXAMPLE_QUERIES]
    st.dataframe(pd.DataFrame(mcp_rows), hide_index=True, use_container_width=True)

st.markdown(
    '<div style="background:#0f1f3d;border:1px solid #1e40af;border-radius:8px;padding:1rem;'
    'margin-top:0.8rem;font-size:0.83rem;color:#93c5fd;">'
    '<strong>Connect IBM Bob:</strong> Register the MCP server using the config in '
    '<code>docs/setup-guide.md</code>. IBM Bob will call '
    '<span class="mcp-tag">get_fleet_readiness</span>, '
    '<span class="mcp-tag">get_asset_risk</span>, and '
    '<span class="mcp-tag">get_maintenance_plan</span> '
    'directly — grounding every response in verified sensor telemetry and maintenance logs.'
    '</div>',
    unsafe_allow_html=True,
)

# ── Live MCP Tool Test ──
with st.expander("Live MCP Tool Test — Verify Backend Integration"):
    st.markdown(
        "<p style='color:#94a3b8;font-size:0.82rem;'>These buttons call the MCP handlers "
        "directly and display the raw JSON response — the same data IBM Bob receives.</p>",
        unsafe_allow_html=True,
    )
    t1, t2, t3 = st.columns(3)
    with t1:
        if st.button("Test get_fleet_readiness", use_container_width=True):
            try:
                st.json(handle_get_fleet_readiness())
            except Exception as e:
                st.error(str(e))
    with t2:
        if st.button("Test get_asset_risk (Tail-108)", use_container_width=True):
            try:
                st.json(handle_get_asset_risk(asset_id="Tail-108"))
            except Exception as e:
                st.error(str(e))
    with t3:
        if st.button("Test get_maintenance_plan", use_container_width=True):
            try:
                st.json(handle_get_maintenance_plan())
            except Exception as e:
                st.error(str(e))
