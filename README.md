# ⚡ CompetIQ — AI-Powered Competitive Intelligence Engine

A multi-agent system that autonomously researches companies and generates comprehensive competitive intelligence reports in real-time.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square&logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-orange?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-Llama3.3_70B-red?style=flat-square)

---

## 🎯 What It Does

Enter a company and its competitors — 5 specialized AI agents spin up in **parallel**, each researching a different dimension of the competitive landscape. A Synthesizer agent compiles all findings into a structured report, and a Critic agent evaluates quality and triggers rewrites if the score is below 7/10.

The entire process streams live to a browser UI, with real-time agent status updates, charts, and one-click PDF export.

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────┐
│         LangGraph Orchestrator          │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │   News   │  │ Product  │            │
│  │  Agent   │  │  Agent   │  (parallel) │
│  └────┬─────┘  └────┬─────┘            │
│  ┌────┴─────┐  ┌────┴─────┐            │
│  │ Pricing  │  │Sentiment │            │
│  │  Agent   │  │  Agent   │  (parallel) │
│  └────┬─────┘  └────┬─────┘            │
│       │    ┌──────┐  │                 │
│       └────┤Market├──┘                 │
│            │Agent │                   │
│            └──┬───┘                   │
│               │                       │
│         ┌─────▼──────┐                │
│         │Synthesizer │                │
│         └─────┬──────┘                │
│               │                       │
│         ┌─────▼──────┐                │
│         │   Critic   │◄──── Reflexion  │
│         │   Agent    │      Loop      │
│         └─────┬──────┘                │
└───────────────┼─────────────────────┘
                ▼
         Final Report + PDF
```

---

## ✨ Features

- **5 Parallel Research Agents** — News, Product, Pricing, Sentiment, Market — run simultaneously via `ThreadPoolExecutor`
- **Self-Critique Loop (Reflexion Pattern)** — Critic agent scores the report 1–10 and triggers rewrites for scores below 7
- **Real-Time Streaming UI** — Server-Sent Events (SSE) stream live agent updates to the browser
- **Confidence Scoring** — Each agent scores its findings based on source quality (powered by Tavily)
- **Source Citations** — Every claim is traceable to a real URL
- **SQLite Persistence** — All analyses saved with full history and trend tracking
- **PDF Export** — One-click professional report download (ReportLab)
- **Interactive Charts** — Sentiment comparison bar chart + report quality radar chart (Chart.js)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Groq (Llama 3.3 70B) |
| Agent Orchestration | LangGraph |
| Web Search | Tavily API |
| Backend | FastAPI + SSE |
| Database | SQLite (SQLAlchemy) |
| PDF Generation | ReportLab |
| Frontend | Vanilla JS + Chart.js |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/competiq.git
cd competiq
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and add your API keys:
```
GROQ_API_KEY=your_groq_key_here       # Free at console.groq.com
TAVILY_API_KEY=your_tavily_key_here   # Free at tavily.com
```

### 5. Run the server
```bash
python main.py
```

Open **http://localhost:8080** in your browser.

---

## 📸 Usage

1. Enter the company you want to analyze (e.g. `Salesforce`)
2. Add one or more competitors (e.g. `HubSpot`, `Zoho`)
3. Click **Run Analysis**
4. Watch 5 agents work in real-time in the Agent Status panel
5. Read the full report, explore charts, check sources
6. Export to PDF with one click

---

## 📁 Project Structure

```
competiq/
├── main.py                  # FastAPI app + SSE streaming
├── requirements.txt
├── .env.example
├── graph/
│   └── orchestrator.py      # LangGraph parallel execution + Reflexion loop
├── agents/
│   ├── news_agent.py        # Recent news & press coverage
│   ├── product_agent.py     # Features & capabilities analysis
│   ├── pricing_agent.py     # Pricing models & tiers
│   ├── sentiment_agent.py   # Customer reviews & sentiment scoring
│   ├── market_agent.py      # Market share & positioning
│   ├── synthesizer.py       # Report synthesis
│   └── critic_agent.py      # Quality evaluation + Reflexion
├── tools/
│   └── search.py            # Tavily search with confidence scoring
├── database/
│   ├── models.py            # SQLAlchemy models + persistence
│   └── pdf_export.py        # ReportLab PDF generation
└── frontend/
    └── index.html           # Streaming UI with Chart.js
```

---

## 🔑 API Keys (Free Tiers)

| Service | Free Tier | Link |
|---------|-----------|------|
| Groq | Unlimited (rate limited) | [console.groq.com](https://console.groq.com) |
| Tavily | 1,000 searches/month | [tavily.com](https://tavily.com) |

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

Built by [Bhavesh Sonje](https://www.linkedin.com/in/bhavesh-sonje)
