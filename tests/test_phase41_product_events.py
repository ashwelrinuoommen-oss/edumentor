"""
Phase 41 — Product Events Test Suite
Validates that all required product events and design-document recommended events
are accurately tracked, persisted, aggregated, and queryable.

Required Events:
- signup
- login
- note_uploaded
- note_processed
- concepts_generated
- study_path_generated
- concept_started
- student_ready
- question_generated
- answer_submitted
- answer_uploaded
- evaluation_completed
- confidence_selected
- concept_passed
- concept_failed
- concept_resurfaced
- concept_mastered
- session_completed
- notification_sent
- notification_opened

Design Document Recommendations:
- note import (note_import)
- concept completion (concept_completion)
- recall response (recall_response)
- confidence rating (confidence_rating)
- mastery progression (mastery_progression)
"""

import io
import uuid
import unittest
from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from server import app, repo, orchestrator
from edumentor.events import (
    ProductEvent,
    ProductEventRecord,
    ProductEventTracker,
    event_tracker,
    EVENT_ALIASES
)


class TestPhase41ProductEvents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        event_tracker.clear()
        event_tracker.set_repository(repo)

    def _create_sample_pdf(self) -> bytes:
        """Create sample 2-module test PDF."""
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.drawString(72, 750, "1. Virtual Memory Translation")
        c.drawString(72, 720, "Virtual memory provides logical address translation to physical frames via MMU.")
        c.drawString(72, 700, "Page tables map virtual page numbers to physical frame numbers.")
        c.showPage()
        c.drawString(72, 750, "2. Page Replacement Mechanics")
        c.drawString(72, 720, "LRU page replacement evicts the least recently accessed victim page to disk.")
        c.save()
        buf.seek(0)
        return buf.getvalue()

    # -------------------------------------------------------------------------
    # TEST 1: PRODUCT EVENT ENUMERATIONS & ALIASES
    # -------------------------------------------------------------------------
    def test_product_event_definitions_and_aliases(self):
        """Verify all required events and design document recommendations are defined."""
        required_events = [
            "signup",
            "login",
            "note_uploaded",
            "note_processed",
            "concepts_generated",
            "study_path_generated",
            "concept_started",
            "student_ready",
            "question_generated",
            "answer_submitted",
            "answer_uploaded",
            "evaluation_completed",
            "confidence_selected",
            "concept_passed",
            "concept_failed",
            "concept_resurfaced",
            "concept_mastered",
            "session_completed",
            "notification_sent",
            "notification_opened"
        ]
        all_defined = ProductEvent.all_events()
        for ev in required_events:
            self.assertIn(ev, all_defined, f"Required product event '{ev}' missing from ProductEvent")

        # Design document specific recommendations
        design_doc_recommendations = [
            "note_import",
            "concept_completion",
            "recall_response",
            "confidence_rating",
            "mastery_progression"
        ]
        for rec in design_doc_recommendations:
            self.assertIn(rec, all_defined, f"Design doc recommended event '{rec}' missing")

        # Verify alias mappings exist
        self.assertIn(ProductEvent.NOTE_IMPORT, EVENT_ALIASES[ProductEvent.NOTE_UPLOADED])
        self.assertIn(ProductEvent.RECALL_RESPONSE, EVENT_ALIASES[ProductEvent.ANSWER_SUBMITTED])
        self.assertIn(ProductEvent.CONFIDENCE_RATING, EVENT_ALIASES[ProductEvent.CONFIDENCE_SELECTED])
        self.assertIn(ProductEvent.CONCEPT_COMPLETION, EVENT_ALIASES[ProductEvent.CONCEPT_MASTERED])
        self.assertIn(ProductEvent.MASTERY_PROGRESSION, EVENT_ALIASES[ProductEvent.CONCEPT_MASTERED])

    # -------------------------------------------------------------------------
    # TEST 2: TRACKER FUNCTIONALITY, ALIAS EMISSION, AND FILTERING
    # -------------------------------------------------------------------------
    def test_tracker_record_creation_and_filtering(self):
        """Verify event tracker creates structured records, handles aliases, and filters correctly."""
        tracker = ProductEventTracker(repo=repo)

        # Track note upload (should also emit note_import alias)
        rec = tracker.track(
            ProductEvent.NOTE_UPLOADED,
            user_id="user_alice",
            properties={"filename": "os_notes.pdf", "size_bytes": 1024}
        )
        self.assertEqual(rec.event_name, ProductEvent.NOTE_UPLOADED)
        self.assertEqual(rec.user_id, "user_alice")
        self.assertEqual(rec.properties["filename"], "os_notes.pdf")

        # Both note_uploaded and note_import should exist
        uploaded_events = tracker.get_events(user_id="user_alice", event_name="note_uploaded")
        import_events = tracker.get_events(user_id="user_alice", event_name="note_import")
        self.assertGreaterEqual(len(uploaded_events), 1)
        self.assertGreaterEqual(len(import_events), 1)

        # Track recall answer (should emit recall_response alias)
        tracker.track(
            ProductEvent.ANSWER_SUBMITTED,
            user_id="user_alice",
            concept_id="concept_vm",
            properties={"score": 85.0}
        )
        self.assertTrue(tracker.has_event("answer_submitted", user_id="user_alice"))
        self.assertTrue(tracker.has_event("recall_response", user_id="user_alice"))

        # Event counts aggregation
        counts = tracker.get_event_counts(user_id="user_alice")
        self.assertEqual(counts.get("note_uploaded"), 1)
        self.assertEqual(counts.get("note_import"), 1)
        self.assertEqual(counts.get("answer_submitted"), 1)
        self.assertEqual(counts.get("recall_response"), 1)

    # -------------------------------------------------------------------------
    # TEST 3: REST API ENDPOINTS FOR PRODUCT EVENTS
    # -------------------------------------------------------------------------
    def test_product_events_rest_endpoints(self):
        """Verify POST /api/events/track, GET /api/events, and GET /api/events/summary."""
        test_uid = f"user_test_{uuid.uuid4().hex[:6]}"

        # 1. Post custom client-side event
        post_res = self.client.post("/api/events/track", json={
            "event_name": "student_ready",
            "user_id": test_uid,
            "concept_id": "concept_scheduling",
            "properties": {"client": "web", "device": "desktop"}
        })
        self.assertEqual(post_res.status_code, 200)
        post_data = post_res.json()
        self.assertEqual(post_data["status"], "ok")
        self.assertEqual(post_data["event"]["event_name"], "student_ready")
        self.assertEqual(post_data["event"]["user_id"], test_uid)

        # 2. Query events via GET /api/events
        get_res = self.client.get(f"/api/events?user_id={test_uid}")
        self.assertEqual(get_res.status_code, 200)
        get_data = get_res.json()
        self.assertEqual(get_data["status"], "ok")
        self.assertGreaterEqual(get_data["total"], 1)
        found_ev = get_data["events"][0]
        self.assertEqual(found_ev["event_name"], "student_ready")

        # 3. Query funnel summary via GET /api/events/summary
        sum_res = self.client.get(f"/api/events/summary?user_id={test_uid}")
        self.assertEqual(sum_res.status_code, 200)
        sum_data = sum_res.json()
        self.assertEqual(sum_data["status"], "ok")
        summary = sum_data["summary"]
        self.assertIn("counts", summary)
        self.assertIn("funnel", summary)
        self.assertGreaterEqual(summary["total_events_logged"], 1)

    # -------------------------------------------------------------------------
    # TEST 4: END-TO-END WORKSPACE JOURNEY PRODUCT EVENTS TRACKING
    # -------------------------------------------------------------------------
    def test_full_workspace_journey_emits_product_events(self):
        """
        Execute core operations and verify that every relevant product event is logged.
        """
        uid_rand = uuid.uuid4().hex[:6]
        username = f"Student_{uid_rand}"
        email = f"student_{uid_rand}@edu.ai"
        user_id = f"user_{username.lower()}"

        # 1. Signup
        signup_res = self.client.post("/api/auth/signup", json={
            "username": username,
            "email": email,
            "password": "Password123!",
            "studying": "Operating Systems"
        })
        self.assertEqual(signup_res.status_code, 200)
        self.assertTrue(event_tracker.has_event(ProductEvent.SIGNUP, user_id=user_id))

        # 2. Login
        login_res = self.client.post("/api/auth/login", json={
            "identifier": username,
            "password": "Password123!"
        })
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(event_tracker.has_event(ProductEvent.LOGIN, user_id=user_id))

        # 3. Note Upload / Processed / Concepts & Path Generated
        pdf_bytes = self._create_sample_pdf()
        upload_res = self.client.post(
            "/api/upload",
            files={"file": ("OS_Lecture.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        )
        self.assertEqual(upload_res.status_code, 200)

        # Verify note upload & design doc note_import
        self.assertTrue(event_tracker.has_event(ProductEvent.NOTE_UPLOADED, user_id=user_id))
        self.assertTrue(event_tracker.has_event(ProductEvent.NOTE_IMPORT, user_id=user_id))
        self.assertTrue(event_tracker.has_event(ProductEvent.NOTE_PROCESSED, user_id=user_id))
        self.assertTrue(event_tracker.has_event(ProductEvent.CONCEPTS_GENERATED, user_id=user_id))
        self.assertTrue(event_tracker.has_event(ProductEvent.STUDY_PATH_GENERATED, user_id=user_id))
        self.assertTrue(event_tracker.has_event(ProductEvent.CONCEPT_STARTED, user_id=user_id))

        # 4. Student Ready & Question Generated
        ready_res = self.client.post("/api/ready")
        self.assertEqual(ready_res.status_code, 200)
        self.assertTrue(event_tracker.has_event(ProductEvent.STUDENT_READY, user_id=user_id))
        self.assertTrue(event_tracker.has_event(ProductEvent.QUESTION_GENERATED, user_id=user_id))

        # 5. Answer Submitted (Recall Response) & Evaluation Completed
        answer_text = "Virtual memory provides logical address translation to physical frames via MMU."
        submit_res = self.client.post("/api/recall/submit", json={"answer": answer_text})
        self.assertEqual(submit_res.status_code, 200)

        self.assertTrue(event_tracker.has_event(ProductEvent.ANSWER_SUBMITTED, user_id=user_id))
        self.assertTrue(event_tracker.has_event(ProductEvent.RECALL_RESPONSE, user_id=user_id))
        self.assertTrue(event_tracker.has_event(ProductEvent.EVALUATION_COMPLETED, user_id=user_id))

        # Check either concept_passed or concept_failed
        has_passed = event_tracker.has_event(ProductEvent.CONCEPT_PASSED, user_id=user_id)
        has_failed = event_tracker.has_event(ProductEvent.CONCEPT_FAILED, user_id=user_id)
        self.assertTrue(has_passed or has_failed, "Should log either concept_passed or concept_failed")

        # 6. Confidence Selected (and design doc confidence_rating)
        conf_res = self.client.post("/api/recall/confidence", json={"confidence": "Very confident"})
        self.assertEqual(conf_res.status_code, 200)
        self.assertTrue(event_tracker.has_event(ProductEvent.CONFIDENCE_SELECTED, user_id=user_id))
        self.assertTrue(event_tracker.has_event(ProductEvent.CONFIDENCE_RATING, user_id=user_id))

        # 7. Answer Uploaded (PDF answer file submission)
        upload_ans_res = self.client.post(
            "/api/recall/upload-answer",
            files={"file": ("my_answer.txt", io.BytesIO(b"Page tables map logical pages to physical frames."), "text/plain")}
        )
        self.assertEqual(upload_ans_res.status_code, 200)
        self.assertTrue(event_tracker.has_event(ProductEvent.ANSWER_UPLOADED, user_id=user_id))

        # 8. Notification Sent & Opened
        notif_gen = self.client.post("/api/notifications/generate")
        self.assertEqual(notif_gen.status_code, 200)
        self.assertTrue(event_tracker.has_event(ProductEvent.NOTIFICATION_SENT, user_id=user_id))

        read_res = self.client.post("/api/notifications/read", json={})
        self.assertEqual(read_res.status_code, 200)
        self.assertTrue(event_tracker.has_event(ProductEvent.NOTIFICATION_OPENED))

        # 9. Concept Resurfaced
        resurface_res = self.client.post("/api/resurface/trigger")
        self.assertEqual(resurface_res.status_code, 200)
        self.assertTrue(event_tracker.has_event(ProductEvent.CONCEPT_RESURFACED, user_id=user_id))

        # 10. Concept Mastered / Concept Completion / Mastery Progression
        # Submit deep answer to reach mastery
        self.client.post("/api/resurface/accept")
        deep_ans = (
            "Virtual memory decouples the process logical address space from physical RAM frames. "
            "The Memory Management Unit MMU uses page tables to translate logical addresses to physical frames. "
            "When an address references an unmapped page a page fault exception traps to the OS kernel to load it from disk."
        )
        sub2 = self.client.post("/api/recall/submit", json={"answer": deep_ans})
        self.assertEqual(sub2.status_code, 200)
        self.assertTrue(event_tracker.has_event(ProductEvent.CONCEPT_MASTERED, user_id=user_id))
        self.assertTrue(event_tracker.has_event(ProductEvent.CONCEPT_COMPLETION, user_id=user_id))
        self.assertTrue(event_tracker.has_event(ProductEvent.MASTERY_PROGRESSION, user_id=user_id))

        # 11. Advance and complete session
        self.client.post("/api/advance")
        # If second concept also completed, session_completed is logged
        self.client.post("/api/ready")
        self.client.post("/api/recall/submit", json={"answer": "LRU algorithm selects the least recently accessed page to evict."})
        self.client.post("/api/advance")
        self.assertTrue(event_tracker.has_event(ProductEvent.SESSION_COMPLETED, user_id=user_id))

        # Verify Funnel Metrics
        funnel = event_tracker.get_funnel_summary(user_id=user_id)
        self.assertGreater(funnel["total_events_logged"], 10)
        self.assertGreaterEqual(funnel["unique_event_types"], 10)


if __name__ == "__main__":
    unittest.main()
