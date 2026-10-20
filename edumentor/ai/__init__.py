"""
EduMentor AI Services Subsystem.
Provides question generation, answer evaluation, concept extraction, Socratic feedback,
and the Phase 37 Failure Fallbacks Pipeline:
Validation -> Retry -> Fallback -> User-friendly error.
"""

from edumentor.ai.schemas import (
    BaseSchema,
    ConceptExtractionSchema,
    QuestionGenerationSchema,
    EvaluationJudgeSchema,
    SocraticHintsSchema,
    ConversationalReplySchema,
    validate_schema,
    SchemaValidationError
)

from edumentor.ai.fallback_pipeline import (
    safe_parse_json,
    AIPipelineResult,
    execute_ai_pipeline
)

from edumentor.ai.llm_client import (
    LLMConfig,
    call_llm,
    call_llm_json,
    test_llm_connection,
    get_default_config
)

from edumentor.ai.embedding_cache import EmbeddingCache, embedding_cache
from edumentor.ai.llm_cache import LLMCache, llm_cache

__all__ = [
    "BaseSchema",
    "ConceptExtractionSchema",
    "QuestionGenerationSchema",
    "EvaluationJudgeSchema",
    "SocraticHintsSchema",
    "ConversationalReplySchema",
    "validate_schema",
    "SchemaValidationError",
    "safe_parse_json",
    "AIPipelineResult",
    "execute_ai_pipeline",
    "LLMConfig",
    "call_llm",
    "call_llm_json",
    "test_llm_connection",
    "get_default_config",
    "EmbeddingCache",
    "embedding_cache",
    "LLMCache",
    "llm_cache"
]
