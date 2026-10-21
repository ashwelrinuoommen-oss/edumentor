"""
Unit and integration tests for Phase 10 — Mastery Engine.
Verifies multidimensional concept scoring, curriculum mastery calculation,
newly-mastered celebratory transition detection, and orchestrator integration.
"""

import unittest
from edumentor.services.mastery_service import MasteryService
from edumentor.orchestrator import EduMentorOrchestrator


class TestMasteryEnginePhase10(unittest.TestCase):
    def setUp(self):
        self.orch = EduMentorOrchestrator(student_name="Ashwel")

    def test_evaluate_unseen_concept(self):
        c = {
            "id": "c_unseen",
            "title": "Virtual Memory",
            "total_reviews": 0,
            "last_quality_score": 0,
            "consecutive_correct": 0,
            "interval_days": 0,
            "repetition_n": 0
        }
        res = MasteryService.evaluate_concept_mastery(c)
        self.assertEqual(res["mastery_score"], 0)
        self.assertEqual(res["mastery_level"], "Unseen")
        self.assertFalse(res["is_mastered"])
        self.assertEqual(res["recommended_action"], "introduce")
        self.assertEqual(res["components"]["recall_quality"], 0)

    def test_evaluate_learning_concept(self):
        c = {
            "id": "c_weak",
            "title": "Deadlocks",
            "total_reviews": 1,
            "last_quality_score": 2,
            "consecutive_correct": 0,
            "interval_days": 1,
            "repetition_n": 0,
            "easiness_factor": 2.1
        }
        res = MasteryService.evaluate_concept_mastery(c)
        self.assertLess(res["mastery_score"], 45)
        self.assertEqual(res["mastery_level"], "Learning")
        self.assertFalse(res["is_mastered"])
        self.assertEqual(res["recommended_action"], "review_notes")

    def test_evaluate_practicing_concept(self):
        c = {
            "id": "c_practice",
            "title": "Process Scheduling",
            "total_reviews": 1,
            "last_quality_score": 3,
            "consecutive_correct": 1,
            "interval_days": 1,
            "repetition_n": 1,
            "easiness_factor": 2.5
        }
        res = MasteryService.evaluate_concept_mastery(c)
        self.assertGreaterEqual(res["mastery_score"], 38)
        self.assertEqual(res["mastery_level"], "Practicing")
        self.assertFalse(res["is_mastered"])
        self.assertEqual(res["recommended_action"], "active_recall")

    def test_evaluate_proficient_concept(self):
        c = {
            "id": "c_proficient",
            "title": "Processes",
            "total_reviews": 2,
            "last_quality_score": 4,
            "consecutive_correct": 1,
            "interval_days": 6,
            "repetition_n": 2,
            "easiness_factor": 2.5
        }
        res = MasteryService.evaluate_concept_mastery(c)
        self.assertGreaterEqual(res["mastery_score"], 68)
        self.assertEqual(res["mastery_level"], "Proficient")
        self.assertFalse(res["is_mastered"])
        self.assertEqual(res["recommended_action"], "reinforce")

    def test_evaluate_mastered_concept(self):
        c = {
            "id": "c_mastered",
            "title": "CPU Scheduling Algorithms",
            "total_reviews": 3,
            "last_quality_score": 5,
            "consecutive_correct": 2,
            "interval_days": 14,
            "repetition_n": 3,
            "easiness_factor": 2.6
        }
        res = MasteryService.evaluate_concept_mastery(c)
        self.assertGreaterEqual(res["mastery_score"], 85)
        self.assertEqual(res["mastery_level"], "Mastered")
        self.assertTrue(res["is_mastered"])
        self.assertEqual(res["recommended_action"], "ready_for_next")

    def test_prerequisite_health_calculation(self):
        c = {
            "id": "c_child",
            "title": "Multithreading",
            "total_reviews": 1,
            "last_quality_score": 4,
            "consecutive_correct": 1,
            "interval_days": 1,
            "repetition_n": 1
        }
        # Case A: Prerequisite is passed
        prereqs_passed = [{"id": "c_p1", "last_quality_score": 4, "mastery_level": "Proficient"}]
        res_a = MasteryService.evaluate_concept_mastery(c, prereqs_passed)
        self.assertEqual(res_a["prerequisite_health"], 1.0)
        self.assertEqual(res_a["components"]["prerequisite_health"], 10)

        # Case B: Prerequisite failed / unreviewed
        prereqs_failed = [{"id": "c_p1", "last_quality_score": 1, "mastery_level": "Learning"}]
        res_b = MasteryService.evaluate_concept_mastery(c, prereqs_failed)
        self.assertEqual(res_b["prerequisite_health"], 0.0)
        self.assertEqual(res_b["components"]["prerequisite_health"], 0)
        self.assertLess(res_b["mastery_score"], res_a["mastery_score"])

    def test_calculate_curriculum_mastery(self):
        concepts = {
            "p1": {"id": "p1", "title": "Base", "total_reviews": 3, "last_quality_score": 5, "consecutive_correct": 2, "interval_days": 14, "repetition_n": 3},
            "p2": {"id": "p2", "title": "Mid", "total_reviews": 2, "last_quality_score": 4, "consecutive_correct": 1, "interval_days": 6, "repetition_n": 2},
            "p3": {"id": "p3", "title": "Leaf", "total_reviews": 0, "last_quality_score": 0, "consecutive_correct": 0, "interval_days": 0, "repetition_n": 0}
        }
        dependencies = [("p1", "p2"), ("p2", "p3")]
        curr_mastery = MasteryService.calculate_curriculum_mastery(concepts, dependencies)

        self.assertEqual(curr_mastery["total_concepts"], 3)
        self.assertEqual(curr_mastery["mastered_count"], 1)
        self.assertEqual(curr_mastery["proficient_count"], 1)
        self.assertEqual(curr_mastery["unseen_count"], 1)
        self.assertGreater(curr_mastery["overall_mastery_percent"], 0)
        self.assertIn("p3", curr_mastery["knowledge_frontier"])
        self.assertEqual(curr_mastery["curriculum_status"], "In Progress")

    def test_check_newly_mastered(self):
        self.assertTrue(MasteryService.check_newly_mastered("Proficient", "Mastered"))
        self.assertTrue(MasteryService.check_newly_mastered("Unseen", "Mastered"))
        self.assertTrue(MasteryService.check_newly_mastered("Learning", "Mastered"))
        self.assertFalse(MasteryService.check_newly_mastered("Mastered", "Mastered"))
        self.assertFalse(MasteryService.check_newly_mastered("Learning", "Proficient"))

    def test_backwards_compatible_calculate_metrics(self):
        concepts = {
            "c1": {"id": "c1", "last_quality_score": 5, "sm2_status": "mastered"},
            "c2": {"id": "c2", "last_quality_score": 2, "sm2_status": "weak"},
            "c3": {"id": "c3", "last_quality_score": 4, "sm2_status": "reviewing"}
        }
        metrics = MasteryService.calculate_metrics(concepts)
        self.assertEqual(metrics["total"], 3)
        self.assertEqual(metrics["mastered_count"], 2)
        self.assertEqual(metrics["passing_count"], 2)
        self.assertEqual(metrics["mastery_percent"], 67)

    def test_orchestrator_celebration_on_concept_mastery(self):
        # Load sample curriculum
        self.orch.load_sample_module("Operating Systems")
        first_cid = self.orch.current_concept_id
        c = self.orch.concepts[first_cid]

        # Prime the concept so one more solid attempt achieves Mastered
        c["total_reviews"] = 2
        c["consecutive_correct"] = 1
        c["interval_days"] = 6
        c["repetition_n"] = 2
        c["last_quality_score"] = 4
        c["mastery_level"] = "Proficient"

        self.orch.trigger_ready_for_recall()

        # Submit an excellent recall response
        high_score_answer = (
            "Process scheduling is the mechanism where the OS dispatcher allocates CPU time slices "
            "to runnable processes in the ready queue using algorithms like Round Robin or Priority Scheduling "
            "to maximize throughput and minimize waiting time."
        )
        res = self.orch.submit_recall_response(high_score_answer)

        # Check that concept reached Mastered
        updated_c = self.orch.concepts[first_cid]
        self.assertEqual(updated_c["mastery_level"], "Mastered")
        self.assertTrue(updated_c["is_mastered"])

        # Check teacher celebratory state and message
        self.assertEqual(self.orch.teacher_state, "celebration")
        latest_msg = self.orch.chat_history[-1]
        self.assertEqual(latest_msg["message_type"], "mastered")
        self.assertEqual(latest_msg["expression_state"], "celebration")
        self.assertTrue(latest_msg["content"].startswith("Yes! You've got this one now. 🎉 Let's move on."))

        # Check state payload includes mastery diagnostics
        self.assertIn("mastery_metrics", res)
        self.assertIn("concept_mastery", res)
        self.assertGreaterEqual(res["mastery_percent"], 0)


if __name__ == "__main__":
    unittest.main()
