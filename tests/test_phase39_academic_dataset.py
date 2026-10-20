"""
Unit and Integration Tests for Phase 39 — Academic Dataset & Engine Validation
Covers:
1. Academic benchmark dataset integrity across 5 core CS domains
2. Extraction and evaluation of Concept, Reference explanation, Student answer, Human evaluation
3. Calculation of Semantic score, LLM score, and Hybrid score
4. Evaluation engine accuracy and statistical correlation against human judgment
"""

import os
import unittest
from edumentor.data.academic_dataset import get_academic_dataset, ACADEMIC_BENCHMARK_DATASET
from edumentor.ai.benchmark_runner import run_benchmark, evaluate_dataset_entry


class TestPhase39AcademicDataset(unittest.TestCase):
    def setUp(self):
        self.dataset = get_academic_dataset()

    def test_dataset_contains_all_five_cs_domains(self):
        """Verify the academic dataset contains all 5 required domains."""
        subjects = set(item["subject"] for item in self.dataset)
        expected_subjects = {
            "Operating Systems",
            "Computer Networks",
            "DBMS",
            "Data Structures",
            "Software Engineering"
        }
        self.assertTrue(
            expected_subjects.issubset(subjects),
            f"Dataset must include all 5 domains. Found: {subjects}"
        )

    def test_dataset_entries_have_required_fields(self):
        """Verify each entry contains Concept, Reference explanation, Student answer, Human evaluation."""
        self.assertGreaterEqual(len(self.dataset), 25, "Dataset should have at least 25 realistic samples")

        for entry in self.dataset:
            entry_id = entry.get("id", "UNKNOWN")
            self.assertIn("subject", entry, f"{entry_id} missing subject")
            self.assertIn("concept", entry, f"{entry_id} missing concept")
            self.assertIn("reference_explanation", entry, f"{entry_id} missing reference_explanation")
            self.assertIn("student_answer", entry, f"{entry_id} missing student_answer")
            self.assertIn("human_evaluation", entry, f"{entry_id} missing human_evaluation")

            # Check human evaluation subfields
            h_eval = entry["human_evaluation"]
            self.assertIn("score", h_eval, f"{entry_id} human evaluation missing score")
            self.assertIn("verdict", h_eval, f"{entry_id} human evaluation missing verdict")
            self.assertIn("feedback", h_eval, f"{entry_id} human evaluation missing feedback")
            self.assertIn(h_eval["verdict"], ["correct", "almost_correct", "wrong"])
            self.assertTrue(0.0 <= h_eval["score"] <= 100.0)

    def test_single_entry_evaluation_generates_all_three_scores(self):
        """Verify single entry generates Semantic score, LLM score, and Hybrid score."""
        sample = self.dataset[0]
        evaluated = evaluate_dataset_entry(sample)

        self.assertIsNotNone(evaluated["semantic_score"], "Semantic score must be calculated")
        self.assertIsNotNone(evaluated["llm_score"], "LLM score must be calculated")
        self.assertIsNotNone(evaluated["hybrid_score"], "Hybrid score must be calculated")
        self.assertIn(evaluated["system_verdict"], ["correct", "almost_correct", "wrong"])

        self.assertTrue(0.0 <= evaluated["semantic_score"] <= 100.0)
        self.assertTrue(0.0 <= evaluated["llm_score"] <= 100.0)
        self.assertTrue(0.0 <= evaluated["hybrid_score"] <= 100.0)

    def test_benchmark_runner_and_human_correlation(self):
        """Verify the evaluation engine demonstrates strong statistical correlation with human judgment."""
        evaluated_entries, metrics = run_benchmark(self.dataset[:15])  # fast subset validation

        hybrid_metrics = metrics["hybrid_vs_human"]
        pearson_r = hybrid_metrics["pearson_r"]
        spearman_rho = hybrid_metrics["spearman_rho"]
        verdict_accuracy = hybrid_metrics["verdict_accuracy_percent"]
        mae = hybrid_metrics["mae"]

        # Engine validation benchmarks
        self.assertGreaterEqual(pearson_r, 0.75, f"Pearson r must be >= 0.75, got {pearson_r}")
        self.assertGreaterEqual(spearman_rho, 0.75, f"Spearman rho must be >= 0.75, got {spearman_rho}")
        self.assertGreaterEqual(verdict_accuracy, 60.0, f"Verdict accuracy must be >= 60%, got {verdict_accuracy}%")
        self.assertLessEqual(mae, 25.0, f"MAE must be <= 25 points, got {mae}")


if __name__ == "__main__":
    unittest.main()
