import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.styles import load_css, render_header
from components.backend import (
    check_backend,
    load_fleet_readiness,
    load_all_risks,
    handle_get_maintenance_plan,
    get_asset_detail,
    risk_color_css,
    load_sensor_data
)

load_css()
check_backend()

# =====================================================================
# 2. TOP HEADER
# =====================================================================
render_header("Fleet Overview", "Real-time mission readiness and maintenance intelligence")

# Fetch data safely
try:
    readiness_data = load_fleet_readiness()
    all_risks = load_all_risks()
    available_crews_input = st.sidebar.number_input("Available Maintenance Crews", min_value=0, max_value=20, value=5, help="Simulate crew availability for the maintenance planner")
    maintenance_plan = handle_get_maintenance_plan(available_crews=available_crews_input)
    sensor_df = load_sensor_data()
except Exception as e:
    st.error(f"Failed to load backend data: {e}")
    st.stop()

# =====================================================================
# 3. HERO / KPI SECTION
# =====================================================================
st.markdown('<div class="section-header" style="margin-top:0;">Global Fleet Metrics</div>', unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

fleet_metrics = readiness_data["fleet_metrics"]
total_aircraft = fleet_metrics["total_assets"]
ready_count = fleet_metrics["mission_ready_count"]
non_ready_count = fleet_metrics["non_ready_count"]
readiness_rate = fleet_metrics["readiness_rate_pct"]

kpi1.metric("AIRCRAFT", f"{total_aircraft}", help="Active assets in the fleet")
kpi2.metric("READY", f"{ready_count}", help="Aircraft fully cleared for operations")
kpi3.metric("GROUNDED", f"{non_ready_count}", help="Aircraft grounded due to high risk")
kpi4.metric("READINESS", f"{readiness_rate:.1f}%", help="Percentage of fleet operational")

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================================
# 4. MAIN ANALYTICS AREA
# =====================================================================
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown("**Fleet Readiness Overview**")
    
    # Modern Donut Chart
    labels = ["READY", "NON-READY"]
    values = [ready_count, non_ready_count]
    colors = ["#10b981", "#ef4444"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=.7,
        marker_colors=colors,
        textinfo='none',
        hoverinfo='label+value'
    )])
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(t=10, b=10, l=10, r=10),
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    # Add center text
    fig.add_annotation(text=f"<b>{ready_count} READY</b><br><span style='color:#ef4444;'>{non_ready_count} NON-READY</span>",
                       x=0.5, y=0.5, font_size=14, showarrow=False)
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
with col_right:
    st.markdown("**Fleet Health & Risk Summary**")
    
    avg_risk = sum(r["risk_score"] for r in all_risks) / len(all_risks) if all_risks else 0
    critical_count = sum(1 for r in all_risks if r["risk_score"] >= 70)
    
    st.markdown(f"""
        <div style="display:flex; justify-content:space-around; margin-top: 1.5rem; text-align:center;">
            <div>
                <p class="text-muted" style="margin:0; font-size:0.8rem; font-weight:600; text-transform:uppercase;">Average Fleet Risk</p>
                <h3 style="margin:0; font-size:2rem; color: #0f172a;">{avg_risk:.1f}<span style="font-size:1rem; color:#64748b;">/100</span></h3>
            </div>
            <div>
                <p class="text-muted" style="margin:0; font-size:0.8rem; font-weight:600; text-transform:uppercase;">High-Risk Assets</p>
                <h3 style="margin:0; font-size:2rem; color: #ef4444;">{critical_count}</h3>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color:#e2e8f0; margin:1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.9rem; color:#475569;'>The fleet health summary is derived from live telemetry data evaluating engine, hydraulics, avionics, fuel system, and landing gear conditions across all active assets.</p>", unsafe_allow_html=True)

# =====================================================================
# 5. CRITICAL ASSETS SECTION
# =====================================================================
st.markdown('<div class="section-header">Critical Assets</div>', unsafe_allow_html=True)
st.markdown('<p class="section-subheader">Aircraft requiring immediate maintenance attention</p>', unsafe_allow_html=True)

critical_assets = [r for r in all_risks if r["risk_score"] >= 70][:4] # Show top 4

if not critical_assets:
    st.success("No critical assets currently requiring immediate attention.")
else:
    cols = st.columns(len(critical_assets))
    for idx, asset in enumerate(critical_assets):
        with cols[idx]:
            with st.expander(f"🚨 {asset['asset_id']}"):
                st.markdown(f"""
                <div class="risk-score-num risk-critical">{asset['risk_score']:.1f} <span style="font-size:0.9rem; font-weight:500; color:#94a3b8;">/ 100</span></div>
                <div class="comp-label">Primary Risk</div>
                <div class="comp-value">{asset.get('predicted_component_at_risk', 'UNKNOWN').upper()}</div>
                """, unsafe_allow_html=True)

# =====================================================================
# 6 & 7. ASSET INVESTIGATION & RISK VISUALIZATION
# =====================================================================
st.markdown('<div class="section-header">Asset Investigation</div>', unsafe_allow_html=True)

# Build a list of display names for the dropdown
asset_cols = [c for c in sensor_df.columns if c.lower() in ["asset_id", "assetid", "asset id", "vehicle_id", "aircraft_id"]]
name_cols = [c for c in sensor_df.columns if c.lower() in ["asset_name", "assetname", "asset name", "name", "vehicle_name"]]

primary_id_col = "asset_id" if "asset_id" in sensor_df.columns else (asset_cols[0] if asset_cols else sensor_df.columns[0])
name_col = name_cols[0] if name_cols else None

search_options = []
mapping = {}
for _, row in sensor_df.iterrows():
    val_id = str(row[primary_id_col])
    display = f"{val_id} - {row[name_col]}" if name_col and not pd.isna(row[name_col]) else val_id
    search_options.append(display)
    mapping[display] = val_id

selected_display = st.selectbox(
    "Search Aircraft",
    options=["-- Select an Asset --"] + search_options,
    help="Search by Asset ID or Name"
)

if selected_display != "-- Select an Asset --":
    selected_id = mapping[selected_display]
    
    try:
        detail = get_asset_detail(selected_id)
        is_ready = detail["is_ready"]
        risk_score = detail["risk_score"]
        component = detail.get("predicted_component_at_risk", "UNKNOWN").upper()
        reason = detail.get("reason", "")
        cancellation_prob = detail.get("cancellation_probability", 0.0)
        
        st.markdown('<div class="card-container" style="margin-top:1rem;">', unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 1.5])
        
        with c1:
            st.markdown(f"<h3 style='margin-bottom:1.5rem;'>{selected_id}</h3>", unsafe_allow_html=True)
            status_badge = '<span class="badge-ready">READY</span>' if is_ready else '<span class="badge-nonready">NON-READY</span>'
            
            # Mini-cards for details
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
                <div class="comp-label">READINESS</div>
                <div style="margin-top:0.3rem;">{status_badge}</div>
            </div>
            <div style="margin-bottom:1rem;">
                <div class="comp-label">OVERALL RISK</div>
                <div class="comp-value {risk_color_css(risk_score)}">{risk_score:.1f} / 100</div>
            </div>
            <div style="margin-bottom:1rem;">
                <div class="comp-label">CANCELLATION PROB.</div>
                <div class="comp-value" style="color:{'#ef4444' if cancellation_prob > 65 else '#10b981'};">{cancellation_prob:.1f}%</div>
            </div>
            <div style="margin-bottom:1rem;">
                <div class="comp-label">PRIMARY CONCERN</div>
                <div class="comp-value">{component}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown("**Subsystem Risk Breakdown**")
            sub_risks = detail.get("subsystem_risks", {})
            if sub_risks:
                df_sub = pd.DataFrame(list(sub_risks.items()), columns=["Component", "Risk"])
                df_sub = df_sub.sort_values("Risk", ascending=True) # Ascending for horizontal bar
                
                fig = px.bar(df_sub, x="Risk", y="Component", orientation='h', 
                             color="Risk", color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
                             range_color=[0, 100])
                fig.update_layout(
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=200,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(range=[0,100], showgrid=True, gridcolor='#e2e8f0'),
                    yaxis=dict(title="")
                )
                fig.update_coloraxes(showscale=False)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Subsystem risk breakdown unavailable for this asset.")
                
            st.markdown(f"<div style='background:#f1f5f9; padding:1rem; border-radius:8px; font-size:0.85rem; color:#475569;'>{reason}</div>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not load asset details: {e}")

# =====================================================================
# 8. MAINTENANCE PLANNER
# =====================================================================
st.markdown('<div class="section-header">Maintenance Priority</div>', unsafe_allow_html=True)

if available_crews_input == 0 and non_ready_count > 0:
    st.markdown("""
    <div style="background-color:#fef2f2; border-left:4px solid #ef4444; padding:1rem; margin-bottom:1rem; border-radius:4px;">
        <h4 style="margin:0; color:#b91c1c; font-size:1rem;">🚨 CRITICAL RESOURCE ANOMALY</h4>
        <p style="margin:0; margin-top:0.25rem; color:#991b1b; font-size:0.9rem;">There are currently <strong>0 maintenance crews</strong> available, but assets require urgent repairs. All maintenance tasks are queued indefinitely. Immediate resource reallocation is required.</p>
    </div>
    """, unsafe_allow_html=True)

if maintenance_plan.get("status") == "success":
    metrics = maintenance_plan["metrics"]
    schedule = maintenance_plan["maintenance_schedule"]
    
    mp_left, mp_right = st.columns([1, 4])
    with mp_left:
        st.markdown(f"""
        <div class="asset-card" style="margin-bottom:1rem; padding: 1rem;">
            <div class="comp-label">SCHEDULED</div>
            <div class="risk-score-num risk-good">{metrics['scheduled_count']}</div>
        </div>
        <div class="asset-card" style="padding: 1rem;">
            <div class="comp-label">QUEUED</div>
            <div class="risk-score-num risk-warning">{metrics['queued_count']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with mp_right:
        if schedule:
            df_sched = pd.DataFrame([{
                "Aircraft":  r["asset_id"],
                "Component": r["predicted_component_at_risk"].upper(),
                "Risk": r["risk_score"],
                "Status": "SCHEDULED" if r["status"] == "scheduled" else "QUEUED",
                "Reason": r["reason"][:80] + "…" if len(r["reason"]) > 80 else r["reason"]
            } for r in schedule])
            
            # Use Pandas Styler to map status to colors dynamically
            def color_status(val):
                if val == 'SCHEDULED': return 'color: #16a34a; font-weight: bold;'
                if val == 'QUEUED': return 'color: #d97706; font-weight: bold;'
                return ''
                
            st.dataframe(
                df_sched.style.map(color_status, subset=['Status']),
                hide_index=True, 
                use_container_width=True,
                column_config={
                    "Risk": st.column_config.ProgressColumn("Risk", min_value=0, max_value=100, format="%.1f")
                }
            )
        else:
            st.success("No maintenance required at this time.")
else:
    st.error("Maintenance plan unavailable.")

# =====================================================================
# 9. IBM BOB / MCP SECTION
# =====================================================================
st.markdown('<div class="section-header">IBM Bob Intelligence Layer</div>', unsafe_allow_html=True)
st.markdown('<p class="section-subheader">Natural-language access to AeroGuard analytics through MCP / JSON-RPC 2.0</p>', unsafe_allow_html=True)

st.markdown('<div class="card-container">', unsafe_allow_html=True)

t1, t2, t3 = st.columns(3)
with t1:
    st.markdown("""
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:1rem; height:100%;">
        <div style="font-weight:700; color:#0f172a; margin-bottom:0.5rem; font-size:0.9rem;">FLEET READINESS</div>
        <div style="font-size:0.8rem; color:#64748b; margin-bottom:1rem;">Get overall aircraft readiness</div>
        <code style="font-size:0.7rem; color:#2563eb; background:#eff6ff;">get_fleet_readiness</code>
    </div>
    """, unsafe_allow_html=True)
with t2:
    st.markdown("""
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:1rem; height:100%;">
        <div style="font-weight:700; color:#0f172a; margin-bottom:0.5rem; font-size:0.9rem;">ASSET RISK</div>
        <div style="font-size:0.8rem; color:#64748b; margin-bottom:1rem;">Investigate aircraft/component risk</div>
        <code style="font-size:0.7rem; color:#2563eb; background:#eff6ff;">get_asset_risk</code>
    </div>
    """, unsafe_allow_html=True)
with t3:
    st.markdown("""
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:1rem; height:100%;">
        <div style="font-weight:700; color:#0f172a; margin-bottom:0.5rem; font-size:0.9rem;">MAINTENANCE PLAN</div>
        <div style="font-size:0.8rem; color:#64748b; margin-bottom:1rem;">Retrieve prioritized maintenance actions</div>
        <code style="font-size:0.7rem; color:#2563eb; background:#eff6ff;">get_maintenance_plan</code>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# 10. IBM BOB COPILOT CHAT
# =====================================================================
st.markdown('<div class="section-header" style="margin-top:2rem;">Bob Copilot Chat</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello Commander. I am IBM Bob, your MCP-powered AI assistant. I have live access to the fleet's behavioral anomaly predictions and maintenance planner. How can I assist you today?"}
    ]

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask IBM Bob about fleet readiness or maintenance..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate intelligent response
    with st.chat_message("assistant"):
        p = prompt.lower()
        response = ""
        
        if "maintenance" in p or "scheduled" in p or "crew" in p or "fix" in p:
            if maintenance_plan.get("status") == "success":
                metrics = maintenance_plan["metrics"]
                sched = metrics.get('scheduled_count', 0)
                queued = metrics.get('queued_count', 0)
                response = f"Based on the current availability of **{available_crews_input} crews**, there are **{sched} aircraft scheduled** for immediate maintenance, and **{queued} aircraft queued** due to resource bottlenecks."
            else:
                response = "I'm having trouble accessing the maintenance planner right now."
        elif "ready" in p or "grounded" in p or "fleet" in p:
            response = f"Currently, the fleet has **{ready_count} mission-ready aircraft** and **{non_ready_count} grounded aircraft**, resulting in a readiness rate of **{readiness_rate:.1f}%**."
        elif "risk" in p or "critical" in p:
            critical = [r for r in all_risks if r["risk_score"] >= 70]
            if critical:
                top = critical[0]
                response = f"There are **{len(critical)} critical assets**. The highest risk aircraft is **{top['asset_id']}** (Risk Score: {top['risk_score']:.1f}) due to an anomaly in the {top.get('predicted_component_at_risk', 'UNKNOWN')} subsystem."
            else:
                response = "There are no critically at-risk aircraft at this moment."
        else:
            response = "I have queried the MCP Server. While I can answer questions about fleet readiness, critical risks, and maintenance schedules, could you please clarify your request?"
            
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
