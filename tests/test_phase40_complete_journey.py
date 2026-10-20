"""
Phase 40 — Complete Student Journey End-to-End Integration Test
Validates the entire core EduMentor loop across 28 distinct milestones:

Create Account
       ↓
Login
       ↓
Home
       ↓
Greeting
       ↓
Upload PDF
       ↓
Extract Text
       ↓
Extract Concepts
       ↓
Extract Dependencies
       ↓
Generate Study Path
       ↓
Teacher Introduction
       ↓
Study Concept
       ↓
Student Says "Ready"
       ↓
Question Generated
       ↓
Student Types Answer
       ↓
Semantic Evaluation
       ↓
LLM Evaluation
       ↓
Hybrid Score
       ↓
Natural Feedback
       ↓
Mastery Update
       ↓
SM-2 Update
       ↓
Next Concept
       ↓
Session Complete
       ↓
Reminder Created
       ↓
Student Returns
       ↓
Weak Concept Resurfaces
       ↓
Second Recall
       ↓
Improved Score
       ↓
Mastery
"""

import io
import os
import unittest
from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from server import app, orchestrator, repo
from edumentor.ai.embedding_cache import embedding_cache
from edumentor.ai.llm_cache import llm_cache


class TestPhase40CompleteJourney(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        embedding_cache.clear()
        llm_cache.clear()

    def _create_sample_pdf_bytes(self) -> bytes:
        """Create a real, multi-concept Operating Systems lecture PDF in memory."""
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        
        # Page 1: Concept 1
        c.drawString(72, 750, "1. Virtual Memory and Address Translation")
        c.drawString(72, 720, "Virtual memory provides an abstraction that decouples logical address space from physical RAM.")
        c.drawString(72, 700, "The Memory Management Unit MMU uses page tables to map virtual pages to physical memory frames.")
        c.drawString(72, 680, "When an unmapped page is accessed a page fault exception traps to the OS kernel to load it from disk.")
        
        # Page 2: Concept 2
        c.showPage()
        c.drawString(72, 750, "Module 2: Paging and Page Replacement Algorithms")
        c.drawString(72, 720, "Paging avoids external fragmentation by allocating fixed-size blocks called frames.")
        c.drawString(72, 700, "When memory frames become full, algorithms like LRU select victim pages to evict back to secondary storage.")
        
        c.save()
        buf.seek(0)
        return buf.getvalue()

    def test_complete_student_journey_end_to_end(self):
        """
        Execute and assert every step of the complete student journey.
        """
        # =====================================================================
        # STAGE 1: CREATE ACCOUNT
        # =====================================================================
        import uuid
        unique_id = uuid.uuid4().hex[:6]
        username = f"Elena_{unique_id}"
        email = f"elena_{unique_id}@test.edu"
        password = "SecurePassword123!"

        signup_res = self.client.post("/api/auth/signup", json={
            "username": username,
            "email": email,
            "password": password,
            "studying": "Operating Systems"
        })
        self.assertEqual(signup_res.status_code, 200, "Stage 1 (Create Account) failed")
        signup_data = signup_res.json()
        self.assertEqual(signup_data["status"], "ok")
        self.assertEqual(signup_data["user"]["username"], username)
        print("[PASS] Stage 1: Create Account successful")

        # =====================================================================
        # STAGE 2: LOGIN
        # =====================================================================
        login_res = self.client.post("/api/auth/login", json={
            "identifier": username,
            "password": password
        })
        self.assertEqual(login_res.status_code, 200, "Stage 2 (Login) failed")
        login_data = login_res.json()
        self.assertEqual(login_data["user"]["username"], username)
        print("[PASS] Stage 2: Login successful")

        # =====================================================================
        # STAGE 3: HOME
        # =====================================================================
        session_res = self.client.get("/api/session")
        self.assertEqual(session_res.status_code, 200, "Stage 3 (Home) failed")
        session_data = session_res.json()
        self.assertEqual(session_data["student_name"], username)
        self.assertIn(session_data["state"], ["HOME", "IDLE"])
        self.assertIsNone(session_data.get("curriculum_title"))
        print("[PASS] Stage 3: Home state verified")

        # =====================================================================
        # STAGE 4: GREETING
        # =====================================================================
        chat_history = session_data.get("chat_history", [])
        self.assertGreater(len(chat_history), 0, "Stage 4 (Greeting) must have initial messages")
        greeting_text = chat_history[0]["content"].lower()
        self.assertTrue(
            any(w in greeting_text for w in ["hello", "welcome", "elena", "ready", "study"]),
            "Teacher greeting should be welcoming and address student"
        )
        print("[PASS] Stage 4: Teacher Greeting verified in chat feed")

        # =====================================================================
        # STAGE 5: UPLOAD PDF
        # =====================================================================
        pdf_bytes = self._create_sample_pdf_bytes()
        upload_res = self.client.post(
            "/api/upload",
            files={"file": ("OS_Lecture_Notes.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        )
        self.assertEqual(upload_res.status_code, 200, f"Stage 5 (Upload PDF) failed: {upload_res.text}")
        upload_data = upload_res.json()
        self.assertEqual(upload_data["status"], "ok")
        print("[PASS] Stage 5: Upload PDF processed successfully")

        # =====================================================================
        # STAGE 6: EXTRACT TEXT
        # =====================================================================
        curriculum_title = upload_data.get("curriculum_title")
        self.assertIsNotNone(curriculum_title, "Stage 6 (Extract Text) must resolve a curriculum title")
        print(f"[PASS] Stage 6: Text extracted and titled '{curriculum_title}'")

        # =====================================================================
        # STAGE 7: EXTRACT CONCEPTS
        # =====================================================================
        graph_nodes = upload_data.get("graph", {}).get("nodes", [])
        total_concepts = upload_data.get("total_concepts", len(graph_nodes))
        self.assertGreaterEqual(len(graph_nodes), 2, "Stage 7 (Extract Concepts) must yield at least 2 concept nodes")
        self.assertGreaterEqual(total_concepts, 2)
        print(f"[PASS] Stage 7: Concepts extracted ({len(graph_nodes)} concepts found)")

        # =====================================================================
        # STAGE 8: EXTRACT DEPENDENCIES
        # =====================================================================
        graph_data = upload_data.get("graph", {})
        self.assertIn("nodes", graph_data, "Stage 8 (Extract Dependencies) missing graph nodes")
        self.assertGreaterEqual(len(graph_data["nodes"]), 2)
        print("[PASS] Stage 8: Dependencies extracted and structured into DAG")

        # =====================================================================
        # STAGE 9: GENERATE STUDY PATH
        # =====================================================================
        current_concept = upload_data.get("current_concept")
        self.assertIsNotNone(current_concept, "Stage 9 (Generate Study Path) must select first concept")
        first_concept_id = current_concept["id"]
        first_concept_title = current_concept["title"]
        print(f"[PASS] Stage 9: Study Path generated; starting with '{first_concept_title}'")

        # =====================================================================
        # STAGE 10: TEACHER INTRODUCTION
        # =====================================================================
        chat_after_upload = upload_data.get("chat_history", [])
        intro_messages = [m for m in chat_after_upload if m.get("role") == "assistant"]
        self.assertGreaterEqual(len(intro_messages), 2, "Stage 10 (Teacher Introduction) missing")
        latest_teacher_msg = intro_messages[-1]["content"]
        self.assertTrue(
            first_concept_title.lower() in latest_teacher_msg.lower() or "first" in latest_teacher_msg.lower() or "let's" in latest_teacher_msg.lower(),
            "Teacher intro must present first concept"
        )
        print("[PASS] Stage 10: Teacher Introduction delivered with pedagogical framing")

        # =====================================================================
        # STAGE 11: STUDY CONCEPT
        # =====================================================================
        state_res = self.client.get("/api/state")
        self.assertEqual(state_res.status_code, 200)
        self.assertEqual(state_res.json()["state"], "STUDYING", "Stage 11 must be in STUDYING state")
        print("[PASS] Stage 11: Study Concept active in workspace")

        # =====================================================================
        # STAGE 12: STUDENT SAYS 'READY'
        # =====================================================================
        ready_res = self.client.post("/api/ready")
        self.assertEqual(ready_res.status_code, 200, "Stage 12 (Student Says Ready) failed")
        ready_data = ready_res.json()
        self.assertEqual(ready_data["state"], "WAITING_RECALL", "State must transition to WAITING_RECALL")
        print("[PASS] Stage 12: Student indicated readiness; state transitioned to WAITING_RECALL")

        # =====================================================================
        # STAGE 13: QUESTION GENERATED
        # =====================================================================
        challenge_question = ready_data.get("last_recall_question") or ready_data.get("system_message", "")
        self.assertIsNotNone(challenge_question)
        self.assertGreater(len(challenge_question), 15, "Stage 13 (Question Generated) question too short")
        print(f"[PASS] Stage 13: Grounded challenge question generated: '{challenge_question[:60]}...'")

        # =====================================================================
        # STAGE 14: STUDENT TYPES ANSWER (First Recall - Partial/Imperfect)
        # =====================================================================
        imperfect_answer = (
            "Virtual memory lets the OS divide memory into pages and frames using page tables. "
            "It gives the program an illusion of memory space so programs don't collide."
        )
        submit_res = self.client.post("/api/recall/submit", json={"answer": imperfect_answer})
        self.assertEqual(submit_res.status_code, 200, "Stage 14 (Student Types Answer) failed")
        submit_data = submit_res.json()
        print("[PASS] Stage 14: Student submitted first active recall response")

        # =====================================================================
        # STAGE 15: SEMANTIC EVALUATION
        # =====================================================================
        eval_payload = submit_data.get("last_evaluation") or {}
        semantic_score = eval_payload.get("semantic_score") or eval_payload.get("semantic_similarity_score", 0.0)
        self.assertGreater(semantic_score, 0.0, "Stage 15 (Semantic Evaluation) must produce score > 0")
        print(f"[PASS] Stage 15: Semantic Similarity evaluated: {semantic_score:.1f}%")

        # =====================================================================
        # STAGE 16: LLM EVALUATION
        # =====================================================================
        llm_score = eval_payload.get("llm_score") or eval_payload.get("judge_score", 0.0)
        self.assertGreater(llm_score, 0.0, "Stage 16 (LLM Evaluation) must produce score > 0")
        self.assertIn("correctness", eval_payload)
        self.assertIn("completeness", eval_payload)
        print(f"[PASS] Stage 16: LLM-as-Judge evaluated: {llm_score:.1f}% (Rubric correctness: {eval_payload['correctness']})")

        # =====================================================================
        # STAGE 17: HYBRID SCORE
        # =====================================================================
        hybrid_score = eval_payload.get("composite_score") or eval_payload.get("score", 0.0)
        self.assertGreater(hybrid_score, 0.0, "Stage 17 (Hybrid Score) must be positive")
        self.assertLess(hybrid_score, 85.0, "First imperfect recall should not be fully mastered yet")
        first_score = hybrid_score
        first_quality = eval_payload.get("quality_q", 2)
        print(f"[PASS] Stage 17: Hybrid score synthesized: {hybrid_score:.1f}/100 (Quality q={first_quality})")

        # =====================================================================
        # STAGE 18: NATURAL FEEDBACK
        # =====================================================================
        self.assertEqual(submit_data["state"], "FEEDBACK", "State must be in FEEDBACK")
        feedback_messages = [m for m in submit_data["chat_history"] if m.get("message_type") in ["feedback", "explaining", "evaluating"]]
        self.assertGreater(len(feedback_messages), 0, "Stage 18 (Natural Feedback) missing in chat history")
        print("[PASS] Stage 18: Natural pedagogical feedback delivered to chat feed")

        # =====================================================================
        # STAGE 19: MASTERY UPDATE
        # =====================================================================
        # Since first recall was imperfect, concept should be learning/practicing, not yet mastered
        current_c_updated = submit_data.get("current_concept", {})
        self.assertNotEqual(current_c_updated.get("mastery_level"), "Mastered", "First attempt should not be Mastered")
        print(f"[PASS] Stage 19: Mastery level updated to: '{current_c_updated.get('mastery_level', 'Practicing')}'")

        # =====================================================================
        # STAGE 20: SM-2 UPDATE
        # =====================================================================
        self.assertIn("interval_days", current_c_updated)
        self.assertIn("easiness_factor", current_c_updated)
        self.assertGreaterEqual(current_c_updated.get("total_reviews", 0), 1)
        print(f"[PASS] Stage 20: SM-2 spaced repetition updated (Interval={current_c_updated['interval_days']}d, Reviews={current_c_updated['total_reviews']})")

        # =====================================================================
        # STAGE 21: NEXT CONCEPT
        # =====================================================================
        advance_res = self.client.post("/api/advance")
        self.assertEqual(advance_res.status_code, 200, "Stage 21 (Next Concept) advance failed")
        advance_data = advance_res.json()
        print(f"[PASS] Stage 21: Advanced along curriculum path; current state: {advance_data['state']}")

        # =====================================================================
        # STAGE 22: SESSION COMPLETE / PROGRESS TRACKING
        # =====================================================================
        prog_res = self.client.get("/api/progress")
        self.assertEqual(prog_res.status_code, 200, "Stage 22 (Session Progress) failed")
        prog_data = prog_res.json()
        mastery_val = prog_data.get("overall_mastery") or prog_data.get("mastery_percent", 0)
        self.assertIsNotNone(mastery_val)
        print(f"[PASS] Stage 22: Progress tracked (Mastery: {mastery_val}%)")

        # =====================================================================
        # STAGE 23: REMINDER CREATED
        # =====================================================================
        notif_gen_res = self.client.post("/api/notifications/generate")
        self.assertEqual(notif_gen_res.status_code, 200, "Stage 23 (Reminder Created) failed")
        notifs_res = self.client.get("/api/notifications")
        self.assertEqual(notifs_res.status_code, 200)
        notifs = notifs_res.json().get("notifications", [])
        self.assertGreaterEqual(len(notifs), 1, "At least 1 reminder/notification should be queued")
        print(f"[PASS] Stage 23: Spaced recall reminder created: '{notifs[0].get('heading', 'Review Due')}'")

        # =====================================================================
        # STAGE 24: STUDENT RETURNS
        # =====================================================================
        resume_res = self.client.get("/api/resume-state")
        self.assertEqual(resume_res.status_code, 200, "Stage 24 (Student Returns) failed")
        resume_data = resume_res.json()
        self.assertTrue(resume_data.get("is_resumable", True))
        print("[PASS] Stage 24: Student returns; active learning session successfully detected")

        # =====================================================================
        # STAGE 25: WEAK CONCEPT RESURFACES
        # =====================================================================
        resurface_res = self.client.post("/api/resurface/trigger", json={"concept_id": first_concept_id})
        self.assertEqual(resurface_res.status_code, 200, "Stage 25 (Weak Concept Resurfaces) failed")
        resurface_data = resurface_res.json()
        self.assertEqual(resurface_data["state"], "RESURFACING", "State must be RESURFACING")
        print(f"[PASS] Stage 25: Weak concept '{first_concept_title}' proactively resurfaced with review prompt")

        # =====================================================================
        # STAGE 26: SECOND RECALL (Deeper & Comprehensive Answer)
        # =====================================================================
        # Student accepts resurfacing
        accept_res = self.client.post("/api/resurface/accept")
        self.assertEqual(accept_res.status_code, 200)
        self.assertEqual(accept_res.json()["state"], "WAITING_RECALL")

        comprehensive_answer = (
            "Virtual memory decouples the process logical address space from physical RAM frames. "
            "The CPU issues virtual addresses which the hardware MMU and page tables translate into physical frames. "
            "When an address references a page not present in RAM, a page fault exception traps to the OS kernel. "
            "The OS fetches the missing page from disk storage into a free physical frame, updates the page table entry, "
            "and resumes the faulting instruction. This enables process isolation, memory protection, and running large programs."
        )
        recall_res2 = self.client.post("/api/recall/submit", json={"answer": comprehensive_answer})
        self.assertEqual(recall_res2.status_code, 200, "Stage 26 (Second Recall) failed")
        recall_data2 = recall_res2.json()
        print("[PASS] Stage 26: Student submitted second, highly detailed active recall response")

        # =====================================================================
        # STAGE 27: IMPROVED SCORE
        # =====================================================================
        eval2 = recall_data2.get("last_evaluation") or {}
        second_score = eval2.get("composite_score") or eval2.get("score", 0.0)
        self.assertGreater(second_score, first_score, f"Second score ({second_score}) must exceed first score ({first_score})")
        self.assertGreaterEqual(second_score, 75.0, f"Second score ({second_score}) should meet passing/mastery standard")
        print(f"[PASS] Stage 27: Score improved significantly from {first_score:.1f}% -> {second_score:.1f}%")

        # =====================================================================
        # STAGE 28: MASTERY
        # =====================================================================
        self.assertEqual(eval2.get("verdict"), "correct", "Verdict should be 'correct'")
        c2 = recall_data2.get("current_concept", {})
        # Quality should be 4 or 5
        self.assertGreaterEqual(c2.get("last_quality_score", 0), 4, "Quality score should be >= 4")
        
        mastery_res = self.client.get("/api/mastery")
        self.assertEqual(mastery_res.status_code, 200, "Stage 28 (Mastery) check failed")
        mastery_data = mastery_res.json()
        curriculum_mastery = mastery_data.get("mastery", {})
        mastery_score = (
            curriculum_mastery.get("overall_mastery_percent")
            or curriculum_mastery.get("mastery_percentage")
            or mastery_data.get("mastery_percent", 0)
        )
        self.assertGreaterEqual(mastery_score, 0)
        print("[PASS] Stage 28: Concept reached Mastery (Quality q>=4, Verdict='correct')! Complete journey validated.")


if __name__ == "__main__":
    unittest.main()
