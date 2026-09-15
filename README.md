# 🚀 MissionMind AI — Mission Readiness & Predictive Maintenance Copilot

> ⚠️ **Replace everything in `[ ]` brackets with your actual content before submission.**

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | MissionMind AI |
| **Track** | AI |
| **Team Lead** | Ramani Tanvi Chandreshbhai — 24it083@charusat.edu.in |
| **Members** | Vekariya Hardi Ghanshyambhai, Vyas Rucha, Ughareja Purv HiteshBhai |

---

## 🎯 Problem Statement

> In 2–3 sentences: What problem does your project solve? Who experiences this problem?

Military organizations cannot reliably determine whether aircraft, vehicles, and equipment are mission-ready, because maintenance runs on fixed calendar schedules regardless of actual component condition. HUMS (Health & Usage Monitoring System) sensor data that could predict failures weeks in advance sits unanalyzed, and when platforms fail unexpectedly, operational readiness drops and recovery takes weeks. The US military spends $90B/year on maintenance — most of it reactive rather than predictive.

---

## 💡 Solution

> In 2–3 sentences: What did you build? How does it solve the problem above?

MissionMind AI ingests HUMS sensor data and uses AI to predict component failures before they occur, shifting maintenance from fixed calendar intervals to condition-based, predictive scheduling. The copilot surfaces mission-readiness scores and early-warning alerts in natural language, so maintenance teams can act weeks ahead instead of finding out after a platform goes down.

---

## ✨ Key Features

- **Feature 1:** Predictive failure detection from HUMS sensor data using AI/ML models
- **Feature 2:** Condition-based maintenance scheduling instead of fixed calendar intervals
- **Feature 3:** Mission-readiness scoring for aircraft, vehicles, and equipment
- **Feature 4:** Natural language maintenance recommendations via conversational copilot
- **Feature 5:** Early-warning alerts generated weeks in advance of predicted failure

---
---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python |
| **Frameworks** | FastAPI |
| **IBM Technologies** | watsonx.ai, IBM Bob |
| **Databases** | PostgreSQL |
| **Other** | Docker |

---

## 📁 Repository Structure

```
├── src/                  # All source code
├── docs/                 # Written documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                 # Demo artifacts
│   ├── screenshots/      # App screenshots
│   └── demo-video-link.txt  # Link to demo video
├── presentation/         # Slide deck
└── submission.yaml       # Structured submission metadata
```

---

## ⚡ How to Run

> **Copy these exact steps from your [`docs/setup-guide.md`](docs/setup-guide.md)**

```bash
# 1. Clone the repo
git clone https://github.com/[your-repo].git
cd [your-repo]

# 2. Install dependencies
[your install command here]

# 3. Configure environment
cp .env.example .env
# Edit .env with your values

# 4. Run the project
[your run command here]
```

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/slides.pdf](presentation/) |

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
