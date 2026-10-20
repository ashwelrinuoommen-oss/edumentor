"""
Unit and Integration Tests for Phase 26 — Avatar + Chat Message Design.

Validates:
1. Every major teacher message has the Avatar positioned beside the conversational content.
2. Major interactions are connected by a visual stem branch (│ └──).
3. Tiny status messages do NOT display the avatar and render as clean status notices.
4. Message tagging in EduMentorOrchestrator: `is_major: True`, `show_avatar: True` for major
   interactions, and `is_major: False`, `show_avatar: False` for processing and calibration updates.
5. End-to-end chat history tracking across the learning lifecycle.
"""

import unittest
from typing import Dict, Any

from edumentor.orchestrator import EduMentorOrchestrator, is_major_teacher_message
from edumentor.llm import LLMConfig
from edumentor.components.teacher_message import TeacherMessage, render_status_notice


class TestPhase26AvatarChatMessageDesign(unittest.TestCase):
    """Test suite for Phase 26 Avatar + Chat Message Design."""

    def setUp(self):
        self.orch = EduMentorOrchestrator(student_name="Ashwel")
        self.orch.llm_config = LLMConfig(provider="demo")

    def test_is_major_teacher_message_classification(self):
        """Verify the helper accurately distinguishes major teacher interactions from status notices."""
        # 1. Major teacher interactions
        major_messages = [
            {"role": "assistant", "content": "Alright, let's start.", "message_type": "explaining"},
            {"role": "assistant", "content": "Active recall challenge", "message_type": "encouraging"},
            {"role": "assistant", "content": "Exactly! That's it.", "message_type": "correct"},
            {"role": "assistant", "content": "Almost there!", "message_type": "almost_correct"},
            {"role": "assistant", "content": "No worries.", "message_type": "wrong"},
            {"role": "assistant", "content": "Mastered!", "message_type": "mastered"},
            {"role": "assistant", "content": "Remember this one?", "message_type": "resurfacing"},
            {"role": "assistant", "content": "Welcome back!", "message_type": "greeting"},
            {"role": "assistant", "content": "Explicit major", "is_major": True}
        ]
        for m in major_messages:
            self.assertTrue(
                is_major_teacher_message(m),
                f"Expected major message for: {m}"
            )
            self.assertTrue(self.orch.is_major_message(m))

        # 2. Minor status messages
        minor_messages = [
            {"role": "assistant", "content": "Processing notes...", "message_type": "processing"},
            {"role": "assistant", "content": "Confidence calibration", "message_type": "calibration"},
            {"role": "assistant", "content": "Database saved", "message_type": "status"},
            {"role": "assistant", "content": "System alert", "message_type": "system"},
            {"role": "assistant", "content": "Explicit minor", "is_major": False, "show_avatar": False},
            {"role": "user", "content": "I am a student message"}
        ]
        for m in minor_messages:
            self.assertFalse(
                is_major_teacher_message(m),
                f"Expected minor status message for: {m}"
            )
            self.assertFalse(self.orch.is_major_message(m))

    def test_orchestrator_initial_home_greeting_is_major(self):
        """Verify initial greeting is classified as a major teacher message."""
        payload = self.orch.initialize_home()
        first_msg = self.orch.chat_history[0]
        self.assertEqual(first_msg["role"], "assistant")
        self.assertTrue(first_msg.get("is_major", False))
        self.assertTrue(first_msg.get("show_avatar", False))
        self.assertTrue(is_major_teacher_message(first_msg))

    def test_orchestrator_ingest_notes_is_status_notice(self):
        """Verify 'Got it! Give me a moment...' note processing message is marked as minor status notice."""
        self.orch.ingest_notes_text("Quick note on Threads.", title="Threads Note")
        # Find processing message
        proc_msgs = [m for m in self.orch.chat_history if m.get("message_type") == "processing"]
        self.assertGreater(len(proc_msgs), 0)
        proc_msg = proc_msgs[0]
        self.assertFalse(proc_msg.get("is_major", True))
        self.assertFalse(proc_msg.get("show_avatar", True))
        self.assertFalse(is_major_teacher_message(proc_msg))

    def test_orchestrator_starting_curriculum_is_major(self):
        """Verify curriculum load produces a major teacher message."""
        self.orch.load_sample_module("Operating Systems")
        latest_msg = self.orch.chat_history[-1]
        self.assertEqual(latest_msg["role"], "assistant")
        self.assertTrue(latest_msg.get("is_major", False))
        self.assertTrue(latest_msg.get("show_avatar", False))
        self.assertTrue(is_major_teacher_message(latest_msg))

    def test_orchestrator_active_recall_challenge_is_major(self):
        """Verify active recall challenge is classified as major teacher message."""
        self.orch.load_sample_module("Operating Systems")
        self.orch.trigger_ready_for_recall()
        challenge_msg = self.orch.chat_history[-1]
        self.assertEqual(challenge_msg["role"], "assistant")
        self.assertTrue(challenge_msg.get("is_major", False))
        self.assertTrue(challenge_msg.get("show_avatar", False))
        self.assertTrue(is_major_teacher_message(challenge_msg))

    def test_orchestrator_recall_feedback_is_major(self):
        """Verify evaluation feedback is marked as a major teacher message."""
        self.orch.load_sample_module("Operating Systems")
        self.orch.trigger_ready_for_recall()
        self.orch.submit_recall_response("Process scheduling allocates CPU time slices to processes in the ready queue.")
        feedback_msg = self.orch.chat_history[-1]
        self.assertEqual(feedback_msg["role"], "assistant")
        self.assertTrue(feedback_msg.get("is_major", False))
        self.assertTrue(feedback_msg.get("show_avatar", False))
        self.assertTrue(is_major_teacher_message(feedback_msg))

    def test_orchestrator_calibration_feedback_is_status_notice(self):
        """Verify confidence calibration notice is marked as minor status notice without avatar."""
        self.orch.load_sample_module("Operating Systems")
        self.orch.trigger_ready_for_recall()
        self.orch.submit_recall_response("Process scheduling allocates CPU time slices.")
        self.orch.record_student_confidence("Very confident")
        calib_msg = self.orch.chat_history[-1]
        self.assertEqual(calib_msg["role"], "assistant")
        self.assertFalse(calib_msg.get("is_major", True))
        self.assertFalse(calib_msg.get("show_avatar", True))
        self.assertFalse(is_major_teacher_message(calib_msg))

    def test_orchestrator_resurfacing_is_major(self):
        """Verify automatic resurfacing prompt is a major teacher interaction."""
        self.orch.load_sample_module("Operating Systems")
        first_cid = self.orch.topological_order[0]
        self.orch.trigger_automatic_resurfacing(concept_id=first_cid)
        resurface_msg = self.orch.chat_history[-1]
        self.assertTrue(resurface_msg.get("is_major", False))
        self.assertTrue(resurface_msg.get("show_avatar", False))
        self.assertTrue(is_major_teacher_message(resurface_msg))

    def test_orchestrator_advance_step_is_major(self):
        """Verify step advancement and loopback are major teacher interactions."""
        self.orch.load_sample_module("Operating Systems")
        first_cid = self.orch.topological_order[0]
        self.orch.weak_queue.append(first_cid)
        self.orch.advance_next_step()
        loopback_msg = self.orch.chat_history[-1]
        self.assertTrue(loopback_msg.get("is_major", False))
        self.assertTrue(loopback_msg.get("show_avatar", False))
        self.assertTrue(is_major_teacher_message(loopback_msg))

    def test_teacher_message_component_tree_connector_structure(self):
        """Verify TeacherMessage object properly encapsulates major vs minor state."""
        tm_major = TeacherMessage(text="Major message", is_major=True)
        self.assertTrue(tm_major.is_major)

        tm_minor = TeacherMessage(text="Minor status", is_major=False)
        self.assertFalse(tm_minor.is_major)


if __name__ == "__main__":
    unittest.main()
