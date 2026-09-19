import streamlit as st

def load_css():
    st.html("""
    <style>
    /* ── AeroGuard-Bob Enterprise Light Theme ── */
    
    :root {
        --primary-blue: #2563eb;
        --bg-light: #f8fafc;
        --card-bg: #ffffff;
        --text-main: #0f172a;
        --text-muted: #64748b;
        --border-color: #e2e8f0;
        
        --status-ready: #10b981;
        --status-ready-bg: #d1fae5;
        --status-warning: #f59e0b;
        --status-warning-bg: #fef3c7;
        --status-critical: #ef4444;
        --status-critical-bg: #fee2e2;
    }

    /* Override Streamlit base */
    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-light) !important;
        color: var(--text-main) !important;
        font-family: "Inter", "Segoe UI", Roboto, sans-serif !important;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid var(--border-color);
    }
    
    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricLabel"] { 
        font-size: 0.8rem; 
        color: var(--text-muted);
        letter-spacing: 0.05em; 
        text-transform: uppercase; 
        font-weight: 600;
    }
    [data-testid="stMetricValue"] { 
        font-size: 2.2rem; 
        font-weight: 800; 
        color: var(--text-main);
    }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* ── DataFrames ── */
    [data-testid="stDataFrame"] { 
        border: 1px solid var(--border-color); 
        border-radius: 8px; 
        background: var(--card-bg);
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }

    /* ── Forms & inputs ── */
    [data-testid="stForm"] {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* ── Section headers ── */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-main);
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border-color);
    }
    .section-subheader {
        font-size: 0.9rem;
        color: var(--text-muted);
        margin-top: -0.8rem;
        margin-bottom: 1.5rem;
    }

    /* ── Asset cards ── */
    .asset-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.2rem;
        height: 100%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        display: flex;
        flex-direction: column;
    }
    .asset-card.critical { 
        border-top: 4px solid var(--status-critical);
    }
    .asset-id { 
        font-size: 1.1rem; 
        font-weight: 700; 
        color: var(--text-main); 
    }
    .risk-score-num { 
        font-size: 1.8rem; 
        font-weight: 800; 
        margin-top: 0.5rem;
    }
    .risk-critical { color: var(--status-critical); }
    .risk-warning  { color: var(--status-warning); }
    .risk-good     { color: var(--status-ready); }
    
    .comp-label { 
        font-size: 0.75rem; 
        text-transform: uppercase; 
        color: var(--text-muted);
        margin-top: 0.5rem;
    }
    .comp-value { 
        font-size: 0.95rem; 
        font-weight: 600; 
        color: var(--text-main); 
    }

    /* ── Bob panel ── */
    .bob-card {
        background: var(--bg-light);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .bob-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-main);
        margin-bottom: 0.2rem;
    }
    .bob-desc {
        font-size: 0.85rem;
        color: var(--text-muted);
    }

    /* ── Status badges ── */
    .badge-ready    { background: var(--status-ready-bg); color: var(--status-ready); padding: 4px 10px; border-radius: 16px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em; display: inline-block;}
    .badge-nonready { background: var(--status-critical-bg); color: var(--status-critical); padding: 4px 10px; border-radius: 16px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em; display: inline-block;}
    .badge-warning  { background: var(--status-warning-bg); color: var(--status-warning); padding: 4px 10px; border-radius: 16px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em; display: inline-block;}

    /* Utility */
    .text-muted { color: var(--text-muted); font-size: 0.9rem; }
    .card-container {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        margin-bottom: 1.5rem;
    }
    </style>
    """)

def render_header(title, subtitle):
    col_title, col_status = st.columns([3, 1])
    with col_title:
        st.markdown(
            f'<h1 style="margin-bottom:0;font-size:1.8rem;font-weight:800;color:#0f172a;">{title}</h1>',
            unsafe_allow_html=True,
        )
        if subtitle:
            st.markdown(
                f'<p style="margin-top:0.2rem;margin-bottom:1rem;font-size:1rem;color:#64748b;">{subtitle}</p>',
                unsafe_allow_html=True,
            )
    with col_status:
        st.markdown(
            '''
            <div style="display: flex; flex-direction: column; align-items: flex-end; justify-content: center; height: 100%; padding-top: 0.5rem; gap: 6px;">
                <div style="display: flex; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; padding: 4px 10px; border-radius: 20px;">
                    <div style="width: 8px; height: 8px; background-color: #10b981; border-radius: 50%; margin-right: 6px;"></div>
                    <span style="color: #475569; font-size: 0.7rem; font-weight: 700;">SYSTEM OPERATIONAL</span>
                </div>
                <div style="display: flex; align-items: center; background: #f0fdf4; border: 1px solid #bbf7d0; padding: 4px 10px; border-radius: 20px;">
                    <span style="color: #16a34a; font-size: 0.7rem; font-weight: 700;">MCP CONNECTED</span>
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
    st.markdown(f"<hr style='margin:1rem 0 2rem 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
