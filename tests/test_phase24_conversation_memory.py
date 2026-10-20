"""
Tests for Phase 24 — Conversation Memory & Session Context Subsystem.

Verifies:
1. All 8 core session context items are explicitly maintained:
   - Current subject
   - Current module
   - Current concept
   - Previous concepts
   - Previous answers
   - Previous feedback
   - Current mastery
   - Next review
2. Token-efficient selective context retrieval (structured state without unbounded raw chat dump).
3. Concise LLM prompt formatting via format_llm_prompt_context.
4. End-to-end integration with EduMentorOrchestrator across study lifecycle:
   - Loading curriculum/modules
   - Active recall question generation
   - Answer submission and feedback evaluation
   - Concept advancement and previous concept archival
   - Review scheduling updates
5. Conversation memory serialization, persistence via SQLite session state, and resume restoration.
6. Web payload exposure for client and inspector UI.
"""

import unittest
import tempfile
import os
from datetime import datetime

from edumentor.conversation_memory import (
    ConversationMemory,
    ConceptStudyRecord,
    RecallAttemptRecord
)
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.state_machine import ConversationState


class TestPhase24ConversationMemory(unittest.TestCase):

    def setUp(self):
        self.memory = ConversationMemory(student_name="Ashwel")
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.orch = EduMentorOrchestrator(student_name="Ashwel", db_path=self.db_path)

    def tearDown(self):
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except Exception:
            pass

    def test_eight_core_items_initialization_and_access(self):
        """Verify that all 8 core items exist and are accessible as properties."""
        mem = self.memory

        # 1. Current subject
        self.assertIn("id", mem.current_subject)
        self.assertIn("title", mem.current_subject)
        self.assertIsNone(mem.current_subject["id"])

        # 2. Current module
        self.assertIn("id", mem.current_module)
        self.assertIn("number", mem.current_module)
        self.assertIn("title", mem.current_module)

        # 3. Current concept
        self.assertIn("id", mem.current_concept)
        self.assertIn("title", mem.current_concept)
        self.assertIn("key_points", mem.current_concept)
        self.assertIn("prerequisites", mem.current_concept)

        # 4. Previous concepts
        self.assertIsInstance(mem.previous_concepts, list)
        self.assertEqual(len(mem.previous_concepts), 0)

        # 5. Previous answers
        self.assertIsInstance(mem.previous_answers, list)
        self.assertEqual(len(mem.previous_answers), 0)

        # 6. Previous feedback
        self.assertIsInstance(mem.previous_feedback, list)
        self.assertEqual(len(mem.previous_feedback), 0)

        # 7. Current mastery
        self.assertIn("concept_score", mem.current_mastery)
        self.assertIn("concept_level", mem.current_mastery)
        self.assertIn("overall_mastery_percent", mem.current_mastery)
        self.assertIn("mastered_count", mem.current_mastery)

        # 8. Next review
        self.assertIn("next_review_date", mem.next_review)
        self.assertIn("interval_days", mem.next_review)
        self.assertIn("repetition_count", mem.next_review)

    def test_direct_memory_mutations(self):
        """Test explicit mutation methods for subject, module, concept, answer, and feedback."""
        mem = self.memory

        # Subject and module mutation
        mem.set_subject(subject_id="operating_systems", subject_title="Operating Systems")
        mem.set_module(module_id="mod_1", module_number=1, module_title="Module 1: Process Management")

        self.assertEqual(mem.current_subject["id"], "operating_systems")
        self.assertEqual(mem.current_subject["title"], "Operating Systems")
        self.assertEqual(mem.current_module["number"], 1)
        self.assertEqual(mem.current_module["title"], "Module 1: Process Management")

        # Concept mutation
        concept_data = {
            "id": "os_process_scheduling",
            "title": "Process Scheduling",
            "summary": "Allocates CPU resources to ready tasks.",
            "key_points": ["Preemption vs Non-preemption", "Ready queue dispatch"],
            "canonical_explanation": "Determines which runnable process gets the CPU.",
            "prerequisites": [],
            "module_id": "mod_1",
            "module_number": 1,
            "mastery_score": 40.0,
            "mastery_level": "Learning",
            "mastery_state": "Needs relearning",
            "interval_days": 1,
            "next_review": "2026-09-15"
        }
        mem.set_current_concept(concept_data)
        self.assertEqual(mem.current_concept["id"], "os_process_scheduling")
        self.assertEqual(mem.current_concept["title"], "Process Scheduling")
        self.assertEqual(mem.current_mastery["concept_score"], 40.0)
        self.assertEqual(mem.next_review["interval_days"], 1)

        # Answer & Feedback recording
        eval_result = {
            "composite_score": 85.0,
            "quality_q": 4,
            "verdict": "Correct",
            "strengths": ["Clear definition of preemption"],
            "missing_concepts": [],
            "actionable_tip": "Connect scheduling algorithms to latency guarantees.",
            "reasoning": "Strong conceptual recall."
        }
        sm2_result = {
            "repetition": 1,
            "interval": 3,
            "next_review": "2026-09-18",
            "status": "review"
        }
        mastery_eval = {
            "mastery_score": 85.0,
            "mastery_level": "Proficient",
            "mastery_state": "Strong understanding",
            "is_mastered": True
        }
        record = mem.record_answer_and_feedback(
            concept_id="os_process_scheduling",
            concept_title="Process Scheduling",
            question_text="How does preemption work in CPU scheduling?",
            student_answer="Preemption interrupts the executing task when higher priority work arrives.",
            eval_result=eval_result,
            sm2_result=sm2_result,
            mastery_eval=mastery_eval
        )

        self.assertEqual(len(mem.previous_answers), 1)
        self.assertEqual(mem.previous_answers[0]["student_answer"], "Preemption interrupts the executing task when higher priority work arrives.")
        self.assertEqual(len(mem.previous_feedback), 1)
        self.assertEqual(mem.previous_feedback[0]["verdict"], "Correct")
        self.assertEqual(mem.previous_feedback[0]["coaching_tip"], "Connect scheduling algorithms to latency guarantees.")

        # Verify current mastery and next review updated
        self.assertEqual(mem.current_mastery["concept_score"], 85.0)
        self.assertEqual(mem.current_mastery["concept_level"], "Proficient")
        self.assertEqual(mem.next_review["interval_days"], 3)
        self.assertEqual(mem.next_review["next_review_date"], "2026-09-18")

    def test_selective_context_retrieval_does_not_dump_raw_conversation(self):
        """
        Verify that retrieve_relevant_context selects high-signal structured state
        instead of dumping unbounded raw conversations.
        """
        mem = self.memory
        mem.set_subject("operating_systems", "Operating Systems")
        mem.set_module("mod_1", 1, "Module 1: Concurrency")
        mem.set_current_concept({
            "id": "os_threads",
            "title": "Threads & Concurrency",
            "summary": "Lightweight execution units sharing address space.",
            "key_points": ["Shared memory", "Separate registers and stack"],
            "prerequisites": ["os_process_scheduling"],
            "mastery_score": 70.0,
            "mastery_level": "Practicing"
        })

        # Record 5 historical attempts
        for i in range(5):
            mem.record_answer_and_feedback(
                concept_id=f"concept_{i}",
                concept_title=f"Concept {i}",
                question_text=f"Question {i}?",
                student_answer=f"Answer {i}",
                eval_result={"composite_score": 50.0 + i * 5, "quality_q": 3, "verdict": "Almost Correct", "strengths": [], "missing_concepts": [], "actionable_tip": f"Tip {i}"},
                sm2_result={"repetition": i, "interval": i + 1, "next_review": f"2026-09-{20+i}"}
            )

        # Retrieve selective context with limit = 2
        ctx = mem.retrieve_relevant_context(intent="chat", max_history_turns=2)

        # Should contain structured keys
        self.assertIn("subject", ctx)
        self.assertIn("module", ctx)
        self.assertIn("current_concept", ctx)
        self.assertIn("mastery", ctx)
        self.assertIn("next_review", ctx)
        self.assertIn("recent_recall_history", ctx)

        # Must bound recall turns to at most max_history_turns, NOT all 5 attempts
        self.assertLessEqual(len(ctx["recent_recall_history"]), 2)
        # Verify it has the most recent attempts
        self.assertEqual(ctx["recent_recall_history"][-1]["student_answer"], "Answer 4")

    def test_format_llm_prompt_context_efficiency(self):
        """Verify format_llm_prompt_context produces a concise, information-rich context block."""
        mem = self.memory
        mem.set_subject("operating_systems", "Operating Systems")
        mem.set_module("mod_2", 2, "Module 2: Memory Management")
        mem.set_current_concept({
            "id": "os_virtual_memory",
            "title": "Virtual Memory",
            "summary": "Abstracts physical memory using page tables and address translation.",
            "key_points": ["Hardware MMU lookup", "Page faults trigger disk fetch"],
            "prerequisites": ["os_process_scheduling"],
            "mastery_score": 60.0,
            "mastery_level": "Practicing"
        })
        mem.record_answer_and_feedback(
            concept_id="os_virtual_memory",
            concept_title="Virtual Memory",
            question_text="What happens on a page fault?",
            student_answer="The CPU generates a trap and the OS brings the page from disk into RAM.",
            eval_result={
                "composite_score": 88.0,
                "quality_q": 4,
                "verdict": "Correct",
                "strengths": ["Accurately described trap and disk retrieval"],
                "missing_concepts": [],
                "actionable_tip": "Review page replacement algorithms."
            },
            sm2_result={"repetition": 1, "interval": 3, "next_review": "2026-09-17"}
        )

        prompt_str = mem.format_llm_prompt_context(intent="chat")

        self.assertIn("[ACTIVE SESSION CONTEXT]", prompt_str)
        self.assertIn("Current Subject: Operating Systems", prompt_str)
        self.assertIn("Module 2: Memory Management", prompt_str)
        self.assertIn("Current Concept: Virtual Memory", prompt_str)
        self.assertIn("Hardware MMU lookup", prompt_str)
        self.assertIn("Last Recall Attempt:", prompt_str)
        self.assertIn("Verdict: Correct (88%)", prompt_str)
        self.assertIn("Review page replacement algorithms.", prompt_str)

        # Context string should be token-efficient (typically < 1000 characters)
        self.assertLess(len(prompt_str), 1200)

    def test_orchestrator_lifecycle_memory_synchronization(self):
        """
        Verify memory updates seamlessly across the full orchestrator study session:
        load curriculum -> answer question -> receive feedback -> advance to next concept.
        """
        orch = self.orch

        # 1. Load Curriculum
        orch.load_sample_module("Operating Systems")
        mem = orch.conversation_memory

        self.assertEqual(mem.current_subject["title"], orch.curriculum_title)
        self.assertIsNotNone(mem.current_concept["id"])
        self.assertEqual(mem.current_concept["id"], orch.current_concept_id)
        first_concept_title = mem.current_concept["title"]

        # 2. Student says "I'm ready"
        res = orch.handle_user_chat("I'm ready")
        self.assertEqual(orch.conversation_state, ConversationState.WAITING_FOR_ANSWER)
        self.assertIsNotNone(mem._last_question_text)

        # 3. Student submits answer
        answer = "Process scheduling allocates the CPU among ready queue processes to optimize throughput."
        res2 = orch.handle_user_chat(answer)
        self.assertEqual(orch.conversation_state, ConversationState.FEEDBACK)

        # Memory should now have 1 answer, 1 feedback, updated mastery and next review
        self.assertEqual(len(mem.previous_answers), 1)
        self.assertEqual(mem.previous_answers[0]["student_answer"], answer)
        self.assertEqual(len(mem.previous_feedback), 1)
        self.assertIn("verdict", mem.previous_feedback[0])
        self.assertGreater(mem.current_mastery["concept_score"], 0)
        self.assertIsNotNone(mem.next_review["next_review_date"])

        # 4. Advance to Next Concept
        res3 = orch.handle_user_chat("next")
        self.assertEqual(orch.conversation_state, ConversationState.STUDYING_CONCEPT)

        # The previous concept should now be recorded in previous_concepts
        self.assertGreaterEqual(len(mem.previous_concepts), 1)
        self.assertEqual(mem.previous_concepts[0]["title"], first_concept_title)

        # Current concept should have shifted to second topic in DAG
        second_concept_id = orch.current_concept_id
        self.assertNotEqual(second_concept_id, mem.previous_concepts[0]["concept_id"])
        self.assertEqual(mem.current_concept["id"], second_concept_id)

    def test_conversational_chat_uses_structured_context_not_unbounded_dump(self):
        """
        Verify that handle_user_chat constructs teacher responses using the structured
        format_llm_prompt_context rather than passing raw empty context.
        """
        orch = self.orch
        orch.load_sample_module("Operating Systems")

        # Call a general conversational question
        res = orch.handle_user_chat("Can you explain why preemption is necessary?")
        self.assertIn("system_message", res)

        # The state payload must expose structured conversation_memory and session_context
        self.assertIn("conversation_memory", res)
        self.assertIn("session_context", res)
        summary = res["conversation_memory"]
        self.assertIn("current_subject", summary)
        self.assertIn("current_concept", summary)
        self.assertIn("previous_concepts", summary)
        self.assertIn("current_mastery", summary)

    def test_serialization_persistence_and_resume(self):
        """
        Verify that ConversationMemory serializes to dict and restores accurately
        via save_session_state and resume_session.
        """
        orch = self.orch
        orch.load_sample_module("Operating Systems")

        # Run an active recall cycle
        orch.handle_user_chat("I'm ready")
        orch.handle_user_chat("Virtual memory translates virtual addresses into physical addresses via the MMU.")
        orch.save_session_state()

        original_mem = orch.conversation_memory.get_summary()

        # Create a new orchestrator simulating a fresh app restart
        restored_orch = EduMentorOrchestrator(student_name="Ashwel", db_path=self.db_path)
        restored_orch.resume_session()

        restored_mem = restored_orch.conversation_memory.get_summary()

        # Compare core memory state
        self.assertEqual(restored_mem["current_subject"]["title"], original_mem["current_subject"]["title"])
        self.assertEqual(restored_mem["current_concept"]["id"], original_mem["current_concept"]["id"])
        self.assertEqual(len(restored_mem["previous_answers"]), len(original_mem["previous_answers"]))
        self.assertEqual(len(restored_mem["previous_feedback"]), len(original_mem["previous_feedback"]))
        self.assertEqual(
            restored_mem["previous_answers"][0]["student_answer"],
            original_mem["previous_answers"][0]["student_answer"]
        )


if __name__ == "__main__":
    unittest.main()
