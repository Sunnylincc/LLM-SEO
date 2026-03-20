from __future__ import annotations

import math

from llm_seo.models import Chunk


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text.split()) * 1.3))


def chunk_text(markdown: str, min_tokens: int = 300, max_tokens: int = 800) -> list[Chunk]:
    paragraphs = [p.strip() for p in markdown.split("\n\n") if p.strip()]
    chunks: list[Chunk] = []
    current: list[str] = []

    def flush() -> None:
        if not current:
            return
        text = "\n\n".join(current)
        chunks.append(
            Chunk(id=f"chunk-{len(chunks)+1}", text=text, token_estimate=estimate_tokens(text))
        )

    for para in paragraphs:
        candidate = "\n\n".join(current + [para])
        tokens = estimate_tokens(candidate)
        if tokens > max_tokens and current:
            flush()
            current = [para]
        else:
            current.append(para)

        if estimate_tokens("\n\n".join(current)) >= min_tokens:
            flush()
            current = []

    flush()
    return chunks
