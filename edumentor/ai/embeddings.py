"""
Embeddings and Semantic Vector Cosine engine using sentence-transformers with fallback.
"""

from typing import List, Optional
from edumentor.evaluation import compute_semantic_similarity, get_sentence_transformer_model
from edumentor.ai.embedding_cache import EmbeddingCache, embedding_cache


def get_embedding_score(student_answer: str, canonical_text: str, key_points: Optional[List[str]] = None) -> float:
    """Compute normalized 0-100 semantic similarity using EmbeddingCache."""
    return compute_semantic_similarity(student_answer, canonical_text, key_points)


__all__ = [
    "get_embedding_score",
    "compute_semantic_similarity",
    "get_sentence_transformer_model",
    "EmbeddingCache",
    "embedding_cache"
]
