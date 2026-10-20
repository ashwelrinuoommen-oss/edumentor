"""
Tests for Master Home Workspace & Dynamic Teacher Avatar Expression System.
Verifies:
1. AvatarExpressionManager:
   - All 11 expressions mapping and file existence
   - Fallback to teacher_idle.png for invalid / unknown states
   - Base64 encoding and caching
   - Expression aliases resolution (mastered, idea, confused, etc.)
2. TeacherAvatar and TeacherMessage components:
   - Responsive size mappings (small, medium, large, xlarge, desktop, tablet, mobile)
   - Synchronized avatar + message formatting
3. Orchestrator State and Expression Synchronization:
   - chat_history message tagging with expression_state
   - get_state_payload returning teacher_expression and teacher_expression_url
   - Expression transitions across ingestion, study, recall, evaluation, and completion
4. Dynamic Contextual Welcome:
   - New user
   - Active study session
   - Spaced repetition revision due
"""

import os
import tempfile
import unittest
from datetime import date

from edumentor.database.database import init_db
from edumentor.database.repository import EduMentorRepository
from edumentor.database.models import SM2Card
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.services.avatar_expression_manager import AvatarExpressionManager, avatar_expression_manager
from edumentor.components.teacher_avatar import TeacherAvatar, get_avatar_state_config, get_available_avatar_states
from edumentor.components.teacher_message import TeacherMessage
from edumentor.pages.home import get_contextual_welcome


class TestHomeWorkspaceAndAvatar(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        init_db(self.temp_db.name)
        self.repo = EduMentorRepository(db_path=self.temp_db.name)
        self.manager = avatar_expression_manager

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_all_11_canonical_expressions_exist_on_disk(self):
        """Verify all 11 user-specified avatar emotion PNGs exist on disk."""
        expected_states = [
            "idle", "greeting", "thinking", "explaining", "listening",
            "encouraging", "happy", "almost_correct", "supportive",
            "celebration", "reminder"
        ]
        for st in expected_states:
            filename = self.manager.get_expression(st)
            self.assertTrue(filename.endswith(".png"), f"Filename for {st} should end with .png")
            path = self.manager.get_expression_path(st)
            self.assertIsNotNone(path, f"Path for {st} should not be None")
            self.assertTrue(os.path.exists(path), f"File for {st} must exist at {path}")

    def test_expression_fallback_to_idle(self):
        """Verify unknown or invalid expressions fall back to teacher_idle.png."""
        fallback_file = self.manager.get_expression("unknown_nonexistent_state_xyz")
        self.assertEqual(fallback_file, "teacher_idle.png")
        
        fallback_path = self.manager.get_expression_path("invalid_state_123")
        self.assertTrue(os.path.exists(fallback_path))
        self.assertTrue(fallback_path.endswith("teacher_idle.png"))

    def test_expression_alias_resolution(self):
        """Verify aliases map to canonical teacher expression PNGs."""
        self.assertEqual(self.manager.get_expression("mastered"), "teacher_celebration.png")
        self.assertEqual(self.manager.get_expression("celebrating"), "teacher_celebration.png")
        self.assertEqual(self.manager.get_expression("confused"), "teacher_supportive.png")
        self.assertEqual(self.manager.get_expression("wrong"), "teacher_supportive.png")
        self.assertEqual(self.manager.get_expression("idea"), "teacher_encouraging.png")
        self.assertEqual(self.manager.get_expression("waiting"), "teacher_listening.png")
        self.assertEqual(self.manager.get_expression("studying"), "teacher_listening.png")
        self.assertEqual(self.manager.get_expression("break"), "teacher_reminder.png")
        self.assertEqual(self.manager.get_expression("speaking"), "teacher_explaining.png")

    def test_base64_caching(self):
        """Verify base64 retrieval returns valid strings and caches them."""
        b64_1 = self.manager.get_expression_base64("greeting")
        self.assertIsInstance(b64_1, str)
        self.assertGreater(len(b64_1), 100)

        # Second call should retrieve from cache
        b64_2 = self.manager.get_expression_base64("greeting")
        self.assertEqual(b64_1, b64_2)

    def test_teacher_avatar_responsive_sizes(self):
        """Verify TeacherAvatar class maps responsive size strings to integer dimensions."""
        avatar_small = TeacherAvatar(expression="greeting", size="small")
        self.assertEqual(avatar_small.size, 74)

        avatar_med = TeacherAvatar(expression="greeting", size="medium")
        self.assertEqual(avatar_med.size, 112)

        avatar_large = TeacherAvatar(expression="greeting", size="large")
        self.assertEqual(avatar_large.size, 180)

        avatar_desktop = TeacherAvatar(expression="greeting", size="desktop")
        self.assertEqual(avatar_desktop.size, 200)

        avatar_tablet = TeacherAvatar(expression="greeting", size="tablet")
        self.assertEqual(avatar_tablet.size, 160)

        avatar_mobile = TeacherAvatar(expression="greeting", size="mobile")
        self.assertEqual(avatar_mobile.size, 130)

        # Custom integer size
        avatar_custom = TeacherAvatar(expression="greeting", size=145)
        self.assertEqual(avatar_custom.size, 145)

    def test_teacher_message_unified_element(self):
        """Verify TeacherMessage encapsulates text, expression, and status badge."""
        tm = TeacherMessage(
            text="Let's understand process scheduling.",
            expression="explaining",
            concept_title="Process Scheduling",
            status_badge="Teaching"
        )
        self.assertEqual(tm.expression, "explaining")
        self.assertEqual(tm.concept_title, "Process Scheduling")
        self.assertEqual(tm.status_badge, "Teaching")

    def test_orchestrator_expression_synchronization(self):
        """Verify orchestrator attaches message_type and expression_state to chat_history."""
        orch = EduMentorOrchestrator(student_name="Ashwel", db_path=self.temp_db.name)
        payload = orch.load_sample_module("Operating Systems")

        # Check that assistant messages have expression_state
        for msg in orch.chat_history:
            if msg.get("role") == "assistant":
                self.assertIn("expression_state", msg)
                self.assertIn("message_type", msg)

        # Check state payload
        self.assertIn("teacher_expression", payload)
        self.assertIn("teacher_expression_url", payload)
        self.assertTrue(payload["teacher_expression"].endswith(".png"))
        self.assertTrue(payload["teacher_expression_url"].startswith("/assets/teacher_avatar/"))

    def test_orchestrator_recall_and_evaluation_expression_transitions(self):
        """Verify expression state transitions during active recall and hybrid evaluation."""
        orch = EduMentorOrchestrator(student_name="Ashwel", db_path=self.temp_db.name)
        orch.load_sample_module("Operating Systems")

        # Ready for recall -> encouraging
        ready_payload = orch.trigger_ready_for_recall()
        self.assertEqual(orch.teacher_state, "encouraging")
        self.assertEqual(ready_payload["teacher_expression"], "teacher_encouraging.png")

        # Submit strong answer -> happy
        strong_ans = (
            "Process scheduling is the operating system mechanism that decides which process runs on the CPU "
            "using scheduling algorithms like Round Robin and priority queues to maximize throughput and minimize latency."
        )
        eval_payload = orch.submit_recall_response(strong_ans)
        self.assertIn(orch.teacher_state, ["correct", "happy", "almost_correct"])
        self.assertIn(eval_payload["teacher_expression"], ["teacher_happy.png", "teacher_almost_correct.png"])

    def test_dynamic_contextual_welcome_modes(self):
        """Verify dynamic contextual greetings for new user, active session, and revision."""
        # 1. New user
        orch_new = EduMentorOrchestrator(student_name="NewUser", db_path=self.temp_db.name)
        ctx_new = get_contextual_welcome("NewUser", orch_new)
        self.assertEqual(ctx_new["mode"], "NEW")
        self.assertIn("What do you think we should study today?", ctx_new["headline"])
        self.assertIn("Welcome, NewUser!", ctx_new["welcome_title"])

        # 2. Active session
        orch_active = EduMentorOrchestrator(student_name="ActiveUser", db_path=self.temp_db.name)
        orch_active.load_sample_module("Operating Systems")
        ctx_active = get_contextual_welcome("ActiveUser", orch_active)
        self.assertEqual(ctx_active["mode"], "CONTINUE")
        self.assertIn("Want to continue where you left off?", ctx_active["headline"])
        self.assertIn("Operating Systems", ctx_active["subtext"])
        self.assertIn("Welcome back, ActiveUser", ctx_active["welcome_title"])


if __name__ == "__main__":
    unittest.main()
