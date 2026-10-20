"""
Unit tests for EduMentor AI components and SQLite database repository.
"""

import os
import tempfile
import unittest
from edumentor.ai.question_generator import generate_recall_question
from edumentor.ai.feedback_generator import generate_feedback_summary
from edumentor.database.database import init_db
from edumentor.database.repository import EduMentorRepository
from edumentor.database.models import RecallAttempt, SM2Card
from edumentor.utils.security import hash_password, verify_password


class TestAIAndDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        init_db(self.temp_db.name)
        self.repo = EduMentorRepository(db_path=self.temp_db.name)

        # Pre-seed curriculum and concepts to satisfy Foreign Key constraints
        self.repo.save_curriculum(
            curriculum_id="curric_os",
            title="Operating Systems",
            description="OS Foundations",
            concepts=[
                {
                    "id": "c_virt_mem",
                    "title": "Virtual Memory",
                    "summary": "Translates virtual addresses to physical frames.",
                    "canonical_explanation": "Virtual memory gives each process the illusion of a contiguous address space.",
                    "key_points": ["Page tables", "TLB caching", "Page faults"],
                    "tier": 0
                },
                {
                    "id": "c_paging",
                    "title": "Paging",
                    "summary": "Fixed size blocks",
                    "canonical_explanation": "Paging divides virtual memory into pages and physical memory into page frames.",
                    "key_points": ["Page tables", "Frames"],
                    "tier": 1
                }
            ],
            dependencies=[("c_virt_mem", "c_paging")]
        )

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_security_hashing(self):
        pwd = "secure_study_pass"
        hashed = hash_password(pwd)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("wrong_pass", hashed))

    def test_question_generator(self):
        concept = {
            "title": "Virtual Memory",
            "summary": "Translates virtual addresses to physical frames.",
            "canonical_explanation": "Virtual memory gives each process the illusion of a contiguous address space.",
            "key_points": ["Page tables", "TLB caching", "Page faults"]
        }
        q = generate_recall_question(concept)
        self.assertIn("Virtual Memory", q)
        self.assertTrue(q.endswith("?"))

    def test_feedback_summary(self):
        summary_good = generate_feedback_summary({"composite_score": 85, "actionable_tip": "Review TLB caching."})
        self.assertIn("Outstanding", summary_good)
        self.assertIn("Review TLB caching", summary_good)

    def test_database_user_and_attempts(self):
        user = self.repo.get_or_create_user(username="TestAshwel", email="test@edumentor.ai")
        self.assertEqual(user.username, "TestAshwel")

        attempt = RecallAttempt(
            user_id=user.id,
            concept_id="c_virt_mem",
            question="Explain virtual memory?",
            answer="It maps virtual addresses to physical pages via page tables.",
            similarity_score=0.85,
            judge_score=0.90,
            composite_score=87.5,
            quality_q=4,
            verdict="Correct",
            strengths=["Mentioned address translation", "Mentioned page tables"],
            missing_concepts=["TLB caching"],
            misconceptions=[],
            actionable_tip="Keep in mind how TLB caching speeds up lookup."
        )
        self.repo.record_attempt(attempt)

        attempts = self.repo.get_recent_attempts(user.id)
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]["quality_q"], 4)
        self.assertEqual(attempts[0]["verdict"], "Correct")

    def test_database_sm2_card_flow(self):
        user = self.repo.get_or_create_user(username="CardStudent")
        card = SM2Card(
            user_id=user.id,
            concept_id="c_paging",
            repetition_n=1,
            easiness_factor=2.5,
            interval_days=1,
            next_due_date="2026-09-10",
            status="active"
        )
        self.repo.update_sm2_card(card)

        due = self.repo.get_due_or_weak_concepts(user.id, today_iso="2026-09-10")
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0]["concept_id"], "c_paging")


if __name__ == "__main__":
    unittest.main()
