"""
Database entity data models for EduMentor.
Phase 33 Database Model definitions for all 15 SQLite tables.
"""

import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime


class ModelDictAccess:
    """Provides backwards-compatible dictionary subscripting and mapping behavior."""
    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key)

    def __iter__(self):
        return iter(self.__dict__)

    def keys(self) -> List[str]:
        return list(self.__dict__.keys())

    def values(self) -> List[Any]:
        return list(self.__dict__.values())

    def items(self) -> List[Tuple[str, Any]]:
        return list(self.__dict__.items())


# 1. users
@dataclass
class User(ModelDictAccess):
    id: str
    username: str
    email: str
    password_hash: str
    studying: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# 2. documents
@dataclass
class Document(ModelDictAccess):
    id: str
    title: str
    raw_text: str
    file_type: str = "text"
    subject_id: Optional[str] = None
    module_id: Optional[str] = None
    filename: Optional[str] = None
    user_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# 3. document_chunks
@dataclass
class DocumentChunk(ModelDictAccess):
    id: str
    document_id: str
    chunk_index: int
    chunk_text: str
    module_id: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# 4. subjects
@dataclass
class Subject(ModelDictAccess):
    id: str
    title: str
    description: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# 5. concepts
@dataclass
class Concept(ModelDictAccess):
    id: str
    title: str
    summary: str
    canonical_explanation: str
    key_points: List[str]
    tier: int = 0
    curriculum_id: Optional[str] = None
    subject_id: Optional[str] = None
    document_id: Optional[str] = None
    prompt_question: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# 6. concept_dependencies
@dataclass
class ConceptDependency(ModelDictAccess):
    prerequisite_id: str
    concept_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

# Backwards compatibility alias
Dependency = ConceptDependency


# 7. study_sessions
@dataclass
class StudySession(ModelDictAccess):
    id: str
    user_id: str
    subject_title: str
    state: str = "HOME"
    subject_id: Optional[str] = None
    current_concept_id: Optional[str] = None
    current_concept_title: Optional[str] = None
    finished_count: int = 0
    total_count: int = 0
    is_active: bool = True
    session_data_json: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    ended_at: Optional[str] = None
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


# 8. study_path_items
@dataclass
class StudyPathItem(ModelDictAccess):
    id: str
    user_id: str
    concept_id: str
    sequence_order: int
    session_id: Optional[str] = None
    status: str = "upcoming"  # 'mastered', 'current', 'proficient', 'review', 'upcoming'
    score: Optional[float] = None
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


# 9. recall_questions
@dataclass
class RecallQuestion(ModelDictAccess):
    id: str
    concept_id: str
    question_text: str
    question_type: str = "open_ended"
    sample_solution: Optional[str] = None
    explanation: Optional[str] = None
    document_id: Optional[str] = None
    subject_id: Optional[str] = None
    grounding_chunk_ids_json: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# 10. recall_attempts
@dataclass
class RecallAttempt(ModelDictAccess):
    user_id: str
    concept_id: str
    question: str
    answer: str
    similarity_score: float
    judge_score: float
    composite_score: float
    quality_q: int
    verdict: str
    strengths: List[str]
    missing_concepts: List[str]
    misconceptions: List[str]
    actionable_tip: str
    id: Optional[int] = None
    question_id: Optional[str] = None
    attempted_at: str = field(default_factory=lambda: datetime.now().isoformat())


# 11. mastery_states
@dataclass
class MasteryState(ModelDictAccess):
    id: str
    user_id: str
    concept_id: str
    mastery_level: str = "New"  # 'New', 'Developing', 'Partial', 'Strong', 'Mastered'
    mastery_percent: float = 0.0
    consecutive_correct: int = 0
    total_attempts: int = 0
    is_mastered: bool = False
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


# 12. spaced_repetition_states
@dataclass
class SpacedRepetitionState(ModelDictAccess):
    user_id: str
    concept_id: str
    id: Optional[str] = None
    repetition_n: int = 0
    easiness_factor: float = 2.5
    interval_days: int = 1
    next_due_date: str = field(default_factory=lambda: datetime.now().date().isoformat())
    last_reviewed_at: Optional[str] = None
    consecutive_correct: int = 0
    status: str = "new"  # 'new', 'learning', 'reviewing', 'mastered', 'weak'
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

# Backwards compatibility alias
SM2Card = SpacedRepetitionState


# 13. notifications
@dataclass
class Notification(ModelDictAccess):
    user_id: str
    title: str
    message: str
    concept_id: Optional[str] = None
    id: Optional[int] = None
    is_read: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


VALID_CONVERSATION_ROLES = {"user", "assistant", "system"}

VALID_MESSAGE_TYPES = {
    "greeting",
    "upload",
    "analysis",
    "study_instruction",
    "question",
    "answer",
    "evaluation",
    "feedback",
    "revision",
    "mastery",
}


# 14. conversation_messages (Phase 34: Conversation Database)
@dataclass
class ConversationMessage(ModelDictAccess):
    conversation_id: str = "conv_default"
    user_id: str = ""
    role: str = "assistant"  # 'user', 'assistant', 'system'
    message: str = ""
    message_type: str = "greeting"  # 'greeting', 'upload', 'analysis', 'study_instruction', 'question', 'answer', 'evaluation', 'feedback', 'revision', 'mastery'
    concept_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    # Backwards compatibility fields
    session_id: Optional[str] = None
    content: Optional[str] = None
    metadata_json: Optional[str] = None
    expression_state: Optional[str] = None

    def __post_init__(self):
        # Sync conversation_id and session_id
        if self.session_id and (not self.conversation_id or self.conversation_id == "conv_default"):
            self.conversation_id = self.session_id
        elif self.conversation_id and not self.session_id:
            self.session_id = self.conversation_id

        # Sync message and content
        if self.content and not self.message:
            self.message = self.content
        elif self.message and not self.content:
            self.content = self.message

        # Sync metadata and metadata_json
        if self.metadata is None and self.metadata_json:
            try:
                self.metadata = json.loads(self.metadata_json)
            except Exception:
                self.metadata = {}
        elif self.metadata is not None and not self.metadata_json:
            self.metadata_json = json.dumps(self.metadata)


# 15. learning_events
@dataclass
class LearningEvent(ModelDictAccess):
    id: str
    user_id: str
    event_type: str  # 'session_start', 'concept_study', 'recall_submit', 'eval_complete', 'mastery_achieved', 'resurface_prompt'
    session_id: Optional[str] = None
    concept_id: Optional[str] = None
    payload_json: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
