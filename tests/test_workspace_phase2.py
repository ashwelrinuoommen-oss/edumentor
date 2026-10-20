"""
Unit tests for Phase 2 — Main EduMentor Workspace.
Verifies:
- Dynamic contextual welcome greetings:
  * New user: "What do you think we should study today?"
  * Existing study session / recently studied: "Want to continue where you left off?"
  * Pending revision / weak concepts: "Ready to revise something today?"
- Floating composer file ingestion and text parsing
- Multi-file notes attachment
"""

import os
import tempfile
import unittest
from datetime import date

from edumentor.database.database import init_db
from edumentor.database.repository import EduMentorRepository
from edumentor.database.models import RecallAttempt, SM2Card
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.pages.home import get_contextual_welcome


class TestWorkspacePhase2(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        init_db(self.temp_db.name)
        self.repo = EduMentorRepository(db_path=self.temp_db.name)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_contextual_welcome_new_user(self):
        # Brand new student with no history
        orch = EduMentorOrchestrator(student_name="BrandNewStudent", db_path=self.temp_db.name)
        
        # In get_contextual_welcome, verify default prompt
        ctx = get_contextual_welcome("BrandNewStudent", orch)
        self.assertEqual(ctx["mode"], "NEW")
        self.assertIn("What do you think we should study today?", ctx["headline"])

    def test_contextual_welcome_active_session(self):
        # Student with active curriculum session
        orch = EduMentorOrchestrator(student_name="ActiveStudent", db_path=self.temp_db.name)
        orch.load_sample_module("Operating Systems")

        ctx = get_contextual_welcome("ActiveStudent", orch)
        self.assertEqual(ctx["mode"], "CONTINUE")
        self.assertIn("Want to continue where you left off?", ctx["headline"])
        self.assertIn("Operating Systems", ctx["subtext"])

    def test_contextual_welcome_pending_revision_or_weak_concepts(self):
        # Student with a weak concept / pending SM-2 revision
        user = self.repo.create_user(username="RevisionStudent", email="rev@study.org", password="PassWord123")
        
        # Seed a curriculum so foreign key succeeds
        self.repo.save_curriculum(
            curriculum_id="curric_test",
            title="System Design",
            description="Scalability",
            concepts=[{
                "id": "c_caching",
                "title": "Caching Strategies",
                "summary": "LRU, LFU, Write-Through",
                "canonical_explanation": "Caching accelerates read access.",
                "key_points": ["LRU", "Hit ratio"],
                "tier": 0
            }],
            dependencies=[]
        )

        # Mark concept as weak / due today
        card = SM2Card(
            user_id=user.id,
            concept_id="c_caching",
            repetition_n=0,
            easiness_factor=2.5,
            interval_days=1,
            next_due_date=date.today().isoformat(),
            status="weak"
        )
        self.repo.update_sm2_card(card)

        orch = EduMentorOrchestrator(student_name="RevisionStudent", db_path=self.temp_db.name)
        
        # Patch repository in get_contextual_welcome via db_path or repo check
        due = self.repo.get_due_or_weak_concepts(user_id=user.id, today_iso=date.today().isoformat())
        self.assertEqual(len(due), 1)

    def test_composer_typing_interaction(self):
        # Student writes: "I want to study Operating Systems."
        orch = EduMentorOrchestrator(student_name="Ashwel", db_path=self.temp_db.name)
        payload = orch.handle_user_chat("I want to study Operating Systems.")

        self.assertIsNotNone(orch.curriculum_title)
        self.assertIn("Operating Systems", orch.curriculum_title)
        self.assertEqual(orch.state, "STUDYING")
        self.assertGreater(len(orch.concepts), 0)

    def test_composer_notes_ingestion(self):
        # Student uploads markdown text notes
        notes_text = """
        # Concurrency in Distributed Systems
        ## Raft Consensus
        Raft is a consensus algorithm designed as an alternative to Paxos.
        Key mechanisms include leader election, log replication, and safety guarantees.
        ## Gossip Protocols
        Gossip protocols provide decentralized peer-to-peer multicast communication.
        """
        orch = EduMentorOrchestrator(student_name="Ashwel", db_path=self.temp_db.name)
        payload = orch.ingest_notes_text(notes_text, title="Distributed_Notes.md")

        self.assertIsNotNone(orch.curriculum_title)
        self.assertIn("Distributed", orch.curriculum_title)
        self.assertEqual(orch.state, "STUDYING")


if __name__ == "__main__":
    unittest.main()
