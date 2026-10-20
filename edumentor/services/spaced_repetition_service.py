"""
Spaced Repetition Service using SuperMemo SM-2.
"""

from typing import Dict, Any, Optional
from datetime import date
from edumentor.scheduler import calculate_sm2, map_score_to_quality, get_quality_label, prioritize_study_queue


class SpacedRepetitionService:
    @staticmethod
    def calculate_review(quality_q: int, repetition_n: int, easiness_factor: float = 2.5, current_interval: int = 0) -> Dict[str, Any]:
        return calculate_sm2(
            quality_q=quality_q,
            repetition_n=repetition_n,
            easiness_factor=easiness_factor,
            current_interval=current_interval
        )

    @staticmethod
    def score_to_quality(score: float) -> int:
        return map_score_to_quality(score)

    @staticmethod
    def get_label(quality_q: int):
        return get_quality_label(quality_q)
