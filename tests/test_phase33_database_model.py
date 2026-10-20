"""
Unit and Integration Tests for Phase 33 — Database Model.

Validates:
1. SQLite database initialization.
2. Presence of all 15 required tables:
   - users
   - documents
   - document_chunks
   - subjects
   - concepts
   - concept_dependencies
   - study_sessions
   - study_path_items
   - recall_questions
   - recall_attempts
   - mastery_states
   - spaced_repetition_states
   - notifications
   - conversation_messages
   - learning_events
3. Integrity, constraints, and CRUD operations across all 15 tables via EduMentorRepository.
4. Backwards compatibility with existing modules and models.
"""

import os
import tempfile
import unittest

from edumentor.database.database import init_db, get_db_connection
from edumentor.database.repository import EduMentorRepository
from edumentor.database.models import (
    User, Document, DocumentChunk, Subject, Concept, ConceptDependency,
    StudySession, StudyPathItem, RecallQuestion, RecallAttempt,
    MasteryState, SpacedRepetitionState, Notification, ConversationMessage, LearningEvent
)
from edumentor.db import init_db as init_db_legacy, get_connection as get_connection_legacy


class TestPhase33DatabaseModel(unittest.TestCase):
    """Test suite ensuring Phase 33 Database Model specifications."""

    REQUIRED_TABLES = [
        "users",
        "documents",
        "document_chunks",
        "subjects",
        "concepts",
        "concept_dependencies",
        "study_sessions",
        "study_path_items",
        "recall_questions",
        "recall_attempts",
        "mastery_states",
        "spaced_repetition_states",
        "notifications",
        "conversation_messages",
        "learning_events"
    ]

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        init_db(self.db_path)
        self.repo = EduMentorRepository(self.db_path)

    def tearDown(self):
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except Exception:
            pass

    def test_all_15_minimum_tables_exist_in_database(self):
        """Verify that every one of the 15 required tables exists in SQLite."""
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cur.fetchall()]
        conn.close()

        for required_table in self.REQUIRED_TABLES:
            self.assertIn(
                required_table,
                tables,
                f"Missing required table '{required_table}' in SQLite database schema"
            )

    def test_legacy_db_init_creates_all_15_tables(self):
        """Verify that edumentor.db.init_db also initializes the full 15 tables."""
        temp_legacy = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_legacy.close()
        legacy_path = temp_legacy.name
        try:
            init_db_legacy(legacy_path)
            with get_connection_legacy(legacy_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row["name"] for row in cur.fetchall()]

            for required_table in self.REQUIRED_TABLES:
                self.assertIn(
                    required_table,
                    tables,
                    f"Missing required table '{required_table}' in legacy db.py init"
                )
        finally:
            if os.path.exists(legacy_path):
                os.remove(legacy_path)

    def test_crud_users_and_subjects(self):
        """Verify inserting and querying users and subjects."""
        user = self.repo.create_user("TestStudent", "test@edumentor.ai", "secret123", "Computer Systems")
        self.assertEqual(user.username, "TestStudent")
        self.assertEqual(user.email, "test@edumentor.ai")

        subject = self.repo.create_subject("sub_os", "Operating Systems", "OS internals and scheduling")
        self.assertEqual(subject.title, "Operating Systems")
        fetched_sub = self.repo.get_subject("sub_os")
        self.assertIsNotNone(fetched_sub)
        self.assertEqual(fetched_sub.title, "Operating Systems")

    def test_crud_documents_and_document_chunks(self):
        """Verify inserting and querying documents and document_chunks."""
        doc = self.repo.save_document(
            doc_id="doc_os_mod1",
            title="Module 1: Virtual Memory",
            raw_text="Paging translates virtual addresses to physical addresses.",
            file_type="pdf",
            subject_id="sub_os"
        )
        self.assertEqual(doc.title, "Module 1: Virtual Memory")

        chunk = self.repo.save_document_chunk(
            chunk_id="chk_001",
            document_id="doc_os_mod1",
            chunk_index=0,
            chunk_text="Virtual memory decouples logical addresses from physical memory frames.",
            metadata={"page": 1, "topic": "paging"}
        )
        self.assertEqual(chunk.chunk_index, 0)

        chunks = self.repo.get_document_chunks("doc_os_mod1")
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].id, "chk_001")

    def test_crud_concepts_and_concept_dependencies(self):
        """Verify inserting and querying concepts and concept_dependencies."""
        c1 = self.repo.save_concept(
            concept_id="c_paging",
            title="Paging & Address Spaces",
            summary="Translating virtual addresses to physical pages",
            canonical_explanation="Paging divides memory into fixed-size frames and pages.",
            key_points=["Page Table", "TLB", "Page Faults"]
        )
        c2 = self.repo.save_concept(
            concept_id="c_virtual_memory",
            title="Virtual Memory",
            summary="Foundational memory management",
            canonical_explanation="Virtual memory allows executing processes that are not completely in memory.",
            key_points=["Address space", "Secondary storage", "Swap space"]
        )
        dep = self.repo.save_concept_dependency("c_virtual_memory", "c_paging")
        self.assertEqual(dep.prerequisite_id, "c_virtual_memory")
        self.assertEqual(dep.concept_id, "c_paging")

        deps = self.repo.get_concept_dependencies("c_paging")
        self.assertTrue(len(deps) >= 1)
        self.assertEqual(deps[0].prerequisite_id, "c_virtual_memory")
        self.assertEqual(deps[0].concept_id, "c_paging")

    def test_crud_study_sessions_and_path_items(self):
        """Verify inserting and querying study_sessions and study_path_items."""
        user = self.repo.get_or_create_user("Ashwel")
        self.repo.save_concept("c_paging", "Paging")

        session = self.repo.create_study_session(
            session_id="sess_001",
            user_id=user.id,
            subject_title="Operating Systems",
            state="STUDYING"
        )
        self.assertEqual(session.id, "sess_001")

        item = self.repo.save_study_path_item(
            item_id="item_001",
            user_id=user.id,
            concept_id="c_paging",
            sequence_order=1,
            session_id="sess_001",
            status="current"
        )
        self.assertEqual(item.sequence_order, 1)

        items = self.repo.get_study_path_items("sess_001")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].concept_id, "c_paging")

    def test_crud_recall_questions_and_recall_attempts(self):
        """Verify inserting and querying recall_questions and recall_attempts."""
        user = self.repo.get_or_create_user("Ashwel")
        self.repo.save_concept("c_paging", "Paging")

        q = self.repo.save_recall_question(
            question_id="q_page_fault",
            concept_id="c_paging",
            question_text="Explain what triggers a page fault and how the OS resolves it.",
            sample_solution="The CPU checks the page table, sees present bit is 0, triggers trap 14..."
        )
        self.assertEqual(q.question_text, "Explain what triggers a page fault and how the OS resolves it.")

        questions = self.repo.get_recall_questions("c_paging")
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].id, "q_page_fault")

        attempt = RecallAttempt(
            user_id=user.id,
            concept_id="c_paging",
            question="Explain what triggers a page fault",
            answer="A page fault occurs when a program accesses a page not resident in RAM.",
            similarity_score=0.92,
            judge_score=0.95,
            composite_score=93.5,
            quality_q=5,
            verdict="Correct",
            strengths=["Identified page table lookup", "Mentioned RAM residency"],
            missing_concepts=[],
            misconceptions=[],
            actionable_tip="Keep practicing TLB hit rate calculations."
        )
        attempt_id = self.repo.save_recall_attempt(attempt)
        self.assertIsNotNone(attempt_id)

    def test_crud_mastery_and_spaced_repetition_states(self):
        """Verify mastery_states and spaced_repetition_states tracking."""
        user = self.repo.get_or_create_user("Ashwel")
        self.repo.save_concept("c_paging", "Paging")

        mst = self.repo.save_mastery_state(
            user_id=user.id,
            concept_id="c_paging",
            mastery_level="Strong",
            mastery_percent=88.5,
            consecutive_correct=3,
            total_attempts=3,
            is_mastered=False
        )
        self.assertEqual(mst.mastery_level, "Strong")
        fetched_mst = self.repo.get_mastery_state(user.id, "c_paging")
        self.assertIsNotNone(fetched_mst)
        self.assertEqual(fetched_mst.mastery_percent, 88.5)

        sr = self.repo.save_spaced_repetition_state(
            user_id=user.id,
            concept_id="c_paging",
            repetition_n=3,
            easiness_factor=2.6,
            interval_days=6,
            status="reviewing"
        )
        self.assertEqual(sr.interval_days, 6)
        fetched_sr = self.repo.get_spaced_repetition_state(user.id, "c_paging")
        self.assertIsNotNone(fetched_sr)
        self.assertEqual(fetched_sr.status, "reviewing")

    def test_crud_conversation_messages_and_learning_events(self):
        """Verify conversation_messages and learning_events logging."""
        user = self.repo.get_or_create_user("Ashwel")
        msg = self.repo.log_conversation_message(
            message_id="msg_001",
            user_id=user.id,
            role="assistant",
            content="Welcome back Ashwel! What are we studying today?",
            session_id="sess_001",
            expression_state="greeting"
        )
        self.assertEqual(msg.role, "assistant")
        messages = self.repo.get_conversation_messages(user.id)
        self.assertTrue(len(messages) >= 1)
        self.assertEqual(messages[0].content, "Welcome back Ashwel! What are we studying today?")

        evt = self.repo.log_learning_event(
            event_id="evt_001",
            user_id=user.id,
            event_type="recall_submit",
            session_id="sess_001",
            concept_id="c_paging",
            payload={"score": 93.5, "quality": 5}
        )
        self.assertEqual(evt.event_type, "recall_submit")
        events = self.repo.get_learning_events(user.id)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "recall_submit")


if __name__ == "__main__":
    unittest.main()
