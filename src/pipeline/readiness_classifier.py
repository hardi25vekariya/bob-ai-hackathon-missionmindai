"""
readiness_classifier.py
-----------------------
Evaluates the mission readiness of military aircraft assets using a Behavior-Based 
Anomaly Detection Machine Learning model. 

Flags non-ready aircraft when their behavioral cancellation probability exceeds 
a safe threshold, providing plain-language diagnostic explanations.
"""

import pandas as pd
import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

from behavioral_anomaly import calculate_cancellation_probabilities

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "data"))
DEFAULT_SENSOR_FILE = os.path.join(DEFAULT_DATA_DIR, "sensor_data.csv")
DEFAULT_SERVICE_FILE = os.path.join(DEFAULT_DATA_DIR, "service_history.csv")

if not os.path.exists(DEFAULT_SENSOR_FILE) and os.path.exists("src/data/sensor_data.csv"):
    DEFAULT_SENSOR_FILE = "src/data/sensor_data.csv"
if not os.path.exists(DEFAULT_SERVICE_FILE) and os.path.exists("src/data/service_history.csv"):
    DEFAULT_SERVICE_FILE = "src/data/service_history.csv"

# =====================================================================
# READINESS THRESHOLD
# =====================================================================
CANCELLATION_PROBABILITY_THRESHOLD = 65.0  # %


def load_datasets(sensor_file=None, service_file=None):
    if sensor_file is None:
        sensor_file = DEFAULT_SENSOR_FILE
    if service_file is None:
        service_file = DEFAULT_SERVICE_FILE

    if not os.path.exists(sensor_file):
        raise FileNotFoundError(f"Sensor data file not found: {sensor_file}")
    if not os.path.exists(service_file):
        raise FileNotFoundError(f"Service history file not found: {service_file}")

    sensor_df = pd.read_csv(sensor_file)
    service_df = pd.read_csv(service_file)

    service_df["date"] = pd.to_datetime(service_df["date"])
    service_df = service_df.sort_values(by="date", ascending=False)
    
    # Process behavioral anomaly AI scoring
    sensor_df = calculate_cancellation_probabilities(sensor_df)

    return sensor_df, service_df


def get_latest_service_record(asset_id, service_df):
    asset_history = service_df[service_df["asset_id"] == asset_id]
    if asset_history.empty:
        return "No prior service records on file."
    latest_event = asset_history.iloc[0]
    date_str = latest_event["date"].strftime("%Y-%m-%d")
    component = latest_event["component"]
    action = latest_event["action_taken"]
    issue = latest_event["issue_found"]
    return f"Last service: {component} {action} on {date_str} (Issue: '{issue}')"


def evaluate_asset(row, service_df):
    asset_id = row["asset_id"]
    prob = row.get("cancellation_probability", 0.0)

    # We determine readiness based on the behavioral ML output
    if prob < CANCELLATION_PROBABILITY_THRESHOLD:
        is_ready = True
        explanation = f"READY: Low cancellation probability ({prob:.1f}%). Behavior is within normal fleet patterns."
    else:
        is_ready = False
        latest_service_note = get_latest_service_record(asset_id, service_df)
        
        # Add contextual explanations based on the anomaly features present
        reasons = []
        if row.get("vibration_7d_trend", 0) > 1.0:
            reasons.append("rapid vibration trend")
        if row.get("temp_volatility", 0) > 15.0:
            reasons.append("severe temperature volatility")
        if row.get("oil_degradation_rate", 0) > 2.0:
            reasons.append("accelerated oil degradation")
        if row.get("past_cancellations", 0) > 0:
            reasons.append("pattern of past cancellations")
            
        reason_str = " (" + ", ".join(reasons) + ")" if reasons else ""
        explanation = f"NON-READY: High cancellation probability ({prob:.1f}%){reason_str}. [{latest_service_note}]"

    return is_ready, explanation


def classify_readiness(sensor_file=None, service_file=None):
    sensor_df, service_df = load_datasets(sensor_file, service_file)
    results = []
    for _, row in sensor_df.iterrows():
        is_ready, explanation = evaluate_asset(row, service_df)
        results.append({
            "asset_id": row["asset_id"],
            "is_ready": is_ready,
            "explanation": explanation
        })
    return pd.DataFrame(results)

if __name__ == "__main__":
    report = classify_readiness()
    for _, row in report.iterrows():
        print(row["asset_id"], "READY" if row["is_ready"] else "NON-READY", row["explanation"])
