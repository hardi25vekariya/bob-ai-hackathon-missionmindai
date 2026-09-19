import streamlit as st
import os

# Define pages
# OVERVIEW
dashboard = st.Page("pages/dashboard.py", title="Fleet Dashboard", icon=":material/dashboard:", default=True)
squadron_status = st.Page("pages/squadron_status.py", title="Mission Readiness", icon=":material/flight:")

# ANALYTICS
fleet_risk = st.Page("pages/fleet_risk_profile.py", title="Asset Risk", icon=":material/analytics:")
asset_investigation = st.Page("pages/asset_investigation.py", title="Failure Analysis", icon=":material/search:")

# MAINTENANCE
maintenance_triage = st.Page("pages/maintenance_triage.py", title="Maintenance Planner", icon=":material/build:")

# INTEGRATION
bob_copilot = st.Page("pages/bob_copilot.py", title="IBM Bob / MCP", icon=":material/smart_toy:")

# ADMINISTRATION
admin = st.Page("pages/admin_data.py", title="Data Management", icon=":material/storage:")

# Extra detail pages we are keeping around for deep links but not putting in the main nav if not requested.
# The prompt says "Do not remove any existing functionality" but explicitly provided the navigation structure.
# I will tuck the remaining ones under an "OTHER VIEWS" or just inside ANALYTICS.
fleet_overview = st.Page("pages/fleet_overview.py", title="Fleet Overview", icon=":material/list_alt:")
critical_assets = st.Page("pages/critical_assets.py", title="Critical Assets", icon=":material/warning:")
maintenance_history = st.Page("pages/maintenance_history.py", title="Maintenance History", icon=":material/history:")
about = st.Page("pages/about.py", title="About Platform", icon=":material/info:")

# Navigation setup
pg = st.navigation({
    "OVERVIEW": [dashboard, squadron_status],
    "ANALYTICS": [fleet_risk, asset_investigation],
    "MAINTENANCE": [maintenance_triage],
    "INTEGRATION": [bob_copilot],
    "ADMINISTRATION": [admin],
    "EXTRA VIEWS (LEGACY)": [fleet_overview, critical_assets, maintenance_history, about]
})

# Sidebar Controls
with st.sidebar:
    st.markdown("### AeroGuard-Bob")
    st.markdown("<p style='font-size:0.85rem;color:#64748b;margin-top:-10px;'>Mission Readiness & Predictive Maintenance</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top:0; margin-bottom:1rem;'>", unsafe_allow_html=True)

# Run the selected page
pg.run()
