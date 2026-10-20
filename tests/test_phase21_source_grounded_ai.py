"""
Test Suite for Phase 21 — Source-Grounded AI.
Validates:
1. Every generated question maintains the strict relationship:
   Subject -> Module -> Concept -> Source Text
2. Provenance references are stored:
   Question ID, Concept ID, Module ID, Document ID, Source chunk IDs.
3. Formulates exact explanation:
   “I asked this because it was covered in your Module 2 notes.”
4. Elimination of hallucinations through strict note grounding.
"""

import unittest
import tempfile
import os
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.database.repository import EduMentorRepository
from edumentor.samples import SAMPLE_OS_MODULES
from edumentor.ai.question_generator import (
    generate_grounded_recall_question,
    generate_recall_question,
    build_question_grounding_metadata
)


class TestPhase21SourceGroundedAI(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.orchestrator = EduMentorOrchestrator(student_name="Ashwel", db_path=self.db_path)
        self.repo = EduMentorRepository(db_path=self.db_path)

        # Ingest Module 1 and Module 2
        for sm in SAMPLE_OS_MODULES[:2]:
            self.orchestrator.add_module_to_subject(
                subject_title="Operating Systems",
                module_title=sm["title"],
                module_number=sm["module_number"],
                text_or_bytes=sm["text"],
                filename=sm["filename"]
            )

    def tearDown(self):
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except Exception:
            pass

    def test_question_grounding_provenance_chain(self):
        """Verify provenance chain: Subject -> Module -> Concept -> Source Text."""
        c = self.orchestrator.concepts["os_virtual_memory"]
        grounding = generate_grounded_recall_question(
            concept=c,
            note_chunks=c.get("note_chunks")
        )

        self.assertIn("question", grounding)
        self.assertTrue(grounding["question_id"].startswith("q_os_virtual_memory"))
        self.assertEqual(grounding["subject_id"], "operating_systems")
        self.assertEqual(grounding["document_id"], c["document_id"])
        self.assertTrue(grounding["document_id"].startswith("doc_"))
        self.assertEqual(grounding["concept_id"], "os_virtual_memory")
        self.assertGreaterEqual(len(grounding["source_chunk_ids"]), 1)

    def test_pedagogical_explanation_format(self):
        """
        Verify exact pedagogical explanation:
        “I asked this because it was covered in your Module 2 notes.”
        """
        c_mod2 = self.orchestrator.concepts["os_virtual_memory"]
        meta2 = build_question_grounding_metadata(
            concept=c_mod2,
            question_text="Explain the concept of Virtual Memory."
        )
        self.assertEqual(
            meta2["explanation"],
            "I asked this because it was covered in your Module 2 notes."
        )

        c_mod1 = self.orchestrator.concepts["os_process_scheduling"]
        meta1 = build_question_grounding_metadata(
            concept=c_mod1,
            question_text="What is process scheduling?"
        )
        self.assertEqual(
            meta1["explanation"],
            "I asked this because it was covered in your Module 1 notes."
        )

    def test_orchestrator_trigger_recall_records_grounding(self):
        """Verify that triggering recall persists question grounding to SQLite database."""
        # Focus on Virtual Memory (Module 2)
        self.orchestrator.current_concept_id = "os_virtual_memory"
        payload = self.orchestrator.trigger_ready_for_recall()

        # Check in memory payload
        self.assertIn("question_grounding", payload)
        grounding = payload["question_grounding"]
        self.assertIsNotNone(grounding)
        self.assertEqual(grounding["module_number"], 2)
        self.assertEqual(grounding["explanation"], "I asked this because it was covered in your Module 2 notes.")

        # Check chat history contains the grounding note
        last_msg = self.orchestrator.chat_history[-1]["content"]
        self.assertIn("I asked this because it was covered in your Module 2 notes.", last_msg)

        # Check repository persistence
        q_id = grounding["question_id"]
        db_record = self.repo.get_question_grounding(q_id)
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record["subject_id"], "operating_systems")
        self.assertEqual(db_record["concept_id"], "os_virtual_memory")
        self.assertEqual(db_record["explanation"], "I asked this because it was covered in your Module 2 notes.")
        self.assertIsInstance(db_record["source_chunk_ids"], list)

    def test_backward_compatibility_generate_recall_question(self):
        """Ensure standard generate_recall_question still returns str by default."""
        c = self.orchestrator.concepts["os_process_scheduling"]
        q_str = generate_recall_question(c)
        self.assertIsInstance(q_str, str)
        self.assertGreater(len(q_str), 10)


if __name__ == "__main__":
    unittest.main()
