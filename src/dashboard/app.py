"""
AeroGuard-Bob — Mission Readiness & Predictive Maintenance Dashboard
=====================================================================
Streamlit dashboard that wraps the existing MCP handler functions.
All readiness, risk, and maintenance logic lives in src/pipeline/ and
src/mcp/. This file only displays data — it does not reimplement logic.

Run from project root:
    streamlit run src/dashboard/app.py
"""

import sys
import os

# ---------------------------------------------------------------------------
# PATH BOOTSTRAP — works regardless of the working directory the user launches from
# ---------------------------------------------------------------------------
_DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.abspath(os.path.join(_DASHBOARD_DIR, ".."))
_MCP_DIR = os.path.join(_SRC_DIR, "mcp")
_PIPELINE_DIR = os.path.join(_SRC_DIR, "pipeline")
_DATA_DIR = os.path.join(_SRC_DIR, "data")

for _p in [_MCP_DIR, _PIPELINE_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Import MCP handlers — this is the ONLY integration boundary with the backend
try:
    from mcp_server import (
        handle_get_fleet_readiness,
        handle_get_asset_risk,
        handle_get_maintenance_plan,
        DEFAULT_AVAILABLE_CREWS,
        DEFAULT_PARTS_INVENTORY,
    )
    _BACKEND_OK = True
except Exception as _e:
    _BACKEND_OK = False
    _BACKEND_ERR = str(_e)

# ---------------------------------------------------------------------------
# PAGE CONFIG (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AeroGuard-Bob | Mission Readiness",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# DARK MILITARY THEME
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0e1a;
    color: #e2e8f0;
}
[data-testid="stHeader"] { background-color: #0a0e1a; }
[data-testid="block-container"] { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background-color: #060a14; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 1rem 1.2rem;
}
[data-testid="stMetricLabel"] { color: #94a3b8; font-size: 0.78rem; letter-spacing: 0.06em; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: #e2e8f0; font-size: 1.9rem; font-weight: 700; }
[data-testid="stMetricDelta"] svg { display: none; }

/* ── DataFrames ── */
[data-testid="stDataFrame"] { border: 1px solid #1e3a5f; border-radius: 6px; }

/* ── Forms & inputs ── */
[data-testid="stForm"] {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 1.2rem;
}
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: #1a2235 !important;
    color: #e2e8f0 !important;
    border: 1px solid #1e3a5f !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
}

/* ── Buttons ── */
.stButton > button {
    background: #1e3a5f;
    color: #e2e8f0;
    border: 1px solid #3b82f6;
    border-radius: 6px;
    font-weight: 600;
    letter-spacing: 0.04em;
}
.stButton > button:hover {
    background: #3b82f6;
    color: #ffffff;
}

/* ── Dividers ── */
hr { border-color: #1e3a5f; }

/* ── Section headers ── */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #93c5fd;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
    margin-top: 1.5rem;
}

/* ── Status badges ── */
.badge-ready    { background:#064e3b; color:#6ee7b7; border:1px solid #10b981; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; letter-spacing:0.06em; }
.badge-nonready { background:#450a0a; color:#fca5a5; border:1px solid #ef4444; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; letter-spacing:0.06em; }
.badge-sched    { background:#052e16; color:#86efac; border:1px solid #22c55e; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; letter-spacing:0.06em; }
.badge-queued   { background:#451a03; color:#fcd34d; border:1px solid #f59e0b; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; letter-spacing:0.06em; }
.badge-critical { background:#450a0a; color:#f87171; border:1px solid #dc2626; padding:3px 10px; border-radius:12px; font-size:0.78rem; font-weight:700; letter-spacing:0.06em; }

/* ── Asset cards ── */
.asset-card {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 1rem;
    height: 100%;
}
.asset-card.critical { border-color: #dc2626; }
.asset-id { font-size: 1.3rem; font-weight: 800; color: #93c5fd; font-family: monospace; }
.risk-score-num { font-size: 2rem; font-weight: 900; }
.risk-critical { color: #ef4444; }
.risk-warning  { color: #f59e0b; }
.risk-good     { color: #10b981; }
.comp-label { font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; }
.comp-value { font-size: 0.9rem; font-weight: 700; color: #fbbf24; }
.diag-text  { font-size: 0.78rem; color: #94a3b8; margin-top: 0.4rem; line-height: 1.5; }

/* ── Bob panel ── */
.bob-card {
    background: #111827;
    border: 1px solid #1e40af;
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.85rem;
    color: #bfdbfe;
}
.bob-header {
    font-size: 1.4rem;
    font-weight: 800;
    color: #60a5fa;
    letter-spacing: 0.04em;
}
.mcp-tag {
    background: #1e3a5f;
    color: #93c5fd;
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 0.72rem;
    font-family: monospace;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# BACKEND GUARD
# ---------------------------------------------------------------------------
if not _BACKEND_OK:
    st.error(f"❌ Could not load backend: {_BACKEND_ERR}")
    st.info("Ensure you run this from the project root: `streamlit run src/dashboard/app.py`")
    st.stop()

# ---------------------------------------------------------------------------
# CACHED DATA LOADERS
# ---------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_fleet_readiness():
    result = handle_get_fleet_readiness()
    if result.get("status") != "success":
        raise RuntimeError(result.get("message", "Unknown error from get_fleet_readiness"))
    return result

@st.cache_data(ttl=60)
def load_all_risks():
    result = handle_get_asset_risk()
    if result.get("status") != "success":
        raise RuntimeError(result.get("message", "Unknown error from get_asset_risk"))
    return result["ranked_risk_list"]  # list of dicts, sorted by risk_score desc

@st.cache_data(ttl=60)
def load_sensor_data():
    path = os.path.join(_DATA_DIR, "sensor_data.csv")
    return pd.read_csv(path)

@st.cache_data(ttl=60)
def load_service_history():
    path = os.path.join(_DATA_DIR, "service_history.csv")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date", ascending=False)

def get_asset_detail(asset_id: str):
    result = handle_get_asset_risk(asset_id=asset_id)
    if result.get("status") != "success":
        raise RuntimeError(result.get("message", f"Asset '{asset_id}' not found"))
    return result

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def risk_color_css(score: float) -> str:
    if score >= 70:
        return "risk-critical"
    if score >= 40:
        return "risk-warning"
    return "risk-good"

def risk_color_hex(score: float) -> str:
    if score >= 70:
        return "#ef4444"
    if score >= 40:
        return "#f59e0b"
    return "#10b981"

def short_diag(text: str, n: int = 90) -> str:
    return text[:n] + "…" if len(text) > n else text

# ---------------------------------------------------------------------------
# ── HEADER ──────────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------
col_title, col_refresh = st.columns([5, 1])
with col_title:
    st.markdown(
        '<h1 style="color:#93c5fd;margin-bottom:0;font-size:2rem;letter-spacing:0.04em;">✈ AeroGuard-Bob</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#94a3b8;margin-top:0.1rem;margin-bottom:0.2rem;font-size:1rem;">'
        'Mission Readiness &amp; Predictive Maintenance Copilot</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<span style="background:#1e3a5f;color:#93c5fd;border-radius:4px;padding:3px 10px;'
        'font-size:0.72rem;font-weight:700;letter-spacing:0.06em;">'
        'IBM BOB HACKATHON · DEFENSE &amp; AEROSPACE · D1</span>',
        unsafe_allow_html=True,
    )
with col_refresh:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("<hr style='margin:1rem 0 0.5rem 0;'>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# LOAD DATA (with graceful error handling)
# ---------------------------------------------------------------------------
try:
    fleet_data = load_fleet_readiness()
    fleet_metrics = fleet_data["fleet_metrics"]
    all_risks = load_all_risks()
    sensor_df = load_sensor_data()
    service_df = load_service_history()
except FileNotFoundError as e:
    st.error(f"📁 Data file not found: {e}")
    st.info("Run `python src/data/generate_dataset.py` to regenerate the CSV files.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Failed to load backend data: {e}")
    st.stop()

# Pre-compute useful structures
risk_df = pd.DataFrame(all_risks)  # already sorted by risk_score desc
critical_count = int((risk_df["risk_score"] >= 70).sum())

# ---------------------------------------------------------------------------
# ── KPI ROW ─────────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">Squadron Status</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Aircraft",   fleet_metrics["total_assets"])
k2.metric("Mission Ready",    fleet_metrics["mission_ready_count"],
          delta=f"+{fleet_metrics['mission_ready_count']} ready")
k3.metric("Non-Ready / Grounded", fleet_metrics["non_ready_count"],
          delta=f"-{fleet_metrics['non_ready_count']} grounded", delta_color="inverse")
k4.metric("Readiness Rate",   f"{fleet_metrics['readiness_rate_pct']}%")
k5.metric("Critical Risk (≥70)", critical_count,
          delta="action required" if critical_count > 0 else "none",
          delta_color="inverse" if critical_count > 0 else "normal")

# ---------------------------------------------------------------------------
# ── FLEET OVERVIEW TABLE ─────────────────────────────────────────────────────
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">Fleet Overview</div>', unsafe_allow_html=True)

# Build display DataFrame
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

# ---------------------------------------------------------------------------
# ── CRITICAL ASSETS PANEL ────────────────────────────────────────────────────
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">Critical Assets — Immediate Attention Required</div>',
            unsafe_allow_html=True)

critical_assets = [r for r in all_risks if not r["is_ready"] and r["risk_score"] >= 40]
top5 = critical_assets[:5]

if not top5:
    st.success("✅ No critical assets — full fleet is mission ready.")
else:
    cols = st.columns(len(top5))
    for col, asset in zip(cols, top5):
        score = asset["risk_score"]
        css_score = risk_color_css(score)
        is_critical = score >= 70
        card_border = "critical" if is_critical else ""
        badge = '<span class="badge-nonready">NON-READY</span>' if not asset["is_ready"] else '<span class="badge-ready">READY</span>'

        col.markdown(f"""
<div class="asset-card {card_border}">
  <div class="asset-id">{asset['asset_id']}</div>
  <div style="margin:0.3rem 0;">{badge}</div>
  <div class="risk-score-num {css_score}">{score:.1f}<span style="font-size:0.9rem;color:#94a3b8;">/100</span></div>
  <div class="comp-label">At-Risk Component</div>
  <div class="comp-value">{asset['predicted_component_at_risk'].upper()}</div>
  <div class="diag-text">{short_diag(asset['reason'], 120)}</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ── ASSET INVESTIGATION ──────────────────────────────────────────────────────
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">Asset Investigation</div>', unsafe_allow_html=True)

asset_ids_by_risk = [r["asset_id"] for r in all_risks]  # already sorted high → low risk
selected_id = st.selectbox(
    "Select Aircraft for Deep Inspection",
    options=asset_ids_by_risk,
    help="Assets ordered by risk score (highest first)",
)

try:
    detail = get_asset_detail(selected_id)
    s_row = sensor_lookup.loc[selected_id] if selected_id in sensor_lookup.index else None
    asset_service = service_df[service_df["asset_id"] == selected_id].copy()

    is_ready = detail["is_ready"]
    risk_score = detail["risk_score"]
    component = detail["predicted_component_at_risk"].upper()
    reason = detail["reason"]
    readiness_text = detail["readiness_details"]

    left, right = st.columns(2)

    # ── Left: Readiness + Risk ──
    with left:
        status_badge = '<span class="badge-ready">✓ READY</span>' if is_ready else '<span class="badge-nonready">✗ NON-READY</span>'
        st.markdown(f"**Readiness Status** &nbsp; {status_badge}", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#94a3b8;font-size:0.83rem;margin-top:0.3rem;'>{readiness_text}</p>",
                    unsafe_allow_html=True)

        st.markdown(f"**Risk Score: <span class='{risk_color_css(risk_score)}'>{risk_score:.1f} / 100</span>**",
                    unsafe_allow_html=True)
        st.progress(int(risk_score))

        st.markdown(f"**Predicted Component at Risk:** &nbsp;<span class='comp-value'>{component}</span>",
                    unsafe_allow_html=True)
        st.markdown(f"<p style='color:#94a3b8;font-size:0.82rem;margin-top:0.4rem;'>{reason}</p>",
                    unsafe_allow_html=True)

    # ── Right: Sensor Readings ──
    with right:
        st.markdown("**Live Sensor Readings**")
        if s_row is not None:
            vib   = float(s_row["vibration_level"])
            temp  = float(s_row["engine_temp_c"])
            oil   = float(s_row["oil_quality_index"])
            insp  = int(s_row["last_inspection_days_ago"])
            cyc   = int(s_row["usage_cycles"])

            c1, c2 = st.columns(2)
            c1.metric("Vibration Level",    f"{vib:.2f} mm/s",
                      delta=f"{vib - 9.0:+.2f} vs limit",
                      delta_color="inverse" if vib > 9.0 else "normal")
            c2.metric("Engine Temp",        f"{temp:.1f} °C",
                      delta=f"{temp - 600.0:+.1f} vs limit",
                      delta_color="inverse" if temp > 600.0 else "normal")

            c3, c4 = st.columns(2)
            c3.metric("Oil Quality Index",  f"{oil:.0f} / 100",
                      delta=f"{oil - 50.0:+.0f} vs minimum",
                      delta_color="normal" if oil >= 50.0 else "inverse")
            c4.metric("Last Inspection",    f"{insp} days ago",
                      delta=f"{insp - 150:+d} vs limit",
                      delta_color="inverse" if insp > 150 else "normal")

            st.metric("Usage Cycles", f"{cyc:,}")
        else:
            st.info("Sensor data not available for this asset.")

    # ── Service History ──
    st.markdown("**Maintenance History**")
    if asset_service.empty:
        st.info("No service history records found for this asset.")
    else:
        disp_service = asset_service[["date", "component", "issue_found", "action_taken"]].copy()
        disp_service["date"] = disp_service["date"].dt.strftime("%Y-%m-%d")
        disp_service.columns = ["Date", "Component", "Issue Found", "Action Taken"]
        st.dataframe(disp_service, hide_index=True, use_container_width=True)

    # ── Recommendation ──
    st.markdown("**Recommendation**")
    if not is_ready:
        if risk_score >= 70:
            rec = (f"🔴 **CRITICAL — Ground immediately.** "
                   f"Schedule urgent maintenance on the **{component}** subsystem. "
                   f"Risk score {risk_score:.1f}/100 — do not clear for flight until resolved.")
        else:
            rec = (f"🟡 **NON-READY — Schedule maintenance.** "
                   f"Priority repair required on **{component}** subsystem. "
                   f"Risk score {risk_score:.1f}/100.")
        st.warning(rec)
    else:
        st.success(f"✅ **{selected_id} is mission ready.** "
                   f"All sensor metrics within operational limits. "
                   f"Residual risk score {risk_score:.1f}/100 — continue standard monitoring schedule.")

except Exception as e:
    st.error(f"⚠️ Could not load details for {selected_id}: {e}")

# ---------------------------------------------------------------------------
# ── MAINTENANCE TRIAGE ───────────────────────────────────────────────────────
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">Maintenance Triage & Resource Planning</div>',
            unsafe_allow_html=True)

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

                # Executive summary
                st.info(f"📋 **Executive Summary:** {summary}")

                # Metrics row
                m1, m2, m3 = st.columns(3)
                m1.metric("Requiring Maintenance", metrics["total_requiring_maintenance"])
                m2.metric("Scheduled",  metrics["scheduled_count"])
                m3.metric("Queued",     metrics["queued_count"])

                sched_items  = [r for r in schedule if r["status"] == "scheduled"]
                queued_items = [r for r in schedule if r["status"] == "queued"]

                # SCHEDULED table
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

                # QUEUED table
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

# ---------------------------------------------------------------------------
# ── RISK VISUALIZATION ───────────────────────────────────────────────────────
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">Fleet Risk Profile</div>', unsafe_allow_html=True)

try:
    # Sort ascending so highest risk appears at top of horizontal bar chart
    viz_df = risk_df.sort_values("risk_score", ascending=True).copy()

    bar_colors = [risk_color_hex(s) for s in viz_df["risk_score"]]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=viz_df["risk_score"],
        y=viz_df["asset_id"],
        orientation="h",
        marker_color=bar_colors,
        text=[f"{s:.1f}" for s in viz_df["risk_score"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=11),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Risk Score: %{x:.1f}/100<br>"
            "<extra></extra>"
        ),
    ))

    # Critical threshold line
    fig.add_vline(
        x=70, line_width=1.5, line_dash="dash", line_color="#dc2626",
        annotation_text="Critical (70)", annotation_position="top",
        annotation_font_color="#dc2626", annotation_font_size=11,
    )

    fig.update_layout(
        title=dict(text="Subsystem Failure Risk Score by Aircraft  (0–100)",
                   font=dict(color="#93c5fd", size=14), x=0),
        xaxis=dict(
            range=[0, 115], title="Risk Score",
            tickfont=dict(color="#94a3b8"), title_font=dict(color="#94a3b8"),
            gridcolor="#1e3a5f", zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(color="#e2e8f0", size=11),
            gridcolor="#1e3a5f",
        ),
        plot_bgcolor="#0a0e1a",
        paper_bgcolor="#0a0e1a",
        margin=dict(l=20, r=40, t=50, b=30),
        height=600,
        hoverlabel=dict(bgcolor="#111827", font_color="#e2e8f0"),
    )

    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"⚠️ Chart rendering failed: {e}")

# ---------------------------------------------------------------------------
# ── BOB COPILOT PANEL ────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">🤖 Bob Copilot</div>', unsafe_allow_html=True)

st.markdown(
    '<p class="bob-header">🤖 BOB COPILOT</p>'
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
            f'<div class="bob-card">💬 &nbsp;<em>"{q}"</em></div>',
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
    '📡 <strong>Connect IBM Bob:</strong> Register the MCP server using the config in '
    '<code>docs/setup-guide.md</code>. IBM Bob will call '
    '<span class="mcp-tag">get_fleet_readiness</span>, '
    '<span class="mcp-tag">get_asset_risk</span>, and '
    '<span class="mcp-tag">get_maintenance_plan</span> '
    'directly — grounding every response in verified sensor telemetry and maintenance logs.'
    '</div>',
    unsafe_allow_html=True,
)

# ── Live MCP Tool Test ──
with st.expander("🔧 Live MCP Tool Test — Verify Backend Integration"):
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

# ---------------------------------------------------------------------------
# ── FOOTER ──────────────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------
st.markdown("<hr style='margin:2rem 0 0.8rem 0;border-color:#1e3a5f;'>", unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center;color:#475569;font-size:0.75rem;">'
    'AeroGuard-Bob &nbsp;·&nbsp; IBM Bob AI Hackathon &nbsp;·&nbsp; '
    'Defense &amp; Aerospace Track D1 &nbsp;·&nbsp; '
    'Data pipeline: <code style="color:#64748b;">src/pipeline/</code> &nbsp;·&nbsp; '
    'MCP layer: <code style="color:#64748b;">src/mcp/mcp_server.py</code>'
    '</p>',
    unsafe_allow_html=True,
)
