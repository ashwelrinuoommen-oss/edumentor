import unittest
from edumentor.evaluation import compute_semantic_similarity, evaluate_recall
from edumentor.llm import LLMConfig


class TestEvaluation(unittest.TestCase):
    def test_semantic_similarity_exact_or_close(self):
        canonical = "Virtual memory isolates process address spaces and translates addresses via page tables."
        student = "Virtual memory isolates each process address space and translates addresses using page tables."
        score = compute_semantic_similarity(student, canonical, ["process isolation", "page tables"])
        self.assertGreater(score, 60.0)

    def test_blank_or_idk_response(self):
        concept = {
            "id": "c1",
            "title": "Paging",
            "canonical_explanation": "Splits memory into fixed pages and frames.",
            "key_points": ["Fixed-size blocks", "Page tables"]
        }
        res = evaluate_recall(concept, "I don't know")
        self.assertEqual(res["quality_q"], 0)
        self.assertEqual(res["verdict"], "Wrong")

    def test_evaluate_recall_strong(self):
        concept = {
            "id": "c1",
            "title": "Virtual Memory",
            "canonical_explanation": "Translates virtual addresses to physical RAM and provides memory protection.",
            "key_points": ["Address translation", "Process memory isolation", "MMU support"]
        }
        answer = "Virtual memory translates virtual addresses into physical RAM frames using the MMU and page tables. It gives every process its own isolated memory space."
        res = evaluate_recall(concept, answer, llm_config=LLMConfig(provider="demo"))
        self.assertGreaterEqual(res["composite_score"], 65.0)
        self.assertIn(res["verdict"], ["Correct", "Almost Correct"])
        self.assertTrue(len(res["strengths"]) > 0)


if __name__ == "__main__":
    unittest.main()
