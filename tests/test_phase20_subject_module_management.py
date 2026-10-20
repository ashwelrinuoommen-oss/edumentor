"""
Test Suite for Phase 20 — Subject / Module Management.
Validates:
1. Ingesting multiple modules under one unified subject (e.g. Operating Systems: Module 1, 2, 3, 4).
2. EduMentor treats multiple modules as ONE cohesive subject with a unified DAG and learning path.
3. Maintaining individual source documents and source chunks in the SQLite database.
4. Correct module retrieval and ordering.
"""

import unittest
import tempfile
import os
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.database.repository import EduMentorRepository
from edumentor.samples import SAMPLE_OS_MODULES


class TestPhase20SubjectModuleManagement(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.orchestrator = EduMentorOrchestrator(student_name="Ashwel", db_path=self.db_path)
        self.repo = EduMentorRepository(db_path=self.db_path)

    def tearDown(self):
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except Exception:
            pass

    def test_single_module_creation_and_provenance(self):
        """Test initial module ingestion sets up subject, module, and document records."""
        payload = self.orchestrator.add_module_to_subject(
            subject_title="Operating Systems",
            module_title="Module 1: Process Scheduling",
            module_number=1,
            text_or_bytes="Process Scheduling determines which runnable process in the ready queue is assigned the CPU.",
            filename="OS_Mod1.pdf"
        )
        self.assertIn("Operating Systems", payload.get("curriculum_title", ""))
        self.assertEqual(payload.get("subject_id"), "operating_systems")
        self.assertGreaterEqual(len(payload.get("modules", [])), 1)

        # Check repository persistence
        modules = self.repo.get_modules_for_subject("operating_systems")
        self.assertEqual(len(modules), 1)
        self.assertEqual(modules[0]["module_number"], 1)
        self.assertIn("Process Scheduling", modules[0]["title"])

        # Check document persistence
        doc = self.repo.get_document(modules[0]["document_id"])
        self.assertIsNotNone(doc)
        self.assertEqual(doc["filename"], "OS_Mod1.pdf")
        self.assertEqual(doc["subject_id"], "operating_systems")

    def test_multi_module_unified_subject(self):
        """
        Verify that uploading Module 1, Module 2, Module 3, Module 4:
        1. Results in ONE unified subject ('Operating Systems')
        2. Merges concepts into a single study graph
        3. Preserves individual source documents
        """
        # Upload Module 1
        m1 = SAMPLE_OS_MODULES[0]
        self.orchestrator.add_module_to_subject(
            subject_title="Operating Systems",
            module_title=m1["title"],
            module_number=m1["module_number"],
            text_or_bytes=m1["text"],
            filename=m1["filename"]
        )

        # Upload Module 2
        m2 = SAMPLE_OS_MODULES[1]
        self.orchestrator.add_module_to_subject(
            subject_title="Operating Systems",
            module_title=m2["title"],
            module_number=m2["module_number"],
            text_or_bytes=m2["text"],
            filename=m2["filename"]
        )

        # Upload Module 3
        m3 = SAMPLE_OS_MODULES[2]
        self.orchestrator.add_module_to_subject(
            subject_title="Operating Systems",
            module_title=m3["title"],
            module_number=m3["module_number"],
            text_or_bytes=m3["text"],
            filename=m3["filename"]
        )

        # Upload Module 4
        m4 = SAMPLE_OS_MODULES[3]
        payload = self.orchestrator.add_module_to_subject(
            subject_title="Operating Systems",
            module_title=m4["title"],
            module_number=m4["module_number"],
            text_or_bytes=m4["text"],
            filename=m4["filename"]
        )

        # 1. Unified Subject
        self.assertEqual(self.orchestrator.subject_id, "operating_systems")
        self.assertIn("Operating Systems", self.orchestrator.curriculum_title)

        # 2. Unified DAG: all 6 concepts from all 4 modules are united
        self.assertEqual(len(self.orchestrator.concepts), 6)
        self.assertIn("os_process_scheduling", self.orchestrator.concepts)
        self.assertIn("os_virtual_memory", self.orchestrator.concepts)
        self.assertIn("os_paging", self.orchestrator.concepts)
        self.assertIn("os_page_faults", self.orchestrator.concepts)
        self.assertIn("os_threads_concurrency", self.orchestrator.concepts)
        self.assertIn("os_mutex_deadlock", self.orchestrator.concepts)

        # Topological order exists and starts with foundational concept
        top_order = self.orchestrator.topological_order
        self.assertEqual(len(top_order), 6)
        self.assertEqual(top_order[0], "os_process_scheduling")

        # 3. Individual source documents maintained
        modules = self.repo.get_modules_for_subject("operating_systems")
        self.assertEqual(len(modules), 4)

        doc_ids = [m["document_id"] for m in modules]
        self.assertEqual(len(set(doc_ids)), 4, "Each module must have an individual source document")

        for m in modules:
            doc = self.repo.get_document(m["document_id"])
            self.assertIsNotNone(doc)
            self.assertTrue(doc["filename"].startswith("Operating_Systems_Module_"))

    def test_concept_module_grounding_tags(self):
        """Test that every concept is tagged with its correct module and document references."""
        for sm in SAMPLE_OS_MODULES:
            self.orchestrator.add_module_to_subject(
                subject_title="Operating Systems",
                module_title=sm["title"],
                module_number=sm["module_number"],
                text_or_bytes=sm["text"],
                filename=sm["filename"]
            )

        c_proc = self.orchestrator.concepts["os_process_scheduling"]
        self.assertEqual(c_proc["module_number"], 1)

        c_vm = self.orchestrator.concepts["os_virtual_memory"]
        self.assertEqual(c_vm["module_number"], 2)

        c_threads = self.orchestrator.concepts["os_threads_concurrency"]
        self.assertEqual(c_threads["module_number"], 3)

        c_deadlock = self.orchestrator.concepts["os_mutex_deadlock"]
        self.assertEqual(c_deadlock["module_number"], 4)


if __name__ == "__main__":
    unittest.main()
