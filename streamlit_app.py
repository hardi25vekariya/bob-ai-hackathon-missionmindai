import streamlit as st
import os

# Initialize theme state if not exists
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Define pages
dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon="🏠", default=True)

# System Capabilities (Detail Pages)
squadron_status = st.Page("pages/squadron_status.py", title="Squadron Status", icon="✈️")
fleet_overview = st.Page("pages/fleet_overview.py", title="Fleet Overview", icon="📋")
critical_assets = st.Page("pages/critical_assets.py", title="Critical Assets", icon="⚠️")
asset_investigation = st.Page("pages/asset_investigation.py", title="Asset Investigation", icon="🔍")
maintenance_history = st.Page("pages/maintenance_history.py", title="Maintenance History", icon="🕒")
maintenance_triage = st.Page("pages/maintenance_triage.py", title="Maintenance Triage", icon="⚙️")
fleet_risk = st.Page("pages/fleet_risk_profile.py", title="Fleet Risk Profile", icon="📊")
bob_copilot = st.Page("pages/bob_copilot.py", title="BOB COPILOT", icon="🤖")

# Admin & About
about = st.Page("pages/about.py", title="About Platform", icon="ℹ️")
admin = st.Page("pages/admin_data.py", title="Data Management", icon="🗄️")

# Navigation setup
pg = st.navigation({
    "Home": [dashboard],
    "System Capabilities": [
        squadron_status,
        fleet_overview,
        critical_assets,
        asset_investigation,
        maintenance_history,
        maintenance_triage,
        fleet_risk,
        bob_copilot
    ],
    "Administration": [admin, about]
})

# Sidebar Controls
with st.sidebar:
    st.markdown("### ⚙️ Global Settings")
    st.info("Use the standard Streamlit menu (⋮) in the top right to switch between Light and Dark mode.")

# Run the selected page
pg.run()
