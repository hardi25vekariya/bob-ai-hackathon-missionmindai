# 🚀 MissionMind AI — Mission Readiness & Predictive Maintenance Copilot

> An explainable mission-readiness and predictive maintenance copilot for military aviation squadrons.

---

## 👥 Team

| Field         | Value                                                              |
| ------------- | ------------------------------------------------------------------ |
| **Team Name** | MissionMind AI                                                     |
| **Track**     | AI                                                                 |
| **Team Lead** | Ramani Tanvi Chandreshbhai — 24it083@charusat.edu.in               |
| **Members**   | Vekariya Hardi Ghanshyambhai, Vyas Rucha, Ughareja Purv HiteshBhai |

---

## 🎯 Problem Statement

Military aviation organizations need to determine which aircraft are mission-ready while dealing with large amounts of HUMS (Health & Usage Monitoring System) telemetry and historical maintenance data. Fixed maintenance schedules can miss condition-based warning signals, while unexpected failures, limited technicians, and spare-parts constraints can delay aircraft recovery and reduce operational readiness.

MissionMind AI addresses this challenge by transforming telemetry and maintenance history into explainable readiness decisions, subsystem risk scores, and prioritized maintenance actions.

---

## 💡 Solution

MissionMind AI, implemented as **AeroGuard-Bob**, is an explainable end-to-end mission-readiness and predictive maintenance copilot. It processes HUMS-style telemetry and historical maintenance records for a synthetic fleet, identifies READY and NON-READY aircraft, calculates subsystem failure-risk scores, and generates maintenance priorities under resource constraints.

The complete decision pipeline is exposed through the **Model Context Protocol (MCP)**, allowing IBM Bob to retrieve grounded fleet information, investigate individual assets, and generate maintenance plans through natural-language interaction.

---

## ✨ Key Features

- **Feature 1:** Multi-source fusion of HUMS telemetry and historical maintenance records

- **Feature 2:** Automated mission-readiness classification with plain-language explanations

- **Feature 3:** Explainable 0–100 subsystem failure-risk scoring across engine, hydraulics, fuel system, landing gear, and avionics

- **Feature 4:** Resource-constrained maintenance planning using technician teams and spare-parts availability

- **Feature 5:** IBM Bob conversational copilot integration through MCP tools for fleet readiness, asset risk, and maintenance planning

---

## 🛠️ Tech Stack

| Category                   | Technologies                                                                  |
| -------------------------- | ----------------------------------------------------------------------------- |
| **Languages**              | Python                                                                        |
| **Frameworks / Protocols** | Model Context Protocol (MCP), JSON-RPC 2.0                                    |
| **IBM Technologies**       | IBM Bob                                                                       |
| **Data Storage / Format**  | CSV, synthetic HUMS and maintenance datasets                                  |
| **Other**                  | Explainable rule-based scoring, resource-constrained maintenance optimization |

---

## 📁 Repository Structure

````text
bob-ai-hackathon-missionmindai/
│
├── .github/
│   └── workflows/
│       └── validate.yml
│
├── demo/
│   ├── screenshots/
│   │   ├── 01-dashboard.png
│   │   ├── 02-asset-details.png
│   │   └── 03-maintenance-plan.png
│   ├── demo-video-link.txt
│   └── live-demo-url.txt
│
├── docs/
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
│
├── presentation/
│   └── slides.pdf
│
├── src/
│   ├── data/
│   ├── mcp/
│   │   ├── mcp_server.py
│   │   └── verify_mcp.py
│   └── pipeline/
│       ├── failure_predictor.py
│       ├── maintenance_planner.py
│       └── readiness_classifier.py
│
├── .gitignore
├── CONTRIBUTING.md
├── README.md
└── submission.yaml

---

## ⚡ How to Run

# 1. Clone the repo
git clone https://github.com/hardi25vekariya/bob-ai-hackathon-missionmindai.git

# 2. Enter the repository
cd bob-ai-hackathon-missionmindai

# 3. Follow the Python environment and dependency setup
# See docs/setup-guide.md for the exact commands

# 4. Run the data processing and readiness pipeline
# See docs/setup-guide.md for the exact execution order

# 5. Verify the MCP server
# See docs/setup-guide.md for MCP verification instructions
---

## 🖥️ Demo

| Artifact        | Link                                                     |
| --------------- | -------------------------------------------------------- |
| 📹 Demo Video   | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo    | [See demo/live-demo-url.txt](demo/live-demo-url.txt)     |
| 🖼️ Screenshots  | [See demo/screenshots/](demo/screenshots/)               |
| 📊 Presentation | [See presentation/slides.pdf](presentation/)             |

---

## ⚠️ Known Limitations

> Be honest — judges appreciate transparency over overclaiming.

- Predictive model is trained/tested on a limited dataset and has not been validated against real HUMS data at scale
- Only tested on synthetic/simulated sensor data — not yet validated against live HUMS feeds from real platforms
- Real-time streaming ingestion is scaffolded but not fully implemented; current version processes batched sensor data rather than a continuous live feed.

---

## 🏅 What We're Most Proud Of

The predictive model turns raw HUMS sensor data into actionable, weeks-ahead failure predictions — directly targeting the $90B/year the military spends on maintenance and demonstrating how a shift to predictive, condition-based maintenance can save billions and keep more platforms mission-ready.

---
