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
    <div style="background: rgba(17, 24, 39, 0.5); border-radius: 12px; border: 1px solid var(--border-color); padding: 2rem;">
        
        <h4 style="color: #60a5fa; margin-bottom: 1rem;">1. Data Engineering Layer</h4>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem;">
            Raw telemetry data is collected from aircraft sensors. We synthesize critical behavioral metrics including <strong>7-day vibration trends</strong>, <strong>temperature volatility</strong>, and <strong>oil degradation rates</strong>. This historical behavior data forms the foundation for predictive analytics rather than relying on static thresholds.
        </p>

        <h4 style="color: #60a5fa; margin-bottom: 1rem;">2. Machine Learning Pipeline (Behavioral Anomaly)</h4>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem;">
            The core engine uses an unsupervised <strong>Isolation Forest</strong> algorithm (`scikit-learn`) to evaluate the high-dimensional feature space of each aircraft. It detects complex, non-linear anomalies in asset behavior and translates them into a normalized <strong>Cancellation Probability (0-100%)</strong>.
        </p>
        
        <h4 style="color: #60a5fa; margin-bottom: 1rem;">3. Business Logic & Triage (Backend)</h4>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem;">
            The <code>readiness_classifier</code> and <code>failure_predictor</code> modules aggregate the ML probabilities with raw sensor states to determine the overall Risk Score and Primary Component at Risk. The <code>maintenance_planner</code> then applies a greedy algorithm to schedule urgent repairs based on dynamically configurable crew and spare part constraints.
        </p>

        <h4 style="color: #60a5fa; margin-bottom: 1rem;">4. MCP / IBM Bob Intelligence Layer</h4>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem;">
            The entire backend is exposed via a Model Context Protocol (MCP) server. This allows AI assistants (like IBM Bob) to query live fleet readiness, asset risks, and maintenance queues using JSON-RPC. This ensures zero hallucination—the chatbot answers are 100% grounded in live telemetry data.
        </p>

        <h4 style="color: #60a5fa; margin-bottom: 1rem;">5. Streamlit Presentation Layer</h4>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 0;">
            The frontend provides an executive dashboard, detailed asset investigation, and interactive resource planning. It seamlessly integrates the AI's cancellation predictions and chatbot interfaces into a modern, responsive web application.
        </p>

    </div>
    """
)

st.markdown("<br><hr style='border-color: #1e3a5f;'><br>", unsafe_allow_html=True)

col_back = st.columns([1, 4])[0]
with col_back:
    if st.button("← Back to Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")
