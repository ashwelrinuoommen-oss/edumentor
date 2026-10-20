"""
Phase 41 — Product Events Telemetry Engine.
Tracks core learning and engagement events across the entire EduMentor platform:

Track:
- signup
- login
- note_uploaded / note_import
- note_processed
- concepts_generated
- study_path_generated
- concept_started
- student_ready
- question_generated
- answer_submitted / recall_response
- answer_uploaded
- evaluation_completed
- confidence_selected / confidence_rating
- concept_passed
- concept_failed
- concept_resurfaced
- concept_mastered / concept_completion / mastery_progression
- session_completed
- notification_sent
- notification_opened
"""

import json
import uuid
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict


class ProductEvent:
    """Canonical product event names for EduMentor."""
    SIGNUP = "signup"
    LOGIN = "login"
    NOTE_UPLOADED = "note_uploaded"
    NOTE_IMPORT = "note_import"                     # Design doc alias
    NOTE_PROCESSED = "note_processed"
    CONCEPTS_GENERATED = "concepts_generated"
    STUDY_PATH_GENERATED = "study_path_generated"
    CONCEPT_STARTED = "concept_started"
    STUDENT_READY = "student_ready"
    QUESTION_GENERATED = "question_generated"
    ANSWER_SUBMITTED = "answer_submitted"
    RECALL_RESPONSE = "recall_response"             # Design doc alias
    ANSWER_UPLOADED = "answer_uploaded"
    EVALUATION_COMPLETED = "evaluation_completed"
    CONFIDENCE_SELECTED = "confidence_selected"
    CONFIDENCE_RATING = "confidence_rating"         # Design doc alias
    CONCEPT_PASSED = "concept_passed"
    CONCEPT_FAILED = "concept_failed"
    CONCEPT_RESURFACED = "concept_resurfaced"
    CONCEPT_MASTERED = "concept_mastered"
    CONCEPT_COMPLETION = "concept_completion"       # Design doc alias
    MASTERY_PROGRESSION = "mastery_progression"     # Design doc alias
    SESSION_COMPLETED = "session_completed"
    NOTIFICATION_SENT = "notification_sent"
    NOTIFICATION_OPENED = "notification_opened"

    @classmethod
    def all_events(cls) -> List[str]:
        return [
            cls.SIGNUP,
            cls.LOGIN,
            cls.NOTE_UPLOADED,
            cls.NOTE_IMPORT,
            cls.NOTE_PROCESSED,
            cls.CONCEPTS_GENERATED,
            cls.STUDY_PATH_GENERATED,
            cls.CONCEPT_STARTED,
            cls.STUDENT_READY,
            cls.QUESTION_GENERATED,
            cls.ANSWER_SUBMITTED,
            cls.RECALL_RESPONSE,
            cls.ANSWER_UPLOADED,
            cls.EVALUATION_COMPLETED,
            cls.CONFIDENCE_SELECTED,
            cls.CONFIDENCE_RATING,
            cls.CONCEPT_PASSED,
            cls.CONCEPT_FAILED,
            cls.CONCEPT_RESURFACED,
            cls.CONCEPT_MASTERED,
            cls.CONCEPT_COMPLETION,
            cls.MASTERY_PROGRESSION,
            cls.SESSION_COMPLETED,
            cls.NOTIFICATION_SENT,
            cls.NOTIFICATION_OPENED,
        ]


# Aliases mapping to ensure both user-requested and design-document names are tracked
EVENT_ALIASES: Dict[str, List[str]] = {
    ProductEvent.NOTE_UPLOADED: [ProductEvent.NOTE_IMPORT],
    ProductEvent.NOTE_IMPORT: [ProductEvent.NOTE_UPLOADED],
    ProductEvent.ANSWER_SUBMITTED: [ProductEvent.RECALL_RESPONSE],
    ProductEvent.RECALL_RESPONSE: [ProductEvent.ANSWER_SUBMITTED],
    ProductEvent.CONFIDENCE_SELECTED: [ProductEvent.CONFIDENCE_RATING],
    ProductEvent.CONFIDENCE_RATING: [ProductEvent.CONFIDENCE_SELECTED],
    ProductEvent.CONCEPT_MASTERED: [ProductEvent.CONCEPT_COMPLETION, ProductEvent.MASTERY_PROGRESSION],
    ProductEvent.CONCEPT_COMPLETION: [ProductEvent.CONCEPT_MASTERED, ProductEvent.MASTERY_PROGRESSION],
    ProductEvent.MASTERY_PROGRESSION: [ProductEvent.CONCEPT_MASTERED, ProductEvent.CONCEPT_COMPLETION],
}


@dataclass
class ProductEventRecord:
    id: str
    event_name: str
    user_id: str
    session_id: Optional[str] = None
    concept_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "event_name": self.event_name,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "concept_id": self.concept_id,
            "properties": self.properties,
            "timestamp": self.timestamp,
        }


class ProductEventTracker:
    """
    Central product telemetry manager.
    Buffers events in-memory and persists them asynchronously or synchronously into SQLite.
    """

    def __init__(self, repo: Optional[Any] = None):
        self._repo = repo
        self._events: List[ProductEventRecord] = []
        self._lock = threading.Lock()

    def set_repository(self, repo: Any) -> None:
        """Attach or update database repository."""
        self._repo = repo

    def track(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        concept_id: Optional[str] = None,
        session_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        emit_aliases: bool = True
    ) -> ProductEventRecord:
        """
        Record a product event.
        Also automatically emits companion design-document aliases when appropriate.
        """
        clean_user_id = str(user_id or "user_guest").strip()
        clean_props = dict(properties or {})
        event_id = str(uuid.uuid4())
        record = ProductEventRecord(
            id=event_id,
            event_name=event_name,
            user_id=clean_user_id,
            session_id=session_id,
            concept_id=concept_id,
            properties=clean_props,
            timestamp=datetime.now().isoformat()
        )

        with self._lock:
            self._events.append(record)

        # Persist to database repository if available
        if self._repo and hasattr(self._repo, "log_learning_event"):
            try:
                self._repo.log_learning_event(
                    event_id=event_id,
                    user_id=clean_user_id,
                    event_type=event_name,
                    session_id=session_id,
                    concept_id=concept_id,
                    payload=clean_props
                )
            except Exception:
                pass

        # Automatically emit companion alias events without recursion
        if emit_aliases and event_name in EVENT_ALIASES:
            for alias_name in EVENT_ALIASES[event_name]:
                self.track(
                    event_name=alias_name,
                    user_id=clean_user_id,
                    concept_id=concept_id,
                    session_id=session_id,
                    properties=clean_props,
                    emit_aliases=False
                )

        return record

    def get_events(
        self,
        user_id: Optional[str] = None,
        event_name: Optional[str] = None,
        concept_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ProductEventRecord]:
        """Query logged events matching filters, ordered latest first."""
        with self._lock:
            filtered = list(self._events)

        if user_id:
            clean_uid = user_id.lower().strip()
            filtered = [e for e in filtered if e.user_id.lower().strip() == clean_uid]
        if event_name:
            clean_ev = event_name.lower().strip()
            filtered = [e for e in filtered if e.event_name.lower().strip() == clean_ev]
        if concept_id:
            filtered = [e for e in filtered if e.concept_id == concept_id]
        if session_id:
            filtered = [e for e in filtered if e.session_id == session_id]

        filtered.sort(key=lambda e: e.timestamp, reverse=True)
        return filtered[:limit]

    def has_event(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        concept_id: Optional[str] = None
    ) -> bool:
        """Check if a specific event has occurred."""
        events = self.get_events(user_id=user_id, event_name=event_name, concept_id=concept_id, limit=1)
        return len(events) > 0

    def get_event_counts(self, user_id: Optional[str] = None) -> Dict[str, int]:
        """Aggregate event counts by event type."""
        with self._lock:
            events = list(self._events)
        if user_id:
            clean_uid = user_id.lower().strip()
            events = [e for e in events if e.user_id.lower().strip() == clean_uid]

        counts: Dict[str, int] = {}
        for e in events:
            counts[e.event_name] = counts.get(e.event_name, 0) + 1
        return counts

    def get_funnel_summary(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate conversion rates along the primary student pedagogical funnel:
        Note Upload -> Concepts Generated -> Study Path -> Concept Started ->
        Student Ready -> Question Generated -> Answer Submitted -> Evaluation Completed ->
        Concept Mastered -> Spaced Notification Sent.
        """
        counts = self.get_event_counts(user_id=user_id)

        funnel_stages = [
            ("Signup", ProductEvent.SIGNUP),
            ("Login", ProductEvent.LOGIN),
            ("Note Uploaded", ProductEvent.NOTE_UPLOADED),
            ("Concepts Generated", ProductEvent.CONCEPTS_GENERATED),
            ("Study Path Generated", ProductEvent.STUDY_PATH_GENERATED),
            ("Concept Started", ProductEvent.CONCEPT_STARTED),
            ("Student Ready", ProductEvent.STUDENT_READY),
            ("Question Generated", ProductEvent.QUESTION_GENERATED),
            ("Answer Submitted", ProductEvent.ANSWER_SUBMITTED),
            ("Evaluation Completed", ProductEvent.EVALUATION_COMPLETED),
            ("Concept Passed", ProductEvent.CONCEPT_PASSED),
            ("Concept Mastered", ProductEvent.CONCEPT_MASTERED),
            ("Notification Sent", ProductEvent.NOTIFICATION_SENT),
            ("Notification Opened", ProductEvent.NOTIFICATION_OPENED),
        ]

        steps = []
        for label, ev in funnel_stages:
            cnt = counts.get(ev, 0)
            steps.append({
                "stage": label,
                "event_name": ev,
                "count": cnt,
            })

        # Calculate step-by-step conversion relative to Note Uploaded
        base_count = counts.get(ProductEvent.NOTE_UPLOADED, counts.get(ProductEvent.NOTE_IMPORT, 1))
        base_count = max(1, base_count)
        for s in steps:
            s["conversion_percent"] = round((s["count"] / base_count) * 100.0, 1)

        return {
            "total_events_logged": sum(counts.values()),
            "unique_event_types": len(counts),
            "counts": counts,
            "funnel": steps
        }

    def clear(self) -> None:
        """Reset in-memory event buffer (primarily for test runs)."""
        with self._lock:
            self._events.clear()


# Global Singleton Tracker Instance
event_tracker = ProductEventTracker()
