# Setup & Execution Guide: AeroGuard-Bob

This guide provides step-by-step instructions for running, verifying, and connecting the AeroGuard-Bob mission readiness pipeline to IBM Bob within the restructured `src/` directory layout.

---

## 1. Prerequisites

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.9 or higher (tested on Python 3.10.11)
- **Python Libraries**: `pandas`, `numpy` (and standard library modules `sys`, `json`, `os`, `datetime`)
- **IBM Bob**: Installed locally or accessible via web environment with MCP support (`bob.ibm.com`)

---

## 2. Environment Setup

Open your terminal or PowerShell console in the project root directory:

```bash
# 1. Verify Python installation
python --version

# 2. Install required dependencies
pip install pandas numpy
```

---

## 3. Step-by-Step Pipeline Execution & Verification

Execute all modules from the project root directory using their paths inside `src/`:

### Step 3.1: (Optional) Dataset Generation
```bash
python src/data/generate_dataset.py
```
- **What it does**: Generates `src/data/sensor_data.csv` (25 aircraft) and `src/data/service_history.csv` (74 maintenance records).
- **Verification Output**:
  ```text
  Generated src/data/sensor_data.csv: 25 rows
  Generated src/data/service_history.csv: 74 rows
  ```

---

### Step 3.2: Mission Readiness Classification
```bash
python src/pipeline/readiness_classifier.py
```
- **What it does**: Evaluates operational thresholds (vibration, temp, oil quality, inspection age) and generates grounded explanations.
- **Verification Output**:
  ```text
  ================================================================================
  MILITARY ASSET MISSION-READINESS CLASSIFICATION REPORT
  ================================================================================
  Total Fleet Assets : 25
  Mission Ready      : 9 (36.0%)
  Grounded/Non-Ready : 16 (64.0%)
  --------------------------------------------------------------------------------
  [READY]     Tail-101: READY: All sensor metrics within operational limits...
  [NON-READY] Tail-103: NON-READY: Engine temp 649.1°C exceeds 600.0°C threshold...
  [NON-READY] Tail-105: NON-READY: Inspection overdue (166 days ago, exceeds 150-day limit)...
  [NON-READY] Tail-108: NON-READY: Vibration level 11.41 mm/s exceeds 9.0 mm/s threshold...
  ```

---

### Step 3.3: Subsystem Failure Risk Prediction
```bash
python src/pipeline/failure_predictor.py
```
- **What it does**: Computes 0–100 component failure risk scores and diagnoses at-risk subsystems.
- **Verification Output**:
  ```text
  ====================================================================================================
  MILITARY ASSET PREDICTIVE FAILURE & SUBSYSTEM RISK REPORT
  ====================================================================================================
  ASSET ID   | STATUS      | AT-RISK COMPONENT  | RISK SCORE | PRIMARY DIAGNOSTIC REASON
  ----------------------------------------------------------------------------------------------------
  Tail-108   | NON-READY   | engine             | 98.0       | ENGINE risk (98.0/100): vibration 11.41 mm/s...
  Tail-112   | NON-READY   | engine             | 72.4       | ENGINE risk (72.4/100): vibration 9.67 mm/s...
  Tail-121   | NON-READY   | engine             | 71.4       | ENGINE risk (71.4/100): vibration 13.36 mm/s...
  ...
  Tail-101   | READY       | engine             | 23.6       | ENGINE risk (23.6/100): 1 prior repair...
  ```

---

### Step 3.4: Constrained Maintenance Action Planner
```bash
python src/pipeline/maintenance_planner.py
```
- **What it does**: Dynamically schedules repairs against available crew and spare-parts limits.
- **Verification Output**:
  ```text
  =========================================================================================================
  MILITARY ASSET OPTIMIZED MAINTENANCE ACTION PLAN
  =========================================================================================================
  EXECUTIVE SUMMARY:
    -> 16 assets require maintenance. 3 scheduled immediately with available crews & spare parts. 
       13 queued pending crew/parts availability.
  ---------------------------------------------------------------------------------------------------------
  RANK  | ASSET ID   | COMPONENT      | RISK   | STATUS      | ACTION / BOTTLENECK DETAILS
  1     | Tail-108   | engine         | 98.0   | [SCHEDULED] | SCHEDULED: Crew assigned; 1x engine spare allocated...
  2     | Tail-112   | engine         | 72.4   | [SCHEDULED] | SCHEDULED: Crew assigned; 1x engine spare allocated...
  3     | Tail-121   | engine         | 71.4   | [QUEUED]    | QUEUED: Deferred due to no spare engine parts in stock...
  10    | Tail-110   | avionics       | 56.3   | [SCHEDULED] | SCHEDULED: Crew assigned; 1x avionics spare allocated...
  ```

---

### Step 3.5: MCP Server Testing
1. **Run Standalone Test Suite**:
   ```bash
   python src/mcp/mcp_server.py
   ```
2. **Run Automated JSON-RPC Stdio Protocol Test**:
   ```bash
   python src/mcp/verify_mcp.py
   ```
3. **Run Live Stdio Server Mode for IBM Bob**:
   ```bash
   python src/mcp/mcp_server.py --stdio
   ```

---

## 4. Connecting to IBM Bob via MCP

To register the MCP server with IBM Bob (per `bob.ibm.com/docs`):

1. Open your IBM Bob configuration file (e.g., `mcp_config.json` or Bob Assistant Settings).
2. Add the server entry under `mcpServers`:

```json
{
  "mcpServers": {
    "military-readiness-copilot": {
      "command": "python",
      "args": ["src/mcp/mcp_server.py", "--stdio"],
      "env": {}
    }
  }
}
```

3. Restart IBM Bob. The 3 tools (`get_fleet_readiness`, `get_asset_risk`, `get_maintenance_plan`) will automatically be available for conversational tool-calling.

---

## 5. Troubleshooting Guide

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **`FileNotFoundError: sensor_data.csv not found`** | Script was run from a different directory. | Run `python src/data/generate_dataset.py` to regenerate CSVs in `src/data/`. |
| **`The term 'readiness_classifier.py' is not recognized` (PowerShell)** | PowerShell requires python interpreter prefix. | Use `python src/pipeline/readiness_classifier.py`. |
| **`ModuleNotFoundError: No module named 'pandas'`** | `pandas` is not installed in the active Python environment. | Run `pip install pandas numpy` in the terminal. |
| **`Asset 'Tail-999' not found in fleet database`** | User queried a non-existent asset ID. | Bob receives an `AssetNotFound` JSON error containing the list of valid tail numbers (`Tail-101` to `Tail-125`). |
| **MCP Tool Calls Timing Out in Bob** | Stdio buffer not flushing properly. | Ensure `--stdio` flag is passed in Bob's MCP config. `src/mcp/mcp_server.py` handles auto-flush on every stdout message. |
