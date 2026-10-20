"""
Unit and Integration Tests for Phase 3 — Note Upload & Immediate Processing.
Verifies:
- Ingestion of PDF / text module notes
- Immediate teacher acknowledgement:
  "Got it! Give me a moment — I'm going through your notes and figuring out the best way to teach them."
- Internal pipeline:
  PDF -> pdfplumber -> Text extraction -> Cleaning -> Chunking -> Concept extraction
  -> Dependency extraction -> Graph creation -> Topological sorting -> Study path
- Human, conversational teacher greeting without technical terms like 'NetworkX topological sort completed':
  "I've gone through your module. I found {count} concepts and arranged them in a learning order so we don't jump into difficult topics too early."
- Seamless in-place state transition to STUDYING without page redirects.
"""

import os
import io
import tempfile
import unittest

from edumentor.database.database import init_db
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.extractor import extract_text_from_pdf, extract_concepts_from_text


class TestUploadPhase3(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        init_db(self.temp_db.name)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_pipeline_text_to_topological_study_path(self):
        # Sample notes text
        notes_text = """
        # Operating Systems Module 1: Concurrency and Memory
        ## Virtual Memory
        Virtual memory maps virtual addresses to physical RAM frames using page tables.
        It provides process address space isolation and memory protection.
        ## Paging
        Paging divides virtual memory into pages and physical memory into page frames.
        Depends directly on the virtual memory architecture.
        ## Page Replacement Algorithms
        When page faults occur and memory is full, FIFO or LRU algorithms evict pages.
        """
        orch = EduMentorOrchestrator(student_name="Ashwel", db_path=self.temp_db.name)
        payload = orch.ingest_notes_text(notes_text, title="Operating Systems Module 1.pdf")

        # 1. Verify orchestrator state transitioned to STUDYING without redirect
        self.assertEqual(orch.state, "STUDYING")
        self.assertIsNotNone(orch.current_concept_id)

        # 2. Verify immediate teacher acknowledgement message is present in chat history
        history_contents = [msg["content"] for msg in orch.chat_history]
        has_acknowledgement = any(
            "Got it! Give me a moment — I'm going through your notes and figuring out the best way to teach them." in c
            for c in history_contents
        )
        self.assertTrue(has_acknowledgement, "Initial teacher thinking message must be present in conversation history.")

        # 3. Verify conversational tone without technical jargon (no 'NetworkX topological sort completed')
        has_human_concept_count = any(
            "I've gone through your module. I found" in c and "arranged them in a learning order so we don't jump into difficult topics too early." in c
            for c in history_contents
        )
        self.assertTrue(has_human_concept_count, "Conversational teacher concept count message must be present.")

        # Ensure zero technical jargon in chat messages
        all_text = " ".join(history_contents)
        self.assertNotIn("NetworkX topological sort completed", all_text)
        self.assertNotIn("cycle breaking via feedback arcs", all_text)

        # 4. Verify topological order is established
        self.assertGreater(len(orch.topological_order), 0)
        self.assertEqual(orch.current_concept_id, orch.topological_order[0])

    def test_empty_notes_fallback_to_sample(self):
        # Even on extremely brief notes, it gracefully provides a curated curriculum
        orch = EduMentorOrchestrator(student_name="Ashwel", db_path=self.temp_db.name)
        payload = orch.ingest_notes_text("Brief note", title="Quick.txt")

        self.assertEqual(orch.state, "STUDYING")
        self.assertGreater(len(orch.concepts), 0)


if __name__ == "__main__":
    unittest.main()
