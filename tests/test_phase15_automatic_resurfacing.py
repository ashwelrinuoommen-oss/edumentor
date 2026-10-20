"""
Unit Tests for Phase 15: Automatic Resurfacing.

Validates:
1. The student does NOT need to open a 'Revision' tab or manually search for weak topics.
2. EduMentor proactively and automatically initiates:
     Hey Ashwel, remember Process Scheduling from yesterday?
     You were almost there last time. Want to give it another try?
3. Teacher avatar appears in encouraging expression state.
4. Answering affirmatively (or clicking accept) immediately starts the active recall process.
5. Declining is handled gracefully without penalty.
6. Automatic candidate selection prioritizes weak queue and partially understood concepts.
"""

import unittest
from edumentor.orchestrator import EduMentorOrchestrator


class TestPhase15AutomaticResurfacing(unittest.TestCase):

    def setUp(self):
        self.orchestrator = EduMentorOrchestrator(student_name="Ashwel")
        self.orchestrator.load_sample_module("Operating Systems")

    def test_proactive_prompt_exact_wording_and_avatar(self):
        """
        Verify Phase 15 exact proactive dialogue and encouraging teacher avatar:
          Hey Ashwel, remember Process Scheduling from yesterday?
          You were almost there last time. Want to give it another try?
        """
        # Set Process Scheduling to almost correct / partial understanding
        ps_id = "os_process_scheduling"
        if ps_id in self.orchestrator.concepts:
            self.orchestrator.concepts[ps_id]["last_quality_score"] = 3
            self.orchestrator.concepts[ps_id]["mastery_state"] = "Partial understanding"

        payload = self.orchestrator.trigger_automatic_resurfacing(concept_id=ps_id)

        # 1. State transitions to RESURFACING
        self.assertEqual(self.orchestrator.state, "RESURFACING")
        self.assertEqual(payload["state"], "RESURFACING")

        # 2. Teacher avatar appears in encouraging expression
        self.assertEqual(self.orchestrator.teacher_state, "encouraging")
        self.assertEqual(payload["teacher_state"], "encouraging")
        self.assertIn("encouraging", payload["teacher_expression"].lower())

        # 3. Exact phrasing checks matching user prompt
        latest_msg = self.orchestrator.chat_history[-1]["content"]
        expected_line1 = "Hey Ashwel, remember Process Scheduling from yesterday?"
        expected_line2 = "You were almost there last time. Want to give it another try?"

        self.assertIn(expected_line1, latest_msg)
        self.assertIn(expected_line2, latest_msg)

    def test_chat_affirmative_response_starts_recall_immediately(self):
        """
        Verify that student responding affirmatively via chat immediately transitions
        to WAITING_RECALL with an active recall question, without manual navigation.
        """
        ps_id = "os_process_scheduling"
        self.orchestrator.trigger_automatic_resurfacing(concept_id=ps_id)
        self.assertEqual(self.orchestrator.state, "RESURFACING")

        # Student replies: "Yes, let's give it another try!"
        payload = self.orchestrator.handle_user_chat("Yes, let's give it another try!")

        # System starts active recall challenge immediately
        self.assertEqual(self.orchestrator.state, "WAITING_RECALL")
        self.assertEqual(payload["state"], "WAITING_RECALL")
        self.assertIsNotNone(self.orchestrator.last_recall_question)
        self.assertIn("Active Recall Challenge", payload["system_message"])

    def test_chat_affirmative_variants_start_recall(self):
        """
        Verify common conversational affirmatives trigger recall directly.
        """
        affirmatives = ["yes", "sure", "ok", "ready", "give it a try", "let's do it", "yep"]
        for word in affirmatives:
            orch = EduMentorOrchestrator(student_name="Ashwel")
            orch.load_sample_module("Operating Systems")
            orch.trigger_automatic_resurfacing("os_process_scheduling")
            
            payload = orch.handle_user_chat(word)
            self.assertEqual(orch.state, "WAITING_RECALL", f"Failed for affirmative: '{word}'")
            self.assertEqual(payload["state"], "WAITING_RECALL")

    def test_chat_decline_handled_gracefully(self):
        """
        Verify declining the proactive offer is handled gracefully without penalty.
        """
        self.orchestrator.trigger_automatic_resurfacing("os_process_scheduling")
        self.assertEqual(self.orchestrator.state, "RESURFACING")

        payload = self.orchestrator.handle_user_chat("Maybe later")

        self.assertNotEqual(self.orchestrator.state, "RESURFACING")
        self.assertEqual(self.orchestrator.state, "STUDYING")
        self.assertIn("revisit it whenever", payload["system_message"])

    def test_automatic_candidate_selection_weak_queue(self):
        """
        Verify candidate resolution prioritizes weak queue concepts.
        """
        self.orchestrator.weak_queue = ["os_virtual_memory"]
        candidate = self.orchestrator.check_resurfacing_candidate()
        self.assertEqual(candidate, "os_virtual_memory")

        payload = self.orchestrator.trigger_automatic_resurfacing()
        self.assertEqual(self.orchestrator.current_concept_id, "os_virtual_memory")
        self.assertIn("Virtual Memory", payload["system_message"])

    def test_automatic_candidate_selection_partial_mastery(self):
        """
        Verify candidate resolution detects concepts with quality score 3.
        """
        self.orchestrator.weak_queue = []
        ps_id = "os_process_scheduling"
        self.orchestrator.concepts[ps_id]["last_quality_score"] = 3
        self.orchestrator.concepts[ps_id]["mastery_state"] = "Partial understanding"

        candidate = self.orchestrator.check_resurfacing_candidate()
        self.assertEqual(candidate, ps_id)

        payload = self.orchestrator.trigger_automatic_resurfacing()
        self.assertEqual(self.orchestrator.current_concept_id, ps_id)
        self.assertIn("Process Scheduling", payload["system_message"])

    def test_zero_navigation_recall_pipeline_e2e(self):
        """
        End-to-end flow:
        Proactive prompt -> Accept -> Recall Prompt -> Student Answer -> Evaluation & Feedback.
        Zero navigation to revision page needed.
        """
        ps_id = "os_process_scheduling"
        self.orchestrator.concepts[ps_id]["last_quality_score"] = 3
        
        # 1. EduMentor proactively prompts
        resurface_payload = self.orchestrator.trigger_automatic_resurfacing(ps_id)
        self.assertEqual(resurface_payload["state"], "RESURFACING")

        # 2. Student accepts
        recall_payload = self.orchestrator.handle_user_chat("Sure, I'll try now")
        self.assertEqual(recall_payload["state"], "WAITING_RECALL")

        # 3. Student explains
        eval_payload = self.orchestrator.handle_user_chat(
            "Process scheduling allocates CPU time to ready processes using algorithms like Round Robin or Priority."
        )
        self.assertEqual(eval_payload["state"], "FEEDBACK")
        self.assertIsNotNone(self.orchestrator.last_evaluation)
        self.assertTrue(self.orchestrator.awaiting_confidence)


if __name__ == "__main__":
    unittest.main()
