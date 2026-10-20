"""
AI Failure Fallbacks & Robust Execution Pipeline (Phase 37).
Implements the universal 4-stage pipeline for all AI operations:
Validation -> Retry -> Fallback -> User-friendly error.

"Never assume the model returns valid JSON."
"""

import ast
import json
import logging
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from edumentor.ai.schemas import BaseSchema, validate_schema
from edumentor.utils.error_handler import (
    ERROR_LLM_MSG,
    ERROR_PROCESSING_MSG,
    EduMentorLLMError,
    resolve_friendly_error
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# 1. ROBUST JSON EXTRACTION AND REPAIR ENGINE
# -----------------------------------------------------------------------------
def safe_parse_json(text: Any) -> Tuple[Optional[Any], Optional[str]]:
    """
    Extract and parse JSON from messy, conversational, or malformed LLM responses.
    Handles:
    - Markdown code fences (```json ... ``` or ``` ... ```)
    - Preamble and postamble text
    - Trailing commas in arrays and objects
    - Single-quoted keys and values
    - Python booleans/None (True, False, None)
    - Truncated closing braces/brackets
    """
    if text is None:
        return None, "Empty/None input provided"

    if isinstance(text, (dict, list)):
        return text, None

    if not isinstance(text, str):
        try:
            return json.loads(str(text)), None
        except Exception as e:
            return None, f"Non-string input could not be converted: {e}"

    raw = text.strip()
    if not raw:
        return None, "Empty text provided"

    # 1. Direct standard parse
    try:
        return json.loads(raw), None
    except json.JSONDecodeError:
        pass

    # 2. Extract markdown code block content
    block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw, re.IGNORECASE)
    if block_match:
        block_content = block_match.group(1).strip()
        try:
            return json.loads(block_content), None
        except json.JSONDecodeError:
            raw = block_content  # Continue sanitizing the block content

    # 3. Locate outer JSON structure bounds ({ ... } or [ ... ])
    start_brace = raw.find("{")
    start_bracket = raw.find("[")

    if start_brace == -1 and start_bracket == -1:
        # Check if Python literal dict or list representation
        try:
            literal_val = ast.literal_eval(raw)
            if isinstance(literal_val, (dict, list)):
                return literal_val, None
        except Exception:
            pass
        return None, "No JSON object '{' or array '[' found in LLM response"

    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        start_pos = start_brace
        end_pos = raw.rfind("}")
        expected_closer = "}"
    else:
        start_pos = start_bracket
        end_pos = raw.rfind("]")
        expected_closer = "]"

    if end_pos != -1 and end_pos > start_pos:
        candidate = raw[start_pos : end_pos + 1]
    else:
        candidate = raw[start_pos:]  # Possibly truncated

    # 4. Attempt parsing candidate
    try:
        return json.loads(candidate), None
    except json.JSONDecodeError:
        pass

    # 5. Clean common LLM syntax irregularities:
    cleaned = candidate

    # Replace Python literals
    cleaned = re.sub(r"\bTrue\b", "true", cleaned)
    cleaned = re.sub(r"\bFalse\b", "false", cleaned)
    cleaned = re.sub(r"\bNone\b", "null", cleaned)

    # Remove trailing commas before } or ]
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

    # Remove single-line JS comments // ...
    cleaned = re.sub(r"//.*?\n", "\n", cleaned)

    try:
        return json.loads(cleaned), None
    except json.JSONDecodeError:
        pass

    # 6. Attempt single-quote to double-quote conversion for keys and strings
    try:
        single_quote_fixed = re.sub(r"(?<![\w\\])'([^'\\]*(?:\\.[^'\\]*)*)'(?=\s*[:,\}\]])", r'"\1"', cleaned)
        single_quote_fixed = re.sub(r"(?<=[{\[,])\s*'([^'\\]*(?:\\.[^'\\]*)*)'\s*:", r'"\1":', single_quote_fixed)
        return json.loads(single_quote_fixed), None
    except json.JSONDecodeError:
        pass

    # 7. Safe literal evaluation (AST) for single-quoted Python dicts
    try:
        parsed_ast = ast.literal_eval(cleaned)
        if isinstance(parsed_ast, (dict, list)):
            return parsed_ast, None
    except Exception:
        pass

    # 8. Attempt healing truncated structures by auto-closing braces/brackets
    open_braces = cleaned.count("{") - cleaned.count("}")
    open_brackets = cleaned.count("[") - cleaned.count("]")

    healed = cleaned
    if open_brackets > 0:
        healed += "]" * open_brackets
    if open_braces > 0:
        healed += "}" * open_braces

    try:
        # Strip trailing commas that might have preceded closing
        healed = re.sub(r",\s*([}\]])", r"\1", healed)
        return json.loads(healed), None
    except json.JSONDecodeError as err:
        return None, f"Failed to parse or repair JSON: {err}"


# -----------------------------------------------------------------------------
# 2. AI PIPELINE RESULT CONTAINER
# -----------------------------------------------------------------------------
class AIPipelineResult:
    """
    Standardized result object representing the outcome of an AI operation.
    Provides transparent dictionary-like access if data is a dict.
    """
    def __init__(
        self,
        success: bool,
        data: Any,
        stage: str,  # "validation", "retry", "fallback", "error"
        fallback_used: bool = False,
        attempts: int = 1,
        errors: Optional[List[str]] = None,
        error_message: Optional[str] = None,
        operation_name: str = "ai_operation"
    ):
        self.success = success
        self.data = data
        self.stage = stage
        self.fallback_used = fallback_used
        self.attempts = attempts
        self.errors = errors or []
        self.error_message = error_message
        self.operation_name = operation_name

    def __getitem__(self, key: Any) -> Any:
        if isinstance(self.data, dict):
            return self.data[key]
        if hasattr(self.data, "__getitem__"):
            return self.data[key]
        raise KeyError(f"Data in {self.operation_name} is of type {type(self.data).__name__}, not dict-like")

    def __setitem__(self, key: Any, value: Any) -> None:
        if isinstance(self.data, dict):
            self.data[key] = value
        else:
            raise TypeError(f"Cannot set item on non-dict data {type(self.data).__name__}")

    def get(self, key: Any, default: Any = None) -> Any:
        if isinstance(self.data, dict):
            return self.data.get(key, default)
        return default

    def __contains__(self, key: Any) -> bool:
        if isinstance(self.data, dict):
            return key in self.data
        return False

    def keys(self):
        if isinstance(self.data, dict):
            return self.data.keys()
        return [].keys()

    def values(self):
        if isinstance(self.data, dict):
            return self.data.values()
        return [].values()

    def items(self):
        if isinstance(self.data, dict):
            return self.data.items()
        return [].items()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "stage": self.stage,
            "fallback_used": self.fallback_used,
            "attempts": self.attempts,
            "errors": self.errors,
            "error_message": self.error_message,
            "operation_name": self.operation_name
        }

    def __repr__(self) -> str:
        return (
            f"AIPipelineResult(operation='{self.operation_name}', stage='{self.stage}', "
            f"fallback_used={self.fallback_used}, attempts={self.attempts}, success={self.success})"
        )


# -----------------------------------------------------------------------------
# 3. CORE 4-STAGE PIPELINE: Validation -> Retry -> Fallback -> User-friendly error
# -----------------------------------------------------------------------------
def execute_ai_pipeline(
    operation_name: str,
    llm_callable: Callable[[int, Optional[str]], Any],
    schema: Optional[Union[BaseSchema, type, Dict[str, Any]]] = None,
    validator: Optional[Callable[[Any], Tuple[bool, Optional[str]]]] = None,
    max_retries: int = 2,
    fallback_fn: Optional[Callable[[], Any]] = None,
    default_fallback: Optional[Any] = None,
    is_json: bool = True,
    user_friendly_error: str = ERROR_LLM_MSG
) -> AIPipelineResult:
    """
    Universal 4-stage AI execution pipeline:
      Validation -> Retry -> Fallback -> User-friendly error

    Arguments:
      - operation_name: Human-readable identifier for telemetry and logging.
      - llm_callable: Function taking (attempt_index, previous_error_str) -> raw LLM output.
      - schema: Schema class or dict specification to validate LLM output.
      - validator: Optional extra validation predicate returning (is_valid, error_msg).
      - max_retries: Number of retries permitted after initial failure (total attempts = 1 + max_retries).
      - fallback_fn: Fallback function executed if all retries fail.
      - default_fallback: Static fallback value if fallback_fn is not provided.
      - is_json: Whether the operation expects structured JSON.
      - user_friendly_error: Error message to return if fallback is missing or fails.
    """
    collected_errors: List[str] = []
    total_attempts = 1 + max(0, max_retries)
    last_error_context: Optional[str] = None

    # STAGE 1 & 2: VALIDATION & RETRY
    for attempt in range(1, total_attempts + 1):
        stage_name = "validation" if attempt == 1 else "retry"
        try:
            # Call the LLM
            raw_output = llm_callable(attempt, last_error_context)

            # Check if LLM output itself signaled an error
            if raw_output == ERROR_LLM_MSG or (isinstance(raw_output, str) and raw_output.startswith("Error connecting to")):
                err_msg = f"Attempt {attempt}: LLM provider returned connection or runtime error"
                collected_errors.append(err_msg)
                last_error_context = err_msg
                continue

            # Process output
            if is_json:
                parsed_json, parse_err = safe_parse_json(raw_output)
                if parse_err:
                    err_msg = f"Attempt {attempt}: JSON parse failed - {parse_err}"
                    collected_errors.append(err_msg)
                    last_error_context = err_msg
                    continue

                # Schema validation
                if schema is not None:
                    valid, schema_err, normalized = validate_schema(parsed_json, schema)
                    if not valid:
                        err_msg = f"Attempt {attempt}: Schema validation failed - {schema_err}"
                        collected_errors.append(err_msg)
                        last_error_context = err_msg
                        continue
                    final_data = normalized
                else:
                    final_data = parsed_json

                # Optional custom validator
                if validator is not None:
                    v_ok, v_err = validator(final_data)
                    if not v_ok:
                        err_msg = f"Attempt {attempt}: Custom validator failed - {v_err}"
                        collected_errors.append(err_msg)
                        last_error_context = err_msg
                        continue

                # Passed validation!
                return AIPipelineResult(
                    success=True,
                    data=final_data,
                    stage=stage_name,
                    fallback_used=False,
                    attempts=attempt,
                    errors=collected_errors,
                    operation_name=operation_name
                )

            else:
                # Raw text validation
                text_output = str(raw_output or "").strip()
                if not text_output or text_output == ERROR_LLM_MSG:
                    err_msg = f"Attempt {attempt}: Empty or error text response"
                    collected_errors.append(err_msg)
                    last_error_context = err_msg
                    continue

                if schema is not None:
                    valid, schema_err, normalized = validate_schema(text_output, schema)
                    if not valid:
                        err_msg = f"Attempt {attempt}: Schema validation failed - {schema_err}"
                        collected_errors.append(err_msg)
                        last_error_context = err_msg
                        continue
                    final_text = normalized
                else:
                    final_text = text_output

                if validator is not None:
                    v_ok, v_err = validator(final_text)
                    if not v_ok:
                        err_msg = f"Attempt {attempt}: Custom validator failed - {v_err}"
                        collected_errors.append(err_msg)
                        last_error_context = err_msg
                        continue

                return AIPipelineResult(
                    success=True,
                    data=final_text,
                    stage=stage_name,
                    fallback_used=False,
                    attempts=attempt,
                    errors=collected_errors,
                    operation_name=operation_name
                )

        except Exception as exc:
            err_msg = f"Attempt {attempt}: Unexpected exception during execution - {type(exc).__name__}: {str(exc)}"
            collected_errors.append(err_msg)
            last_error_context = err_msg
            logger.warning(f"[{operation_name}] {err_msg}")

    # STAGE 3: FALLBACK
    logger.info(f"[{operation_name}] Retries exhausted. Initiating fallback.")

    if fallback_fn is not None:
        try:
            fallback_data = fallback_fn()
            # If schema is defined and fallback is dict, normalize through schema if applicable
            if schema is not None and isinstance(fallback_data, dict):
                v_ok, _, norm_fallback = validate_schema(fallback_data, schema)
                if v_ok and norm_fallback is not None:
                    fallback_data = norm_fallback

            return AIPipelineResult(
                success=True,
                data=fallback_data,
                stage="fallback",
                fallback_used=True,
                attempts=total_attempts,
                errors=collected_errors,
                operation_name=operation_name
            )
        except Exception as fb_exc:
            err_msg = f"Fallback function failed - {type(fb_exc).__name__}: {str(fb_exc)}"
            collected_errors.append(err_msg)
            logger.error(f"[{operation_name}] {err_msg}")

    elif default_fallback is not None:
        return AIPipelineResult(
            success=True,
            data=default_fallback,
            stage="fallback",
            fallback_used=True,
            attempts=total_attempts,
            errors=collected_errors,
            operation_name=operation_name
        )

    # STAGE 4: USER-FRIENDLY ERROR
    friendly_msg = user_friendly_error or ERROR_LLM_MSG
    return AIPipelineResult(
        success=False,
        data=None,
        stage="error",
        fallback_used=False,
        attempts=total_attempts,
        errors=collected_errors,
        error_message=friendly_msg,
        operation_name=operation_name
    )
