import sys
import os
import pandas as pd
import streamlit as st

_PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.abspath(os.path.join(_PAGES_DIR, ".."))
_SRC_DIR = os.path.join(_ROOT_DIR, "src")
_MCP_DIR = os.path.join(_SRC_DIR, "mcp")
_PIPELINE_DIR = os.path.join(_SRC_DIR, "pipeline")
_DATA_DIR = os.path.join(_SRC_DIR, "data")

for _p in [_ROOT_DIR, _MCP_DIR, _PIPELINE_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from mcp_server import (
        handle_get_fleet_readiness,
        handle_get_asset_risk,
        handle_get_maintenance_plan,
        DEFAULT_AVAILABLE_CREWS,
        DEFAULT_PARTS_INVENTORY,
    )
    _BACKEND_OK = True
    _BACKEND_ERR = ""
except Exception as _e:
    _BACKEND_OK = False
    _BACKEND_ERR = str(_e)
    
    handle_get_fleet_readiness = None
    handle_get_asset_risk = None
    handle_get_maintenance_plan = None
    DEFAULT_AVAILABLE_CREWS = 0
    DEFAULT_PARTS_INVENTORY = {}

def check_backend():
    if not _BACKEND_OK:
        st.error(f"❌ Could not load backend: {_BACKEND_ERR}")
        st.info("Ensure you run this from the project root: `streamlit run streamlit_app.py`")
        st.stop()

def get_active_sensor_file():
    """Retrieve the path to the active sensor dataset (uploaded by admin) or fallback to default."""
    return st.session_state.get("active_sensor_file", os.path.join(_DATA_DIR, "sensor_data.csv"))

def clear_backend_cache():
    """Clear all @st.cache_data to force the app to read from the newly imported dataset."""
    st.cache_data.clear()

@st.cache_data(ttl=3600)
def load_fleet_readiness(sensor_file_path=None):
    if sensor_file_path is None:
        sensor_file_path = get_active_sensor_file()
    result = handle_get_fleet_readiness(sensor_file=sensor_file_path)
    if result.get("status") != "success":
        raise RuntimeError(result.get("message", "Unknown error from get_fleet_readiness"))
    return result

@st.cache_data(ttl=3600)
def load_all_risks(sensor_file_path=None):
    if sensor_file_path is None:
        sensor_file_path = get_active_sensor_file()
    result = handle_get_asset_risk(sensor_file=sensor_file_path)
    if result.get("status") != "success":
        raise RuntimeError(result.get("message", "Unknown error from get_asset_risk"))
    return result["ranked_risk_list"]

@st.cache_data(ttl=3600)
def load_sensor_data(sensor_file_path=None):
    if sensor_file_path is None:
        sensor_file_path = get_active_sensor_file()
    return pd.read_csv(sensor_file_path)

@st.cache_data(ttl=3600)
def load_service_history():
    path = os.path.join(_DATA_DIR, "service_history.csv")
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        return df.sort_values("date", ascending=False)
    return df

def get_asset_detail(asset_id: str, sensor_file_path=None):
    if sensor_file_path is None:
        sensor_file_path = get_active_sensor_file()
    result = handle_get_asset_risk(asset_id=asset_id, sensor_file=sensor_file_path)
    if result.get("status") != "success":
        raise RuntimeError(result.get("message", f"Asset '{asset_id}' not found"))
    return result

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
