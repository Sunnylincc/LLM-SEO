from __future__ import annotations

import json

from llm_seo.chunking import chunk_text
from llm_seo.content import extract_sections, load_input, normalize_markdown
from llm_seo.models import AnalysisReport, ContentDocument, Section
from llm_seo.retrieval import simulate_retrieval
from llm_seo.scoring import score_citation_likelihood
from llm_seo.semantic import build_faq_schema, build_qa, improve_clarity


def build_ai_ready_snippets(sections: list[Section]) -> dict[str, list[str]]:
    authoritative = [
        f"{section.title}: {section.body.splitlines()[0][:220]}" for section in sections if section.body
    ][:5]
    definitions = [f"{section.title} is {section.body.splitlines()[0][:180]}" for section in sections if section.body][
        :5
    ]
    bullet_summaries = [f"- {section.title}: {len(section.body.split())} words" for section in sections][:8]
    return {
        "authoritative_answers": authoritative,
        "definitions": definitions,
        "bullet_summaries": bullet_summaries,
    }


def run_pipeline(source: str, min_tokens: int = 300, max_tokens: int = 800, provider: str = "hash") -> ContentDocument:
    src, raw = load_input(source)
    normalized = normalize_markdown(raw)

    sections = [Section(level=l, title=t, body=b) for l, t, b in extract_sections(normalized)]
    qa_pairs = build_qa(sections)
    faq_schema = build_faq_schema(qa_pairs)

    optimized_markdown, structure_findings, clarity_suggestions = improve_clarity(normalized)
    chunks = chunk_text(optimized_markdown, min_tokens=min_tokens, max_tokens=max_tokens)
    retrieval_results = simulate_retrieval(chunks, provider=provider)

    score, explanation, score_suggestions, low_signal_sections = score_citation_likelihood(
        sections=sections,
        retrieval_results=retrieval_results,
        structure_findings=structure_findings,
    )
    suggestions = clarity_suggestions + score_suggestions

    snippets = build_ai_ready_snippets(sections)
    optimized_with_snippets = (
        optimized_markdown
        + "\n\n## AI-Ready Snippets\n\n"
        + "\n".join(snippets["bullet_summaries"])
        + "\n\n```json\n"
        + json.dumps(snippets, indent=2)
        + "\n```\n"
    )

    report = AnalysisReport(
        citation_score=score,
        score_explanation=explanation,
        suggestions=suggestions,
        structure_findings=structure_findings,
        low_signal_sections=low_signal_sections,
        retrieval_results=retrieval_results,
    )

    return ContentDocument(
        source=src,
        raw_text=raw,
        normalized_markdown=normalized,
        sections=sections,
        qa_pairs=qa_pairs,
        faq_schema=faq_schema,
        chunks=chunks,
        optimized_markdown=optimized_with_snippets,
        report=report,
    )
