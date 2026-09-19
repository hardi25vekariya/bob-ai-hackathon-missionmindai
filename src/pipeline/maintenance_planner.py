"""
maintenance_planner.py
----------------------
Generates an operational maintenance triage and action plan for non-ready military assets.

Design Philosophy:
Why Greedy Prioritization by Risk Score?
In high-tempo military and defense aviation operations, maintenance resources (certified technician
crews and mission-critical spare parts) are strictly limited. Rather than servicing jets on a
first-come-first-served or random basis, this module prioritizes aircraft with the highest failure
risk scores and cumulative airframe fatigue, maximizing operational fleet readiness and safety.
"""

import sys
import os
import pandas as pd
import copy

# Ensure the pipeline directory is on the path for local sibling imports
_PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
if _PIPELINE_DIR not in sys.path:
    sys.path.insert(0, _PIPELINE_DIR)

from readiness_classifier import load_datasets
from failure_predictor import predict_failures

# =====================================================================
# DEFAULT RESOURCE CONSTRAINTS (Adjustable for Scenarios)
# =====================================================================
DEFAULT_AVAILABLE_CREWS = 3

DEFAULT_PARTS_INVENTORY = {
    "engine": 2,
    "landing_gear": 1,
    "avionics": 3,
    "hydraulics": 2,
    "fuel_system": 2
}


def generate_maintenance_plan(
    available_crews=DEFAULT_AVAILABLE_CREWS,
    available_parts=None,
    sensor_file=None,
    service_file=None
):
    """
    Constructs a constrained, prioritized maintenance work order schedule.

    Parameters:
        available_crews (int): Number of maintenance teams on duty.
        available_parts (dict): Count of spare replacement parts per component.
        sensor_file (str): Path to sensor telemetry CSV.
        service_file (str): Path to maintenance logs CSV.

    Returns:
        summary_text (str): Executive summary of the maintenance plan.
        plan_df (pandas.DataFrame): Ranked schedule with priority, status, and rationale.
    """
    # 1. Use default parts inventory if not provided
    if available_parts is None:
        parts_stock = copy.deepcopy(DEFAULT_PARTS_INVENTORY)
    else:
        parts_stock = copy.deepcopy(available_parts)

    crews_remaining = available_crews

    # 2. Get predictions from failure_predictor.py
    failure_df = predict_failures(sensor_file, service_file)

    # 3. Load sensor telemetry to merge usage_cycles for secondary tiebreaking
    sensor_df, _ = load_datasets(sensor_file, service_file)
    merged_df = failure_df.merge(
        sensor_df[["asset_id", "usage_cycles"]],
        on="asset_id",
        how="left"
    )

    # 4. Filter strictly to non-ready aircraft
    non_ready_df = merged_df[merged_df["is_ready"] == False].copy()

    if non_ready_df.empty:
        summary = "All fleet assets are mission ready. No maintenance required."
        empty_plan = pd.DataFrame(columns=[
            "priority_rank", "asset_id", "predicted_component_at_risk",
            "risk_score", "status", "reason"
        ])
        return summary, empty_plan

    # 5. Priority Sorting:
    # Primary: risk_score (descending - highest risk first)
    # Tiebreaker: usage_cycles (descending - older airframe wear first)
    ranked_df = non_ready_df.sort_values(
        by=["risk_score", "usage_cycles"],
        ascending=[False, False]
    ).reset_index(drop=True)

    # 6. Greedy Allocation of Crews and Spare Parts
    plan_records = []
    scheduled_count = 0
    queued_count = 0

    for idx, row in ranked_df.iterrows():
        rank = idx + 1
        asset_id = row["asset_id"]
        comp = row["predicted_component_at_risk"]
        score = row["risk_score"]
        diagnostic_reason = row["reason"]

        parts_available_for_comp = parts_stock.get(comp, 0)

        # Check resource availability
        can_schedule = (crews_remaining > 0) and (parts_available_for_comp > 0)

        if can_schedule:
            # Allocate resources
            crews_remaining -= 1
            parts_stock[comp] -= 1
            scheduled_count += 1

            status = "scheduled"
            assignment_note = (
                f"SCHEDULED: Crew assigned; 1x {comp} spare allocated (Stock remaining: {parts_stock[comp]}). "
                f"Triage diagnosis: {diagnostic_reason}"
            )
        else:
            queued_count += 1
            status = "queued"

            # Explain specific bottleneck
            bottlenecks = []
            if crews_remaining <= 0:
                bottlenecks.append("all maintenance crews allocated")
            if parts_available_for_comp <= 0:
                bottlenecks.append(f"no spare {comp} parts available in stock")

            bottleneck_str = " & ".join(bottlenecks)
            assignment_note = (
                f"QUEUED: Deferred due to {bottleneck_str}. "
                f"Triage diagnosis: {diagnostic_reason}"
            )

        plan_records.append({
            "priority_rank": rank,
            "asset_id": asset_id,
            "predicted_component_at_risk": comp,
            "risk_score": score,
            "status": status,
            "reason": assignment_note
        })

    plan_df = pd.DataFrame(plan_records)

    # 7. Generate Plain-Language Executive Summary
    total_non_ready = len(ranked_df)
    summary_text = (
        f"{total_non_ready} assets require maintenance. "
        f"{scheduled_count} scheduled immediately with available crews & spare parts. "
        f"{queued_count} queued pending crew/parts availability "
        f"(Remaining Crews: {crews_remaining}, Spare Stock: {parts_stock})."
    )

    return summary_text, plan_df


if __name__ == "__main__":
    print("=" * 105)
    print("MILITARY ASSET OPTIMIZED MAINTENANCE ACTION PLAN")
    print("=" * 105)

    test_crews = 3
    test_parts = {
        "engine": 2,
        "landing_gear": 1,
        "avionics": 3,
        "hydraulics": 2,
        "fuel_system": 2
    }

    print(f"\nInitial Resource Constraints:")
    print(f"  Available Crews : {test_crews}")
    print(f"  Spare Parts     : {test_parts}\n")

    summary, action_plan = generate_maintenance_plan(
        available_crews=test_crews,
        available_parts=test_parts
    )

    print("EXECUTIVE SUMMARY:")
    print(f"  -> {summary}\n")

    print("-" * 105)
    print(f"{'RANK':<5} | {'ASSET ID':<10} | {'COMPONENT':<14} | {'RISK':<6} | {'STATUS':<11} | {'ACTION / BOTTLENECK DETAILS'}")
    print("-" * 105)

    for _, row in action_plan.iterrows():
        status_badge = "[SCHEDULED]" if row["status"] == "scheduled" else "[QUEUED]   "
        print(f"{row['priority_rank']:<5} | {row['asset_id']:<10} | {row['predicted_component_at_risk']:<14} | {row['risk_score']:<6.1f} | {status_badge:<11} | {row['reason']}")

    print("=" * 105)
