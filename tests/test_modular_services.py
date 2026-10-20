"""
Unit tests for EduMentor modular services:
- StudyPathService
- RecallService
- MasteryService
- SpacedRepetitionService
- NotificationService
- HistoryService
"""

import unittest
from edumentor.services.study_path_service import StudyPathService
from edumentor.services.mastery_service import MasteryService
from edumentor.services.spaced_repetition_service import SpacedRepetitionService
from edumentor.services.notification_service import NotificationService
from edumentor.services.history_service import HistoryService
from edumentor.samples import SAMPLE_CURRICULA


class TestModularServices(unittest.TestCase):
    def setUp(self):
        self.curriculum = SAMPLE_CURRICULA["Operating Systems: Concurrency & Virtual Memory"]

    def test_study_path_service(self):
        concepts = self.curriculum["concepts"]
        deps = self.curriculum["dependencies"]
        svc = StudyPathService(concepts=concepts, dependencies=deps)

        order = svc.get_topological_order()
        self.assertEqual(len(order), len(concepts))

        # Check topological validity: Virtual Memory must precede Paging
        idx_vm = order.index("os_virtual_memory")
        idx_paging = order.index("os_paging")
        self.assertLess(idx_vm, idx_paging)

    def test_mastery_service(self):
        concepts = {
            "c1": {"id": "c1", "last_quality_score": 5, "sm2_status": "mastered"},
            "c2": {"id": "c2", "last_quality_score": 2, "sm2_status": "weak"},
            "c3": {"id": "c3", "last_quality_score": 4, "sm2_status": "reviewing"},
        }
        metrics = MasteryService.calculate_metrics(concepts)
        self.assertEqual(metrics["total"], 3)
        self.assertEqual(metrics["mastered_count"], 2)  # c1 and c3
        self.assertEqual(metrics["passing_count"], 2)
        self.assertEqual(metrics["mastery_percent"], 67)

    def test_spaced_repetition_service(self):
        # First successful recall
        res1 = SpacedRepetitionService.calculate_review(quality_q=5, repetition_n=0, easiness_factor=2.5, current_interval=0)
        self.assertEqual(res1["repetition_n"], 1)
        self.assertEqual(res1["interval_days"], 1)
        self.assertGreaterEqual(res1["easiness_factor"], 2.5)

        # Second successful recall
        res2 = SpacedRepetitionService.calculate_review(quality_q=4, repetition_n=1, easiness_factor=res1["easiness_factor"], current_interval=1)
        self.assertEqual(res2["repetition_n"], 2)
        self.assertEqual(res2["interval_days"], 6)

        # Failing recall
        res_fail = SpacedRepetitionService.calculate_review(quality_q=2, repetition_n=2, easiness_factor=2.5, current_interval=6)
        self.assertEqual(res_fail["repetition_n"], 0)
        self.assertEqual(res_fail["interval_days"], 1)

    def test_notification_service(self):
        concepts = {
            "c1": {"title": "Paging", "next_due_date": "2026-09-01", "total_reviews": 1, "sm2_status": "reviewing"},
            "c2": {"title": "Threads", "next_due_date": "2026-09-20", "total_reviews": 1, "sm2_status": "reviewing"}
        }
        alerts = NotificationService.check_due_notifications(concepts, today_iso="2026-09-10")
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["concept_id"], "c1")
        self.assertIn("Review Due", alerts[0]["title"])

    def test_history_service(self):
        svc = HistoryService()
        svc.log_action("STUDY_START", {"module": "Operating Systems"})
        history = svc.get_recent_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["action"], "STUDY_START")


if __name__ == "__main__":
    unittest.main()
