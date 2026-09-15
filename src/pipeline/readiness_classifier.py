"""
readiness_classifier.py
-----------------------
Evaluates the mission readiness of military aircraft assets by analyzing real-time
telemetry from src/data/sensor_data.csv and historical maintenance records from src/data/service_history.csv.

Flags non-ready aircraft with plain-language diagnostic explanations and references to
their most recent relevant service event.
"""

import pandas as pd
import os

# Resolve default data directory relative to this file
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "data"))
DEFAULT_SENSOR_FILE = os.path.join(DEFAULT_DATA_DIR, "sensor_data.csv")
DEFAULT_SERVICE_FILE = os.path.join(DEFAULT_DATA_DIR, "service_history.csv")

# Fallback paths for root execution
if not os.path.exists(DEFAULT_SENSOR_FILE) and os.path.exists("src/data/sensor_data.csv"):
    DEFAULT_SENSOR_FILE = "src/data/sensor_data.csv"
if not os.path.exists(DEFAULT_SERVICE_FILE) and os.path.exists("src/data/service_history.csv"):
    DEFAULT_SERVICE_FILE = "src/data/service_history.csv"

# =====================================================================
# READINESS THRESHOLDS (Operational Safety Limits)
# =====================================================================
MAX_VIBRATION = 9.0        # Vibration level above 9.0 mm/s indicates mechanical stress
MAX_ENGINE_TEMP = 600.0    # Engine temperature above 600°C indicates thermal overheating
MIN_OIL_QUALITY = 50       # Oil quality index below 50 indicates lubricant degradation
MAX_INSPECTION_DAYS = 150  # Overdue for inspection if last inspection was > 150 days ago


def load_datasets(sensor_file=None, service_file=None):
    """
    Loads sensor and service history CSV files into pandas DataFrames.
    Ensures dates in service history are sorted chronologically.
    """
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

    # Convert date column to datetime for proper sorting (most recent first)
    service_df["date"] = pd.to_datetime(service_df["date"])
    service_df = service_df.sort_values(by="date", ascending=False)

    return sensor_df, service_df


def get_latest_service_record(asset_id, service_df):
    """
    Finds the most recent maintenance event for a given asset.
    Returns a formatted string or fallback message if no record exists.
    """
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
    """
    Checks an individual asset's sensor telemetry against threshold limits.
    Returns:
        is_ready (bool): True if all checks pass, False otherwise.
        explanation (str): Human-readable diagnosis.
    """
    asset_id = row["asset_id"]
    vibration = row["vibration_level"]
    temp = row["engine_temp_c"]
    oil_quality = row["oil_quality_index"]
    inspection_days = row["last_inspection_days_ago"]

    issues = []

    if vibration > MAX_VIBRATION:
        issues.append(f"Vibration level {vibration} mm/s exceeds {MAX_VIBRATION} mm/s threshold")

    if temp > MAX_ENGINE_TEMP:
        issues.append(f"Engine temp {temp}°C exceeds {MAX_ENGINE_TEMP}°C threshold")

    if oil_quality < MIN_OIL_QUALITY:
        issues.append(f"Oil quality index {oil_quality} is below {MIN_OIL_QUALITY} minimum")

    if inspection_days > MAX_INSPECTION_DAYS:
        issues.append(f"Inspection overdue ({inspection_days} days ago, exceeds {MAX_INSPECTION_DAYS}-day limit)")

    # Determine readiness status
    if len(issues) == 0:
        is_ready = True
        explanation = "READY: All sensor metrics within operational limits and scheduled inspection is current."
    else:
        is_ready = False
        latest_service_note = get_latest_service_record(asset_id, service_df)
        joined_issues = "; ".join(issues)
        explanation = f"NON-READY: {joined_issues}. [{latest_service_note}]"

    return is_ready, explanation


def classify_readiness(sensor_file=None, service_file=None):
    """
    Main function to process the fleet dataset and generate readiness classifications.
    Returns a pandas DataFrame with columns: asset_id, is_ready, explanation.
    """
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
    print("=" * 80)
    print("MILITARY ASSET MISSION-READINESS CLASSIFICATION REPORT")
    print("=" * 80)

    readiness_report = classify_readiness()

    total_assets = len(readiness_report)
    ready_count = readiness_report["is_ready"].sum()
    non_ready_count = total_assets - ready_count
    readiness_rate = (ready_count / total_assets) * 100

    print(f"\nTotal Fleet Assets : {total_assets}")
    print(f"Mission Ready      : {ready_count} ({readiness_rate:.1f}%)")
    print(f"Grounded/Non-Ready : {non_ready_count} ({100 - readiness_rate:.1f}%)\n")

    print("-" * 80)
    print("DETAILED ASSET BREAKDOWN:")
    print("-" * 80)

    for _, row in readiness_report.iterrows():
        status_tag = "[READY]    " if row["is_ready"] else "[NON-READY]"
        print(f"{status_tag} {row['asset_id']}: {row['explanation']}")

    print("=" * 80)
