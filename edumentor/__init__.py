"""
EduMentor - Adaptive Concept Recall Mastery
Core engine package
"""
from edumentor.state_machine import ConversationState, ConversationStateMachine, StateString
from edumentor.dependency_engine import ConceptDependencyEngine
from edumentor.conversation_memory import ConversationMemory, ConceptStudyRecord, RecallAttemptRecord
from edumentor.services.teacher_message_engine import TeacherMessageEngine, teacher_message_engine

from edumentor.orchestrator import is_major_teacher_message
from edumentor.scope import (
    DEFERRED_MVP_FEATURES,
    MVP_CORE_FEATURES,
    FeatureDeferredError,
    is_feature_enabled,
    get_deferred_features,
    get_deferred_feature_keys,
    get_deferred_feature_names,
    get_mvp_manifest
)

__version__ = "1.0.0"

__all__ = [
    "ConversationState",
    "ConversationStateMachine",
    "StateString",
    "ConceptDependencyEngine",
    "ConversationMemory",
    "ConceptStudyRecord",
    "RecallAttemptRecord",
    "TeacherMessageEngine",
    "teacher_message_engine",
    "is_major_teacher_message",
    "DEFERRED_MVP_FEATURES",
    "MVP_CORE_FEATURES",
    "FeatureDeferredError",
    "is_feature_enabled",
    "get_deferred_features",
    "get_deferred_feature_keys",
    "get_deferred_feature_names",
    "get_mvp_manifest",
]

