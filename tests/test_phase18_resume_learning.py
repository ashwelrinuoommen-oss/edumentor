"""
Unit and integration tests for Phase 18 — Resume Learning.
Verifies persistent session saving, exact welcome dialogue, continue/dismiss actions,
and REST API endpoints.
"""

import unittest
import os
import tempfile
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.database.repository import EduMentorRepository


class TestPhase18ResumeLearning(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_resume.db")
        self.orchestrator = EduMentorOrchestrator(student_name="Ashwel", db_path=self.db_path)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_save_and_retrieve_active_session(self):
        """Verify active learning session is persisted and retrieved with correct metadata."""
        self.orchestrator.load_sample_module("Operating Systems")
        self.orchestrator.save_session_state()

        resume_state = self.orchestrator.get_resume_state()
        self.assertTrue(resume_state["has_resumable"])
        self.assertEqual(resume_state["student_name"], "Ashwel")
        self.assertEqual(resume_state["subject"], "Operating Systems")
        self.assertIn("Process Scheduling", resume_state["revisit_concept"])
        self.assertEqual(resume_state["buttons"], ["Continue", "Start Something Else"])

    def test_exact_dialogue_formatting(self):
        """
        Verify exact wording from user specification:
        Welcome back, Ashwel.

        You were studying:
        Operating Systems

        You finished 6 of 14 concepts.

        We were about to revisit:
        CPU Scheduling

        Continue where you left off?
        """
        repo = EduMentorRepository(self.db_path)
        user_id = "user_ashwel"
        repo.save_active_session(
            user_id=user_id,
            subject="Operating Systems",
            current_concept_id="os_process_scheduling",
            current_concept_title="CPU Scheduling",
            finished_count=6,
            total_count=14,
            state="STUDYING",
            session_data={"curriculum_title": "Operating Systems"},
            is_active=1
        )

        state = self.orchestrator.get_resume_state()
        self.assertTrue(state["has_resumable"])
        self.assertEqual(state["finished_count"], 6)
        self.assertEqual(state["total_count"], 14)
        self.assertEqual(state["revisit_concept"], "CPU Scheduling")

        expected_dialogue = (
            "Welcome back, Ashwel.\n\n"
            "You were studying:\n"
            "Operating Systems\n\n"
            "You finished 6 of 14 concepts.\n\n"
            "We were about to revisit:\n"
            "CPU Scheduling\n\n"
            "Continue where you left off?"
        )
        self.assertEqual(state["dialogue"].strip(), expected_dialogue.strip())
        self.assertEqual(state["buttons"], ["Continue", "Start Something Else"])

    def test_resume_continue_action(self):
        """Verify [ Continue ] resumes learning right where the student left off."""
        self.orchestrator.load_sample_module("Operating Systems")
        self.orchestrator.save_session_state()

        # Simulate closing the app and resetting in-memory orchestrator
        fresh_orch = EduMentorOrchestrator(student_name="Ashwel", db_path=self.db_path)
        resume_info = fresh_orch.get_resume_state()
        self.assertTrue(resume_info["has_resumable"])

        # Click Continue
        payload = fresh_orch.resume_session()
        self.assertEqual(payload["curriculum_title"], "Operating Systems: Concurrency & Virtual Memory")
        self.assertIn("Process Scheduling", payload["current_concept"]["title"])
        self.assertEqual(payload["state"], "STUDYING")
        self.assertTrue(any("picking right back up" in msg["content"] for msg in payload["chat_history"]))

    def test_resume_dismiss_action(self):
        """Verify [ Start Something Else ] clears the session and resets to HOME."""
        self.orchestrator.load_sample_module("Operating Systems")
        self.orchestrator.save_session_state()

        # Student clicks Start Something Else
        home_payload = self.orchestrator.dismiss_resume()
        self.assertEqual(home_payload["state"], "HOME")
        self.assertIsNone(home_payload["curriculum_title"])

        # Subsequent check reports no resumable session
        resume_check = self.orchestrator.get_resume_state()
        self.assertFalse(resume_check["has_resumable"])

    def test_server_resume_endpoints(self):
        """Verify FastAPI REST API endpoints for resume state, continue, and dismiss."""
        from starlette.testclient import TestClient
        from server import app, orchestrator

        client = TestClient(app)
        # Ensure fresh state
        orchestrator.load_sample_module("Operating Systems")
        orchestrator.save_session_state()

        # 1. GET /api/resume-state
        res = client.get("/api/resume-state")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["has_resumable"])
        self.assertIn("Operating Systems", data["subject"])
        self.assertIn("Continue where you left off?", data["dialogue"])

        # 2. POST /api/resume/continue
        res_cont = client.post("/api/resume/continue")
        self.assertEqual(res_cont.status_code, 200)
        cont_data = res_cont.json()
        self.assertIsNotNone(cont_data["curriculum_title"])

        # 3. POST /api/resume/dismiss
        res_dism = client.post("/api/resume/dismiss")
        self.assertEqual(res_dism.status_code, 200)
        dism_data = res_dism.json()
        self.assertEqual(dism_data["state"], "HOME")


if __name__ == "__main__":
    unittest.main()
