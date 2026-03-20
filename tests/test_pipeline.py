from llm_seo.chunking import chunk_text
from llm_seo.content import normalize_markdown
from llm_seo.optimizer import run_pipeline


def test_normalize_markdown_collapses_lines() -> None:
    normalized = normalize_markdown("a\n\n\n\nb\r\n")
    assert normalized == "a\n\nb\n"


def test_chunking_produces_chunks() -> None:
    text = "\n\n".join(["Paragraph with useful content " * 30 for _ in range(8)])
    chunks = chunk_text(text, min_tokens=90, max_tokens=150)
    assert len(chunks) >= 2
    assert all(chunk.token_estimate > 0 for chunk in chunks)


def test_pipeline_raw_text() -> None:
    doc = run_pipeline("# Topic\n\nThis is a helpful explanation for retrieval and citation.")
    assert doc.report.citation_score >= 0
    assert "AI-Ready Snippets" in doc.optimized_markdown
    assert isinstance(doc.faq_schema, dict)
