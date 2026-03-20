from __future__ import annotations

import re
from collections import Counter

from llm_seo.models import Section


AMBIGUOUS_TERMS = {"it", "this", "that", "thing", "stuff"}


def build_qa(sections: list[Section]) -> list[dict[str, str]]:
    qa_pairs: list[dict[str, str]] = []
    for section in sections:
        answer = section.body.split("\n")[0].strip()
        if answer:
            qa_pairs.append(
                {
                    "question": f"What is {section.title}?",
                    "answer": answer,
                }
            )
    return qa_pairs


def build_faq_schema(qa_pairs: list[dict[str, str]]) -> dict:
    entities = []
    for pair in qa_pairs:
        entities.append(
            {
                "@type": "Question",
                "name": pair["question"],
                "acceptedAnswer": {"@type": "Answer", "text": pair["answer"]},
            }
        )
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities,
    }


def improve_clarity(markdown: str) -> tuple[str, list[str], list[str]]:
    findings: list[str] = []
    suggestions: list[str] = []

    words = re.findall(r"[A-Za-z']+", markdown.lower())
    counts = Counter(words)
    ambiguous_found = [word for word in AMBIGUOUS_TERMS if counts[word] > 0]
    if ambiguous_found:
        findings.append(f"Ambiguous pronouns/terms detected: {', '.join(sorted(ambiguous_found))}.")
        suggestions.append("Replace ambiguous references with explicit nouns.")

    long_sentences = [s for s in re.split(r"(?<=[.!?])\s+", markdown) if len(s.split()) > 35]
    if long_sentences:
        findings.append(f"{len(long_sentences)} long sentence(s) may reduce model comprehension.")
        suggestions.append("Break long sentences into shorter statements with one idea each.")

    optimized = markdown
    optimized = re.sub(r"\bit\b", "the subject", optimized, flags=re.IGNORECASE)
    optimized = re.sub(r"\bthis\b", "this concept", optimized, flags=re.IGNORECASE)

    return optimized, findings, suggestions
