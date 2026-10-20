"""
EduMentor utilities package.
"""

from edumentor.utils.error_handler import (
    ERROR_PROCESSING_MSG,
    ERROR_UPLOAD_MSG,
    ERROR_LLM_MSG,
    EduMentorError,
    EduMentorProcessingError,
    EduMentorUploadError,
    EduMentorLLMError,
    resolve_friendly_error,
    is_llm_error,
    is_upload_error,
)
