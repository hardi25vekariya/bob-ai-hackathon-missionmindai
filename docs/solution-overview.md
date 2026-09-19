# Solution Overview: AeroGuard-Bob Architecture & Decision Logic

## 1. Core Engineering Mechanism: Explainable Scoring over Black-Box ML

A deliberate architectural decision in **AeroGuard-Bob** is the use of **transparent, rule-based physical heuristics** rather than opaque, black-box deep learning models.

### Why Explainability is a Requirement in Military Aviation
In commercial consumer tech, a 95% neural network confidence score is acceptable. In military aviation and defense sustainment, it is **unacceptable**:
- A flight safety officer cannot ground an F-series fighter jet or clear it for combat solely because a neural network outputted `0.87`.
- Maintenance crews require actionable physical diagnostic targets: *Which bearing? What vibration frequency? Which temperature threshold was breached? What was the last recorded repair date?*
- Regulatory airworthiness standards (e.g. MIL-STD-1553, FAA Airworthiness Directives) mandate complete audit trails for every red-flagged flight system.

### How the Risk Scoring Mechanism Works
The failure prediction engine calculates a 0–100 risk score per aircraft subsystem:

$$\text{Total Risk Score} = \min\Big(100,\; \text{Sensor Penalty} + \text{History Penalty} + \text{Usage Wear Penalty}\Big)$$

1. **Sensor Penalty ($\le 50$ pts)**: Measures the percentage deviation beyond critical engineering thresholds:
   - Vibration Level ($> 9.0\text{ mm/s}$ limit): Indicates rotor unbalance, shaft bearing spalling, or acoustic flutter.
   - Engine Temperature ($> 600.0^\circ\text{C}$ limit): Indicates combustor hot streaks, cooling duct blockage, or thermal barrier degradation.
   - Oil Quality Index ($< 50$ index): Indicates particulate debris detected by magnetic chip plugs, fluid thermal breakdown, or carbon seal leakage.
2. **History Penalty ($\le 30$ pts)**: Evaluates subsystem failure recurrence. Repeat repairs on the same component compound the risk score.
3. **Usage Fatigue Penalty ($\le 20$ pts)**: Evaluates cumulative airframe flight cycles ($\text{usage\_cycles} / 4500$) as an airframe fatigue baseline.
4. **Inspection Timeliness**: Penalizes assets exceeding the 150-day inspection limit even when live sensors show nominal values.

---

## 2. Why AeroGuard-Bob is Not Just a Static Dashboard

| Capability | Traditional Fleet Dashboards | AeroGuard-Bob with IBM Bob & MCP |
| :--- | :--- | :--- |
| **Interface** | Complex, multi-tab static charts requiring manual inspection. | Natural language dialogue grounded in real backend data via MCP tools. |
| **Telemetry Context** | Displays isolated numbers without historical maintenance linkage. | Automatically cross-references telemetry with 2-year service logs. |
| **Maintenance Triage** | Lists all broken aircraft without factoring in flight-line resource limits. | Greedily schedules repairs against live crew capacity and spare parts inventory. |
| **Decision Support** | Commander must guess why an asset is non-ready. | Provides plain-language explanations with exact sensor breach percentages. |
| **LLM Reliability** | Prone to LLM hallucinations when fed raw unstructured text. | 100% data-grounded via structured JSON MCP tool calling. |

---

## 3. End-to-End User Experience with IBM Bob

When a commander or maintenance lead interacts with IBM Bob, queries are dynamically dispatched to the appropriate MCP tool:

### Scenario A: Fleet-Level Readiness Briefing
- **User Query**: *"Bob, what is our current squadron readiness status for tomorrow morning's mission?"*
- **Bob Tool Call**: `get_fleet_readiness()`
- **Structured Response**:
  > *"Commander, current squadron readiness is **36.0%** (9 of 25 aircraft mission-ready). 16 aircraft are currently grounded. Key concerns include 6 aircraft with elevated turbine vibration levels, 5 with thermal overheating, and 3 assets (Tail-105, Tail-110, Tail-120) that have exceeded their 150-day mandatory inspection deadline."*

### Scenario B: Deep Diagnostic Investigation
- **User Query**: *"Why is Tail-108 red-flagged? Give me the diagnostic breakdown."*
- **Bob Tool Call**: `get_asset_risk(asset_id="Tail-108")`
- **Structured Response**:
  > *"Tail-108 has the highest failure risk in the fleet with a **Risk Score of 98.0/100 (Engine subsystem)**.  
  > **Sensor Telemetry**: Vibration is at 11.41 mm/s (27% over the 9.0 mm/s limit) and Engine Temp is 673.9°C (12% over the 600°C limit).  
  > **Maintenance History**: 3 prior engine events, most recently a compressor rear bearing cage repair on June 17, 2026.  
  > **Airframe Fatigue**: 4,052 cumulative flight cycles."*

### Scenario C: Resource-Constrained Maintenance Triage
- **User Query**: *"We only have 2 maintenance crews and 1 engine spare part available today. What should we fix first?"*
- **Bob Tool Call**: `get_maintenance_plan(available_crews=2, available_parts_per_component={"engine": 1, ...})`
- **Structured Response**:
  > *"With 2 crews and 1 engine spare:  
  > 1. **Tail-108 (Engine, Risk 98.0)**: **SCHEDULED** (Allocated Crew #1 + 1x Engine spare part).  
  > 2. **Tail-110 (Avionics, Risk 56.3)**: **SCHEDULED** (Allocated Crew #2 + 1x Avionics spare part).  
  > *(Note: Tail-112 and Tail-121 have higher risk but require engine spares which are now exhausted. Crew #2 was efficiently dispatched to Tail-110 to avoid idle technician time.)*  
  > 14 remaining aircraft are **QUEUED** pending spare parts replenishment and crew availability."*
