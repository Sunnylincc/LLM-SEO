from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from llm_seo.optimizer import run_pipeline

app = FastAPI(title="LLM-SEO", version="0.1.0")
base_dir = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(directory=str(base_dir / "web" / "templates"))
app.mount("/static", StaticFiles(directory=str(base_dir / "web" / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None,
        },
    )


@app.post("/analyze", response_class=HTMLResponse)
def analyze(request: Request, source: str = Form(...), min_tokens: int = Form(300), max_tokens: int = Form(800)) -> HTMLResponse:
    doc = run_pipeline(source, min_tokens=min_tokens, max_tokens=max_tokens)
    result = {
        "source": doc.source,
        "citation_score": doc.report.citation_score,
        "score_explanation": doc.report.score_explanation,
        "suggestions": doc.report.suggestions,
        "low_signal_sections": doc.report.low_signal_sections,
        "chunks": [{"id": c.id, "token_estimate": c.token_estimate, "text": c.text[:220]} for c in doc.chunks],
        "retrieval_results": [
            {"query": r.query, "top_chunks": r.top_chunks} for r in doc.report.retrieval_results
        ],
        "optimized_markdown": doc.optimized_markdown,
        "report_json": json.dumps(
            {
                "citation_score": doc.report.citation_score,
                "suggestions": doc.report.suggestions,
                "structure_findings": doc.report.structure_findings,
            },
            indent=2,
        ),
    }
    return templates.TemplateResponse("index.html", {"request": request, "result": result})


@app.post("/api/analyze")
def analyze_api(payload: dict) -> JSONResponse:
    source = payload.get("source", "")
    min_tokens = int(payload.get("min_tokens", 300))
    max_tokens = int(payload.get("max_tokens", 800))
    doc = run_pipeline(source, min_tokens=min_tokens, max_tokens=max_tokens)
    return JSONResponse(
        {
            "source": doc.source,
            "citation_score": doc.report.citation_score,
            "score_explanation": doc.report.score_explanation,
            "suggestions": doc.report.suggestions,
            "optimized_markdown": doc.optimized_markdown,
        }
    )
