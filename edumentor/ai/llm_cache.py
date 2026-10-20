"""
High-Performance LLM Response Cache Subsystem (Phase 38).
Avoids repeated API and inference calls for identical pedagogical prompts,
reducing token costs, eliminating network overhead, and providing 0ms responses.
"""

import hashlib
import threading
import time
from typing import Dict, Any, Optional, Tuple
from edumentor.utils.error_handler import ERROR_LLM_MSG


class LLMCacheEntry:
    def __init__(self, response: str, timestamp: float):
        self.response = response
        self.timestamp = timestamp


class LLMCache:
    """
    Thread-safe in-memory LRU cache with TTL expiration for LLM completions.
    Avoids repeated external network and inference calls.
    """
    def __init__(self, max_size: int = 1000, ttl_seconds: float = 3600.0):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, LLMCacheEntry] = {}
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    @staticmethod
    def compute_cache_key(
        provider: str,
        model: str,
        temperature: float,
        system_prompt: str,
        prompt: str
    ) -> str:
        """Construct normalized SHA-256 fingerprint for the generation request."""
        clean_provider = (provider or "default").lower().strip()
        clean_model = (model or "default").lower().strip()
        clean_sys = system_prompt.strip()
        clean_prompt = prompt.strip()
        temp_rounded = round(float(temperature), 2)

        composite = f"{clean_provider}|{clean_model}|{temp_rounded}|{clean_sys}\n---\n{clean_prompt}"
        return hashlib.sha256(composite.encode("utf-8")).hexdigest()

    def get(
        self,
        provider: str,
        model: str,
        temperature: float,
        system_prompt: str,
        prompt: str
    ) -> Optional[str]:
        """Retrieve cached response if present and unexpired."""
        key = self.compute_cache_key(provider, model, temperature, system_prompt, prompt)
        now = time.time()

        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                # Check TTL expiration
                if self.ttl_seconds > 0 and (now - entry.timestamp) > self.ttl_seconds:
                    del self._cache[key]
                    self.misses += 1
                    return None

                self.hits += 1
                # Move to end for LRU refresh
                val = self._cache.pop(key)
                self._cache[key] = val
                return val.response

            self.misses += 1
            return None

    def set(
        self,
        provider: str,
        model: str,
        temperature: float,
        system_prompt: str,
        prompt: str,
        response: str
    ) -> None:
        """Store completion in cache. Excludes error messages."""
        if not response or response == ERROR_LLM_MSG or response.startswith("Error connecting to"):
            return

        key = self.compute_cache_key(provider, model, temperature, system_prompt, prompt)
        now = time.time()

        with self._lock:
            if key in self._cache:
                self._cache.pop(key)
            elif len(self._cache) >= self.max_size:
                # Evict oldest entry (LRU)
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

            self._cache[key] = LLMCacheEntry(response=response, timestamp=now)

    def size(self) -> int:
        """Return current count of cached LLM responses."""
        with self._lock:
            return len(self._cache)

    def __len__(self) -> int:
        return self.size()

    def get_stats(self) -> Dict[str, Any]:
        """Return cache performance statistics."""
        with self._lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100.0) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "total_lookups": total,
                "hit_rate_percent": round(hit_rate, 2),
                "ttl_seconds": self.ttl_seconds
            }

    def clear(self) -> None:
        """Clear all cached LLM completions and reset stats."""
        with self._lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0


# Global singleton instance
llm_cache = LLMCache()
