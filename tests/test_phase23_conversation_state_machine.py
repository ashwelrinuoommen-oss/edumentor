"""
Tests for Phase 23 — AI Conversation State Machine

Verifies:
1. All 13 states exist in ConversationState:
   IDLE, NOTE_UPLOADING, ANALYZING_NOTES, STUDY_PATH_READY, STUDYING_CONCEPT,
   WAITING_FOR_RECALL, GENERATING_QUESTION, WAITING_FOR_ANSWER, EVALUATING,
   FEEDBACK, NEXT_CONCEPT, REVISION_DUE, COMPLETED.
2. Exact state progression lifecycle:
   STUDYING_CONCEPT
        ↓
   Student: "I'm ready"
        ↓
   WAITING_FOR_RECALL
        ↓
   Question generated
        ↓
   WAITING_FOR_ANSWER
        ↓
   Answer submitted
        ↓
   EVALUATING
        ↓
   FEEDBACK
        ↓
   NEXT_CONCEPT
3. Illegal state transition rejection and history tracking.
4. Backward compatibility via StateString.
5. End-to-end integration with EduMentorOrchestrator.
"""

import unittest
from edumentor.state_machine import (
    ConversationState,
    ConversationStateMachine,
    InvalidStateTransitionError,
    StateString
)
from edumentor.orchestrator import EduMentorOrchestrator


class TestPhase23ConversationStateMachine(unittest.TestCase):

    def test_all_thirteen_states_exist(self):
        """Verify that all 13 states defined in the specification exist."""
        expected_states = [
            "IDLE",
            "NOTE_UPLOADING",
            "ANALYZING_NOTES",
            "STUDY_PATH_READY",
            "STUDYING_CONCEPT",
            "WAITING_FOR_RECALL",
            "GENERATING_QUESTION",
            "WAITING_FOR_ANSWER",
            "EVALUATING",
            "FEEDBACK",
            "NEXT_CONCEPT",
            "REVISION_DUE",
            "COMPLETED"
        ]
        actual_states = [s.value for s in ConversationState]
        self.assertEqual(len(actual_states), 13)
        for state in expected_states:
            self.assertIn(state, actual_states, f"Missing state: {state}")

    def test_specified_lifecycle_progression(self):
        """
        Verify the exact progression specified in the prompt:
        STUDYING_CONCEPT -> WAITING_FOR_RECALL -> GENERATING_QUESTION
        -> WAITING_FOR_ANSWER -> EVALUATING -> FEEDBACK -> NEXT_CONCEPT
        """
        sm = ConversationStateMachine(initial_state=ConversationState.STUDYING_CONCEPT)
        self.assertEqual(sm.current_state, ConversationState.STUDYING_CONCEPT)

        # 1. Student: "I'm ready" -> WAITING_FOR_RECALL
        sm.transition_to(ConversationState.WAITING_FOR_RECALL, trigger_event="STUDENT_READY")
        self.assertEqual(sm.current_state, ConversationState.WAITING_FOR_RECALL)
        self.assertEqual(sm.previous_state, ConversationState.STUDYING_CONCEPT)

        # 2. System starts generating question -> GENERATING_QUESTION
        sm.transition_to(ConversationState.GENERATING_QUESTION, trigger_event="GENERATE_QUESTION")
        self.assertEqual(sm.current_state, ConversationState.GENERATING_QUESTION)

        # 3. Question generated and presented -> WAITING_FOR_ANSWER
        sm.transition_to(ConversationState.WAITING_FOR_ANSWER, trigger_event="QUESTION_GENERATED")
        self.assertEqual(sm.current_state, ConversationState.WAITING_FOR_ANSWER)

        # 4. Answer submitted -> EVALUATING
        sm.transition_to(ConversationState.EVALUATING, trigger_event="ANSWER_SUBMITTED")
        self.assertEqual(sm.current_state, ConversationState.EVALUATING)

        # 5. Evaluation complete -> FEEDBACK
        sm.transition_to(ConversationState.FEEDBACK, trigger_event="FEEDBACK_READY")
        self.assertEqual(sm.current_state, ConversationState.FEEDBACK)

        # 6. Next step -> NEXT_CONCEPT
        sm.transition_to(ConversationState.NEXT_CONCEPT, trigger_event="NEXT_CONCEPT_REQUESTED")
        self.assertEqual(sm.current_state, ConversationState.NEXT_CONCEPT)

        # 7. Advancing to the next concept -> STUDYING_CONCEPT
        sm.transition_to(ConversationState.STUDYING_CONCEPT, trigger_event="START_STUDYING")
        self.assertEqual(sm.current_state, ConversationState.STUDYING_CONCEPT)

    def test_invalid_state_transition_rejection(self):
        """Illegal transitions should raise InvalidStateTransitionError when force=False."""
        sm = ConversationStateMachine(initial_state=ConversationState.IDLE)

        # Cannot jump from IDLE straight to EVALUATING
        with self.assertRaises(InvalidStateTransitionError):
            sm.transition_to(ConversationState.EVALUATING)

        # Cannot jump from STUDYING_CONCEPT directly to EVALUATING without question/answer
        sm.transition_to(ConversationState.STUDYING_CONCEPT)
        with self.assertRaises(InvalidStateTransitionError):
            sm.transition_to(ConversationState.EVALUATING)

    def test_state_string_backward_compatibility(self):
        """
        Verify StateString satisfies both new formal Enum and legacy string equality.
        """
        # 1. STUDYING_CONCEPT matches "STUDYING", "STUDYING_CONCEPT", and Enum
        studying = StateString(ConversationState.STUDYING_CONCEPT, legacy_name="STUDYING")
        self.assertEqual(studying, "STUDYING")
        self.assertEqual(studying, "STUDYING_CONCEPT")
        self.assertEqual(studying, ConversationState.STUDYING_CONCEPT)

        # 2. WAITING_FOR_ANSWER matches "WAITING_RECALL", "WAITING_FOR_ANSWER", and Enum
        waiting = StateString(ConversationState.WAITING_FOR_ANSWER, legacy_name="WAITING_RECALL")
        self.assertEqual(waiting, "WAITING_RECALL")
        self.assertEqual(waiting, "WAITING_FOR_ANSWER")
        self.assertEqual(waiting, ConversationState.WAITING_FOR_ANSWER)

        # 3. IDLE matches "HOME", "IDLE", and Enum
        idle = StateString(ConversationState.IDLE, legacy_name="HOME")
        self.assertEqual(idle, "HOME")
        self.assertEqual(idle, "IDLE")
        self.assertEqual(idle, ConversationState.IDLE)

    def test_orchestrator_end_to_end_state_machine(self):
        """
        Test state transitions across orchestrator lifecycle via conversational interactions.
        """
        orch = EduMentorOrchestrator(student_name="Ashwel")

        # 1. Initial State
        self.assertEqual(orch.conversation_state, ConversationState.IDLE)
        self.assertEqual(orch.state, "HOME")

        # 2. Load module -> STUDYING_CONCEPT
        orch.load_sample_module("Operating Systems")
        self.assertEqual(orch.conversation_state, ConversationState.STUDYING_CONCEPT)
        self.assertEqual(orch.state, "STUDYING")

        # 3. Student says "I'm ready" -> WAITING_FOR_ANSWER
        res = orch.handle_user_chat("I'm ready")
        self.assertEqual(orch.conversation_state, ConversationState.WAITING_FOR_ANSWER)
        self.assertEqual(res["conversation_state"], "WAITING_FOR_ANSWER")
        self.assertEqual(res["state"], "WAITING_RECALL")

        # 4. Student submits answer -> FEEDBACK
        answer = "A process has its own isolated address space while threads share address space within a process."
        res2 = orch.handle_user_chat(answer)
        self.assertEqual(orch.conversation_state, ConversationState.FEEDBACK)
        self.assertEqual(res2["conversation_state"], "FEEDBACK")
        self.assertEqual(res2["state"], "FEEDBACK")

        # 5. Student requests next concept -> STUDYING_CONCEPT
        res3 = orch.handle_user_chat("next")
        self.assertEqual(orch.conversation_state, ConversationState.STUDYING_CONCEPT)
        self.assertEqual(res3["conversation_state"], "STUDYING_CONCEPT")
        self.assertEqual(res3["state"], "STUDYING")


if __name__ == "__main__":
    unittest.main()
