"""
Unit and integration tests for Phase 19 — Progress Page.
Verifies lightweight overview metrics (YOUR LEARNING, 76% Overall Mastery, 32 Mastered,
6 Needs Review, 14 Learning Sessions), recent subjects breakdown, pedagogical insights,
and the GET /api/progress REST endpoint.
"""

import unittest
import os
import tempfile
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.database.repository import EduMentorRepository


class TestPhase19ProgressPage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_progress.db")
        self.orchestrator = EduMentorOrchestrator(student_name="Ashwel", db_path=self.db_path)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_progress_summary_structure_and_metrics(self):
        """
        Verify exact metrics required by user specification:
        YOUR LEARNING
        Overall Mastery: 76%
        Concepts Mastered: 32
        Needs Review: 6
        Learning Sessions: 14
        """
        summary = self.orchestrator.get_progress_summary()
        self.assertEqual(summary["title"], "YOUR LEARNING")
        self.assertEqual(summary["overall_mastery"], 76)
        self.assertEqual(summary["concepts_mastered"], 32)
        self.assertEqual(summary["needs_review"], 6)
        self.assertEqual(summary["learning_sessions"], 14)

    def test_recent_subjects_breakdown(self):
        """
        Verify recent subjects:
        Operating Systems      76%
        DBMS                   84%
        Computer Networks      69%
        """
        summary = self.orchestrator.get_progress_summary()
        recent = summary.get("recent_subjects", [])
        self.assertTrue(len(recent) >= 3)

        subject_map = {s["subject"]: s["mastery"] for s in recent}
        self.assertIn("Operating Systems", subject_map)
        self.assertEqual(subject_map["Operating Systems"], 76)
        self.assertIn("DBMS", subject_map)
        self.assertEqual(subject_map["DBMS"], 84)
        self.assertIn("Computer Networks", subject_map)
        self.assertEqual(subject_map["Computer Networks"], 69)

    def test_pedagogical_insights(self):
        """
        Verify presence of:
        Your strongest area
        ...
        Needs more attention
        ...
        """
        summary = self.orchestrator.get_progress_summary()
        self.assertIn("strongest_area", summary)
        self.assertIn("needs_attention", summary)
        self.assertTrue(len(summary["strongest_area"]) > 10)
        self.assertTrue(len(summary["needs_attention"]) > 10)
        self.assertIn("Virtual Memory", summary["strongest_area"])
        self.assertIn("CPU Scheduling", summary["needs_attention"])

    def test_server_progress_endpoint(self):
        """Verify GET /api/progress endpoint delivers lightweight progress payload."""
        from starlette.testclient import TestClient
        from server import app

        client = TestClient(app)
        res = client.get("/api/progress")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["title"], "YOUR LEARNING")
        self.assertIn("overall_mastery", data)
        self.assertIn("concepts_mastered", data)
        self.assertIn("needs_review", data)
        self.assertIn("learning_sessions", data)
        self.assertTrue(len(data["recent_subjects"]) >= 3)


if __name__ == "__main__":
    unittest.main()
