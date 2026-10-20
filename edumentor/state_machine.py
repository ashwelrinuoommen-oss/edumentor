"""
AI Conversation State Machine for EduMentor (Phase 23).

Defines explicit conversation states for student learning:
IDLE, NOTE_UPLOADING, ANALYZING_NOTES, STUDY_PATH_READY, STUDYING_CONCEPT,
WAITING_FOR_RECALL, GENERATING_QUESTION, WAITING_FOR_ANSWER, EVALUATING,
FEEDBACK, NEXT_CONCEPT, REVISION_DUE, COMPLETED.

Enforces deterministic progression and maintains transition history.
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Any
from datetime import datetime


class ConversationState(str, Enum):
    """
    Formal 13-stage conversation lifecycle states for EduMentor.
    """
    IDLE = "IDLE"
    NOTE_UPLOADING = "NOTE_UPLOADING"
    ANALYZING_NOTES = "ANALYZING_NOTES"
    STUDY_PATH_READY = "STUDY_PATH_READY"
    STUDYING_CONCEPT = "STUDYING_CONCEPT"
    WAITING_FOR_RECALL = "WAITING_FOR_RECALL"
    GENERATING_QUESTION = "GENERATING_QUESTION"
    WAITING_FOR_ANSWER = "WAITING_FOR_ANSWER"
    EVALUATING = "EVALUATING"
    FEEDBACK = "FEEDBACK"
    NEXT_CONCEPT = "NEXT_CONCEPT"
    REVISION_DUE = "REVISION_DUE"
    COMPLETED = "COMPLETED"


class InvalidStateTransitionError(ValueError):
    """Raised when an illegal state transition is attempted."""
    pass


LEGACY_STATE_ALIASES: Dict[ConversationState, Set[str]] = {
    ConversationState.IDLE: {"HOME", "IDLE"},
    ConversationState.NOTE_UPLOADING: {"NOTE_UPLOADING", "UPLOADING"},
    ConversationState.ANALYZING_NOTES: {"ANALYZING_NOTES", "ANALYZING"},
    ConversationState.STUDY_PATH_READY: {"STUDY_PATH_READY", "CURRICULUM_READY"},
    ConversationState.STUDYING_CONCEPT: {"STUDYING_CONCEPT", "STUDYING"},
    ConversationState.WAITING_FOR_RECALL: {"WAITING_FOR_RECALL", "WAITING_RECALL"},
    ConversationState.GENERATING_QUESTION: {"GENERATING_QUESTION", "WAITING_RECALL", "WAITING_FOR_RECALL"},
    ConversationState.WAITING_FOR_ANSWER: {"WAITING_FOR_ANSWER", "WAITING_RECALL", "WAITING_FOR_RECALL"},
    ConversationState.EVALUATING: {"EVALUATING"},
    ConversationState.FEEDBACK: {"FEEDBACK"},
    ConversationState.NEXT_CONCEPT: {"NEXT_CONCEPT", "STUDYING", "STUDYING_CONCEPT"},
    ConversationState.REVISION_DUE: {"REVISION_DUE", "REVISIT_ALERT"},
    ConversationState.COMPLETED: {"COMPLETED", "MASTERED"},
}


class StateString(str):
    """
    A string wrapper that maintains full backward compatibility with legacy
    state identifiers (e.g., 'STUDYING', 'WAITING_RECALL', 'HOME') while also
    evaluating equal to the new formal ConversationState enum values.
    """
    def __new__(cls, current_state: ConversationState, legacy_name: Optional[str] = None):
        val = legacy_name if legacy_name is not None else current_state.value
        obj = super().__new__(cls, val)
        obj.conversation_state = current_state
        return obj

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ConversationState):
            return self.conversation_state == other
        if isinstance(other, str):
            if other == self.conversation_state.value or other == str(self):
                return True
            aliases = LEGACY_STATE_ALIASES.get(self.conversation_state, set())
            if other in aliases:
                return True
        return super().__eq__(other)

    def __hash__(self) -> int:
        return super().__hash__()


# Deterministic transition table enforcing the learning progression:
# STUDYING_CONCEPT -> WAITING_FOR_RECALL -> GENERATING_QUESTION -> WAITING_FOR_ANSWER
# -> EVALUATING -> FEEDBACK -> NEXT_CONCEPT
VALID_TRANSITIONS: Dict[ConversationState, Set[ConversationState]] = {
    ConversationState.IDLE: {
        ConversationState.NOTE_UPLOADING,
        ConversationState.ANALYZING_NOTES,
        ConversationState.STUDY_PATH_READY,
        ConversationState.STUDYING_CONCEPT,
        ConversationState.REVISION_DUE,
    },
    ConversationState.NOTE_UPLOADING: {
        ConversationState.ANALYZING_NOTES,
        ConversationState.IDLE,
    },
    ConversationState.ANALYZING_NOTES: {
        ConversationState.STUDY_PATH_READY,
        ConversationState.STUDYING_CONCEPT,
        ConversationState.IDLE,
    },
    ConversationState.STUDY_PATH_READY: {
        ConversationState.STUDYING_CONCEPT,
        ConversationState.IDLE,
    },
    ConversationState.STUDYING_CONCEPT: {
        ConversationState.WAITING_FOR_RECALL,
        ConversationState.GENERATING_QUESTION,
        ConversationState.STUDYING_CONCEPT,  # In-depth re-explanation / review
        ConversationState.REVISION_DUE,
        ConversationState.COMPLETED,
        ConversationState.IDLE,
    },
    ConversationState.WAITING_FOR_RECALL: {
        ConversationState.GENERATING_QUESTION,
        ConversationState.WAITING_FOR_ANSWER,
        ConversationState.STUDYING_CONCEPT,
        ConversationState.IDLE,
    },
    ConversationState.GENERATING_QUESTION: {
        ConversationState.WAITING_FOR_ANSWER,
        ConversationState.WAITING_FOR_RECALL,
        ConversationState.STUDYING_CONCEPT,
        ConversationState.IDLE,
    },
    ConversationState.WAITING_FOR_ANSWER: {
        ConversationState.EVALUATING,
        ConversationState.WAITING_FOR_RECALL,
        ConversationState.STUDYING_CONCEPT,
        ConversationState.IDLE,
    },
    ConversationState.EVALUATING: {
        ConversationState.FEEDBACK,
        ConversationState.WAITING_FOR_ANSWER,
        ConversationState.STUDYING_CONCEPT,
    },
    ConversationState.FEEDBACK: {
        ConversationState.NEXT_CONCEPT,
        ConversationState.WAITING_FOR_ANSWER,  # Retry answer / follow-up
        ConversationState.STUDYING_CONCEPT,
        ConversationState.REVISION_DUE,
        ConversationState.COMPLETED,
        ConversationState.IDLE,
    },
    ConversationState.NEXT_CONCEPT: {
        ConversationState.STUDYING_CONCEPT,
        ConversationState.COMPLETED,
        ConversationState.REVISION_DUE,
        ConversationState.IDLE,
    },
    ConversationState.REVISION_DUE: {
        ConversationState.STUDYING_CONCEPT,
        ConversationState.WAITING_FOR_RECALL,
        ConversationState.WAITING_FOR_ANSWER,
        ConversationState.IDLE,
    },
    ConversationState.COMPLETED: {
        ConversationState.IDLE,
        ConversationState.REVISION_DUE,
        ConversationState.STUDYING_CONCEPT,
    },
}


class ConversationStateMachine:
    """
    Manages state progression, enforces transitions, and tracks state history.
    """

    def __init__(self, initial_state: ConversationState = ConversationState.IDLE):
        self._current_state: ConversationState = initial_state
        self._previous_state: Optional[ConversationState] = None
        self._history: List[Dict[str, Any]] = [{
            "from_state": None,
            "to_state": initial_state.value,
            "trigger_event": "INITIALIZE",
            "timestamp": datetime.now().isoformat(),
            "metadata": {}
        }]

    @property
    def current_state(self) -> ConversationState:
        return self._current_state

    @property
    def previous_state(self) -> Optional[ConversationState]:
        return self._previous_state

    @property
    def transition_history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def can_transition(self, target_state: ConversationState) -> bool:
        """Check if transition from current state to target_state is permitted."""
        allowed = VALID_TRANSITIONS.get(self._current_state, set())
        return target_state in allowed

    def get_valid_next_states(self) -> List[ConversationState]:
        """Return list of valid states reachable from the current state."""
        return sorted(list(VALID_TRANSITIONS.get(self._current_state, set())), key=lambda s: s.value)

    def transition_to(
        self,
        target_state: ConversationState,
        trigger_event: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> ConversationState:
        """
        Transition to target_state.
        Raises InvalidStateTransitionError if transition is illegal and force=False.
        """
        if not force and not self.can_transition(target_state):
            valid_targets = [s.value for s in self.get_valid_next_states()]
            raise InvalidStateTransitionError(
                f"Invalid state transition: Cannot transition from {self._current_state.value} to {target_state.value}. "
                f"Allowed target states: {valid_targets}"
            )

        self._previous_state = self._current_state
        self._current_state = target_state

        record = {
            "from_state": self._previous_state.value if self._previous_state else None,
            "to_state": self._current_state.value,
            "trigger_event": trigger_event or "TRANSITION",
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self._history.append(record)
        return self._current_state

    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return the most recent state transitions up to limit."""
        return self._history[-limit:]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize current state machine status."""
        return {
            "current_state": self._current_state.value,
            "previous_state": self._previous_state.value if self._previous_state else None,
            "valid_next_states": [s.value for s in self.get_valid_next_states()],
            "history_count": len(self._history),
            "recent_transitions": self.get_recent_history(5)
        }
