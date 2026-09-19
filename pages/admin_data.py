import streamlit as st
import pandas as pd
import os
from components.styles import load_css, render_header
from components.backend import check_backend, clear_backend_cache, get_active_sensor_file, _DATA_DIR

load_css()
check_backend()
render_header("Admin Data Management", "System administration and configuration")

st.markdown('<div class="section-header">Active Dataset</div>', unsafe_allow_html=True)

# ── ACTIVE DATASET INDICATOR ──
current_file = get_active_sensor_file()
try:
    current_df = pd.read_csv(current_file)
    rows, cols = current_df.shape
    file_name = os.path.basename(current_file)
    if "uploaded_" in file_name:
        status_color = "#10b981"  # green
        status_text = "● Active (Uploaded)"
    else:
        status_color = "#3b82f6"  # blue
        status_text = "● Active (Default)"

    st.markdown(f"""
    <div style="background: var(--secondary-background-color); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 1.2rem; font-weight: bold;">Current Dataset</div>
            <div style="color: {status_color}; font-weight: bold;">{status_text}</div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
            <div>
                <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-color); opacity: 0.7;">File</div>
                <div style="font-family: monospace; font-size: 1rem; color: var(--primary-color);">{file_name}</div>
            </div>
            <div>
                <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-color); opacity: 0.7;">Rows</div>
                <div style="font-size: 1.5rem; font-weight: bold;">{rows:,}</div>
            </div>
            <div>
                <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-color); opacity: 0.7;">Columns</div>
                <div style="font-size: 1.5rem; font-weight: bold;">{cols:,}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error reading active dataset: {e}")

st.markdown('<div class="section-header">Upload New Dataset</div>', unsafe_allow_html=True)
st.markdown("Upload a new CSV file to securely replace the active dataset across the platform.")

uploaded_file = st.file_uploader("Choose CSV File", type=["csv"])

if uploaded_file is not None:
    try:
        if not uploaded_file.name.endswith('.csv'):
            st.error("Validation failed: Please verify the file format is a valid CSV.")
        else:
            # Safely read the CSV
            df = pd.read_csv(uploaded_file)
            
            if df.empty:
                st.error("Validation failed: The uploaded CSV is empty.")
            else:
                # Validate required columns loosely
                cols_lower = [str(c).lower() for c in df.columns]
                
                # We need some identifier column
                asset_col = None
                for candidate in ["asset_id", "assetid", "asset id", "vehicle_id", "aircraft_id"]:
                    if candidate in cols_lower:
                        original_col = df.columns[cols_lower.index(candidate)]
                        asset_col = original_col
                        break
                        
                if not asset_col:
                    st.error("Validation failed: Missing required asset identifier column (e.g. 'asset_id').")
                else:
                    st.success("Dataset validated successfully.")
                    
                    st.markdown("**Preview:**")
                    st.dataframe(df.head(), use_container_width=True)
                    
                    st.markdown("**Column Names:**")
                    st.code(", ".join(df.columns))
                    
                    if st.button("Import Dataset", type="primary", use_container_width=True):
                        # Save the dataset to the data directory securely
                        save_path = os.path.join(_DATA_DIR, "uploaded_sensor_data.csv")
                        
                        # We must ensure the identifier is named exactly 'asset_id' for backend pipelines
                        if asset_col != "asset_id":
                            df = df.rename(columns={asset_col: "asset_id"})
                            
                        df.to_csv(save_path, index=False)
                        
                        # Update session state
                        st.session_state["active_sensor_file"] = save_path
                        
                        # Clear cache so other pages immediately pick up the new data
                        clear_backend_cache()
                        
                        st.rerun()

    except Exception as e:
        st.error(f"Unable to import this CSV. Error: {e}")
