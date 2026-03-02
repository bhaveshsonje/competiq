import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

from graph.orchestrator import run_parallel_agents
from database.models import init_db, save_analysis, get_analyses, get_analysis_by_id
from database.pdf_export import generate_pdf

load_dotenv()
init_db()

app = FastAPI(
    title="Competitive Intelligence Engine",
    description="AI-powered competitive analysis with multi-agent parallel research",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Serve frontend
frontend_path = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


class AnalysisRequest(BaseModel):
    company: str
    competitors: List[str]


@app.get("/", response_class=HTMLResponse)
async def root():
    html_file = frontend_path / "index.html"
    return HTMLResponse(content=html_file.read_text())


@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/analyze/stream")
async def analyze_stream(request: AnalysisRequest):
    """
    SSE endpoint: streams real-time progress updates as agents work,
    then delivers the final report.
    """
    async def event_generator():
        messages = asyncio.Queue()

        async def progress_callback(event_type: str, message: str):
            await messages.put({"type": event_type, "message": message})

        async def run_analysis():
            try:
                state = await run_parallel_agents(
                    company=request.company,
                    competitors=request.competitors,
                    progress_callback=progress_callback
                )
                # Save to DB
                saved = save_analysis(state)

                # Send final result
                await messages.put({
                    "type": "result",
                    "data": {
                        "analysis_id": saved.id,
                        "final_report": state.get("final_report", ""),
                        "overall_confidence": state.get("overall_confidence", 0),
                        "critique": state.get("critique", {}),
                        "sources": state.get("all_sources", []),
                        "sentiment_scores": state.get("sentiment_scores", {}),
                        "companies": [request.company] + request.competitors
                    }
                })
            except Exception as e:
                await messages.put({"type": "error", "message": str(e)})
            finally:
                await messages.put({"type": "done"})

        asyncio.create_task(run_analysis())

        while True:
            msg = await messages.get()
            yield {"data": json.dumps(msg)}
            if msg.get("type") in ["done", "error"]:
                break

    return EventSourceResponse(event_generator())


@app.get("/api/analyses")
async def list_analyses(company: str = None, limit: int = 20):
    """Get past analyses, optionally filtered by company."""
    return get_analyses(company=company, limit=limit)


@app.get("/api/analyses/{analysis_id}")
async def get_analysis(analysis_id: int):
    """Get a specific analysis by ID."""
    analysis = get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@app.get("/api/analyses/{analysis_id}/pdf")
async def download_pdf(analysis_id: int):
    """Generate and download PDF report for an analysis."""
    analysis = get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    pdf_path = f"/tmp/intel_report_{analysis_id}.pdf"
    generate_pdf(analysis, pdf_path)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"competitive_intel_{analysis['company']}_{analysis_id}.pdf"
    )


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Competitive Intelligence Engine running at http://localhost:8080\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
