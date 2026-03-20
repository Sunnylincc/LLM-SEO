from __future__ import annotations

import hashlib
import math
import os
from typing import Sequence


def _hash_embedding(text: str, dims: int = 128) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values = [(digest[i % len(digest)] / 255.0) for i in range(dims)]
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


def embed_texts(texts: Sequence[str], provider: str = "hash") -> list[list[float]]:
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for provider=openai")
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(model="text-embedding-3-small", input=list(texts))
        return [item.embedding for item in response.data]

    if provider == "local":
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        vectors = model.encode(list(texts), normalize_embeddings=True)
        return [list(vec) for vec in vectors]

    return [_hash_embedding(text) for text in texts]


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)
