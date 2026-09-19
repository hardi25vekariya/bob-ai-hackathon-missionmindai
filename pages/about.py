import streamlit as st
import sys
import os

# Add root to sys.path if not present so we can import components
_PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.abspath(os.path.join(_PAGES_DIR, ".."))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from components.styles import load_css, render_header

# Load global CSS
load_css()

# Header
render_header("MISSIONMIND AI", "System Architecture & Platform Info")

st.markdown(
    """
    <div class="module-card" style="margin-bottom: 2rem;">
        <h3 style="color: #f8fafc; margin-bottom: 1rem;">Platform Overview</h3>
        <p style="color: #94a3b8; line-height: 1.6;">
            MissionMind AI is an AI-powered aerospace mission intelligence platform.
            The platform is designed using a modular architecture so future AI capabilities can be added independently, 
            allowing for scalable intelligence integration without disrupting existing core workflows.
        </p>
    </div>
    """, unsafe_allow_html=True
)

st.markdown('<div class="section-header">INTELLIGENCE WORKFLOW</div>', unsafe_allow_html=True)

st.html(
    """
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; background: rgba(17, 24, 39, 0.5); border-radius: 12px; border: 1px solid var(--border-color);">
        
        <div style="background: var(--primary-color); color: #ffffff; padding: 10px 20px; border-radius: 8px; font-weight: bold; min-width: 200px; text-align: center;">
            DATA COLLECTION
        </div>
        
        <div style="color: var(--primary-color); font-size: 1.5rem; margin: 10px 0;">↓</div>
        
        <div style="background: var(--primary-color); color: #ffffff; padding: 10px 20px; border-radius: 8px; font-weight: bold; min-width: 200px; text-align: center;">
            AI ANALYSIS
        </div>
        
        <div style="color: var(--primary-color); font-size: 1.5rem; margin: 10px 0;">↓</div>
        
        <div style="background: var(--primary-color); color: #ffffff; padding: 10px 20px; border-radius: 8px; font-weight: bold; min-width: 200px; text-align: center;">
            PREDICTION
        </div>
        
        <div style="color: var(--primary-color); font-size: 1.5rem; margin: 10px 0;">↓</div>
        
        <div style="background: var(--primary-color); color: #ffffff; padding: 10px 20px; border-radius: 8px; font-weight: bold; min-width: 200px; text-align: center;">
            DECISION SUPPORT
        </div>
        
        <div style="color: var(--primary-color); font-size: 1.5rem; margin: 10px 0;">↓</div>
        
        <div style="background: #10b981; color: #ffffff; padding: 10px 20px; border-radius: 8px; font-weight: bold; min-width: 200px; text-align: center;">
            MISSION READINESS
        </div>
        
    </div>
    """
)

st.markdown("<br><hr style='border-color: #1e3a5f;'><br>", unsafe_allow_html=True)

col_back = st.columns([1, 4])[0]
with col_back:
    if st.button("← Back to Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")
