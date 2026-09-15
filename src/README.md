# AeroGuard-Bob — Source Code

This directory contains the complete analytical backend for the AeroGuard-Bob
mission-readiness and predictive maintenance system. All logic runs on pure Python
with `pandas` and `numpy` — no external service or database required.

---

## Directory Structure

```
src/
├── data/                          ← Dataset layer: telemetry + maintenance records
│   ├── generate_dataset.py        ← Synthetic HUMS data generator (seeded, reproducible)
│   ├── sensor_data.csv            ← 25 aircraft × 6 live sensor readings
│   └── service_history.csv        ← 74 historical maintenance event records
│
├── pipeline/                      ← Core analytical pipeline (Stages 2–4)
│   ├── readiness_classifier.py    ← Stage 2: Mission readiness classifier
│   ├── failure_predictor.py       ← Stage 3: Subsystem failure risk scorer
│   └── maintenance_planner.py     ← Stage 4: Resource-constrained maintenance planner
│
└── mcp/                           ← IBM Bob integration layer (Stage 5)
    ├── mcp_server.py              ← MCP server exposing 3 tools over JSON-RPC 2.0 stdio
    └── verify_mcp.py             ← Automated end-to-end MCP protocol test
```

---

## Data Layer (`src/data/`)

### `generate_dataset.py`
Reproducible synthetic dataset generator (NumPy seed 42). Produces both CSV files
with realistic HUMS telemetry profiles across 25 fighter jets (Tail-101 to Tail-125).
Assets are deliberately seeded into four risk categories:
- **High vibration** (6 jets): Tail-104, 108, 112, 117, 121, 125
- **High engine temp** (5 jets): Tail-103, 108, 114, 119, 123
- **Degraded oil quality** (4 jets): Tail-106, 112, 118, 122
- **Overdue inspection** (3 jets, otherwise healthy sensors): Tail-105, 110, 120

Re-run to regenerate CSVs: `python src/data/generate_dataset.py`

### `sensor_data.csv`
25 rows × 6 columns of live airframe telemetry:

| Column | Description |
|---|---|
| `asset_id` | Tail number (Tail-101 … Tail-125) |
| `vibration_level` | Vibration in mm/s (threshold: > 9.0) |
| `engine_temp_c` | Engine temperature in °C (threshold: > 600.0) |
| `oil_quality_index` | Lubricant quality 0–100 (threshold: < 50) |
| `usage_cycles` | Cumulative flight cycles (max baseline: 4500) |
| `last_inspection_days_ago` | Days since last scheduled inspection (threshold: > 150) |

### `service_history.csv`
74 rows of maintenance event records: `asset_id`, `date`, `component`, `issue_found`, `action_taken`.
Components tracked: `engine`, `hydraulics`, `fuel_system`, `landing_gear`, `avionics`.

---

## Pipeline Layer (`src/pipeline/`)

Data flows through the three modules in a strict chain:

```
sensor_data.csv  ──┐
                   ├──▶  readiness_classifier.py
service_history.csv ──┘         │
                                 ▼
                         failure_predictor.py
                                 │
                                 ▼
                        maintenance_planner.py
```

### `readiness_classifier.py`
**Stage 2 — Mission Readiness Classifier**

Entry point: `classify_readiness(sensor_file, service_file) → DataFrame`

Evaluates each asset against four operational safety thresholds:

| Threshold | Limit | Breach Meaning |
|---|---|---|
| Vibration | > 9.0 mm/s | Rotor unbalance / bearing spalling |
| Engine temp | > 600.0 °C | Thermal overheating / cooling duct blockage |
| Oil quality index | < 50 | Lubricant breakdown / particulate contamination |
| Last inspection | > 150 days ago | Mandatory inspection overdue |

Returns `asset_id`, `is_ready` (bool), `explanation` (plain-language diagnostic string).
**Current result: 9 READY / 16 NON-READY (36% readiness rate).**

### `failure_predictor.py`
**Stage 3 — Subsystem Failure Risk Scorer**

Entry point: `predict_failures(sensor_file, service_file) → DataFrame` (sorted by `risk_score` desc)

Calls `classify_readiness()` internally, then computes a **0–100 risk score** for each of
five subsystems — `engine`, `hydraulics`, `fuel_system`, `landing_gear`, `avionics` — using:

```
Total Risk = min(100, Sensor Penalty ≤50 + History Penalty ≤30 + Usage Wear ≤20)
```

Returns the **highest-risk subsystem** per asset along with a plain-language rationale tracing
every contributing factor. **Top risk: Tail-108 at 98.0/100 (engine).**

### `maintenance_planner.py`
**Stage 4 — Resource-Constrained Maintenance Planner**

Entry point: `generate_maintenance_plan(available_crews, available_parts) → (summary_text, DataFrame)`

Calls `predict_failures()` internally, filters to NON-READY assets, then runs a **greedy
priority sort** (primary: `risk_score` desc; tiebreaker: `usage_cycles` desc) and allocates
available technician crews and spare parts. Each work order is marked `scheduled` or `queued`,
with an explicit bottleneck note when deferred (crew shortage vs. parts stockout).

Default constraints: 3 crews, inventory `{engine:2, landing_gear:1, avionics:3, hydraulics:2, fuel_system:2}`.
**Default result: 3 Scheduled / 13 Queued.**

---

## MCP Layer (`src/mcp/`)

### `mcp_server.py`
**Stage 5 — IBM Bob MCP Integration**

Wraps the three pipeline entry points as standard
[Model Context Protocol](https://modelcontextprotocol.io) tools over JSON-RPC 2.0 stdio
(protocol version `2024-11-05`). IBM Bob calls these tools when answering natural-language
queries about fleet health — ensuring every answer is grounded in verified telemetry rather
than LLM inference.

| MCP Tool | Handler | Delegates To |
|---|---|---|
| `get_fleet_readiness` | `handle_get_fleet_readiness()` | `classify_readiness()` |
| `get_asset_risk` | `handle_get_asset_risk(asset_id?)` | `predict_failures()` |
| `get_maintenance_plan` | `handle_get_maintenance_plan(crews, parts)` | `generate_maintenance_plan()` |

Run modes:
```bash
python src/mcp/mcp_server.py            # Standalone self-test (prints tool outputs)
python src/mcp/mcp_server.py --stdio    # Live stdio server for IBM Bob registration
```

IBM Bob MCP registration config:
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

### `verify_mcp.py`
Automated end-to-end protocol test. Spawns `mcp_server.py --stdio` as a subprocess and
exercises the full JSON-RPC handshake (`initialize` → `tools/list` → three `tools/call`
invocations). Run before submitting to confirm the MCP layer is functional:

```bash
python src/mcp/verify_mcp.py
```

---

## Running the Pipeline

```bash
# Install dependencies
pip install -r requirements.txt

# Stage 2 — Readiness classifier
python src/pipeline/readiness_classifier.py

# Stage 3 — Failure risk predictor
python src/pipeline/failure_predictor.py

# Stage 4 — Maintenance planner
python src/pipeline/maintenance_planner.py

# Stage 5 — MCP server self-test
python src/mcp/mcp_server.py

# Stage 5 — Full JSON-RPC protocol verification
python src/mcp/verify_mcp.py
```

See [`docs/setup-guide.md`](../docs/setup-guide.md) for full setup, troubleshooting, and
IBM Bob registration instructions.
