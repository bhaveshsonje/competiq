# CompetIQ — AI Multi-Agent Competitive Intelligence Engine

An AI-powered system that autonomously researches companies using parallel specialized agents and generates structured, citation-backed competitive intelligence reports in real time.

Built to demonstrate multi-agent orchestration, reflexive evaluation loops, and live streaming UX.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square&logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-orange?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-Llama3.3_70B-red?style=flat-square)

---

## 🚀 Why This Project Is Interesting

Instead of prompting a single LLM, CompetIQ:

- Spins up **5 specialized agents in parallel**
- Synthesizes structured intelligence from grounded web sources
- Uses a **self-critique (Reflexion) loop** to evaluate and rewrite weak outputs
- Streams live agent execution to the browser
- Persists full report history with quality scoring

This mirrors how real analyst teams operate — fully automated.

---

## 🧠 System Architecture

```
User Query
    │
    ▼
LangGraph Orchestrator
    │
    ├── News Agent
    ├── Product Agent
    ├── Pricing Agent
    ├── Sentiment Agent
    └── Market Agent     (executed in parallel)
            │
            ▼
        Synthesizer
            │
            ▼
        Critic Agent
        (Scores 1–10)
            │
     If score < 7 → Rewrite
            │
            ▼
        Final Report + PDF
```

### Key Architectural Decisions

- **Parallelism:** `ThreadPoolExecutor` reduces latency across research agents
- **Graph Orchestration:** LangGraph controls execution flow and Reflexion loop
- **Grounded Intelligence:** Tavily search ensures citation-backed analysis
- **Live Feedback:** Server-Sent Events (SSE) stream agent status updates
- **Evaluation Layer:** Critic agent enforces minimum report quality

---

## 🔥 Core Features

### 🧩 Parallel Multi-Agent Research
Five domain-specific agents analyze:
- News & press coverage
- Product capabilities
- Pricing models
- Customer sentiment
- Market positioning

### 🔁 Reflexion (Self-Critique Pattern)
A Critic agent:
- Scores reports from 1–10
- Triggers automatic rewrites if score < 7
- Improves structural clarity and analytical depth

### 📡 Real-Time Streaming UI
- Live agent status panel
- Streaming updates via SSE
- No polling required

### 📊 Visual Intelligence
- Sentiment comparison bar chart
- Quality radar chart
- Source citations for every major claim

### 🗂 Persistence Layer
- SQLite + SQLAlchemy
- Full historical tracking
- Quality trend analysis over time

### 📄 Professional PDF Export
- One-click download
- Executive-ready formatting
- Generated using ReportLab

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | Groq (Llama 3.3 70B) |
| Orchestration | LangGraph |
| Search & Grounding | Tavily API |
| Backend | FastAPI |
| Streaming | Server-Sent Events (SSE) |
| Database | SQLite + SQLAlchemy |
| PDF Generation | ReportLab |
| Frontend | Vanilla JS + Chart.js |

---

## 🧪 What This Demonstrates

This project showcases:

- Multi-agent system design
- Graph-based orchestration
- Parallel execution strategies
- Reflexion-style evaluation loops
- LLM grounding with external tools
- Real-time backend-to-frontend streaming
- End-to-end full-stack AI architecture

---

## 📂 High-Level Project Structure

```
competiq/
├── main.py                # FastAPI + SSE
├── graph/orchestrator.py  # LangGraph execution + Reflexion
├── agents/                # Specialized research agents
├── tools/search.py        # Tavily grounding layer
├── database/              # Persistence + PDF export
└── frontend/              # Live streaming UI
```

---

## 🎯 Example Use Case

**Input:**
- Company: Salesforce  
- Competitors: HubSpot, Zoho  

**Output:**
- Multi-dimensional competitive report
- Citation-backed claims
- Sentiment comparison chart
- Quality-scored analysis
- Downloadable executive PDF

---

## ⚙️ Setup (Optional)

<details>
<summary>Click to expand setup instructions</summary>

### Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/competiq.git
cd competiq
```

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure Environment Variables
```bash
cp .env.example .env
```

Add:
```
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

### Run Server
```bash
python main.py
```

Open:
```
http://localhost:8080
```

</details>

---

## 👤 Built By

Bhavesh Sonje  
MS Information Management — UIUC  
Focused on AI systems, multi-agent architectures, and intelligent automation.

---

MIT License
