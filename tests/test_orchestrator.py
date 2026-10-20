import unittest
from edumentor.orchestrator import EduMentorOrchestrator


class TestOrchestrator(unittest.TestCase):
    def test_full_session_flow(self):
        orch = EduMentorOrchestrator("Ashwel")
        
        # 1. Home
        state = orch.initialize_home()
        self.assertEqual(state["state"], "HOME")
        self.assertEqual(state["student_name"], "Ashwel")

        # 2. Student says: "I want to study Operating Systems"
        state = orch.handle_user_chat("I want to study Operating Systems")
        self.assertEqual(state["state"], "STUDYING")
        self.assertEqual(state["curriculum_title"], "Operating Systems: Concurrency & Virtual Memory")
        self.assertIsNotNone(state["current_concept"])

        # 3. Student ready
        state = orch.trigger_ready_for_recall()
        self.assertEqual(state["state"], "WAITING_RECALL")
        self.assertIsNotNone(state["last_recall_question"])

        # 4. Student answers
        ans = "Process scheduling allocates CPU time slices to runnable processes in the ready queue, balancing CPU utilization and preventing process starvation."
        state = orch.submit_recall_response(ans)
        self.assertEqual(state["state"], "FEEDBACK")
        self.assertIn(state["last_evaluation"]["verdict"], ["Correct", "Almost Correct"])


        # 5. Advance
        state = orch.advance_next_step()
        self.assertEqual(state["state"], "STUDYING")
        self.assertEqual(state["current_concept_index"], 1)


if __name__ == "__main__":
    unittest.main()
