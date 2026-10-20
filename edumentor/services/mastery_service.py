"""
Mastery service calculating comprehension scores and retention radar metrics.
"""

from typing import Dict, List, Any, Optional, Tuple


MASTERY_STATE_METADATA = {
    "Mastered": {
        "band": "90–100",
        "label": "Mastered",
        "icon": "★",
        "description": "Exemplary active recall with deep conceptual clarity.",
        "badge_display": "★ Mastered (90–100%)",
        "color": "#10B981",
        "border": "rgba(16, 185, 129, 0.4)",
        "bg": "rgba(16, 185, 129, 0.12)"
    },
    "Strong understanding": {
        "band": "75–89",
        "label": "Strong understanding",
        "icon": "✓",
        "description": "Accurate, comprehensive explanation with minor detail nuances.",
        "badge_display": "✓ Strong understanding (75–89%)",
        "color": "#25D8E8",
        "border": "rgba(37, 216, 232, 0.4)",
        "bg": "rgba(37, 216, 232, 0.12)"
    },
    "Partial understanding": {
        "band": "60–74",
        "label": "Partial understanding",
        "icon": "⚡",
        "description": "Core idea grasped, but key technical mechanisms missing.",
        "badge_display": "⚡ Partial understanding (60–74%)",
        "color": "#F59E0B",
        "border": "rgba(245, 158, 11, 0.4)",
        "bg": "rgba(245, 158, 11, 0.12)"
    },
    "Developing": {
        "band": "40–59",
        "label": "Developing",
        "icon": "🌱",
        "description": "Initial fragments recalled, but significant misconceptions present.",
        "badge_display": "🌱 Developing (40–59%)",
        "color": "#F97316",
        "border": "rgba(249, 115, 22, 0.4)",
        "bg": "rgba(249, 115, 22, 0.12)"
    },
    "Needs relearning": {
        "band": "0–39",
        "label": "Needs relearning",
        "icon": "⚠️",
        "description": "Concept requires immediate foundational review before proceeding.",
        "badge_display": "⚠️ Needs relearning (0–39%)",
        "color": "#EF4444",
        "border": "rgba(239, 68, 68, 0.4)",
        "bg": "rgba(239, 68, 68, 0.12)"
    }
}


class MasteryService:
    """
    Phases 10-14 Mastery Engine:
    Calculates multidimensional concept and curriculum mastery adhering to the
    Phase 12 5-tier standard:
      0–39   Needs relearning
      40–59  Developing
      60–74  Partial understanding
      75–89  Strong understanding
      90–100 Mastered
    Provides Phase 11 accessible semantic state indicators and Phase 13 metacognitive
    confidence calibration analysis.
    """

    @staticmethod
    def get_mastery_state(score: int, reviews: int = 0) -> str:
        """
        Map a mastery score (0-100) into one of the 5 exact Phase 12 bands:
        0–39   Needs relearning
        40–59  Developing
        60–74  Partial understanding
        75–89  Strong understanding
        90–100 Mastered
        """
        if score >= 90:
            return "Mastered"
        elif score >= 75:
            return "Strong understanding"
        elif score >= 60:
            return "Partial understanding"
        elif score >= 40:
            return "Developing"
        else:
            return "Needs relearning"

    @staticmethod
    def format_mastery_badge(score: int) -> str:
        """Format score in Phase 11 semantic badge format: '82% — Strong understanding'."""
        state = MasteryService.get_mastery_state(score)
        return f"{score}% — {state}"

    @staticmethod
    def get_mastery_indicator(state: str) -> Dict[str, Any]:
        """Return rich semantic indicator metadata (icon, label, description, colors)."""
        return MASTERY_STATE_METADATA.get(state, MASTERY_STATE_METADATA["Needs relearning"])

    @staticmethod
    def analyze_confidence_calibration(
        confidence: str,
        score: float,
        quality: int,
        concept_title: str = "this concept"
    ) -> Dict[str, Any]:
        """
        Phase 13 Metacognitive Confidence Calibration:
        Compares subjective student confidence with objective recall score.
        Example:
          Confidence: Very confident, Actual score: 38%
          EduMentor: "Interesting — you were quite confident there. Let's revisit this one later so we can make sure it really sticks."
        """
        conf_clean = (confidence or "").strip().lower()
        is_high_conf = "very" in conf_clean
        is_low_conf = "not" in conf_clean
        is_mod_conf = "somewhat" in conf_clean or (not is_high_conf and not is_low_conf)

        # Scale score to percentage if given in 0.0-1.0
        score_pct = score * 100 if score <= 1.0 else score

        # Case 1: Overconfidence (High confidence + Weak score)
        if is_high_conf and (score_pct < 60 or quality < 3):
            return {
                "calibration_state": "overconfident",
                "dialogue": "Interesting — you were quite confident there. Let's revisit this one later so we can make sure it really sticks.",
                "teacher_expression": "thoughtful",
                "recommended_action": "schedule_early_revisit",
                "summary": "Overconfidence gap detected: High subjective certainty but low conceptual retention."
            }

        # Case 2: Underconfidence / Imposter Syndrome (Low confidence + High score)
        elif is_low_conf and (score_pct >= 75 or quality >= 4):
            return {
                "calibration_state": "underconfident",
                "dialogue": f"You weren't very confident, but your recall on **{concept_title}** was actually fantastic! Trust your intuition more — you know this much better than you thought! 👍",
                "teacher_expression": "happy",
                "recommended_action": "boost_confidence",
                "summary": "Underconfidence detected: Strong objective recall despite self-doubt."
            }

        # Case 3: Calibrated Mastery (High confidence + High score)
        elif is_high_conf and (score_pct >= 75 or quality >= 4):
            return {
                "calibration_state": "calibrated_high",
                "dialogue": f"Spot on calibration! Your confidence was well-justified — you've demonstrated strong recall on **{concept_title}**. 🎉",
                "teacher_expression": "celebration",
                "recommended_action": "advance",
                "summary": "Calibrated mastery: Confidence and performance aligned."
            }

        # Case 4: Accurate Awareness of Weakness (Low confidence + Low score)
        elif is_low_conf and (score_pct < 60 or quality < 3):
            return {
                "calibration_state": "calibrated_low",
                "dialogue": f"Good self-awareness. Recognizing when a concept feels hazy is a vital superpower in active learning. We'll revisit **{concept_title}** shortly so it truly clicks! 🌱",
                "teacher_expression": "supportive",
                "recommended_action": "reinforce_notes",
                "summary": "Accurate self-awareness of conceptual gaps."
            }

        # Case 5: Moderate / Balanced Confidence
        else:
            return {
                "calibration_state": "moderate",
                "dialogue": f"Honest self-reflection! Keeping track of your confidence helps us fine-tune your personalized review schedule for **{concept_title}**.",
                "teacher_expression": "encouraging",
                "recommended_action": "continue",
                "summary": "Balanced calibration."
            }

    @staticmethod
    def calculate_metrics(concepts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Backwards-compatible summary metrics calculation.
        """
        total = len(concepts)
        if total == 0:
            return {"mastery_percent": 0, "mastered_count": 0, "passing_count": 0, "total": 0}

        mastered = sum(
            1 for c in concepts.values() 
            if c.get("sm2_status") == "mastered" or c.get("last_quality_score", 0) >= 4 or c.get("mastery_level") == "Mastered"
        )
        passing = sum(1 for c in concepts.values() if c.get("last_quality_score", 0) >= 3)
        percent = round((mastered / total) * 100)

        return {
            "mastery_percent": percent,
            "mastered_count": mastered,
            "passing_count": passing,
            "total": total
        }

    @staticmethod
    def evaluate_concept_mastery(
        concept: Dict[str, Any],
        prerequisites: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculates multidimensional concept mastery (0-100%) and categorizes the concept
        into the Phase 12 5-tier mastery scale:
          0–39   Needs relearning
          40–59  Developing
          60–74  Partial understanding
          75–89  Strong understanding
          90–100 Mastered

        Also preserves legacy 'mastery_level' for Phase 10 backwards compatibility.
        """
        cid = concept.get("id", "")
        title = concept.get("title", cid)
        reviews = max(concept.get("total_reviews", 0), concept.get("attempt_count", 0))
        last_q = concept.get("last_quality_score", 0)
        consecutive = concept.get("consecutive_correct", 0)
        interval = max(concept.get("interval_days", 0), concept.get("interval", 0))
        n = max(concept.get("repetition_n", 0), concept.get("repetition", 0))
        ef = concept.get("easiness_factor") if concept.get("easiness_factor") != 2.5 else concept.get("ease_factor", 2.5)
        confidence = concept.get("confidence", "Not rated")
        last_attempt = concept.get("last_attempt")
        next_review = concept.get("next_review", concept.get("next_due_date"))

        # 1. Unseen concept
        if reviews == 0 and last_q == 0:
            mastery_state = "Needs relearning"
            return {
                "concept_id": cid,
                "title": title,
                "mastery_score": 0,
                "mastery_state": mastery_state,
                "mastery_display": "0% — Needs relearning",
                "mastery_level": "Unseen",
                "is_mastered": False,
                "consecutive_correct": 0,
                "retention_strength": 0.0,
                "prerequisite_health": 1.0,
                "recommended_action": "introduce",
                "attempt_count": 0,
                "confidence": confidence,
                "last_attempt": last_attempt,
                "next_review": next_review,
                "ease_factor": ef,
                "interval": interval,
                "repetition": n,
                "components": {
                    "recall_quality": 0,
                    "consistency": 0,
                    "retention_stability": 0,
                    "prerequisite_health": 10
                }
            }

        # 2. Recall Quality Component (0-40 pts)
        q_pts = min(40, round((max(0, last_q) / 5.0) * 40))

        # 3. Historical Consistency Component (0-30 pts)
        cons_pts = min(20, consecutive * 12)
        vol_pts = min(10, reviews * 2)
        consistency_pts = min(30, cons_pts + vol_pts)

        # 4. Retention Stability Component (0-20 pts)
        interval_pts = min(12.0, (min(interval, 14) / 14.0) * 12.0)
        rep_pts = min(8.0, (min(n, 3) / 3.0) * 8.0)
        retention_pts = min(20, round(interval_pts + rep_pts))
        retention_strength = round(min(1.0, (interval / 14.0) * 0.6 + (n / 3.0) * 0.4), 2)

        # 5. Prerequisite Health Component (0-10 pts)
        if prerequisites and len(prerequisites) > 0:
            passed_prereqs = sum(
                1 for p in prerequisites 
                if p.get("last_quality_score", 0) >= 3 or p.get("mastery_level") in ["Proficient", "Mastered"]
            )
            prereq_ratio = passed_prereqs / len(prerequisites)
            prereq_pts = round(prereq_ratio * 10)
            prereq_health = round(prereq_ratio, 2)
        else:
            prereq_pts = 10
            prereq_health = 1.0

        # Total Mastery Score (0-100)
        total_score = max(0, min(100, q_pts + consistency_pts + retention_pts + prereq_pts))

        # Phase 12 5-tier mastery state
        mastery_state = MasteryService.get_mastery_state(total_score, reviews)

        # Legacy Phase 10 mastery_level mapping for backwards compatibility with existing tests
        if (total_score >= 82 and last_q >= 4 and consecutive >= 1 and reviews >= 1) or concept.get("sm2_status") == "mastered":
            mastery_level = "Mastered"
            is_mastered = True
            total_score = max(total_score, 85)
            action = "ready_for_next"
        elif total_score >= 65 and last_q >= 3:
            mastery_level = "Proficient"
            is_mastered = False
            action = "reinforce"
        elif total_score >= 35 and last_q >= 3:
            mastery_level = "Practicing"
            is_mastered = False
            action = "active_recall"
        else:
            mastery_level = "Learning"
            is_mastered = False
            action = "review_notes"

        mastery_display = MasteryService.format_mastery_badge(total_score)

        return {
            "concept_id": cid,
            "title": title,
            "mastery_score": total_score,
            "mastery_state": mastery_state,
            "mastery_display": mastery_display,
            "mastery_level": mastery_level,
            "is_mastered": is_mastered,
            "consecutive_correct": consecutive,
            "retention_strength": retention_strength,
            "prerequisite_health": prereq_health,
            "recommended_action": action,
            "attempt_count": reviews,
            "confidence": confidence,
            "last_attempt": last_attempt,
            "next_review": next_review,
            "ease_factor": ef,
            "interval": interval,
            "repetition": n,
            "components": {
                "recall_quality": q_pts,
                "consistency": consistency_pts,
                "retention_stability": retention_pts,
                "prerequisite_health": prereq_pts
            }
        }

    @staticmethod
    def calculate_curriculum_mastery(
        concepts: Dict[str, Dict[str, Any]],
        dependencies: Optional[List[Tuple[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Calculates curriculum-wide mastery with topological dependency weighting.
        """
        total = len(concepts)
        if total == 0:
            return {
                "overall_mastery_percent": 0,
                "mastered_count": 0,
                "proficient_count": 0,
                "practicing_count": 0,
                "learning_count": 0,
                "unseen_count": 0,
                "total_concepts": 0,
                "concept_mastery_map": {},
                "knowledge_frontier": [],
                "at_risk_concepts": [],
                "curriculum_status": "Not Started"
            }

        # Build reverse dependency map to find prerequisites
        prereq_map: Dict[str, List[Dict[str, Any]]] = {cid: [] for cid in concepts}
        downstream_counts: Dict[str, int] = {cid: 0 for cid in concepts}
        if dependencies:
            for p_id, c_id in dependencies:
                if p_id in concepts and c_id in prereq_map:
                    prereq_map[c_id].append(concepts[p_id])
                if p_id in downstream_counts:
                    downstream_counts[p_id] += 1

        concept_mastery_map: Dict[str, Dict[str, Any]] = {}
        weighted_score_sum = 0.0
        total_weight = 0.0

        mastered_count = 0
        proficient_count = 0
        practicing_count = 0
        learning_count = 0
        unseen_count = 0
        at_risk_concepts: List[str] = []
        knowledge_frontier: List[str] = []

        for cid, c in concepts.items():
            eval_res = MasteryService.evaluate_concept_mastery(c, prereq_map.get(cid))
            concept_mastery_map[cid] = eval_res

            # Weight by topological importance (foundational concepts carry higher weight)
            weight = 1.0 + (downstream_counts.get(cid, 0) * 0.25)
            weighted_score_sum += eval_res["mastery_score"] * weight
            total_weight += weight

            lvl = eval_res["mastery_level"]
            if lvl == "Mastered":
                mastered_count += 1
            elif lvl == "Proficient":
                proficient_count += 1
            elif lvl == "Practicing":
                practicing_count += 1
            elif lvl == "Learning":
                learning_count += 1
                if c.get("last_quality_score", 0) < 3 and c.get("total_reviews", 0) > 0:
                    at_risk_concepts.append(cid)
            elif lvl == "Unseen":
                unseen_count += 1
                # If all prerequisites are proficient or mastered, it's on the frontier
                all_prereqs_met = all(
                    p.get("last_quality_score", 0) >= 3 or p.get("mastery_level") in ["Proficient", "Mastered"]
                    for p in prereq_map.get(cid, [])
                )
                if all_prereqs_met:
                    knowledge_frontier.append(cid)

        overall_percent = round(weighted_score_sum / total_weight) if total_weight > 0 else 0

        if mastered_count == total:
            status = "Fully Mastered"
        elif overall_percent >= 75:
            status = "Approaching Mastery"
        elif unseen_count == total:
            status = "Not Started"
        else:
            status = "In Progress"

        return {
            "overall_mastery_percent": overall_percent,
            "mastered_count": mastered_count,
            "proficient_count": proficient_count,
            "practicing_count": practicing_count,
            "learning_count": learning_count,
            "unseen_count": unseen_count,
            "total_concepts": total,
            "concept_mastery_map": concept_mastery_map,
            "knowledge_frontier": knowledge_frontier,
            "at_risk_concepts": at_risk_concepts,
            "curriculum_status": status
        }

    @staticmethod
    def check_newly_mastered(previous_mastery_level: Optional[str], current_mastery_level: str) -> bool:
        """
        Determines whether a concept has just crossed the threshold into 'Mastered'.
        Used to trigger celebratory AI teacher avatar events.
        """
        return previous_mastery_level != "Mastered" and current_mastery_level == "Mastered"
