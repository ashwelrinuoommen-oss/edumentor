"""
High-Performance Embedding Cache Subsystem (Phase 38).
Caches vector embeddings and semantic similarity computations to eliminate
redundant transformer model inferences for identical concepts and responses.
"""

import hashlib
import threading
from typing import Dict, Any, Optional, List, Tuple, Callable
import numpy as np


class EmbeddingCache:
    """
    Thread-safe in-memory LRU embedding cache.
    Caches vector embeddings by normalized text hash to avoid repeated transformer passes.
    """
    def __init__(self, max_size: int = 2000):
        self.max_size = max_size
        self._cache: Dict[str, np.ndarray] = {}
        self._similarity_cache: Dict[str, float] = {}
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.sim_hits = 0
        self.sim_misses = 0

    @staticmethod
    def _hash_text(text: str) -> str:
        """Compute SHA-256 fingerprint of normalized text."""
        normalized = text.strip().lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def _hash_pair(text_a: str, text_b: str) -> str:
        """Compute composite fingerprint for a pair of texts (order-invariant)."""
        norm_a = text_a.strip().lower()
        norm_b = text_b.strip().lower()
        if norm_a > norm_b:
            norm_a, norm_b = norm_b, norm_a
        composite = f"{norm_a}|||{norm_b}"
        return hashlib.sha256(composite.encode("utf-8")).hexdigest()

    def get(self, text: str) -> Optional[np.ndarray]:
        """Retrieve cached embedding vector for text."""
        key = self._hash_text(text)
        with self._lock:
            if key in self._cache:
                self.hits += 1
                # Move to end for LRU behavior
                val = self._cache.pop(key)
                self._cache[key] = val
                return val
            self.misses += 1
            return None

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Alias for get(text)."""
        return self.get(text)

    def set(self, text: str, embedding: Any) -> None:
        """Store embedding vector in cache."""
        key = self._hash_text(text)
        if not isinstance(embedding, np.ndarray):
            embedding = np.array(embedding, dtype=np.float32)

        with self._lock:
            if key in self._cache:
                self._cache.pop(key)
            elif len(self._cache) >= self.max_size:
                # Evict oldest entry (FIFO / LRU)
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            self._cache[key] = embedding

    def set_embedding(self, text: str, embedding: Any) -> None:
        """Alias for set(text, embedding)."""
        self.set(text, embedding)

    def size(self) -> int:
        """Return current number of cached embeddings."""
        with self._lock:
            return len(self._cache)

    def get_or_compute(self, text: str, compute_fn: Callable[[str], Any]) -> np.ndarray:
        """Retrieve from cache or compute via transformer and cache."""
        cached = self.get(text)
        if cached is not None:
            return cached

        vector = compute_fn(text)
        self.set(text, vector)
        return self._cache[self._hash_text(text)]

    def get_similarity(self, text_a: str, text_b: str) -> Optional[float]:
        """Retrieve cached similarity score for text pair."""
        key = self._hash_pair(text_a, text_b)
        with self._lock:
            if key in self._similarity_cache:
                self.sim_hits += 1
                return self._similarity_cache[key]
            self.sim_misses += 1
            return None

    def set_similarity(self, text_a: str, text_b: str, score: float) -> None:
        """Cache similarity score for text pair."""
        key = self._hash_pair(text_a, text_b)
        with self._lock:
            if len(self._similarity_cache) >= self.max_size:
                oldest = next(iter(self._similarity_cache))
                del self._similarity_cache[oldest]
            self._similarity_cache[key] = float(score)

    def get_stats(self) -> Dict[str, Any]:
        """Return cache performance statistics."""
        with self._lock:
            total_lookups = self.hits + self.misses
            hit_rate = (self.hits / total_lookups * 100.0) if total_lookups > 0 else 0.0
            return {
                "size": len(self._cache),
                "similarity_cache_size": len(self._similarity_cache),
                "hits": self.hits,
                "misses": self.misses,
                "total_lookups": total_lookups,
                "hit_rate_percent": round(hit_rate, 2),
                "similarity_hits": self.sim_hits,
                "similarity_misses": self.sim_misses,
                "max_size": self.max_size
            }

    def clear(self) -> None:
        """Clear all cached embeddings and statistics."""
        with self._lock:
            self._cache.clear()
            self._similarity_cache.clear()
            self.hits = 0
            self.misses = 0
            self.sim_hits = 0
            self.sim_misses = 0


# Global singleton cache instance
embedding_cache = EmbeddingCache()
