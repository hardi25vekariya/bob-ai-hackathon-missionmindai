import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from components.styles import load_css, render_header
from components.backend import check_backend, load_sensor_data, get_asset_detail, risk_color_css

load_css()
check_backend()
render_header("Asset Investigation", "Deep inspection of individual aircraft")

try:
    sensor_df = load_sensor_data()
except Exception as e:
    st.error(f"Failed to load backend data: {e}")
    st.stop()

st.markdown('<div class="section-header">Asset Investigation</div>', unsafe_allow_html=True)

# We want to allow searching by asset ID or Name, if present
asset_cols = [c for c in sensor_df.columns if c.lower() in ["asset_id", "assetid", "asset id", "vehicle_id", "aircraft_id"]]
name_cols = [c for c in sensor_df.columns if c.lower() in ["asset_name", "assetname", "asset name", "name", "vehicle_name"]]

# The backend normalization ensures we have 'asset_id' if uploaded through Admin
primary_id_col = "asset_id" if "asset_id" in sensor_df.columns else (asset_cols[0] if asset_cols else sensor_df.columns[0])
name_col = name_cols[0] if name_cols else None

# Build a list of display names for the dropdown
search_options = []
mapping = {}
for _, row in sensor_df.iterrows():
    val_id = str(row[primary_id_col])
    if name_col and not pd.isna(row[name_col]):
        display = f"{val_id} - {row[name_col]}"
    else:
        display = val_id
    search_options.append(display)
    mapping[display] = val_id

selected_display = st.selectbox(
    "Search Asset / Vehicle",
    options=["-- Select an Asset --"] + search_options,
    help="Search by Asset ID or Name from the active dataset"
)

if selected_display != "-- Select an Asset --":
    selected_id = mapping[selected_display]
    
    st.markdown("<hr style='border-color: var(--border-color); margin: 2rem 0;'>", unsafe_allow_html=True)
    
    # ── AI Risk Diagnosis ──
    try:
        detail = get_asset_detail(selected_id)
        is_ready = detail["is_ready"]
        risk_score = detail["risk_score"]
        component = detail.get("predicted_component_at_risk", "UNKNOWN").upper()
        reason = detail.get("reason", "")
        readiness_text = detail.get("readiness_details", "")
        cancellation_prob = detail.get("cancellation_probability", 0.0)
        
        st.markdown(f"### AI DIAGNOSIS: {selected_id}")
        left, right = st.columns(2)
        with left:
            status_badge = '<span class="badge-ready">READY</span>' if is_ready else '<span class="badge-nonready">NON-READY</span>'
            st.markdown(f"**Readiness Status** &nbsp; {status_badge}", unsafe_allow_html=True)
            st.markdown(f"**Cancellation Probability:** <span style='font-weight:700; color:{'#ef4444' if cancellation_prob > 65 else '#10b981'};'>{cancellation_prob:.1f}%</span>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:var(--text-color);font-size:0.83rem;margin-top:0.3rem;opacity:0.8;'>{readiness_text}</p>",
                        unsafe_allow_html=True)
        with right:
            st.markdown(f"**Risk Score: <span class='{risk_color_css(risk_score)}'>{risk_score:.1f} / 100</span>**",
                        unsafe_allow_html=True)
            st.progress(int(risk_score))
            st.markdown(f"**Predicted Component at Risk:** &nbsp;<span class='comp-value'>{component}</span>",
                        unsafe_allow_html=True)
            st.markdown(f"<p style='color:var(--text-color);font-size:0.82rem;margin-top:0.4rem;opacity:0.8;'>{reason}</p>",
                        unsafe_allow_html=True)
                        
        if cancellation_prob > 65:
            st.markdown(f"""
            <div style="background-color:#fef2f2; border:1px solid #fca5a5; padding:1rem; border-radius:8px; margin-top:1rem;">
                <h4 style="margin:0; color:#b91c1c; font-size:1.05rem;">⚠️ High Risk of Upcoming Cancellation</h4>
                <p style="margin-top:0.5rem; color:#991b1b; font-size:0.9rem;">
                    <strong>Prediction:</strong> This aircraft is highly likely to be grounded for its next flight.<br>
                    <strong>Reason for Cancellation:</strong> {readiness_text.replace('NON-READY: ', '')}<br>
                    <strong>Recommended Action to Fix ASAP:</strong> Dispatch maintenance crew immediately to inspect and repair the <strong>{component}</strong> subsystem. Address the following: <em>{reason}</em>.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color:#f0fdf4; border:1px solid #86efac; padding:1rem; border-radius:8px; margin-top:1rem;">
                <h4 style="margin:0; color:#166534; font-size:1.05rem;">✅ Low Risk of Upcoming Cancellation</h4>
                <p style="margin-top:0.5rem; color:#15803d; font-size:0.9rem;">
                    <strong>Prediction:</strong> This aircraft is highly likely to successfully complete its upcoming flights.<br>
                    <strong>Rationale:</strong> Behavioral anomaly probability is low ({cancellation_prob:.1f}%).<br>
                    <strong>Recommended Action:</strong> Routine monitoring. No immediate maintenance required.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        # Gracefully handle missing AI prediction for a synthetic uploaded asset
        st.info(f"AI Risk Diagnosis unavailable for this asset. ({e})")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Get the row(s) for the selected asset
    asset_records = sensor_df[sensor_df[primary_id_col].astype(str) == selected_id]
    
    if not asset_records.empty:
        # ── Behavioral Trend Analysis (Failure Prediction) ──
        st.markdown("### BEHAVIORAL TREND ANALYSIS")
        st.markdown("<p style='font-size:0.9rem; color:#475569;'>Comparison of this asset's behavior against the fleet average. Used by the AI to predict failure cancellation probability.</p>", unsafe_allow_html=True)
        
        asset_vib_trend = float(asset_records.iloc[0].get("vibration_7d_trend", 0))
        asset_temp_vol = float(asset_records.iloc[0].get("temp_volatility", 0))
        asset_oil_deg = float(asset_records.iloc[0].get("oil_degradation_rate", 0))
        
        fleet_vib_trend = float(sensor_df.get("vibration_7d_trend", pd.Series([0])).mean())
        fleet_temp_vol = float(sensor_df.get("temp_volatility", pd.Series([0])).mean())
        fleet_oil_deg = float(sensor_df.get("oil_degradation_rate", pd.Series([0])).mean())
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=['Vibration Trend', 'Temp Volatility', 'Oil Degradation'],
            x=[asset_vib_trend, asset_temp_vol, asset_oil_deg],
            name='This Asset',
            orientation='h',
            marker=dict(color='#ef4444')
        ))
        fig.add_trace(go.Bar(
            y=['Vibration Trend', 'Temp Volatility', 'Oil Degradation'],
            x=[fleet_vib_trend, fleet_temp_vol, fleet_oil_deg],
            name='Fleet Average',
            orientation='h',
            marker=dict(color='#94a3b8')
        ))
        
        fig.update_layout(
            barmode='group',
            margin=dict(l=0, r=0, t=30, b=0),
            height=250,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#e2e8f0', title="Value"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Complete Asset Details from CSV ──
    st.markdown("### COMPLETE ASSET DETAILS")
    
    if asset_records.empty:
        st.warning(f"No asset matching '{selected_id}' was found in the active dataset.")
    else:
        # Display the most recent record (assuming last row or sorting if timestamp exists)
        if "timestamp" in asset_records.columns:
            asset_records = asset_records.sort_values("timestamp", ascending=False)
            
        record = asset_records.iloc[0].to_dict()
        
        # Categorize columns generically to show everything dynamically
        categories = {
            "IDENTIFICATION": [],
            "HEALTH / SENSOR DATA": [],
            "OPERATING INFORMATION": [],
            "MISSION INFORMATION": [],
            "MAINTENANCE INFORMATION": [],
            "RISK / STATUS": [],
            "OTHER": []
        }
        
        for col, val in record.items():
            c_low = col.lower()
            if any(k in c_low for k in ["id", "name", "type", "squadron"]):
                if "mission" in c_low:
                    categories["MISSION INFORMATION"].append((col, val))
                else:
                    categories["IDENTIFICATION"].append((col, val))
            elif any(k in c_low for k in ["temp", "vib", "pres", "rpm", "oil", "fuel", "sensor"]):
                categories["HEALTH / SENSOR DATA"].append((col, val))
            elif any(k in c_low for k in ["hour", "age", "fail"]):
                categories["OPERATING INFORMATION"].append((col, val))
            elif "mission" in c_low or "readiness" in c_low or "urgency" in c_low:
                categories["MISSION INFORMATION"].append((col, val))
            elif any(k in c_low for k in ["maint", "repair", "replace", "down", "tech", "issue"]):
                categories["MAINTENANCE INFORMATION"].append((col, val))
            elif any(k in c_low for k in ["risk", "status", "critic"]):
                categories["RISK / STATUS"].append((col, val))
            else:
                categories["OTHER"].append((col, val))
                
        # Render the grouped details
        for cat_name, items in categories.items():
            if not items:
                continue
            st.markdown(f"**{cat_name}**")
            cols = st.columns(3)
            for idx, (c_name, c_val) in enumerate(items):
                display_name = c_name.replace("_", " ").title()
                cols[idx % 3].metric(display_name, str(c_val))
            st.markdown("<hr style='border-color: var(--border-color); opacity:0.3; margin: 1rem 0;'>", unsafe_allow_html=True)
