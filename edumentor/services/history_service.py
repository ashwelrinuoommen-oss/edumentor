"""
History and session tracking service for EduMentor.
"""

from typing import List, Dict, Any, Optional
from edumentor.database.repository import EduMentorRepository


class HistoryService:
    def __init__(self, repository: Optional[EduMentorRepository] = None):
        self.repository = repository or EduMentorRepository()
        self.logs: List[Dict[str, Any]] = []

    def log_action(self, action_type: str, details: Dict[str, Any]):
        """Logs an in-session user or agent action."""
        self.logs.append({"action": action_type, "details": details})

    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns in-memory recent event logs."""
        return self.logs[-limit:]

    def get_user_recall_attempts(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves persistent recall attempts and scores from SQLite."""
        try:
            return self.repository.get_recent_attempts(user_id=user_id, limit=limit)
        except Exception:
            return []

    def get_due_reviews(self, user_id: str, today_iso: str) -> List[Dict[str, Any]]:
        """Retrieves cards requiring spaced repetition review."""
        try:
            return self.repository.get_due_or_weak_concepts(user_id=user_id, today_iso=today_iso)
        except Exception:
            return []

    def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves persistent conversation sessions for user."""
        try:
            return self.repository.get_user_conversations(user_id=user_id, limit=limit)
        except Exception:
            return []

    def reconstruct_session(self, conversation_id: str) -> Dict[str, Any]:
        """Reconstructs a pedagogical session from conversation messages."""
        try:
            return self.repository.reconstruct_session(conversation_id=conversation_id)
        except Exception as e:
            return {
                "conversation_id": conversation_id,
                "found": False,
                "error": str(e),
                "turns": [],
                "concepts_covered": [],
                "recall_exchanges": [],
                "mastery_milestones": [],
                "revisions_triggered": []
            }

