"""
Schema Validation System for LLM Outputs (Phase 37).
Validates raw and parsed LLM responses to ensure structural integrity and semantic constraints.
"Never assume the model returns valid JSON."
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Union


class SchemaValidationError(ValueError):
    """Raised when LLM output fails schema validation."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class BaseSchema:
    """Base class for all LLM output schemas."""
    schema_name: str = "BaseSchema"

    @classmethod
    def validate(cls, data: Any) -> Tuple[bool, Optional[str], Any]:
        """
        Validate data against the schema.
        Returns: (is_valid: bool, error_message: Optional[str], normalized_data: Any)
        """
        raise NotImplementedError


class ConceptExtractionSchema(BaseSchema):
    """
    Schema for Concept Extraction from Study Notes:
    {
      "concepts": [
        {
          "id": "c1",
          "title": "Concept Title",
          "summary": "High-level summary",
          "canonical_explanation": "In-depth explanation",
          "key_points": ["point 1", "point 2"],
          "prerequisites": ["c0"]
        }
      ]
    }
    """
    schema_name = "ConceptExtractionSchema"

    @classmethod
    def validate(cls, data: Any) -> Tuple[bool, Optional[str], Any]:
        if not isinstance(data, dict):
            return False, f"Expected root JSON object (dict), got {type(data).__name__}", None

        concepts = data.get("concepts")
        if concepts is None:
            # Check alternative keys models sometimes return
            for alt_key in ["extracted_concepts", "topics", "key_concepts"]:
                if alt_key in data and isinstance(data[alt_key], list):
                    concepts = data[alt_key]
                    break

        if not isinstance(concepts, list):
            return False, f"Expected 'concepts' list, got {type(concepts).__name__ if concepts is not None else 'None'}", None

        if len(concepts) == 0:
            return False, "The 'concepts' list must not be empty", None

        normalized_concepts: List[Dict[str, Any]] = []
        for idx, item in enumerate(concepts):
            if not isinstance(item, dict):
                return False, f"Concept at index {idx} must be a dict, got {type(item).__name__}", None

            title = item.get("title") or item.get("name")
            if not title or not isinstance(title, str) or len(title.strip()) < 2:
                return False, f"Concept at index {idx} missing valid 'title'", None

            summary = item.get("summary") or item.get("description") or ""
            canonical = item.get("canonical_explanation") or item.get("explanation") or summary

            key_points = item.get("key_points") or item.get("principles") or []
            if isinstance(key_points, str):
                key_points = [k.strip("- *") for k in key_points.split("\n") if k.strip()]
            elif not isinstance(key_points, list):
                key_points = [str(key_points)]

            prereqs = item.get("prerequisites") or item.get("deps") or []
            if isinstance(prereqs, str):
                prereqs = [p.strip() for p in prereqs.split(",") if p.strip()]
            elif not isinstance(prereqs, list):
                prereqs = [str(prereqs)]

            cid = item.get("id") or f"c_{idx + 1}"
            cid = re.sub(r"[^a-zA-Z0-9_]", "_", str(cid).lower())

            major_topic = item.get("major_topic") or ""
            named_ents = item.get("named_types_or_methods") or item.get("named_entities") or []
            if isinstance(named_ents, str):
                named_ents = [named_ents]
            definitions = item.get("definitions") or []
            if isinstance(definitions, str):
                definitions = [definitions]
            prompt_q = item.get("prompt_question") or f"In your own words, what is {str(title).strip()} and how does it work?"

            normalized_concepts.append({
                "id": cid,
                "title": str(title).strip(),
                "major_topic": str(major_topic).strip(),
                "summary": str(summary).strip(),
                "canonical_explanation": str(canonical).strip(),
                "key_points": [str(kp).strip() for kp in key_points if str(kp).strip()],
                "named_types_or_methods": [str(ne).strip() for ne in named_ents if str(ne).strip()],
                "named_entities": [str(ne).strip() for ne in named_ents if str(ne).strip()],
                "definitions": [str(d).strip() for d in definitions if str(d).strip()],
                "source_page": str(item.get("source_page") or item.get("source_location") or ""),
                "prompt_question": str(prompt_q).strip(),
                "prerequisites": [str(p).strip() for p in prereqs if str(p).strip()]
            })

        return True, None, {"concepts": normalized_concepts}


class QuestionGenerationSchema(BaseSchema):
    """
    Schema for Active Recall Question Generation:
    {
      "question": "In your own words, what is ... and why ...?",
      "difficulty_level": "medium",
      "grounded_in_notes": true
    }
    """
    schema_name = "QuestionGenerationSchema"

    @classmethod
    def validate(cls, data: Any) -> Tuple[bool, Optional[str], Any]:
        if not isinstance(data, dict):
            return False, f"Expected root JSON object, got {type(data).__name__}", None

        question = data.get("question") or data.get("prompt")
        if not question or not isinstance(question, str):
            return False, "Missing or invalid 'question' field", None

        q_clean = question.strip()
        if len(q_clean) < 15:
            return False, f"Question too short ({len(q_clean)} chars, min 15 required)", None

        difficulty = str(data.get("difficulty_level", "medium")).lower()
        grounded = bool(data.get("grounded_in_notes", True))

        return True, None, {
            "question": q_clean,
            "difficulty_level": difficulty,
            "grounded_in_notes": grounded
        }


class EvaluationJudgeSchema(BaseSchema):
    """
    Schema for LLM-as-a-Judge Recall Evaluation:
    {
      "correctness": 85.0,
      "completeness": 70.0,
      "reasoning": "...",
      "missing_points": ["..."],
      "misconceptions": [],
      "strengths": ["..."],
      "actionable_tip": "...",
      "relevance": 90.0,
      "verdict": "correct"
    }
    """
    schema_name = "EvaluationJudgeSchema"

    @classmethod
    def validate(cls, data: Any) -> Tuple[bool, Optional[str], Any]:
        if not isinstance(data, dict):
            return False, f"Expected root JSON object, got {type(data).__name__}", None

        # Correctness
        raw_correctness = data.get("correctness", data.get("conceptual_accuracy", data.get("score")))
        if raw_correctness is None:
            return False, "Missing required field 'correctness'", None
        try:
            correctness = float(raw_correctness)
            if correctness < 0 or correctness > 100:
                return False, f"'correctness' score {correctness} out of bounds [0, 100]", None
        except (ValueError, TypeError):
            return False, f"Invalid numeric 'correctness': {raw_correctness}", None

        # Completeness
        raw_completeness = data.get("completeness", data.get("key_point_coverage", 50.0))
        try:
            completeness = float(raw_completeness)
            if completeness < 0 or completeness > 100:
                return False, f"'completeness' score {completeness} out of bounds [0, 100]", None
        except (ValueError, TypeError):
            return False, f"Invalid numeric 'completeness': {raw_completeness}", None

        # Reasoning
        reasoning = str(data.get("reasoning", "")).strip()
        if not reasoning:
            reasoning = "Evaluated based on conceptual correctness and key point coverage."

        # Missing points
        missing = data.get("missing_points", data.get("missing_concepts", []))
        if isinstance(missing, str):
            missing_list = [missing.strip()] if missing.strip() else []
        elif isinstance(missing, list):
            missing_list = [str(x).strip() for x in missing if str(x).strip()]
        else:
            missing_list = []

        # Misconceptions
        misconceptions = data.get("misconceptions", [])
        if isinstance(misconceptions, str):
            misc_list = [misconceptions.strip()] if misconceptions.strip() else []
        elif isinstance(misconceptions, list):
            misc_list = [str(x).strip() for x in misconceptions if str(x).strip()]
        else:
            misc_list = []

        # Strengths
        strengths = data.get("strengths", [])
        if isinstance(strengths, str):
            strengths_list = [strengths.strip()] if strengths.strip() else ["Demonstrated recall effort."]
        elif isinstance(strengths, list):
            strengths_list = [str(x).strip() for x in strengths if str(x).strip()] or ["Demonstrated recall effort."]
        else:
            strengths_list = ["Demonstrated recall effort."]

        # Actionable tip
        tip = str(data.get("actionable_tip", data.get("tip", ""))).strip()
        if not tip:
            tip = "Review the core mechanism and practice recalling the key causality."

        # Relevance
        try:
            relevance = float(data.get("relevance", 95.0))
            relevance = max(0.0, min(100.0, relevance))
        except (ValueError, TypeError):
            relevance = 95.0

        # Verdict
        verdict = str(data.get("verdict", "")).lower()
        if verdict not in ["correct", "almost_correct", "wrong"]:
            score_est = (0.55 * correctness) + (0.45 * completeness)
            if score_est >= 75.0:
                verdict = "correct"
            elif score_est >= 55.0:
                verdict = "almost_correct"
            else:
                verdict = "wrong"

        return True, None, {
            "correctness": round(correctness, 1),
            "completeness": round(completeness, 1),
            "reasoning": reasoning,
            "missing_points": missing_list,
            "misconceptions": misc_list,
            "strengths": strengths_list,
            "actionable_tip": tip,
            "relevance": round(relevance, 1),
            "verdict": verdict
        }


class SocraticHintsSchema(BaseSchema):
    """
    Schema for Socratic Scaffolding Hints:
    {
      "hint_tier_1": "High-level intuition...",
      "hint_tier_2": "Operational step...",
      "hint_tier_3": "Targeted guiding question..."
    }
    """
    schema_name = "SocraticHintsSchema"

    @classmethod
    def validate(cls, data: Any) -> Tuple[bool, Optional[str], Any]:
        if not isinstance(data, dict):
            return False, f"Expected root JSON object, got {type(data).__name__}", None

        t1 = str(data.get("hint_tier_1", data.get("tier_1", data.get("tier1", "")))).strip()
        t2 = str(data.get("hint_tier_2", data.get("tier_2", data.get("tier2", "")))).strip()
        t3 = str(data.get("hint_tier_3", data.get("tier_3", data.get("tier3", "")))).strip()

        if not t1 or len(t1) < 8:
            return False, "Missing or invalid 'hint_tier_1' (must be at least 8 chars)", None
        if not t2 or len(t2) < 8:
            return False, "Missing or invalid 'hint_tier_2' (must be at least 8 chars)", None
        if not t3 or len(t3) < 8:
            return False, "Missing or invalid 'hint_tier_3' (must be at least 8 chars)", None

        return True, None, {
            "hint_tier_1": t1,
            "hint_tier_2": t2,
            "hint_tier_3": t3
        }


class ConversationalReplySchema(BaseSchema):
    """
    Schema for freeform teacher conversational responses:
    Ensures non-empty text, reasonable length, and no leaked stack traces or error banners.
    """
    schema_name = "ConversationalReplySchema"

    @classmethod
    def validate(cls, data: Any) -> Tuple[bool, Optional[str], Any]:
        if isinstance(data, dict):
            text = str(data.get("reply") or data.get("message") or data.get("content") or "").strip()
        elif isinstance(data, str):
            text = data.strip()
        else:
            return False, f"Expected string or dict response, got {type(data).__name__}", None

        if len(text) < 5:
            return False, f"Conversational reply too short ({len(text)} chars)", None

        # Check for error leaks
        lower = text.lower()
        if "traceback (most recent call last)" in lower or "keyerror:" in lower or "syntaxerror:" in lower:
            return False, "Detected raw Python exception trace in model response", None

        return True, None, text


def validate_schema(data: Any, schema: Union[BaseSchema, type, Dict[str, Any]]) -> Tuple[bool, Optional[str], Any]:
    """
    Validate data against any supported schema class or specification.
    Returns: (is_valid: bool, error_message: Optional[str], normalized_data: Any)
    """
    if hasattr(schema, "validate") and callable(getattr(schema, "validate")):
        return schema.validate(data)

    if isinstance(schema, dict):
        if not isinstance(data, dict):
            return False, f"Expected dict, got {type(data).__name__}", None
        for key, expected_type in schema.items():
            if key not in data:
                return False, f"Missing required field '{key}'", None
            if not isinstance(data[key], expected_type):
                return False, f"Field '{key}' expected {expected_type.__name__}, got {type(data[key]).__name__}", None
        return True, None, data

    return True, None, data
