"""
EduMentor Error Handling & Resilience Subsystem (Phase 36).
Guarantees the conversational experience never abruptly crashes,
providing natural, friendly pedagogical recovery messages instead of raw stack traces.
"""

from typing import Optional, Dict, Any


# -----------------------------------------------------------------------------
# PHASE 36 CANONICAL ERROR MESSAGES
# -----------------------------------------------------------------------------
ERROR_PROCESSING_MSG = "Hmm, something went wrong while processing that. Give me another moment and I'll try again."
ERROR_UPLOAD_MSG = "I couldn't read that file properly. Try uploading the PDF again or send a text-based PDF."
ERROR_LLM_MSG = "I'm having trouble thinking through that one right now. Let's try again."


# -----------------------------------------------------------------------------
# PHASE 36 CUSTOM EXCEPTION HIERARCHY
# -----------------------------------------------------------------------------
class EduMentorError(Exception):
    """Base class for all EduMentor application errors."""
    def __init__(self, message: Optional[str] = None):
        super().__init__(message or ERROR_PROCESSING_MSG)
        self.friendly_message = message or ERROR_PROCESSING_MSG


class EduMentorProcessingError(EduMentorError):
    """Raised when an internal calculation, state transition, or concept lookup fails."""
    def __init__(self, message: Optional[str] = None):
        super().__init__(message or ERROR_PROCESSING_MSG)
        self.friendly_message = message or ERROR_PROCESSING_MSG


class EduMentorUploadError(EduMentorError):
    """Raised when a study notes file cannot be parsed, read, or extracted properly."""
    def __init__(self, message: Optional[str] = None):
        super().__init__(message or ERROR_UPLOAD_MSG)
        self.friendly_message = message or ERROR_UPLOAD_MSG


class EduMentorLLMError(EduMentorError):
    """Raised when an external or local LLM provider fails, times out, or returns invalid output."""
    def __init__(self, message: Optional[str] = None):
        super().__init__(message or ERROR_LLM_MSG)
        self.friendly_message = message or ERROR_LLM_MSG


# -----------------------------------------------------------------------------
# ERROR CLASSIFICATION AND RESOLUTION HELPERS
# -----------------------------------------------------------------------------
def is_llm_error(exc: Exception) -> bool:
    """Determine if an exception originates from an LLM inference failure."""
    if isinstance(exc, EduMentorLLMError):
        return True
    
    err_str = str(exc).lower()
    type_str = str(type(exc)).lower()

    llm_indicators = [
        "llm", "openai", "gemini", "anthropic", "claude", "ollama",
        "rate limit", "quota", "quotaexceeded", "ratelimiterror",
        "apierror", "connection error", "timeout", "timed out",
        "error connecting to", "trouble thinking", "model_not_found"
    ]
    return any(indicator in err_str or indicator in type_str for indicator in llm_indicators)


def is_upload_error(exc: Exception) -> bool:
    """Determine if an exception originates from a file upload or PDF extraction failure."""
    if isinstance(exc, EduMentorUploadError):
        return True
    
    err_str = str(exc).lower()
    type_str = str(type(exc)).lower()

    upload_indicators = [
        "upload", "pdf", "pdfplumber", "pdfminer", "pypdf",
        "extract_text", "corrupted", "couldn't read that file",
        "unreadable", "empty document", "file syntax", "bad file"
    ]
    return any(indicator in err_str or indicator in type_str for indicator in upload_indicators)


def resolve_friendly_error(exc: Exception, context: str = "general") -> str:
    """
    Map an exception to the appropriate Phase 36 pedagogical error message.
    Guarantees no raw stack traces (e.g. KeyError: concept_id) reach the student.
    """
    if isinstance(exc, EduMentorLLMError) or context == "llm" or is_llm_error(exc):
        return ERROR_LLM_MSG

    if isinstance(exc, EduMentorUploadError) or context == "upload" or is_upload_error(exc):
        return ERROR_UPLOAD_MSG

    # General processing error (KeyError, ValueError, AttributeError, etc.)
    return ERROR_PROCESSING_MSG
