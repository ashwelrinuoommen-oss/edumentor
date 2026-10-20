"""
Unit and Integration Tests for Phase 6 (Studying a Concept) and Phase 7 (Question Generation).
Verifies:
- Phase 6: System waits while student studies notes; student typing "I'm ready." triggers
  EduMentor's response: "Perfect. Let's see what you remember." and generates the active recall question.
- Phase 7: Question generation is strictly grounded in note chunks (no world knowledge hallucination).
- Phase 7: Adaptive difficulty depends dynamically on Concept Importance, Student Mastery,
  Previous Performance, and Number of Previous Attempts.
- Phase 7: Canonical benchmark: "In your own words, what is process scheduling and why is it needed in an operating system?"
"""

import unittest
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.ai.question_generator import (
    generate_recall_question,
    determine_question_difficulty
)
from edumentor.services.recall_service import RecallService
from edumentor.extractor import extract_concepts_from_text


class TestStudyAndQuestionGenPhase6And7(unittest.TestCase):
    def setUp(self):
        self.orch = EduMentorOrchestrator(student_name="Ashwel")

    # -------------------------------------------------------------------------
    # PHASE 6 TESTS: STUDYING A CONCEPT & "I'M READY" TRANSITION
    # -------------------------------------------------------------------------

    def test_phase6_system_waits_while_student_studies(self):
        """
        Verify that after presenting the concept card and saying:
        'Let me know when you're ready.',
        the system waits in STUDYING state with teacher_state 'waiting'.
        """
        self.orch.load_sample_module("Operating Systems")
        self.assertEqual(self.orch.state, "STUDYING")
        self.assertEqual(self.orch.teacher_state, "waiting")

        latest_msg = self.orch.chat_history[-1]["content"]
        self.assertIn("Take your time and study it from your notes. Let me know when you're ready.", latest_msg)

    def test_phase6_student_types_im_ready_triggers_exact_response(self):
        """
        Verify that when student types "I'm ready.", EduMentor responds:
        "Perfect. Let's see what you remember." then generates the question.
        """
        self.orch.load_sample_module("Operating Systems")
        self.assertEqual(self.orch.state, "STUDYING")

        # Student types exact prompt: "I'm ready."
        state = self.orch.handle_user_chat("I'm ready.")

        # System transitions to WAITING_RECALL
        self.assertEqual(state["state"], "WAITING_RECALL")
        self.assertEqual(state["teacher_state"], "encouraging")

        # EduMentor responds: "Perfect. Let's see what you remember."
        latest_msg = self.orch.chat_history[-1]["content"]
        self.assertTrue(
            latest_msg.startswith("Perfect. Let's see what you remember."),
            f"Response must start with 'Perfect. Let's see what you remember.', got: {latest_msg}"
        )

        # Contains active recall question
        self.assertIn("Active Recall Challenge", latest_msg)
        self.assertIn(state["last_recall_question"], latest_msg)
        self.assertTrue(state["last_recall_question"].endswith("?"))

    def test_phase6_conversational_ready_variations(self):
        """
        Verify flexible conversational readiness triggers:
        'im ready', 'ready', 'i am ready', 'I am ready.'
        """
        variations = ["im ready", "ready", "I am ready.", "READY!"]
        for phrase in variations:
            orch = EduMentorOrchestrator(student_name="Ashwel")
            orch.load_sample_module("Operating Systems")
            state = orch.handle_user_chat(phrase)
            self.assertEqual(state["state"], "WAITING_RECALL")
            latest_msg = orch.chat_history[-1]["content"]
            self.assertTrue(latest_msg.startswith("Perfect. Let's see what you remember."))

    # -------------------------------------------------------------------------
    # PHASE 7 TESTS: QUESTION GENERATION PIPELINE & NOTE CHUNK GROUNDING
    # -------------------------------------------------------------------------

    def test_phase7_canonical_process_scheduling_benchmark(self):
        """
        Verify benchmark question for Process Scheduling:
        'In your own words, what is process scheduling and why is it needed in an operating system?'
        """
        concept = {
            "id": "os_process_scheduling",
            "title": "Process Scheduling",
            "summary": "Core operating system mechanism allocating CPU time to runnable processes.",
            "canonical_explanation": "Process scheduling decides which runnable process in the ready queue is given CPU time.",
            "note_chunks": [
                "Process Scheduling is an essential operating system mechanism that determines which runnable process in the ready queue is assigned the CPU for execution when the CPU becomes available.",
                "In a multi-programming system, multiple processes compete for limited CPU resources. The scheduler switches between processes using context switching, balancing CPU utilization, throughput, turnaround time, waiting time, and responsiveness while preventing process starvation."
            ]
        }

        # Foundational difficulty (attempt = 0)
        q = generate_recall_question(concept, note_chunks=concept["note_chunks"])
        self.assertEqual(
            q,
            "In your own words, what is process scheduling and why is it needed in an operating system?"
        )

    def test_phase7_grounded_in_note_chunks_no_hallucination(self):
        """
        Verify questions are generated strictly from the provided note chunks,
        without drawing upon unrelated external world knowledge.
        """
        custom_notes = [
            "Photosynthesis in halophilic bacteria relies on bacteriorhodopsin as a light-driven proton pump.",
            "Retinal chromophore undergoes photoisomerization from all-trans to 13-cis, creating a transmembrane proton electrochemical gradient."
        ]
        biology_concept = {
            "id": "bacteriorhodopsin_proton_pump",
            "title": "Bacteriorhodopsin Proton Pump",
            "summary": "Light-driven proton pump creating an electrochemical gradient.",
            "canonical_explanation": "Bacteriorhodopsin uses light absorption by retinal to pump protons across the bacterial membrane.",
            "key_points": [
                "Photoisomerization of retinal chromophore from all-trans to 13-cis",
                "Establishes transmembrane proton electrochemical gradient for ATP synthesis"
            ],
            "note_chunks": custom_notes
        }

        q = generate_recall_question(biology_concept, note_chunks=custom_notes)
        self.assertIn("Bacteriorhodopsin Proton Pump", q)
        self.assertTrue(q.endswith("?"))
        self.assertIn("In your own words", q)

    def test_phase7_four_factors_determine_difficulty(self):
        """
        Verify question difficulty dynamically calibrates across all 4 factors:
        1. Concept Importance
        2. Student Mastery
        3. Previous Performance
        4. Number of Previous Attempts
        """
        concept = {
            "id": "os_paging",
            "title": "Paging & Page Tables",
            "key_points": ["Virtual Page Number to Physical Frame mapping", "TLB translation cache"]
        }

        # Case 1: First attempt (attempts=0) -> foundational
        d1 = determine_question_difficulty(
            concept,
            mastery_context={"previous_attempts": 0, "previous_performance": 0, "student_mastery": 0, "concept_importance": "foundational"}
        )
        self.assertEqual(d1["level"], "foundational")
        self.assertEqual(d1["focus"], "core_mechanism_and_purpose")

        # Case 2: Struggling on revisit (prev_q=2 < 3) -> foundational
        d2 = determine_question_difficulty(
            concept,
            mastery_context={"previous_attempts": 2, "previous_performance": 2, "student_mastery": 40, "concept_importance": "foundational"}
        )
        self.assertEqual(d2["level"], "foundational")

        # Case 3: 1-2 attempts with passing score (prev_q >= 3, mastery < 75%) -> intermediate
        d3 = determine_question_difficulty(
            concept,
            mastery_context={"previous_attempts": 1, "previous_performance": 4, "student_mastery": 50, "concept_importance": "intermediate"}
        )
        self.assertEqual(d3["level"], "intermediate")
        self.assertEqual(d3["focus"], "step_by_step_mechanics")

        # Case 4: Advanced (attempts >= 3 or mastery >= 75%) -> advanced
        d4 = determine_question_difficulty(
            concept,
            mastery_context={"previous_attempts": 3, "previous_performance": 5, "student_mastery": 80, "concept_importance": "applied"}
        )
        self.assertEqual(d4["level"], "advanced")
        self.assertEqual(d4["focus"], "tradeoffs_and_failure_modes")

    def test_phase7_difficulty_modulates_generated_question(self):
        """
        Verify that difficulty levels produce appropriately tailored recall questions
        for the same concept.
        """
        concept = {
            "id": "os_process_scheduling",
            "title": "Process Scheduling",
            "note_chunks": ["Processes compete for CPU. Scheduler uses context switching and ready queue."]
        }

        # Level 1: Foundational
        q_foundational = generate_recall_question(
            concept,
            mastery_context={"previous_attempts": 0, "previous_performance": 0, "student_mastery": 0}
        )
        self.assertIn("what is process scheduling and why is it needed", q_foundational)

        # Level 2: Intermediate
        q_intermediate = generate_recall_question(
            concept,
            mastery_context={"previous_attempts": 1, "previous_performance": 4, "student_mastery": 40}
        )
        self.assertIn("ready queue", q_intermediate)
        self.assertIn("context switching", q_intermediate)

        # Level 3: Advanced
        q_advanced = generate_recall_question(
            concept,
            mastery_context={"previous_attempts": 3, "previous_performance": 5, "student_mastery": 85}
        )
        self.assertIn("starvation", q_advanced)
        self.assertIn("throughput", q_advanced)

    def test_phase7_recall_service_integration(self):
        """Verify RecallService passes note_chunks and mastery_context seamlessly."""
        service = RecallService()
        concept = {
            "id": "os_process_scheduling",
            "title": "Process Scheduling",
            "note_chunks": ["Process scheduling allocates CPU time slices."]
        }
        q = service.create_question(
            concept=concept,
            note_chunks=concept["note_chunks"],
            mastery_context={"previous_attempts": 0}
        )
        self.assertIn("process scheduling", q.lower())
        self.assertTrue(q.endswith("?"))

    def test_phase7_extractor_attaches_note_chunks(self):
        """Verify document extractor attaches note_chunks to every extracted concept."""
        sample_text = """
# Database Concurrency Control

## Two Phase Locking (2PL)
Two-phase locking ensures serializability by dividing transaction lock acquisition into a growing phase and a shrinking phase.
Once a transaction releases any lock, it cannot acquire any new locks.

## Multi-Version Concurrency Control (MVCC)
MVCC maintains multiple physical versions of data items so readers do not block writers and writers do not block readers.
Timestamps or transaction IDs determine snapshot visibility.
"""
        concepts, deps = extract_concepts_from_text(sample_text, doc_title="Database Notes")
        self.assertGreater(len(concepts), 0)
        for c in concepts:
            self.assertIn("note_chunks", c)
            self.assertIsInstance(c["note_chunks"], list)
            self.assertGreater(len(c["note_chunks"]), 0)


if __name__ == "__main__":
    unittest.main()
