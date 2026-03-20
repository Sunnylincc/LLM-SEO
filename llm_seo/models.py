from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Section:
    level: int
    title: str
    body: str


@dataclass
class Chunk:
    id: str
    text: str
    token_estimate: int


@dataclass
class RetrievalResult:
    query: str
    top_chunks: list[dict[str, Any]]


@dataclass
class AnalysisReport:
    citation_score: float
    score_explanation: str
    suggestions: list[str]
    structure_findings: list[str]
    low_signal_sections: list[str]
    retrieval_results: list[RetrievalResult] = field(default_factory=list)


@dataclass
class ContentDocument:
    source: str
    raw_text: str
    normalized_markdown: str
    sections: list[Section]
    qa_pairs: list[dict[str, str]]
    faq_schema: dict[str, Any]
    chunks: list[Chunk]
    optimized_markdown: str
    report: AnalysisReport
