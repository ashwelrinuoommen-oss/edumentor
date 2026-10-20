import unittest
from datetime import date
from edumentor.scheduler import calculate_sm2, map_score_to_quality, prioritize_study_queue


class TestSM2Scheduler(unittest.TestCase):
    def test_map_score_to_quality(self):
        self.assertEqual(map_score_to_quality(95.0), 5)
        self.assertEqual(map_score_to_quality(80.0), 4)
        self.assertEqual(map_score_to_quality(65.0), 3)
        self.assertEqual(map_score_to_quality(50.0), 2)
        self.assertEqual(map_score_to_quality(25.0), 1)
        self.assertEqual(map_score_to_quality(10.0), 0)

    def test_sm2_first_review_pass(self):
        res = calculate_sm2(quality_q=4, repetition_n=0, easiness_factor=2.5)
        self.assertEqual(res["repetition_n"], 1)
        self.assertEqual(res["interval_days"], 1)
        self.assertGreaterEqual(res["easiness_factor"], 2.5)

    def test_sm2_second_review_pass(self):
        res = calculate_sm2(quality_q=5, repetition_n=1, easiness_factor=2.5)
        self.assertEqual(res["repetition_n"], 2)
        self.assertEqual(res["interval_days"], 6)

    def test_sm2_failure_resets(self):
        res = calculate_sm2(quality_q=2, repetition_n=3, easiness_factor=2.5, current_interval=15)
        self.assertEqual(res["repetition_n"], 0)
        self.assertEqual(res["interval_days"], 1)
        self.assertEqual(res["status"], "weak")

    def test_prioritize_study_queue(self):
        concepts = [
            {"id": "c1", "sm2_status": "mastered", "last_quality_score": 4, "total_reviews": 3, "next_due_date": "2099-01-01"},
            {"id": "c2", "sm2_status": "weak", "last_quality_score": 2, "total_reviews": 1, "next_due_date": "2026-09-10"},
            {"id": "c3", "sm2_status": "new", "last_quality_score": 0, "total_reviews": 0},
        ]
        sorted_c = prioritize_study_queue(concepts, topological_order=["c1", "c2", "c3"], reference_date=date(2026, 9, 10))
        # Weak concepts should come first
        self.assertEqual(sorted_c[0]["id"], "c2")
        # Ready new concept next
        self.assertEqual(sorted_c[1]["id"], "c3")
        # Mastered concept with future due date last
        self.assertEqual(sorted_c[2]["id"], "c1")


if __name__ == "__main__":
    unittest.main()
