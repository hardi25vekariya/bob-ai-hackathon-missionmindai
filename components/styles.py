import streamlit as st

def load_css():
    st.html("""
    <style>
    /* ── Base ── */
    html, body, [data-testid="stAppViewContainer"] {
        /* Let Streamlit handle base background and text via theme */
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem 1.2rem;
    }
    [data-testid="stMetricLabel"] { 
        font-size: 0.78rem; 
        letter-spacing: 0.06em; 
        text-transform: uppercase; 
    }
    [data-testid="stMetricValue"] { 
        font-size: 1.9rem; 
        font-weight: 700; 
    }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* ── DataFrames ── */
    [data-testid="stDataFrame"] { 
        border: 1px solid var(--border-color); 
        border-radius: 6px; 
    }

    /* ── Forms & inputs ── */
    [data-testid="stForm"] {
        background: var(--secondary-background-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.2rem;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        border: 1px solid var(--border-color) !important;
    }

    /* ── Expanders ── */
    [data-testid="stExpander"] {
        background: var(--secondary-background-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }

    /* ── Dashboard Tiles ── */
    .dash-tile {
        background: var(--secondary-background-color);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        position: relative;
        transition: all 0.2s ease;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .dash-tile:hover {
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 8px 15px -3px rgba(0,0,0,0.1);
    }
    .dash-icon {
        font-size: 2.2rem;
        margin-bottom: 0.8rem;
    }
    .dash-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .dash-desc {
        font-size: 0.8rem;
        line-height: 1.3;
        opacity: 0.8;
    }
    .tile-btn-container .stButton > button {
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        width: 100%;
        height: 100%;
        position: absolute;
        top: 0;
        left: 0;
        z-index: 10;
        cursor: pointer;
    }
    .tile-btn-container .stButton > button:hover {
        background: transparent !important;
        border: none !important;
    }

    /* ── Section headers ── */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--primary-color);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
        margin-top: 1.5rem;
    }

    /* ── Asset cards ── */
    .asset-card {
        background: var(--secondary-background-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        height: 100%;
    }
    .asset-card.critical { border-color: #dc2626; }
    .asset-id { font-size: 1.3rem; font-weight: 800; color: var(--primary-color); font-family: monospace; }
    .risk-score-num { font-size: 2rem; font-weight: 900; }
    .risk-critical { color: #ef4444; }
    .risk-warning  { color: #f59e0b; }
    .risk-good     { color: #10b981; }
    .comp-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.7; }
    .comp-value { font-size: 0.9rem; font-weight: 700; color: #fbbf24; }
    .diag-text  { font-size: 0.78rem; margin-top: 0.4rem; line-height: 1.5; opacity: 0.8; }

    /* ── Bob panel ── */
    .bob-card {
        background: var(--secondary-background-color);
        border: 1px solid var(--primary-color);
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.6rem;
        font-size: 0.85rem;
    }
    .bob-header {
        font-size: 1.4rem;
        font-weight: 800;
        color: var(--primary-color);
        letter-spacing: 0.04em;
    }
    .mcp-tag {
        background: var(--background-color);
        color: var(--primary-color);
        border-radius: 4px;
        padding: 2px 7px;
        border: 1px solid var(--border-color);
        font-size: 0.72rem;
        font-family: monospace;
        font-weight: 700;
    }

    /* ── Status badges ── */
    .badge-ready    { background:rgba(16, 185, 129, 0.15); color:#10b981; border:1px solid #10b981; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; letter-spacing:0.06em; }
    .badge-nonready { background:rgba(239, 68, 68, 0.15); color:#ef4444; border:1px solid #ef4444; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; letter-spacing:0.06em; }
    .badge-sched    { background:rgba(16, 185, 129, 0.15); color:#10b981; border:1px solid #10b981; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; letter-spacing:0.06em; }
    .badge-queued   { background:rgba(245, 158, 11, 0.15); color:#f59e0b; border:1px solid #f59e0b; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; letter-spacing:0.06em; }
    .badge-critical { background:rgba(220, 38, 38, 0.15); color:#dc2626; border:1px solid #dc2626; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; letter-spacing:0.06em; }

    </style>
    """)

def render_header(title, subtitle):
    col_title, col_status = st.columns([4, 1])
    with col_title:
        st.markdown(
            f'<h1 style="margin-bottom:0;font-size:2.2rem;letter-spacing:0.04em;font-weight:800;">{title}</h1>',
            unsafe_allow_html=True,
        )
        if subtitle:
            st.markdown(
                f'<p style="margin-top:0.2rem;margin-bottom:1rem;font-size:1.1rem;opacity:0.8;">{subtitle}</p>',
                unsafe_allow_html=True,
            )
    with col_status:
        st.markdown(
            '''
            <div style="display: flex; justify-content: flex-end; align-items: center; height: 100%; padding-top: 1rem;">
                <div style="display: flex; align-items: center; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 6px 12px; border-radius: 20px;">
                    <div style="width: 8px; height: 8px; background-color: #10b981; border-radius: 50%; margin-right: 8px; box-shadow: 0 0 8px #10b981;"></div>
                    <span style="color: #10b981; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em;">SYSTEM ONLINE</span>
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
    st.markdown(f"<hr style='margin:1rem 0 2rem 0; border-color: var(--border-color);'>", unsafe_allow_html=True)
