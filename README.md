# 🛡️ ComplainAI — Civic & Enterprise Grievance Intelligence Ecosystem

> **An autonomous multimodal grievance command and dispatch system that transforms public safety reporting, civil infrastructure maintenance, and service dispute resolution with Vision-Language Models (Ollama / Local Engine), Acoustic Distress Analysis, Spatial Swarm Clustering, and Zero-Touch Agentic Workflows.**

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production-green)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Executive Overview

Traditional 311 tools and customer grievance platforms are passive, text-heavy, and reactive. They suffer from steep citizen drop-off due to tedious forms, catastrophic ticket floods during municipal outages, fraudulent "false closures" by field contractors, and multi-day delays on simple digital billing disputes.

**ComplainAI** reimagines civic and enterprise grievance management as an active, self-healing nervous system:
- **Universal Citizen Intake:** Citizens upload photos or record voice notes in regional dialects. The AI extracts visual hazard severity, translates speech, scores acoustic panic/tremor, and auto-populates the complete structured ticket.
- **Dynamic Priority Formula with Vulnerability Boost:** Replaces static Low/Med/High tags with a calibrated continuous index from $0\text{--}100$ that automatically spikes when hazards are located within 200m of schools, hospitals, or high-risk infrastructure.
- **Swarm Deduplication:** Merges hundreds of concurrent reports into a single pulsing **Master Incident Pin**, using crowd density as a logarithmic priority multiplier.
- **Anti-Fake Closure Guard:** Computer vision compares Before vs. After imagery at verified coordinates, rejecting fraudulent closure attempts and issuing tamper-proof cryptographic certificates.
- **Agentic Zero-Touch Resolver:** Autonomous tool-calling executes CRM queries, anomaly audits, Stripe refunds, and SMS notifications for Tier-1 disputes in under 4 seconds.
- **Empathy-First AI Copilot:** Diagnoses emotional distress (Panicked, Angry, Frustrated) and drafts warm, policy-backed de-escalating responses for field resolvers.
- **Predictive Failure Forecasting:** Detects velocity surges across zones (e.g., 340% spike in voltage fluctuations) and prompts proactive maintenance *before* equipment blowouts occur.

---

## 🏛️ System Architecture

```
ComplainAI/
├── run.py                          # Multi-environment launcher (binds to $PORT / $HOST)
├── requirements.txt                # Pinned production dependencies
├── Dockerfile                      # Production container spec with healthchecks
├── render.yaml                     # Render 1-click deployment blueprint
├── Procfile                        # Heroku / Railway web process entrypoint
├── backend/
│   ├── main.py                     # FastAPI REST API, WebSockets, real upload handlers
│   ├── config.py                   # Priority weights, SLA thresholds, landmark coordinates
│   ├── models.py                   # Pydantic v2 schemas for tickets, SLA, proofs, & AI
│   ├── database.py                 # Spatial in-memory store, search engine, swarm simulator
│   ├── ai/
│   │   ├── ollama_client.py        # Ollama REST client with fast socket probing & fallback
│   │   ├── multimodal_triage.py    # Audio ASR, dialect translation, CV hazard scoring
│   │   ├── priority_engine.py      # Dynamic formula with 200m GIS vulnerability boost
│   │   ├── clustering.py           # Vector similarity + Haversine spatial radius swarm
│   │   ├── anti_fake_closure.py    # Before vs. After CV verification & cryptographic tokens
│   │   ├── zero_touch_resolver.py  # Multi-tool agentic autonomous billing refund
│   │   ├── copilot.py              # Empathy-First de-escalation response generator
│   │   └── forecasting.py          # Spatial-temporal velocity failure forecasting
│   └── static/
│       ├── index.html              # Professional 4-portal civic tech SPA
│       └── images/                 # Crisp vector graphics for Before/After & demo scenes
└── tests/
    └── test_complain_ai.py         # Complete test suite (11 unit and integration tests)
```

---

## 🧮 Dynamic Priority Formula ($P_{\text{score}}$)

ComplainAI calculates a calibrated $0\text{--}100$ Priority Index for every grievance:

$$P_{\text{score}} = (w_1 \cdot \text{NLP}_{\text{Urgency}}) + (w_2 \cdot \text{Vision}_{\text{Hazard}}) + (w_3 \cdot \log(\text{Cluster}_{\text{Size}} + 1)) + (w_4 \cdot \text{Context}_{\text{Risk}})$$

### Parameter Weights:
- $w_1 = 0.35$ (NLP Urgency & Vocal Acoustic Distress)
- $w_2 = 0.30$ (Computer Vision Hazard Severity)
- $w_3 = 0.15$ (Logarithmic Crowd Swarm Multiplier)
- $w_4 = 0.20$ (GIS Environmental Proximity & Vulnerability Boost)

### Vulnerability Boost Mechanics:
When a grievance is geocoded within $200\text{m}$ of a high-consequence facility (**Oakridge Elementary School**, **St. Jude Metropolitan Hospital**, or **Sector 4 High-Voltage Transformer Substation**), $Context_{\text{Risk}}$ automatically spikes from baseline (20) to $95+$, ensuring critical life-safety hazards instantly leap to the top of the queue regardless of the reporter's tone.

---

## 🚀 The 4 User Portals

1. **📝 File a Report (Citizen Intake):**
   - Drag-and-drop real photos or snap with mobile camera.
   - Record voice notes directly with the browser microphone (animated waveform + live Speech-to-Text).
   - "Detect My GPS" button using HTML5 Geolocation.
   - Instant multimodal triage with explainable Priority Breakdown.

2. **🔍 Track Status (Public Transparency):**
   - Search by Ticket Number (e.g. `CMP-7001`) or complainant phone number.
   - Real-time ticking SLA countdown clock.
   - Side-by-side Before vs. After photographic proof of resolution with cryptographic verification stamp.
   - Step-by-step audit trail (Reported $\to$ Triaged $\to$ Unit Dispatched $\to$ Verified Closed).
   - Printable receipt export.

3. **🛠️ Resolver Operations (Field Dispatch):**
   - Queue filterable by Priority, SLA, and Status.
   - **Empathy-First AI Copilot:** Generates personalized, policy-backed de-escalating responses in 3 tones (Empathetic, Formal, Action-Oriented).
   - **Proof-of-Resolution Anti-Fake Guard:** Field resolvers upload an "After" photo; Computer Vision verifies defect remediation and blocks fake/unrelated images.
   - **Agentic Zero-Touch Resolver:** Autonomous 4-second Stripe refund simulation for digital/billing disputes.

4. **📊 City Analytics & Spatial GIS Map (Executive Command):**
   - Real-time city KPI counters.
   - Interactive 2D GIS city map with 200m vulnerability buffer rings around schools and hospitals.
   - **Simulate Swarm Outage Button:** Simulates 25 concurrent outage reports collapsing into 1 Master Incident pin.
   - **Predictive Failure Forecasting:** Transformer surge early warning with 1-click preventative crew deployment.

---

## 🚢 Deployment Guide

ComplainAI is cloud-agnostic and ready to deploy in seconds:

### Option 1: Deploy on Render (Recommended)
1. Fork or push this repository to GitHub.
2. Sign in to [Render](https://render.com).
3. Click **New +** $\to$ **Web Service** $\to$ Select your `ComplainAI` repository.
4. Render automatically detects `render.yaml` and `requirements.txt`:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run.py`
5. Click **Deploy Web Service**. Done!

### Option 2: Deploy on Railway
1. Sign in to [Railway](https://railway.app).
2. Click **New Project** $\to$ **Deploy from GitHub repo**.
3. Select `ComplainAI`. Railway automatically reads the `Procfile` (`web: python run.py`) and exposes your application on a live HTTPS domain.

### Option 3: Deploy with Docker
```bash
# 1. Build the Docker image
docker build -t complainai .

# 2. Run the container
docker run -d -p 8000:8000 --name complainai-app complainai

# 3. Access in browser
open http://localhost:8000
```

### Option 4: Local Development
```bash
# 1. Clone repository
git clone https://github.com/SomnathPal-max/ComplainAI.git
cd ComplainAI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run test suite
python -m pytest -v

# 4. Start server
python run.py
```
Open **`http://localhost:8000`** in your browser.

---

## 🦙 Ollama & Local AI Configuration

ComplainAI is built **Ollama-first**:
- Default Endpoint: `http://127.0.0.1:11434`
- Supported Models: `llama3.2-vision`, `llama3.2`, `llava`, `mistral`, `qwen2.5`
- **Zero-Crash Autonomous Fallback Mode:** If Ollama is offline or starting up, ComplainAI seamlessly activates an autonomous local inference pipeline providing high-accuracy multimodal analysis, ensuring pitches and demonstrations never fail.
- **In-App LLM Control Modal:** Click the top-right **AI Engine: Status** badge to adjust the Ollama URL, switch active models, and test connections live.

---

## 🧪 Automated Test Suite

All 11 unit and integration tests run cleanly:
```bash
python -m pytest -v
```

```
tests/test_complain_ai.py::test_haversine_distance PASSED                [  9%]
tests/test_complain_ai.py::test_dynamic_priority_formula_with_vulnerability_boost PASSED [ 18%]
tests/test_complain_ai.py::test_audio_asr_and_regional_dialect_translation PASSED [ 27%]
tests/test_complain_ai.py::test_computer_vision_hazard_scoring PASSED    [ 36%]
tests/test_complain_ai.py::test_anti_fake_closure_guard_rejection PASSED [ 45%]
tests/test_complain_ai.py::test_anti_fake_closure_guard_approval PASSED  [ 54%]
tests/test_complain_ai.py::test_zero_touch_autonomous_resolution PASSED  [ 63%]
tests/test_complain_ai.py::test_empathy_copilot_de_escalation PASSED     [ 72%]
tests/test_complain_ai.py::test_simulate_mass_outage_crowd_swarm PASSED  [ 81%]
tests/test_complain_ai.py::test_swarm_clustering_radius_match PASSED     [ 90%]
tests/test_complain_ai.py::test_database_state_and_landmarks PASSED      [100%]
======================= 11 passed in 0.72s ========================
```
