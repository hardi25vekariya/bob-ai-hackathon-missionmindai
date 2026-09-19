import streamlit as st
from components.styles import load_css, render_header

load_css()

# Dashboard UI helper
def create_tile(title, description, icon, target_page):
    st.markdown(f"""
        <div class="dash-tile">
            <div class="dash-icon">{icon}</div>
            <div class="dash-title">{title}</div>
            <div class="dash-desc">{description}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # We overlay a transparent button to make the entire tile clickable
    st.markdown('<div class="tile-btn-container">', unsafe_allow_html=True)
    if st.button("GO", key=f"btn_{title}", help=f"Open {title}", use_container_width=True):
        st.switch_page(target_page)
    st.markdown('</div>', unsafe_allow_html=True)


render_header("MISSIONMIND AI", "Professional Aerospace Mission Intelligence Platform")

st.markdown("<br>", unsafe_allow_html=True)

# ROW 1
r1c1, r1c2, r1c3 = st.columns(3)
with r1c1:
    create_tile("Squadron Status", "High-level fleet readiness metrics", "✈️", "pages/squadron_status.py")
with r1c2:
    create_tile("Fleet Overview", "Detailed status of all aircraft", "📋", "pages/fleet_overview.py")
with r1c3:
    create_tile("Critical Assets", "Immediate Attention Required", "⚠️", "pages/critical_assets.py")

st.markdown("<br>", unsafe_allow_html=True)

# ROW 2
r2c1, r2c2, r2c3 = st.columns(3)
with r2c1:
    create_tile("Asset Investigation", "Deep inspection of individual aircraft", "🔍", "pages/asset_investigation.py")
with r2c2:
    create_tile("Maintenance History", "Review past maintenance records", "🕒", "pages/maintenance_history.py")
with r2c3:
    create_tile("Maintenance Triage & Resource Planning", "Optimize resources and plan maintenance", "⚙️", "pages/maintenance_triage.py")

st.markdown("<br>", unsafe_allow_html=True)

# ROW 3
r3c1, r3c2 = st.columns(2)
with r3c1:
    create_tile("Fleet Risk Profile", "Subsystem failure risk analysis", "📊", "pages/fleet_risk_profile.py")
with r3c2:
    create_tile("🤖 BOB COPILOT", "AI-powered mission intelligence", "🤖", "pages/bob_copilot.py")

