"""
failure_predictor.py
--------------------
Predicts at-risk subsystem components and calculates quantifiable risk scores (0-100)
for military aircraft assets prior to mission deployment.

Design Philosophy:
Why Rule-Based Scoring over Black-Box ML?
In defense, aerospace, and HUMS (Health and Usage Monitoring Systems) mission planning,
explainability and safety-critical auditability are paramount. Flight engineers and commanders
must know exactly WHY an asset is flagged (e.g., specific sensor deviations, repeat subsystem
failures, and cumulative fatigue cycles) rather than trusting an opaque neural network output.
"""

import sys
import os
import pandas as pd
import numpy as np

# Ensure the pipeline directory is on the path for local sibling imports
_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
if _PIPELINE_DIR not in sys.path:
    sys.path.insert(0, _PIPELINE_DIR)

from readiness_classifier import classify_readiness, load_datasets

# =====================================================================
# RISK SCORING WEIGHTS & THRESHOLDS (Easily Tunable Constants)
# =====================================================================
WEIGHT_SENSOR = 50.0         # Max points from active sensor threshold breaches
WEIGHT_HISTORY = 30.0        # Max points from past component repair/issue frequency
WEIGHT_USAGE = 20.0          # Max points from cumulative flight usage wear

MAX_EXPECTED_CYCLES = 4500.0 # Baseline maximum airframe cycles for normalization

# Sensor thresholds (aligned with readiness_classifier)
THRESH_VIBRATION = 9.0       # mm/s
THRESH_ENGINE_TEMP = 600.0   # °C
THRESH_OIL_QUALITY = 50.0    # Index out of 100
THRESH_INSPECTION_DAYS = 150 # Days

COMPONENTS = ["engine", "hydraulics", "fuel_system", "landing_gear", "avionics"]


def get_component_history_stats(asset_id, service_df):
    """
    Analyzes historical service records for an asset.
    Returns:
        history_counts (dict): Number of past incidents per component.
        latest_event_by_comp (dict): Details of the most recent event per component.
    """
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
    """
    Computes a risk score (0-100) and rationale for a specific subsystem component.
    """
    vib = sensor_row["vibration_level"]
    temp = sensor_row["engine_temp_c"]
    oil = sensor_row["oil_quality_index"]
    cycles = sensor_row["usage_cycles"]
    insp_days = sensor_row["last_inspection_days_ago"]

    # 1. Base Usage Wear (0 to 20 points)
    usage_score = min(20.0, (cycles / MAX_EXPECTED_CYCLES) * WEIGHT_USAGE)
    
    # 2. Historical Maintenance Penalty (0 to 30 points)
    if history_count == 0:
        history_score = 0.0
    elif history_count == 1:
        history_score = 15.0
    elif history_count == 2:
        history_score = 24.0
    else:
        history_score = 30.0

    # 3. Component-Specific Sensor Penalties (0 to 50 points)
    sensor_score = 0.0
    sensor_notes = []

    if component == "engine":
        if vib > THRESH_VIBRATION:
            pct_over = ((vib - THRESH_VIBRATION) / THRESH_VIBRATION) * 100
            score_add = min(30.0, 15.0 + (pct_over * 0.35))
            sensor_score += score_add
            sensor_notes.append(f"vibration {vib} mm/s (+{pct_over:.0f}% over limit)")

        if temp > THRESH_ENGINE_TEMP:
            pct_over = ((temp - THRESH_ENGINE_TEMP) / THRESH_ENGINE_TEMP) * 100
            score_add = min(30.0, 15.0 + (pct_over * 1.5))
            sensor_score += score_add
            sensor_notes.append(f"engine temp {temp}°C (+{pct_over:.0f}% over limit)")

        if oil < THRESH_OIL_QUALITY:
            pct_under = ((THRESH_OIL_QUALITY - oil) / THRESH_OIL_QUALITY) * 100
            score_add = min(20.0, 10.0 + (pct_under * 0.2))
            sensor_score += score_add
            sensor_notes.append(f"oil quality {oil}/100 (-{pct_under:.0f}% degraded)")

    elif component == "hydraulics":
        if oil < THRESH_OIL_QUALITY:
            pct_under = ((THRESH_OIL_QUALITY - oil) / THRESH_OIL_QUALITY) * 100
            score_add = min(35.0, 15.0 + (pct_under * 0.4))
            sensor_score += score_add
            sensor_notes.append(f"hydraulic fluid/oil index {oil}/100 degraded")
            
    elif component == "fuel_system":
        if temp > THRESH_ENGINE_TEMP:
            sensor_score += 20.0
            sensor_notes.append(f"high thermal load ({temp}°C) stressing fuel metering valves")

    elif component in ["landing_gear", "avionics"]:
        if insp_days > THRESH_INSPECTION_DAYS:
            sensor_score += 25.0
            sensor_notes.append(f"overdue inspection ({insp_days} days ago)")

    sensor_score = min(WEIGHT_SENSOR, sensor_score)
    total_risk = min(100.0, sensor_score + history_score + usage_score)

    reasons = []
    if sensor_notes:
        reasons.append(", ".join(sensor_notes))
    if history_count > 0 and latest_event:
        reasons.append(f"{history_count} prior repair/event(s) [Latest: {latest_event}]")
    reasons.append(f"{cycles} usage cycles ({usage_score:.1f}/20 wear pts)")

    rationale = f"{component.upper()} risk ({total_risk:.1f}/100): " + "; ".join(reasons)

    return round(total_risk, 1), rationale


def evaluate_asset_failures(asset_id, sensor_row, service_df):
    """
    Evaluates all 5 subsystems for an asset and returns the highest-risk component.
    """
    history_counts, latest_events = get_component_history_stats(asset_id, service_df)

    highest_score = -1.0
    top_component = "engine"
    top_rationale = ""

    for comp in COMPONENTS:
        score, rationale = calculate_component_risk(
            component=comp,
            sensor_row=sensor_row,
            history_count=history_counts[comp],
            latest_event=latest_events[comp]
        )
        if score > highest_score:
            highest_score = score
            top_component = comp
            top_rationale = rationale

    return top_component, highest_score, top_rationale


def predict_failures(sensor_file=None, service_file=None):
    """
    Main prediction pipeline. Returns DataFrame sorted by risk_score descending.
    """
    base_readiness_df = classify_readiness(sensor_file, service_file)
    sensor_df, service_df = load_datasets(sensor_file, service_file)

    predictions = []
    for _, readiness_row in base_readiness_df.iterrows():
        asset_id = readiness_row["asset_id"]
        is_ready = readiness_row["is_ready"]
        readiness_exp = readiness_row["explanation"]

        sensor_match = sensor_df[sensor_df["asset_id"] == asset_id].iloc[0]

        top_component, risk_score, rationale = evaluate_asset_failures(
            asset_id=asset_id,
            sensor_row=sensor_match,
            service_df=service_df
        )

        predictions.append({
            "asset_id": asset_id,
            "is_ready": is_ready,
            "predicted_component_at_risk": top_component,
            "risk_score": risk_score,
            "reason": rationale,
            "readiness_explanation": readiness_exp
        })

    results_df = pd.DataFrame(predictions)
    return results_df.sort_values(by="risk_score", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    print("=" * 100)
    print("MILITARY ASSET PREDICTIVE FAILURE & SUBSYSTEM RISK REPORT")
    print("=" * 100)

    report_df = predict_failures()

    print(f"\n{'ASSET ID':<10} | {'STATUS':<11} | {'AT-RISK COMPONENT':<18} | {'RISK SCORE':<10} | {'PRIMARY DIAGNOSTIC REASON'}")
    print("-" * 100)

    for _, row in report_df.iterrows():
        status_str = "READY" if row["is_ready"] else "NON-READY"
        print(f"{row['asset_id']:<10} | {status_str:<11} | {row['predicted_component_at_risk']:<18} | {row['risk_score']:<10.1f} | {row['reason']}")

    print("=" * 100)
