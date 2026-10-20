"""
Unit and Integration Tests for Phase 4 — Automatic Study Path.
Verifies:
- Automatic display of compact study-path visualization without manual button clicking
- Formatted states:
  * Completed / Mastered -> ✓ Ready
  * Active / In-Progress -> → Next
  * Upcoming concepts
- Numbering with leading zeros (01, 02, ...)
- Title header 'YOUR LEARNING PATH'
"""

import unittest
from unittest.mock import patch, MagicMock

from edumentor.components.study_path import render_compact_study_path
from edumentor.orchestrator import EduMentorOrchestrator


class TestStudyPathPhase4(unittest.TestCase):
    def setUp(self):
        self.topological_order = [
            "c_basics",
            "c_processes",
            "c_scheduling",
            "c_threads",
            "c_cpu_algo",
            "c_deadlocks",
            "c_memory"
        ]
        self.concepts = {
            "c_basics": {"id": "c_basics", "title": "Operating System Basics", "mastered": True, "last_quality_score": 5},
            "c_processes": {"id": "c_processes", "title": "Processes", "mastered": False, "last_quality_score": 0},
            "c_scheduling": {"id": "c_scheduling", "title": "Process Scheduling", "mastered": False, "last_quality_score": 0},
            "c_threads": {"id": "c_threads", "title": "Threads", "mastered": False, "last_quality_score": 0},
            "c_cpu_algo": {"id": "c_cpu_algo", "title": "CPU Scheduling Algorithms", "mastered": False, "last_quality_score": 0},
            "c_deadlocks": {"id": "c_deadlocks", "title": "Deadlocks", "mastered": False, "last_quality_score": 0},
            "c_memory": {"id": "c_memory", "title": "Memory Management", "mastered": False, "last_quality_score": 0},
        }

    @patch("streamlit.markdown")
    def test_render_compact_study_path_badges_and_numbers(self, mock_md):
        # Current active concept is 'c_processes' (step 2)
        render_compact_study_path(
            topological_order=self.topological_order,
            concepts=self.concepts,
            current_concept_id="c_processes"
        )

        self.assertTrue(mock_md.called)
        output_html = mock_md.call_args[0][0]

        # Verify Header
        self.assertIn("YOUR LEARNING PATH", output_html)

        # Verify '01' basics has '✓ Ready'
        self.assertIn("01", output_html)
        self.assertIn("Operating System Basics", output_html)
        self.assertIn("✓ Ready", output_html)

        # Verify '02' processes is current with '→ Next'
        self.assertIn("02", output_html)
        self.assertIn("Processes", output_html)
        self.assertIn("→ Next", output_html)

        # Verify upcoming concepts
        self.assertIn("03", output_html)
        self.assertIn("Process Scheduling", output_html)
        self.assertIn("06", output_html)
        self.assertIn("Deadlocks", output_html)
        self.assertIn("Upcoming", output_html)

    def test_automatic_study_path_generation_in_orchestrator(self):
        # When module is loaded, orchestrator automatically computes study path without manual button
        orch = EduMentorOrchestrator(student_name="Ashwel")
        orch.load_sample_module("Operating Systems")

        self.assertEqual(orch.state, "STUDYING")
        self.assertIsNotNone(orch.topological_order)
        self.assertGreater(len(orch.topological_order), 0)
        self.assertEqual(orch.current_concept_id, orch.topological_order[0])


if __name__ == "__main__":
    unittest.main()
