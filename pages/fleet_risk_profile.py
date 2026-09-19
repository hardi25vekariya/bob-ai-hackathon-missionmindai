import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from components.styles import load_css, render_header
from components.backend import check_backend, load_all_risks, risk_color_hex

load_css()
check_backend()
render_header("Fleet Risk Profile", "Subsystem failure risk analysis")

try:
    all_risks = load_all_risks()
    risk_df = pd.DataFrame(all_risks)
except Exception as e:
    st.error(f"⚠️ Failed to load backend data: {e}")
    st.stop()

st.markdown('<div class="section-header">Fleet Risk Profile</div>', unsafe_allow_html=True)

try:
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
        title=dict(text="Subsystem Failure Risk Score by Aircraft  (0–100)", x=0),
        xaxis=dict(
            range=[0, 115], title="Risk Score",
            zeroline=False,
        ),
        yaxis=dict(),
        margin=dict(l=20, r=40, t=50, b=30),
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"⚠️ Chart rendering failed: {e}")
