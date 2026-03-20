from __future__ import annotations

from statistics import mean

from llm_seo.models import RetrievalResult, Section


def score_citation_likelihood(
    sections: list[Section],
    retrieval_results: list[RetrievalResult],
    structure_findings: list[str],
) -> tuple[float, str, list[str], list[str]]:
    suggestions: list[str] = []
    low_signal_sections: list[str] = []

    section_lengths = {section.title: len(section.body.split()) for section in sections}
    for title, length in section_lengths.items():
        if length < 25:
            low_signal_sections.append(title)

    retrieval_scores = [entry["score"] for result in retrieval_results for entry in result.top_chunks[:3]]
    avg_retrieval = mean(retrieval_scores) if retrieval_scores else 0.0

    score = 50.0
    score += min(20.0, len(sections) * 2.5)
    score += min(20.0, avg_retrieval * 35)
    score -= min(15.0, len(structure_findings) * 4)
    score -= min(10.0, len(low_signal_sections) * 1.5)

    if low_signal_sections:
        suggestions.append("Expand low-signal sections with concrete facts, examples, and metrics.")
    if len(sections) < 3:
        suggestions.append("Add more headings to improve semantic hierarchy for retrieval.")
    if avg_retrieval < 0.3:
        suggestions.append("Add explicit definitions and tool comparisons to strengthen retrieval matches.")

    bounded = max(0.0, min(100.0, round(score, 2)))
    explanation = (
        f"Score combines structure depth ({len(sections)} sections), retrieval relevance "
        f"(avg top-3 cosine={avg_retrieval:.2f}), clarity penalties ({len(structure_findings)}), "
        f"and low-signal penalties ({len(low_signal_sections)})."
    )

    return bounded, explanation, suggestions, low_signal_sections
