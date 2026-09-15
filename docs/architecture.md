# System Architecture: Military Asset Mission-Readiness & Predictive Maintenance Copilot

## 1. End-to-End System Architecture

```mermaid
graph TD
    %% Stage 1: Data Layer
    subgraph S1["Stage 1: Data Layer (src/data/)"]
        D1[("src/data/sensor_data.csv")] --> DL["Data Ingestion & Join Engine<br/>(generate_dataset.py / pandas)"]
        D2[("src/data/service_history.csv")] --> DL
        DL --> DF["Unified Asset Feature Matrix"]
    end

    %% Analytics & ML Pipeline (Stages 2, 3, 4)
    subgraph S2["Stage 2: Readiness Classifier (src/pipeline/)"]
        DF --> RC["Readiness Evaluation Engine<br/>(readiness_classifier.py)"]
        RC --> RR["Asset Readiness Status & Root Causes<br/>(READY / NON-READY + Expiry Flags)"]
    end

    subgraph S3["Stage 3: Failure Prediction Module (src/pipeline/)"]
        DF --> FP["Component Failure Predictor<br/>(failure_predictor.py)"]
        RR -.-> FP
        FP --> FR["Failure Probabilities & At-Risk Components<br/>(Engine, Hydraulics, Avionics, etc.)"]
    end

    subgraph S4["Stage 4: Maintenance Plan Generator (src/pipeline/)"]
        RR --> MG["Constrained Scheduler & Optimizer<br/>(maintenance_planner.py)"]
        FR --> MG
        CON["Crew & Spare Parts Constraints"] --> MG
        MG --> MP["Prioritized Action Schedule & Work Orders"]
    end

    %% Stage 5: MCP Integration Layer
    subgraph S5["Stage 5: IBM Bob / MCP Layer (src/mcp/)"]
        MCP["MCP Server & Tool Protocol<br/>(mcp_server.py)"]
        RR --> MCP
        FR --> MCP
        MP --> MCP
        MCP --- T1["Tool: get_fleet_readiness()"]
        MCP --- T2["Tool: get_asset_risk(asset_id)"]
        MCP --- T3["Tool: get_maintenance_plan(crews, parts)"]
    end

    %% Stage 6: User & Conversational Interface
    subgraph S6["Stage 6: User Interface & Copilot Chat"]
        MCP <==> BOB["IBM Bob Conversational Assistant"]
        BOB <==> UI["Tactical Mission Dashboard & Chat UI"]
        USER["Maintenance Commander / Flight Lead"] <==> UI
    end
```

---

## 2. Component Table

| Component | Module / File | Technology | Responsibility |
| :--- | :--- | :--- | :--- |
| **Data Ingestion Layer** | `src/data/generate_dataset.py`, `src/data/sensor_data.csv`, `src/data/service_history.csv` | Python (`pandas`, `numpy`) | Ingests real-time telemetry and 2-year maintenance logs, normalizing timestamps and missing readings. |
| **Mission Readiness Classifier** | `src/pipeline/readiness_classifier.py` | Python (`pandas`) | Evaluates vibration (`>9 mm/s`), temperature (`>600°C`), oil quality (`<50`), and inspection limits (`>150 days`) to flag assets as READY or NON-READY. |
| **Predictive Failure Module** | `src/pipeline/failure_predictor.py` | Python (`pandas`, explainable heuristic scoring) | Calculates subsystem failure risk scores (0–100) across engine, hydraulics, fuel system, landing gear, and avionics. |
| **Maintenance Action Planner** | `src/pipeline/maintenance_planner.py` | Python (`pandas`, greedy constraint optimizer) | Prioritizes repairs by risk score and usage cycles, greedily allocating limited technician crews and spare parts. |
| **IBM Bob / MCP Layer** | `src/mcp/mcp_server.py`, `src/mcp/verify_mcp.py` | Python (`json`, JSON-RPC 2.0 / MCP Protocol) | Exposes stages 2–4 as callable tools so IBM Bob can answer natural language queries grounded in verified telemetry. |
| **Tactical Dashboard & Chat UI** | Stage 6 Dashboard | Web / Streamlit / FastAPI UI | Provides flight leads with real-time fleet health metrics, triage action boards, and conversational copilot chat. |

---

## 3. IBM Bob MCP Registration

To connect IBM Bob to this tool suite (per `bob.ibm.com/docs`):

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
