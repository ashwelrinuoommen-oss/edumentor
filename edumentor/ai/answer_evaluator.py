"""
Hybrid Answer Evaluator combining semantic vector distance and LLM-as-judge scoring.
"""

from typing import Dict, Any, Optional
from edumentor.ai.llm_client import LLMConfig
from edumentor.evaluation import evaluate_recall


def evaluate_student_answer(concept: Dict[str, Any], answer: str, llm_config: Optional[LLMConfig] = None) -> Dict[str, Any]:
    """Execute hybrid evaluation and return composite score and metrics."""
    return evaluate_recall(concept, answer, llm_config=llm_config)
