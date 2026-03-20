# LLM-SEO

LLM-SEO is an open-source CLI + local web UI to optimize content so it is more discoverable, understandable, and citable by LLMs (ChatGPT, Claude, Perplexity).

## What it does

- **Content ingestion** from markdown file, URL, or raw text.
- **Semantic structuring** into headings, Q&A pairs, and FAQ schema.
- **Chunking engine** tuned for LLM retrieval windows (default 300–800 token estimate).
- **Embedding + retrieval simulation** with configurable embedding provider (`hash`, `openai`, `local`).
- **Citation scoring system** with explanation and actionable suggestions.
- **AI-ready snippets** generator (authoritative answers, definitions, bullet summaries).
- **Optimization recommendations** for low-signal sections and ambiguous phrasing.
- Outputs optimized markdown and JSON report.

## Tech stack

- Python package + CLI (Typer)
- FastAPI backend
- Jinja-based local dashboard UI
- Optional OpenAI embeddings or local sentence-transformers embeddings

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Optional providers:

```bash
pip install -e .[openai]
pip install -e .[local-embeddings]
```

## CLI workflow

```bash
llm-seo ingest content.md
llm-seo analyze --min-tokens 300 --max-tokens 800 --provider hash
llm-seo optimize --output optimized_output.md
llm-seo serve --host 127.0.0.1 --port 8000
```

### Commands

- `llm-seo ingest <file/url/raw text>`
- `llm-seo analyze`
- `llm-seo optimize`
- `llm-seo serve`

Generated artifacts are stored in `.llm_seo/`:

- `state.json` (input source)
- `report.json` (citation score, retrieval simulation, suggestions)
- `optimized.md` (optimized markdown + AI-ready snippets)

## API

- `GET /` dashboard
- `POST /analyze` dashboard form submit
- `POST /api/analyze` JSON API endpoint

Example request:

```json
{
  "source": "# Retrieval-Augmented Generation\nRAG improves grounding...",
  "min_tokens": 300,
  "max_tokens": 800
}
```

## Modular architecture

Core modules:

- `llm_seo/content.py` ingestion + normalization
- `llm_seo/semantic.py` structure transforms + clarity checks
- `llm_seo/chunking.py` chunk splitting
- `llm_seo/embeddings.py` embedding providers
- `llm_seo/retrieval.py` retrieval simulation
- `llm_seo/scoring.py` citation scoring
- `llm_seo/optimizer.py` end-to-end orchestration
- `llm_seo/api/app.py` web server and dashboard
- `llm_seo/cli.py` CLI entrypoint

This separation keeps the project ready for future features like auto-publishing, agent workflows, and continuous monitoring.
