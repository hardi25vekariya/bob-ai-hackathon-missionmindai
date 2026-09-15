# AeroGuard-Bob: HUMS Mission-Readiness & Predictive Maintenance Copilot

> **IBM Hackathon Submission — Defense & Aerospace Track (Problem Statement D1)**  
> An explainable, data-grounded AI copilot connecting military Health and Usage Monitoring Systems (HUMS) telemetry to **IBM Bob** via the Model Context Protocol (MCP).

---

## 1. Problem Statement

Modern military aviation commands incur over **$90 billion annually** in maintenance and sustainment costs. Despite advanced Health and Usage Monitoring Systems (HUMS) recording high-frequency telemetry (vibration, turbine heat, lubricant particulate sensors), most maintenance workflows remain tethered to rigid, calendar-based inspection schedules or siloed dashboard logs. 

Flight-line maintenance officers and squadron commanders face critical challenges:
1. **Unanalyzed Sensor Data**: Degraded components (e.g. subtle vibration jitter or lubricant breakdown) go unnoticed until catastrophic in-flight aborts occur.
2. **Disconnected History**: Real-time sensor alerts are rarely unified with historical service logs to detect repeat failure patterns.
3. **Resource-Blind Triage**: When multiple aircraft are grounded simultaneously, maintenance chiefs lack automated triage tools to optimize repair work orders under tight crew headcount and spare-parts shortages.

---

## 2. Solution Overview

**AeroGuard-Bob** bridges the gap between raw aerospace telemetry, explainable engineering heuristics, and conversational intelligence.

The system is architected as an integrated 4-stage analytical pipeline exposed to **IBM Bob** through the **Model Context Protocol (MCP)**:
- **Data Ingestion & Join Layer (`src/data/`)**: Harmonizes live sensor telemetry (`sensor_data.csv`) with 2-year service history logs (`service_history.csv`) across 25 fighter jets (`Tail-101` to `Tail-125`).
- **Readiness Classifier (`src/pipeline/readiness_classifier.py`)**: Automatically flags assets as `READY` or `NON-READY` against operational safety thresholds and scheduled inspection windows.
- **Predictive Failure Module (`src/pipeline/failure_predictor.py`)**: Computes subsystem failure risk scores (0–100) across Engine, Hydraulics, Fuel System, Landing Gear, and Avionics, synthesizing active sensor breaches, repeat failure history, and cumulative flight fatigue.
- **Maintenance Action Planner (`src/pipeline/maintenance_planner.py`)**: Executes a greedy allocation algorithm that ranks grounded aircraft by risk severity and dispatches available technician teams and spare parts, diagnosing exact supply-chain bottlenecks for deferred jets.
- **IBM Bob MCP Server (`src/mcp/mcp_server.py`)**: Exposes the entire pipeline as structured JSON tools over standard JSON-RPC 2.0 stdio, allowing commanders to ask natural language questions with 100% data-grounded answers.

---

## 3. Repository Structure

```
.
├── submission.yaml               <- Official hackathon submission metadata (Track: AI)
├── README.md                     <- Project overview and quickstart guide
├── src/
│   ├── README.md                 <- Source layout & component guide
│   ├── .env.example              <- Environment template file
│   ├── data/
│   │   ├── generate_dataset.py   <- Synthetic HUMS telemetry generator
│   │   ├── sensor_data.csv       <- 25 fighter jet telemetry records
│   │   └── service_history.csv   <- 74 maintenance event records
│   ├── pipeline/
│   │   ├── readiness_classifier.py <- Stage 2: Mission readiness classifier (9 ready, 16 non-ready)
│   │   ├── failure_predictor.py    <- Stage 3: Subsystem failure risk scoring (0-100)
│   │   └── maintenance_planner.py  <- Stage 4: Greedy resource-constrained triage planner
│   └── mcp/
│       ├── mcp_server.py         <- Stage 5: IBM Bob MCP Server (JSON-RPC stdio & CLI)
│       └── verify_mcp.py         <- Automated MCP protocol verification script
└── docs/
    ├── architecture.md           <- Mermaid diagram & component mapping
    ├── problem-statement.md      <- Problem context & sustainment impact
    ├── solution-overview.md      <- Explainability rationale & conversational UX
    └── setup-guide.md            <- Step-by-step execution & troubleshooting
```

---

## 4. Key Features

1. **Deterministic Multi-Source Data Fusion**: Cross-references continuous sensor metrics with historical maintenance logs across 25 fighter aircraft in `src/data/`.
2. **Transparent Readiness Classification**: Flags non-ready aircraft with plain-language diagnostic strings (currently **9 Ready (36.0%)** / **16 Non-Ready (64.0%)**) and detects overdue inspections (>150 days) even if live sensors read green.
3. **Explainable 0–100 Failure Risk Scoring**: Transparently assesses component risk based on sensor deviation percentages, component repair recurrence, and airframe flight cycles without black-box opacity.
4. **Constrained Maintenance Triage Board**: Dynamically schedules repairs based on available technician crews and spare parts stock, identifying whether queued jets are blocked by crew shortages or component stockouts.
5. **Verified IBM Bob MCP Integration**: Provides 3 native MCP tools (`get_fleet_readiness`, `get_asset_risk`, `get_maintenance_plan`) in `src/mcp/mcp_server.py` verified over JSON-RPC stdio protocol.

---

## 5. Tech Stack

- **Core Logic & Analytics**: Python 3.10+, `pandas`, `numpy`
- **MCP Protocol Implementation**: Model Context Protocol (JSON-RPC 2.0 over Stdio, Protocol Version: `2024-11-05`)
- **Conversational Assistant**: IBM Bob (`bob.ibm.com`)
- **Documentation & Architecture**: Mermaid diagrams, Markdown

---

## 6. How to Run

### Step 1: Install Dependencies
```bash
pip install pandas numpy
```

### Step 2: Run Analytical Pipeline Modules
Run each module standalone to verify its analytical output:

1. **Run Mission Readiness Classifier**:
   ```bash
   python src/pipeline/readiness_classifier.py
   ```
   *Outputs fleet readiness status (9 Ready / 16 Non-Ready) with grounded explanations.*

2. **Run Subsystem Failure Predictor**:
   ```bash
   python src/pipeline/failure_predictor.py
   ```
   *Outputs ranked failure risk table (e.g. `Tail-108` at 98.0/100 risk on Engine).*

3. **Run Maintenance Action Planner**:
   ```bash
   python src/pipeline/maintenance_planner.py
   ```
   *Outputs greedy triage schedule (3 Scheduled / 13 Queued under default constraints).*

### Step 3: Run & Verify MCP Server
- **Run Standalone MCP Test Suite**:
  ```bash
  python src/mcp/mcp_server.py
  ```
- **Run Automated JSON-RPC Stdio Protocol Test**:
  ```bash
  python src/mcp/verify_mcp.py
  ```
- **Connect Live MCP Stdio Server to IBM Bob**:
  ```bash
  python src/mcp/mcp_server.py --stdio
  ```

---

## 7. Known Limitations

In the spirit of honest engineering:
1. **Synthetic Telemetry Baseline**: The dataset models 25 representative fighter jets (`Tail-101` to `Tail-125`) rather than streaming classified, multi-gigabyte live military HUMS bus feeds.
2. **Explainable Heuristics vs Trained Deep Models**: Risk scores use weighted physical parameter excess ratios rather than neural time-series regressors, chosen deliberately for flight safety auditability.
3. **Single Airframe Class**: Parameters are calibrated for tactical fighter jets; multi-type fleet deployments (e.g. transport turboprops or attack helicopters) would require subsystem threshold profiles.

---

## 8. What We're Most Proud Of

1. **Complete Explainability**: In military aerospace, a black-box model saying *"Tail-108 has an 82% failure chance"* is inadmissible for flight clearance. AeroGuard-Bob traces every score to exact physical breaches (*"vibration 11.41 mm/s is 27% over limit, temp 673.9°C is 12% over limit, 3 prior compressor repairs"*).
2. **Verified Native MCP Integration**: The MCP server was fully verified with automated JSON-RPC 2.0 handshakes, tool discovery, and tool execution, delivering clean, structured JSON payloads directly to IBM Bob.
3. **Realistic Operational Grounding**: The system successfully catches latent risks (aircraft overdue for 150-day inspections that look healthy on live sensors) and handles supply-chain bottlenecks gracefully.
