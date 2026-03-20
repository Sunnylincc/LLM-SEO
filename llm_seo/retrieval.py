from __future__ import annotations

from llm_seo.embeddings import cosine_similarity, embed_texts
from llm_seo.models import Chunk, RetrievalResult


def simulate_retrieval(chunks: list[Chunk], provider: str = "hash") -> list[RetrievalResult]:
    if not chunks:
        return []

    queries = [
        "What is X?",
        "Best tools for Y",
        "How does this work?",
    ]
    chunk_vectors = embed_texts([chunk.text for chunk in chunks], provider=provider)
    query_vectors = embed_texts(queries, provider=provider)

    results: list[RetrievalResult] = []
    for query, query_vector in zip(queries, query_vectors):
        scores = []
        for chunk, chunk_vector in zip(chunks, chunk_vectors):
            scores.append({"chunk_id": chunk.id, "score": cosine_similarity(query_vector, chunk_vector)})
        scores.sort(key=lambda item: item["score"], reverse=True)
        results.append(RetrievalResult(query=query, top_chunks=scores[:5]))

    return results
