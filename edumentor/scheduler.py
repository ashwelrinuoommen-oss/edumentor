"""
SM-2 (SuperMemo-2) Spaced Repetition Scheduler for EduMentor.
Calculates optimal review intervals, easiness factor updates, and resurfacing queues.
"""

import math
from datetime import date, datetime, timedelta
from typing import Dict, Any, Tuple, List, Optional


MINIMUM_EASINESS_FACTOR = 1.3
DEFAULT_INITIAL_EF = 2.5


def map_score_to_quality(score_0_to_100: float) -> int:
    """
    Map composite score (0-100) to SM-2 quality rating q in [0, 5].
    5 - Perfect response, effortless active recall (>= 90%)
    4 - Correct response with slight omission or hesitation (75 - 89%)
    3 - Passing response with serious effort or minor inaccuracy (60 - 74%)
    2 - Incorrect response, but key fragments recalled (40 - 59%)
    1 - Incorrect response, barely recognizable (20 - 39%)
    0 - Complete failure / no recall (< 20%)
    """
    if score_0_to_100 >= 90.0:
        return 5
    elif score_0_to_100 >= 75.0:
        return 4
    elif score_0_to_100 >= 60.0:
        return 3
    elif score_0_to_100 >= 40.0:
        return 2
    elif score_0_to_100 >= 20.0:
        return 1
    else:
        return 0


def get_quality_label(q: int) -> Tuple[str, str]:
    """Human-readable label and description for SM-2 quality grade."""
    labels = {
        5: ("Perfect Mastery (90-100%)", "Excellent recall of core principles with no hesitation."),
        4: ("Solid Recall (75-89%)", "Accurate comprehension with minor omission in fine detail."),
        3: ("Passing with Effort (60-74%)", "Core idea understood, but needed retrieval effort or partial precision."),
        2: ("Marginal / Weak (40-59%)", "Key fragments recalled, but missed fundamental mechanics."),
        1: ("Incorrect (20-39%)", "Severe inaccuracies and prominent misconceptions."),
        0: ("Complete Blank (<20%)", "No substantive conceptual recall.")
    }
    return labels.get(q, (f"Grade {q}", "Score recorded."))


def calculate_sm2(
    quality_q: int,
    repetition_n: int,
    easiness_factor: float = DEFAULT_INITIAL_EF,
    current_interval: int = 0,
    consecutive_correct: int = 0,
    reference_date: Optional[date] = None,
    schedule_mode: str = "standard"
) -> Dict[str, Any]:
    """
    Compute SM-2 update for a single card review.
    
    Modes:
      'phase14':
        First successful recall (rep 0 -> 1)  -> interval = 1 day (Review tomorrow)
        Second successful recall (rep 1 -> 2) -> interval = 3 days (Review in 3 days)
        Third successful recall (rep 2 -> 3)  -> interval = 7 days (Review in 7 days)
        Strong repeated recall (rep 3+ -> 4+) -> interval = 14 days (Review in 14 days)
        Weak answers (q < 3) reduce interval:
          interval = max(1, current_interval // 2) if current_interval > 1 else 1
      'standard':
        Classic SM-2 (rep 0 -> 1, rep 1 -> 6, rep 2+ -> ceil(interval * EF'))
        
    Stores/Returns:
      ease_factor, interval, repetition, next_review
    """
    if reference_date is None:
        reference_date = date.today()

    # Calculate new easiness factor
    q = max(0, min(5, quality_q))
    ef_delta = 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)
    new_ef = round(max(MINIMUM_EASINESS_FACTOR, easiness_factor + ef_delta), 3)

    if q < 3:
        # Failure / Weak answer
        new_n = 0
        if schedule_mode == "phase14" and current_interval > 1:
            # Weak answers should reduce the interval
            new_interval = max(1, current_interval // 2)
        else:
            new_interval = 1
        new_consecutive = 0
        status = "weak"
    else:
        # Success
        if schedule_mode == "phase14":
            if repetition_n == 0:
                new_interval = 1       # Review tomorrow
            elif repetition_n == 1:
                new_interval = 3       # Review in 3 days
            elif repetition_n == 2:
                new_interval = 7       # Review in 7 days
            elif repetition_n == 3:
                new_interval = 14      # Review in 14 days
            else:
                base_interval = current_interval if current_interval > 0 else 14
                new_interval = min(30, math.ceil(base_interval * (new_ef / 2.5)))
        else:
            # Classic SM-2 standard schedule
            if repetition_n == 0:
                new_interval = 1
            elif repetition_n == 1:
                new_interval = 6
            else:
                base_interval = current_interval if current_interval > 0 else 6
                new_interval = math.ceil(base_interval * new_ef)
        
        new_n = repetition_n + 1
        new_consecutive = consecutive_correct + 1
        status = "mastered" if (new_n >= 3 and q >= 4) else "reviewing"

    next_due = reference_date + timedelta(days=new_interval)

    return {
        "repetition_n": new_n,
        "repetition": new_n,
        "easiness_factor": new_ef,
        "ease_factor": new_ef,
        "interval_days": new_interval,
        "interval": new_interval,
        "next_due_date": next_due.isoformat(),
        "next_review": next_due.isoformat(),
        "consecutive_correct": new_consecutive,
        "last_quality_score": q,
        "status": status
    }


def calculate_phase14_sm2(
    quality_q: int,
    repetition: int,
    ease_factor: float = DEFAULT_INITIAL_EF,
    current_interval: int = 0,
    consecutive_correct: int = 0,
    reference_date: Optional[date] = None
) -> Dict[str, Any]:
    """Convenience wrapper strictly running Phase 14 calibrated SM-2."""
    return calculate_sm2(
        quality_q=quality_q,
        repetition_n=repetition,
        easiness_factor=ease_factor,
        current_interval=current_interval,
        consecutive_correct=consecutive_correct,
        reference_date=reference_date,
        schedule_mode="phase14"
    )


def prioritize_study_queue(
    concepts: List[Dict[str, Any]],
    topological_order: List[str],
    reference_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """
    Prioritizes concepts for the closed-loop study session:
    Category 1: Weak concepts (last_quality_score < 3 and total_reviews > 0) -> highest urgency
    Category 2: Spaced Repetition Due (next_due_date <= today and total_reviews > 0)
    Category 3: Ready New Concepts (prerequisites mastered/reviewed, total_reviews == 0)
    Category 4: Mastered / Future Due Concepts (scheduled for later)
    """
    if reference_date is None:
        reference_date = date.today()
    ref_iso = reference_date.isoformat()

    topo_idx = {cid: i for i, cid in enumerate(topological_order)}

    def sort_key(c: Dict[str, Any]) -> Tuple[int, int, str]:
        cid = c["id"]
        status = c.get("sm2_status", "new")
        last_q = c.get("last_quality_score", 0)
        total_rev = c.get("total_reviews", 0)
        due_date = c.get("next_due_date", ref_iso)
        t_order = topo_idx.get(cid, 9999)

        # 1. Weak concepts (Urgent Resurface)
        if (status == "weak" or last_q < 3) and total_rev > 0:
            return (0, t_order, due_date)
        # 2. Due for spaced review
        elif due_date <= ref_iso and total_rev > 0:
            return (1, t_order, due_date)
        # 3. New concepts ready to learn
        elif total_rev == 0:
            return (2, t_order, due_date)
        # 4. Mastered / Future due
        else:
            return (3, t_order, due_date)

    return sorted(concepts, key=sort_key)
