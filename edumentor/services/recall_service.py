"""
Recall service coordinating questions, student responses, and hybrid evaluations.
"""

from typing import Dict, List, Any, Optional, Union
from edumentor.ai.question_generator import generate_recall_question
from edumentor.ai.answer_evaluator import evaluate_student_answer
from edumentor.ai.feedback_generator import get_socratic_hints
from edumentor.ai.llm_client import LLMConfig


class RecallService:
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.llm_config = llm_config

    def create_question(
        self,
        concept: Dict[str, Any],
        note_chunks: Optional[Union[List[str], str]] = None,
        mastery_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a recall question strictly grounded in note chunks,
        calibrated to student mastery, previous attempts, and concept importance.
        """
        return generate_recall_question(
            concept=concept,
            note_chunks=note_chunks,
            mastery_context=mastery_context,
            llm_config=self.llm_config
        )

    def evaluate_response(self, concept: Dict[str, Any], answer: str) -> Dict[str, Any]:
        return evaluate_student_answer(concept, answer, llm_config=self.llm_config)

    def get_hints(self, concept: Dict[str, Any]) -> Dict[str, str]:
        return get_socratic_hints(concept, llm_config=self.llm_config)

