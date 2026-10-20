"""
Feedback and Socratic hints generation service.
"""

from typing import Dict, List, Any, Optional
from edumentor.ai.llm_client import LLMConfig
from edumentor.evaluation import generate_socratic_hints


def get_socratic_hints(concept: Dict[str, Any], llm_config: Optional[LLMConfig] = None) -> Dict[str, str]:
    """Generate progressive 3-tier Socratic scaffolding hints."""
    return generate_socratic_hints(
        concept.get("title", "Concept"),
        concept.get("canonical_explanation", concept.get("summary", "")),
        concept.get("key_points") or concept.get("principles") or [],
        llm_config=llm_config
    )


def generate_feedback_summary(eval_result: Dict[str, Any]) -> str:
    """Generate a friendly summary sentence based on evaluation results."""
    score = eval_result.get("composite_score", eval_result.get("score", 0))
    verdict = eval_result.get("verdict", "Evaluated")
    tip = eval_result.get("actionable_tip", "")

    if score >= 80 or verdict == "Correct":
        return f"Outstanding mastery! {tip}"
    elif score >= 60 or verdict == "Almost Correct":
        return f"Solid grasp with minor gaps to solidify. {tip}"
    else:
        return f"Needs reinforcement. {tip}"
