from __future__ import annotations

import json
from pathlib import Path

import typer
import uvicorn

from llm_seo.api.app import app as api_app
from llm_seo.optimizer import run_pipeline

app = typer.Typer(help="LLM-SEO CLI: optimize content for LLM discoverability and citations")
state_app = typer.Typer(help="Workflow commands")
app.add_typer(state_app)

STATE_DIR = Path(".llm_seo")
STATE_FILE = STATE_DIR / "state.json"
REPORT_FILE = STATE_DIR / "report.json"
OPTIMIZED_FILE = STATE_DIR / "optimized.md"


def _ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


@state_app.command("ingest")
def ingest(source: str) -> None:
    _ensure_state_dir()
    STATE_FILE.write_text(json.dumps({"source": source}, indent=2), encoding="utf-8")
    typer.echo(f"Ingested source: {source}")


@state_app.command("analyze")
def analyze(
    min_tokens: int = typer.Option(300, help="Minimum target tokens per chunk"),
    max_tokens: int = typer.Option(800, help="Maximum target tokens per chunk"),
    provider: str = typer.Option("hash", help="Embedding provider: hash | openai | local"),
) -> None:
    if not STATE_FILE.exists():
        raise typer.BadParameter("No source ingested. Run: llm-seo ingest <file/url/raw text>")

    source = json.loads(STATE_FILE.read_text(encoding="utf-8"))["source"]
    document = run_pipeline(source, min_tokens=min_tokens, max_tokens=max_tokens, provider=provider)

    report_payload = {
        "source": document.source,
        "citation_score": document.report.citation_score,
        "score_explanation": document.report.score_explanation,
        "suggestions": document.report.suggestions,
        "structure_findings": document.report.structure_findings,
        "low_signal_sections": document.report.low_signal_sections,
        "faq_schema": document.faq_schema,
        "retrieval_results": [
            {"query": result.query, "top_chunks": result.top_chunks}
            for result in document.report.retrieval_results
        ],
        "chunks": [
            {"id": chunk.id, "token_estimate": chunk.token_estimate, "preview": chunk.text[:180]}
            for chunk in document.chunks
        ],
    }
    _ensure_state_dir()
    REPORT_FILE.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    OPTIMIZED_FILE.write_text(document.optimized_markdown, encoding="utf-8")

    typer.echo(f"Citation score: {document.report.citation_score}")
    typer.echo(f"Report written to {REPORT_FILE}")
    typer.echo(f"Optimized markdown written to {OPTIMIZED_FILE}")


@state_app.command("optimize")
def optimize(output: str = typer.Option("optimized_output.md", help="Output markdown file")) -> None:
    if not OPTIMIZED_FILE.exists():
        raise typer.BadParameter("No optimized content found. Run: llm-seo analyze")
    Path(output).write_text(OPTIMIZED_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    typer.echo(f"Optimized markdown exported to {output}")


@state_app.command("serve")
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    uvicorn.run(api_app, host=host, port=port)


if __name__ == "__main__":
    app()
