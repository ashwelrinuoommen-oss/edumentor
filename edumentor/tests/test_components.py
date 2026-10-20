"""
Unit tests for EduMentor UI components rendering logic.
"""

import unittest
from unittest.mock import patch, MagicMock

from edumentor.components.teacher_avatar import render_teacher_avatar
from edumentor.components.chat_message import render_chat_bubble
from edumentor.components.concept_progress import render_concept_progress
from edumentor.components.mastery_meter import render_mastery_meter
from edumentor.components.recall_feedback import render_recall_feedback
from edumentor.components.notification import render_loopback_alert, render_banner


class TestUIComponents(unittest.TestCase):
    @patch("streamlit.markdown")
    def test_teacher_avatar_render(self, mock_md):
        render_teacher_avatar(size=60)
        self.assertTrue(mock_md.called)
        call_arg = mock_md.call_args[0][0]
        self.assertIn("60px", call_arg)

    @patch("streamlit.markdown")
    def test_concept_progress_render(self, mock_md):
        render_concept_progress("Process Scheduling", 1, 5, "In Progress")
        self.assertTrue(mock_md.called)
        call_arg = mock_md.call_args[0][0]
        self.assertIn("Process Scheduling", call_arg)

    @patch("streamlit.markdown")
    def test_mastery_meter_render(self, mock_md):
        render_mastery_meter(0.85, 4, 5)
        self.assertTrue(mock_md.called)
        call_arg = mock_md.call_args[0][0]
        self.assertIn("85%", call_arg)

    @patch("streamlit.markdown")
    def test_recall_feedback_render(self, mock_md):
        eval_result = {
            "score": 0.9,
            "quality_score": 5,
            "verdict": "Mastered",
            "semantic_similarity": 0.88,
            "llm_score": 0.92,
            "strengths": ["Clear explanation"],
            "missing_points": [],
            "actionable_tip": "Keep it up!",
            "summary": "Great job"
        }
        render_recall_feedback(eval_result)
        self.assertTrue(mock_md.called)
        call_arg = mock_md.call_args[0][0]
        self.assertIn("90%", call_arg)
        self.assertIn("Quality 5/5", call_arg)

    @patch("streamlit.markdown")
    def test_notifications_render(self, mock_md):
        render_loopback_alert("Paging", 2, tip="Review virtual address split.")
        self.assertTrue(mock_md.called)
        call_arg = mock_md.call_args[0][0]
        self.assertIn("Adaptive Loopback", call_arg)
        self.assertIn("Paging", call_arg)


if __name__ == "__main__":
    unittest.main()
