"""
failure_predictor.py
--------------------
Predicts at-risk subsystem components and calculates quantifiable risk scores (0-100)
for military aircraft assets prior to mission deployment.

Now uses Behavior-Based AI Cancellation Probabilities.
"""

import sys
import os
import pandas as pd
import numpy as np

_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
if _PIPELINE_DIR not in sys.path:
    sys.path.insert(0, _PIPELINE_DIR)

from readiness_classifier import classify_readiness, load_datasets

MAX_EXPECTED_CYCLES = 4500.0

# Base Thresholds for determining WHICH component is at risk
THRESH_VIBRATION = 9.0       
THRESH_ENGINE_TEMP = 600.0   
THRESH_OIL_QUALITY = 50.0    
THRESH_INSPECTION_DAYS = 150 

COMPONENTS = ["engine", "hydraulics", "fuel_system", "landing_gear", "avionics"]

def get_component_history_stats(asset_id, service_df):
    asset_history = service_df[service_df["asset_id"] == asset_id]
    history_counts = {comp: 0 for comp in COMPONENTS}
    latest_event_by_comp = {comp: None for comp in COMPONENTS}
    for _, row in asset_history.iterrows():
        comp = row["component"]
        if comp in history_counts:
            history_counts[comp] += 1
            if latest_event_by_comp[comp] is None:
                date_str = row["date"].strftime("%Y-%m-%d")
                latest_event_by_comp[comp] = f"{row['action_taken']} on {date_str} ('{row['issue_found']}')"
    return history_counts, latest_event_by_comp


def calculate_component_risk(component, sensor_row, history_count, latest_event):
    vib = sensor_row["vibration_level"]
    temp = sensor_row["engine_temp_c"]
    oil = sensor_row["oil_quality_index"]
    cycles = sensor_row["usage_cycles"]
    insp_days = sensor_row["last_inspection_days_ago"]
    
    # Base Behavioral Risk
    prob = sensor_row.get("cancellation_probability", 0.0)

    sensor_score = 0.0
    sensor_notes = []

    if component == "engine":
        if vib > THRESH_VIBRATION or sensor_row.get("vibration_7d_trend", 0) > 1.0:
            sensor_score += 40.0
            sensor_notes.append(f"anomalous vibration behavior")
        if temp > THRESH_ENGINE_TEMP or sensor_row.get("temp_volatility", 0) > 15.0:
            sensor_score += 40.0
            sensor_notes.append(f"anomalous temperature behavior")
        if oil < THRESH_OIL_QUALITY:
            sensor_score += 20.0
            sensor_notes.append(f"degraded oil")
    elif component == "hydraulics":
        if oil < THRESH_OIL_QUALITY or sensor_row.get("oil_degradation_rate", 0) > 2.0:
            sensor_score += 50.0
            sensor_notes.append(f"rapid hydraulic oil degradation")
    elif component == "fuel_system":
        if temp > THRESH_ENGINE_TEMP or sensor_row.get("temp_volatility", 0) > 15.0:
            sensor_score += 30.0
            sensor_notes.append(f"thermal load stressing fuel system")
    elif component in ["landing_gear", "avionics"]:
        if insp_days > THRESH_INSPECTION_DAYS:
            sensor_score += 40.0
            sensor_notes.append(f"overdue inspection")

    # Final Component Risk is heavily weighted by the overall AI cancellation probability
    # If the AI thinks the asset is bad, all component risks are elevated, but the one with
    # the highest sensor score takes the primary blame.
    base_prob = max(prob, 10.0)
    
    history_score = min(20.0, history_count * 10.0)
    usage_score = min(10.0, (cycles / MAX_EXPECTED_CYCLES) * 10.0)
    
    # 60% Behavior Probability, 20% Component Sensor, 20% History/Usage
    total_risk = (base_prob * 0.60) + (sensor_score * 0.20) + history_score + usage_score
    total_risk = min(100.0, total_risk)

    reasons = []
    if sensor_notes:
        reasons.append(", ".join(sensor_notes))
    if history_count > 0 and latest_event:
        reasons.append(f"{history_count} prior repair/event(s) [Latest: {latest_event}]")
    if prob > 65.0:
        reasons.append(f"Behavioral Anomaly AI Flag (Prob: {prob:.1f}%)")

    rationale = f"{component.upper()} risk ({total_risk:.1f}/100): " + "; ".join(reasons)
    return round(total_risk, 1), rationale


def evaluate_asset_failures(asset_id, sensor_row, service_df):
    history_counts, latest_events = get_component_history_stats(asset_id, service_df)
    highest_score = -1.0
    top_component = "engine"
    top_rationale = ""
    for comp in COMPONENTS:
        score, rationale = calculate_component_risk(
            component=comp, sensor_row=sensor_row,
            history_count=history_counts[comp], latest_event=latest_events[comp]
        )
        if score > highest_score:
            highest_score = score
            top_component = comp
            top_rationale = rationale
    
    # Return all subsystem risks too so the UI can plot them
    subsystem_risks = {}
    for comp in COMPONENTS:
        score, _ = calculate_component_risk(
            component=comp, sensor_row=sensor_row,
            history_count=history_counts[comp], latest_event=latest_events[comp]
        )
        subsystem_risks[comp] = score

    return top_component, highest_score, top_rationale, subsystem_risks


def predict_failures(sensor_file=None, service_file=None):
    base_readiness_df = classify_readiness(sensor_file, service_file)
    sensor_df, service_df = load_datasets(sensor_file, service_file)

    predictions = []
    for _, readiness_row in base_readiness_df.iterrows():
        asset_id = readiness_row["asset_id"]
        is_ready = readiness_row["is_ready"]
        readiness_exp = readiness_row["explanation"]

        sensor_match = sensor_df[sensor_df["asset_id"] == asset_id].iloc[0]

        top_component, risk_score, rationale, subsystem_risks = evaluate_asset_failures(
            asset_id=asset_id, sensor_row=sensor_match, service_df=service_df
        )

        predictions.append({
            "asset_id": asset_id,
            "is_ready": is_ready,
            "predicted_component_at_risk": top_component,
            "risk_score": risk_score,
            "reason": rationale,
            "readiness_explanation": readiness_exp,
            "subsystem_risks": subsystem_risks,
            "cancellation_probability": sensor_match.get("cancellation_probability", 0.0)
        })

    results_df = pd.DataFrame(predictions)
    return results_df.sort_values(by="risk_score", ascending=False).reset_index(drop=True)
