"""
Unit and Integration Tests for Phase 38 — Performance Optimizations
Covers:
1. Embeddings Caching (LRU cache, similarity caching, cache hits/misses)
2. LLM Repeated Calls Avoidance (Prompt response caching, TTL, error exclusions)
3. PDF Asynchronous Processing (Coroutines, non-blocking off event loop)
4. UI Incremental Rendering (Zero rerender on unchanged state, differential row append)
5. Avatar Lightweight Assets (SVG fallbacks, async decoding, lazy loading)
6. Animation Pausing (visibilitychange, IntersectionObserver, reduced motion CSS)
"""

import asyncio
import os
import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from edumentor.ai.embedding_cache import EmbeddingCache, embedding_cache
from edumentor.ai.llm_cache import LLMCache, llm_cache
from edumentor.evaluation import compute_semantic_similarity, compute_cosine_similarity
from edumentor.llm import call_llm
from edumentor.utils.pdf_utils import async_extract_text_from_pdf
from edumentor.extractor import async_extract_concepts_from_text


class TestEmbeddingCache(unittest.TestCase):
    def setUp(self):
        self.cache = EmbeddingCache(max_size=10)
        self.cache.clear()

    def test_embedding_cache_hit_and_miss(self):
        text = "Operating systems manage hardware resources."
        vec = np.array([0.1, 0.2, 0.3], dtype=np.float32)

        # Initially not cached
        self.assertIsNone(self.cache.get(text))
        self.assertIsNone(self.cache.get_embedding(text))
        stats = self.cache.get_stats()
        self.assertEqual(stats["misses"], 2)
        self.assertEqual(stats["hits"], 0)

        # Store vector
        self.cache.set_embedding(text, vec)
        self.assertEqual(self.cache.size(), 1)

        # Retrieve vector (Hit)
        cached_vec = self.cache.get_embedding(text)
        self.assertIsNotNone(cached_vec)
        np.testing.assert_array_equal(cached_vec, vec)

        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 2)

    def test_similarity_pair_caching(self):
        text_a = "Paging avoids external fragmentation."
        text_b = "Paging breaks memory into frames to prevent external fragmentation."

        self.assertIsNone(self.cache.get_similarity(text_a, text_b))
        self.cache.set_similarity(text_a, text_b, 0.88)

        # Order independent retrieval
        score_ab = self.cache.get_similarity(text_a, text_b)
        score_ba = self.cache.get_similarity(text_b, text_a)
        self.assertEqual(score_ab, 0.88)
        self.assertEqual(score_ba, 0.88)

    def test_lru_eviction(self):
        small_cache = EmbeddingCache(max_size=3)
        for i in range(4):
            small_cache.set(f"concept {i}", np.array([i, i], dtype=np.float32))

        # First item should be evicted
        self.assertEqual(small_cache.size(), 3)
        self.assertIsNone(small_cache.get("concept 0"))
        self.assertIsNotNone(small_cache.get("concept 3"))

    def test_get_or_compute(self):
        compute_mock = MagicMock(return_value=np.array([1.0, 2.0]))
        res1 = self.cache.get_or_compute("thrashing", compute_mock)
        self.assertEqual(compute_mock.call_count, 1)

        # Second call must retrieve from cache without executing compute_mock
        res2 = self.cache.get_or_compute("thrashing", compute_mock)
        self.assertEqual(compute_mock.call_count, 1)
        np.testing.assert_array_equal(res1, res2)

    @patch("edumentor.evaluation.get_sentence_transformer_model", return_value=None)
    def test_evaluation_uses_embedding_cache(self, mock_model):
        embedding_cache.clear()
        t1 = "Virtual memory decouples logical address space from physical memory."
        t2 = "Virtual memory allows processes to run with non contiguous physical pages."

        initial_sim_hits = embedding_cache.sim_hits
        # First call computes via TF-IDF fallback and caches similarity
        score1 = compute_semantic_similarity(t1, t2)
        self.assertGreater(score1, 0.0)

        # Second call with exact same inputs must hit similarity cache
        score2 = compute_semantic_similarity(t1, t2)
        self.assertEqual(score1, score2)
        self.assertGreater(embedding_cache.sim_hits, initial_sim_hits)


class TestLLMCache(unittest.TestCase):
    def setUp(self):
        self.cache = LLMCache(max_size=10, ttl_seconds=60)
        self.cache.clear()

    def test_llm_cache_set_and_get(self):
        provider = "gemini"
        model = "gemini-1.5-flash"
        temp = 0.3
        sys_prompt = "You are a teacher."
        prompt = "Explain page tables."
        response = "A page table maps virtual addresses to physical frame numbers."

        # Miss
        self.assertIsNone(self.cache.get(provider, model, temp, sys_prompt, prompt))
        stats = self.cache.get_stats()
        self.assertEqual(stats["misses"], 1)

        # Set
        self.cache.set(provider, model, temp, sys_prompt, prompt, response)

        # Hit
        cached_resp = self.cache.get(provider, model, temp, sys_prompt, prompt)
        self.assertEqual(cached_resp, response)
        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["hit_rate_percent"], 50.0)

    def test_do_not_cache_error_messages(self):
        from edumentor.utils.error_handler import ERROR_LLM_MSG
        self.cache.set("gemini", "model", 0.3, "sys", "prompt", ERROR_LLM_MSG)
        self.assertEqual(self.cache.size(), 0)
        self.assertIsNone(self.cache.get("gemini", "model", 0.3, "sys", "prompt"))

    @patch("edumentor.llm._execute_provider_call")
    def test_call_llm_caches_duplicate_calls(self, mock_exec):
        mock_exec.return_value = "Detailed explanation of deadlock conditions."
        llm_cache.clear()

        prompt = "What are Coffman conditions for deadlocks?"
        # 1st call executes provider
        res1 = call_llm(prompt, use_cache=True)
        self.assertEqual(res1, "Detailed explanation of deadlock conditions.")
        self.assertEqual(mock_exec.call_count, 1)

        # 2nd call should be served from cache without calling provider again!
        res2 = call_llm(prompt, use_cache=True)
        self.assertEqual(res2, "Detailed explanation of deadlock conditions.")
        self.assertEqual(mock_exec.call_count, 1)  # NOT incremented!

        # 3rd call with use_cache=False forces re-call
        res3 = call_llm(prompt, use_cache=False)
        self.assertEqual(res3, "Detailed explanation of deadlock conditions.")
        self.assertEqual(mock_exec.call_count, 2)


class TestAsyncPDFProcessing(unittest.TestCase):
    @patch("edumentor.utils.pdf_utils.extract_text_from_pdf")
    def test_async_extract_text_coroutine(self, mock_sync_extract):
        mock_sync_extract.return_value = ("Operating Systems", "Virtual memory concepts.")

        async def run():
            return await async_extract_text_from_pdf(b"%PDF-1.4 dummy content")

        title, text = asyncio.run(run())
        self.assertEqual(title, "Operating Systems")
        self.assertIn("Virtual memory", text)
        mock_sync_extract.assert_called_once_with(b"%PDF-1.4 dummy content")

    @patch("edumentor.extractor.extract_concepts_from_text")
    def test_async_extract_concepts_coroutine(self, mock_sync_extract):
        mock_sync_extract.return_value = (
            [{"id": "p1", "name": "Paging", "description": "Memory paging"}],
            [("p1", "prereq")]
        )

        async def run():
            return await async_extract_concepts_from_text("Long text content for concepts...")

        concepts, deps = asyncio.run(run())
        self.assertIsInstance(concepts, list)
        self.assertEqual(len(concepts), 1)
        self.assertEqual(concepts[0]["name"], "Paging")
        mock_sync_extract.assert_called_once()


class TestUIAndAvatarOptimizations(unittest.TestCase):
    def test_app_js_contains_incremental_rendering_and_avatar_attributes(self):
        with open("static/js/app.js", "r", encoding="utf-8") as f:
            content = f.read()

        # Incremental chat rendering checks
        self.assertIn("_chatRenderTracker", content)
        self.assertIn("buildMessageRow", content)
        self.assertIn("renderChatFeed", content)
        self.assertIn("DocumentFragment", content)

        # Avatar optimization checks
        self.assertIn("loading=\"lazy\"", content)
        self.assertIn("decoding=\"async\"", content)
        self.assertIn("avatar.svg", content)

        # Visibility animation pausing checks
        self.assertIn("initAnimationVisibilityOptimizer", content)
        self.assertIn("visibilitychange", content)
        self.assertIn("IntersectionObserver", content)
        self.assertIn("animations-paused", content)

    def test_avatar_svg_is_lightweight(self):
        svg_path = "static/assets/teacher_avatar/avatar.svg"
        self.assertTrue(os.path.exists(svg_path))
        file_size = os.path.getsize(svg_path)
        # Vector SVG should be extremely lightweight (< 2 KB)
        self.assertLess(file_size, 2048)

    def test_css_contains_animation_pausing_rules(self):
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn(".animations-paused *", css)
        self.assertIn(".animation-paused", css)
        self.assertIn("animation-play-state: paused !important", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn("content-visibility: auto", css)


if __name__ == "__main__":
    unittest.main()
