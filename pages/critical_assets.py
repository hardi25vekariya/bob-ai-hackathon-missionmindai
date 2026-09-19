import streamlit as st
from components.styles import load_css, render_header
from components.backend import check_backend, load_all_risks, risk_color_css, short_diag

load_css()
check_backend()
render_header("Critical Assets", "Immediate Attention Required")

try:
    all_risks = load_all_risks()
except Exception as e:
    st.error(f"⚠️ Failed to load backend data: {e}")
    st.stop()

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
