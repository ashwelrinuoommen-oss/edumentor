"""
Test suite for Phase 9: Hybrid Answer Evaluation Engine
Validates:
1. Direct sentence-transformers semantic cosine similarity
2. LLM Judge 6-criteria evaluation (correctness, completeness, missing_points, misconceptions, reasoning, relevance)
3. Hybrid engine synthesis and score calibration
4. Structured JSON output schema compliance
5. Edge cases: blank answers, "I don't know", and misconceptions
"""

import unittest
from edumentor.evaluation import (
    compute_cosine_similarity,
    compute_semantic_similarity,
    evaluate_with_llm_judge,
    evaluate_hybrid_answer,
    evaluate_recall,
    VerdictString,
)
from edumentor.llm import LLMConfig


class TestHybridEvaluationPhase9(unittest.TestCase):
    def setUp(self):
        self.demo_config = LLMConfig(provider="demo")
        self.sample_concept = {
            "id": "c_sched_01",
            "title": "Process Scheduling",
            "canonical_explanation": (
                "Process scheduling is the OS activity that selects which process from the ready "
                "queue is allocated the CPU. It optimizes CPU utilization, throughput, and minimizes "
                "turnaround and response times using algorithms like Round Robin, FCFS, and SJF."
            ),
            "key_points": [
                "Selects process from ready queue",
                "Allocates CPU time",
                "Maximizes CPU utilization and throughput",
                "Algorithms like Round Robin, FCFS, SJF",
            ],
            "common_misconceptions": [
                "Process scheduling terminates running processes",
                "Process scheduling manages disk files directly",
            ],
        }

    def test_semantic_cosine_similarity_high_for_aligned_text(self):
        ref = "Process scheduling allocates the CPU to processes in the ready queue to ensure high throughput."
        student = "Process scheduling chooses ready processes and assigns the CPU to them to improve system throughput."
        sim = compute_cosine_similarity(ref, student)
        self.assertIsInstance(sim, float)
        self.assertGreaterEqual(sim, 0.70)

    def test_semantic_cosine_similarity_low_for_unrelated_text(self):
        ref = "Process scheduling allocates the CPU to processes in the ready queue."
        student = "Photosynthesis is the process by which green plants convert light energy into chemical energy."
        sim = compute_cosine_similarity(ref, student)
        self.assertIsInstance(sim, float)
        self.assertLess(sim, 0.40)

    def test_semantic_cosine_similarity_empty_inputs(self):
        self.assertEqual(compute_cosine_similarity("", "Some text"), 0.0)
        self.assertEqual(compute_cosine_similarity("Some text", ""), 0.0)
        self.assertEqual(compute_cosine_similarity("   ", "   "), 0.0)

    def test_llm_judge_six_criteria_evaluation(self):
        student_ans = (
            "Process scheduling is how the operating system picks a process from the ready queue "
            "and gives it CPU time so multiple programs can share the processor."
        )
        judge_res = evaluate_with_llm_judge(
            concept=self.sample_concept,
            student_answer=student_ans,
            llm_config=self.demo_config,
        )

        # Verify all 6 criteria are evaluated and present
        required_fields = [
            "correctness",
            "completeness",
            "missing_points",
            "misconceptions",
            "reasoning",
            "relevance",
            "score",
            "verdict",
        ]
        for field in required_fields:
            self.assertIn(field, judge_res, f"Missing required field: {field}")

        self.assertIsInstance(judge_res["correctness"], (int, float))
        self.assertIsInstance(judge_res["completeness"], (int, float))
        self.assertIsInstance(judge_res["missing_points"], list)
        self.assertIsInstance(judge_res["misconceptions"], list)
        self.assertIsInstance(judge_res["reasoning"], str)
        self.assertIsInstance(judge_res["relevance"], (int, float))
        self.assertIsInstance(judge_res["score"], (int, float))

    def test_hybrid_answer_evaluation_schema_and_verdict(self):
        student_ans = (
            "Process scheduling is the OS function that selects which ready process gets the CPU. "
            "It aims to maximize CPU utilization and throughput using scheduling algorithms."
        )
        res = evaluate_hybrid_answer(
            concept=self.sample_concept,
            student_answer=student_ans,
            llm_config=self.demo_config,
        )

        # Verify exact research schema
        self.assertIn("score", res)
        self.assertIn("correctness", res)
        self.assertIn("completeness", res)
        self.assertIn("missing_points", res)
        self.assertIn("misconceptions", res)
        self.assertIn("reasoning", res)
        self.assertIn("relevance", res)
        self.assertIn("verdict", res)

        # Verify value constraints
        self.assertGreaterEqual(res["score"], 0)
        self.assertLessEqual(res["score"], 100)
        self.assertGreaterEqual(res["correctness"], 0)
        self.assertLessEqual(res["correctness"], 100)
        self.assertGreaterEqual(res["completeness"], 0)
        self.assertLessEqual(res["completeness"], 100)
        self.assertGreaterEqual(res["relevance"], 0)
        self.assertLessEqual(res["relevance"], 100)

        # Verify verdict formatting and dual compatibility
        self.assertIn(res["verdict"], ["correct", "almost_correct", "wrong"])
        self.assertTrue(res["verdict"] in ["Correct", "Almost Correct", "Wrong", "correct", "almost_correct", "wrong"])

    def test_evaluate_recall_integration_with_hybrid_engine(self):
        student_ans = (
            "Process scheduling decides which process runs on the CPU from the ready queue. "
            "It uses algorithms like FCFS and Round Robin to maximize throughput."
        )
        res = evaluate_recall(
            concept=self.sample_concept,
            student_answer=student_ans,
            llm_config=self.demo_config,
        )

        # Check hybrid score and SM-2 quality grade
        self.assertIn("composite_score", res)
        self.assertIn("quality_q", res)
        self.assertIn("semantic_score", res)
        self.assertIn("llm_score", res)
        self.assertIn("hybrid_evaluation", res)

        # Quality grade must be between 0 and 5
        self.assertGreaterEqual(res["quality_q"], 0)
        self.assertLessEqual(res["quality_q"], 5)

        # Detailed breakdown in hybrid_evaluation
        hybrid = res["hybrid_evaluation"]
        self.assertIn("missing_points", hybrid)
        self.assertIn("misconceptions", hybrid)
        self.assertIn("relevance", hybrid)

    def test_blank_or_idk_evaluation(self):
        res = evaluate_hybrid_answer(
            concept=self.sample_concept,
            student_answer="I don't know",
            llm_config=self.demo_config,
        )
        self.assertEqual(res["score"], 0)
        self.assertEqual(res["correctness"], 0)
        self.assertEqual(res["completeness"], 0)
        self.assertEqual(res["verdict"], "wrong")

    def test_verdict_string_compatibility(self):
        v = VerdictString("almost_correct")
        self.assertEqual(v, "almost_correct")
        self.assertEqual(v, "Almost Correct")
        self.assertEqual(v, "almost correct")
        self.assertIn(v, ["Almost Correct", "Correct"])
        self.assertIn(v, ["almost_correct", "correct"])

        w = VerdictString("wrong")
        self.assertEqual(w, "wrong")
        self.assertEqual(w, "Wrong")
        self.assertIn(w, ["Wrong"])
        self.assertIn(w, ["wrong"])


if __name__ == "__main__":
    unittest.main()
