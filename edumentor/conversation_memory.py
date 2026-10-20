"""
Phase 24 — Conversation Memory & Session Context Subsystem.

Maintains structured session context for the active study session:
1. Current subject (id, title)
2. Current module (id, number, title)
3. Current concept (id, title, summary, key points, canonical explanation, prerequisites)
4. Previous concepts (chronological records of studied concepts, timestamps, mastery)
5. Previous answers (history of student recall answers linked to concept and question)
6. Previous feedback (evaluations, scores, verdicts, strengths, missing concepts, coaching tips)
7. Current mastery (active concept mastery score & level, overall curriculum mastery metrics)
8. Next review (SM-2 scheduled review date, interval days, upcoming review queue)

Provides selective context retrieval (`retrieve_relevant_context` and `format_llm_prompt_context`)
so that the LLM is given high-density pedagogical context without unbounded raw conversation dumps.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json


@dataclass
class ConceptStudyRecord:
    """Record of a concept encountered or studied during this session."""
    concept_id: str
    title: str
    module_id: Optional[str] = None
    module_number: Optional[int] = None
    module_title: Optional[str] = None
    studied_at: str = field(default_factory=lambda: datetime.now().isoformat())
    mastery_level: str = "Learning"
    mastery_score: float = 0.0
    quality_q: Optional[int] = None
    verdict: Optional[str] = None
    repetition: int = 0
    interval_days: int = 0
    next_review: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RecallAttemptRecord:
    """Record of a student active recall question, answer, and resulting feedback."""
    attempt_id: str
    concept_id: str
    concept_title: str
    question_text: str
    student_answer: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    quality_q: int = 0
    composite_score: float = 0.0
    verdict: str = "Unrated"
    strengths: List[str] = field(default_factory=list)
    missing_concepts: List[str] = field(default_factory=list)
    coaching_tip: str = ""
    feedback_message: str = ""
    mastery_level_after: str = "Learning"
    next_review: Optional[str] = None
    interval_days: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConversationMemory:
    """
    Structured Session Context & Conversation Memory Manager for EduMentor.
    Tracks the 8 core items and provides selective context retrieval for LLM interactions.
    """

    def __init__(self, student_name: str = "Ashwel"):
        self.student_name = student_name

        # 1. Current Subject
        self._current_subject: Dict[str, Any] = {
            "id": None,
            "title": None
        }

        # 2. Current Module
        self._current_module: Dict[str, Any] = {
            "id": None,
            "number": None,
            "title": None
        }

        # 3. Current Concept
        self._current_concept: Dict[str, Any] = {
            "id": None,
            "title": None,
            "summary": None,
            "key_points": [],
            "canonical_explanation": None,
            "prerequisites": [],
            "module_id": None,
            "module_number": None
        }

        # 4. Previous Concepts (Chronological history of concepts studied in this session)
        self._previous_concepts: List[ConceptStudyRecord] = []

        # 5. Previous Answers (Chronological history of student answers)
        self._previous_answers: List[RecallAttemptRecord] = []

        # 6. Previous Feedback (Chronological history of evaluations & feedback)
        # Maintained synchronously with recall attempts and exposed as structured feedback objects
        self._previous_feedback: List[Dict[str, Any]] = []

        # 7. Current Mastery (Active concept & overall curriculum mastery)
        self._current_mastery: Dict[str, Any] = {
            "concept_id": None,
            "concept_score": 0.0,
            "concept_level": "Unseen",
            "concept_state": "Needs relearning",
            "concept_display": "0% — Needs relearning",
            "is_mastered": False,
            "overall_mastery_percent": 0.0,
            "mastered_count": 0,
            "total_concepts": 0
        }

        # 8. Next Review (SM-2 review schedule for current concept & upcoming queue)
        self._next_review: Dict[str, Any] = {
            "concept_id": None,
            "next_review_date": None,
            "interval_days": 0,
            "repetition_count": 0,
            "due_status": "new",
            "upcoming_queue": []
        }

        # Last question generated for the active concept
        self._last_question_text: Optional[str] = None
        self._last_question_grounding: Optional[Dict[str, Any]] = None

    # -------------------------------------------------------------------------
    # Properties for the 8 Core Items
    # -------------------------------------------------------------------------
    @property
    def current_subject(self) -> Dict[str, Any]:
        """Item 1: Current Subject (id, title)."""
        return dict(self._current_subject)

    @property
    def current_module(self) -> Dict[str, Any]:
        """Item 2: Current Module (id, number, title)."""
        return dict(self._current_module)

    @property
    def current_concept(self) -> Dict[str, Any]:
        """Item 3: Current Concept (id, title, summary, key_points, canonical_explanation, prerequisites)."""
        return dict(self._current_concept)

    @property
    def previous_concepts(self) -> List[Dict[str, Any]]:
        """Item 4: Chronological list of previous concepts studied."""
        return [c.to_dict() for c in self._previous_concepts]

    @property
    def previous_answers(self) -> List[Dict[str, Any]]:
        """Item 5: Chronological list of student recall answers."""
        return [
            {
                "attempt_id": a.attempt_id,
                "concept_id": a.concept_id,
                "concept_title": a.concept_title,
                "question_text": a.question_text,
                "student_answer": a.student_answer,
                "timestamp": a.timestamp
            }
            for a in self._previous_answers
        ]

    @property
    def previous_feedback(self) -> List[Dict[str, Any]]:
        """Item 6: Chronological list of AI feedback evaluations."""
        return list(self._previous_feedback)

    @property
    def current_mastery(self) -> Dict[str, Any]:
        """Item 7: Active concept mastery & curriculum mastery metrics."""
        return dict(self._current_mastery)

    @property
    def next_review(self) -> Dict[str, Any]:
        """Item 8: Next review schedule and queue."""
        return dict(self._next_review)

    # -------------------------------------------------------------------------
    # State Mutation & Synchronization
    # -------------------------------------------------------------------------
    def set_subject(self, subject_id: Optional[str], subject_title: Optional[str]) -> None:
        """Update current subject identity."""
        self._current_subject = {
            "id": subject_id,
            "title": subject_title
        }

    def set_module(self, module_id: Optional[str], module_number: Optional[int], module_title: Optional[str]) -> None:
        """Update current module identity."""
        self._current_module = {
            "id": module_id,
            "number": module_number,
            "title": module_title
        }

    def set_current_concept(self, concept: Optional[Dict[str, Any]]) -> None:
        """
        Update the current concept. If shifting from an earlier concept,
        records the previous concept in `_previous_concepts` if not already recorded.
        """
        if not concept:
            self._current_concept = {
                "id": None,
                "title": None,
                "summary": None,
                "key_points": [],
                "canonical_explanation": None,
                "prerequisites": [],
                "module_id": None,
                "module_number": None
            }
            return

        prev_id = self._current_concept.get("id")
        new_id = concept.get("id")

        # If switching to a new concept from a valid previous concept, record transition
        if prev_id and prev_id != new_id:
            self._archive_concept_visit(self._current_concept)

        # Update module if concept carries module metadata
        c_mod_id = concept.get("module_id") or self._current_module.get("id")
        c_mod_num = concept.get("module_number") or self._current_module.get("number")
        c_mod_title = concept.get("module_title") or self._current_module.get("title")
        if c_mod_id or c_mod_title:
            self.set_module(c_mod_id, c_mod_num, c_mod_title)

        self._current_concept = {
            "id": new_id,
            "title": concept.get("title", new_id),
            "summary": concept.get("summary", ""),
            "key_points": list(concept.get("key_points", [])),
            "canonical_explanation": concept.get("canonical_explanation", concept.get("summary", "")),
            "prerequisites": list(concept.get("prerequisites", [])),
            "module_id": c_mod_id,
            "module_number": c_mod_num,
            "module_title": c_mod_title
        }

        # Update current concept mastery
        self._current_mastery.update({
            "concept_id": new_id,
            "concept_score": float(concept.get("mastery_score", 0.0)),
            "concept_level": concept.get("mastery_level", "Unseen"),
            "concept_state": concept.get("mastery_state", "Needs relearning"),
            "concept_display": concept.get("mastery_display", f"{concept.get('mastery_score', 0)}% — {concept.get('mastery_state', 'Needs relearning')}"),
            "is_mastered": bool(concept.get("is_mastered", False))
        })

        # Update current concept next review
        self._next_review.update({
            "concept_id": new_id,
            "next_review_date": concept.get("next_review") or concept.get("next_due_date"),
            "interval_days": int(concept.get("interval_days", concept.get("interval", 0))),
            "repetition_count": int(concept.get("repetition_n", concept.get("repetition", 0))),
            "due_status": concept.get("sm2_status", "new")
        })

    def _archive_concept_visit(self, concept_dict: Dict[str, Any]) -> None:
        """Helper to append a completed or visited concept to previous_concepts."""
        cid = concept_dict.get("id")
        if not cid:
            return

        record = ConceptStudyRecord(
            concept_id=cid,
            title=concept_dict.get("title", cid),
            module_id=concept_dict.get("module_id"),
            module_number=concept_dict.get("module_number"),
            module_title=concept_dict.get("module_title"),
            mastery_level=self._current_mastery.get("concept_level", "Learning"),
            mastery_score=float(self._current_mastery.get("concept_score", 0.0)),
            repetition=int(self._next_review.get("repetition_count", 0)),
            interval_days=int(self._next_review.get("interval_days", 0)),
            next_review=self._next_review.get("next_review_date")
        )
        # Avoid duplicate consecutive entries if already the last studied
        if self._previous_concepts and self._previous_concepts[-1].concept_id == cid:
            self._previous_concepts[-1] = record
        else:
            self._previous_concepts.append(record)

    def record_recall_question(self, concept_id: str, question_text: str, grounding: Optional[Dict[str, Any]] = None) -> None:
        """Store the active recall question generated for the concept."""
        self._last_question_text = question_text
        self._last_question_grounding = grounding

    def record_answer_and_feedback(
        self,
        concept_id: str,
        concept_title: str,
        question_text: str,
        student_answer: str,
        eval_result: Dict[str, Any],
        sm2_result: Optional[Dict[str, Any]] = None,
        mastery_eval: Optional[Dict[str, Any]] = None
    ) -> RecallAttemptRecord:
        """
        Record a student's answer and the AI teacher's evaluation feedback.
        Updates previous_answers, previous_feedback, current_mastery, and next_review.
        """
        attempt_id = f"att_{len(self._previous_answers) + 1}_{int(datetime.now().timestamp())}"
        q_score = float(eval_result.get("composite_score", eval_result.get("score", 0.0)))
        q_val = int(eval_result.get("quality_q", 0))
        verdict = eval_result.get("verdict", "Evaluated")
        strengths = list(eval_result.get("strengths", []))
        missing = list(eval_result.get("missing_concepts", eval_result.get("missing_points", [])))
        tip = eval_result.get("actionable_tip", "")
        feedback_msg = eval_result.get("reasoning", "")

        next_date = None
        interval_d = 0
        rep_n = 0
        if sm2_result:
            next_date = sm2_result.get("next_review")
            interval_d = sm2_result.get("interval", sm2_result.get("interval_days", 0))
            rep_n = sm2_result.get("repetition", sm2_result.get("repetition_n", 0))

        mastery_lvl = "Learning"
        if mastery_eval:
            mastery_lvl = mastery_eval.get("mastery_level", "Learning")

        # 1. Create Attempt Record
        record = RecallAttemptRecord(
            attempt_id=attempt_id,
            concept_id=concept_id,
            concept_title=concept_title,
            question_text=question_text,
            student_answer=student_answer,
            quality_q=q_val,
            composite_score=q_score,
            verdict=verdict,
            strengths=strengths,
            missing_concepts=missing,
            coaching_tip=tip,
            feedback_message=feedback_msg,
            mastery_level_after=mastery_lvl,
            next_review=next_date,
            interval_days=interval_d
        )
        self._previous_answers.append(record)

        # 2. Append to previous_feedback
        feedback_item = {
            "feedback_id": f"fb_{attempt_id}",
            "attempt_id": attempt_id,
            "concept_id": concept_id,
            "concept_title": concept_title,
            "verdict": verdict,
            "quality_q": q_val,
            "composite_score": q_score,
            "strengths": strengths,
            "missing_concepts": missing,
            "coaching_tip": tip,
            "reasoning": feedback_msg,
            "timestamp": record.timestamp
        }
        self._previous_feedback.append(feedback_item)

        # 3. Update current mastery
        if mastery_eval:
            self._current_mastery.update({
                "concept_id": concept_id,
                "concept_score": float(mastery_eval.get("mastery_score", q_score)),
                "concept_level": mastery_eval.get("mastery_level", mastery_lvl),
                "concept_state": mastery_eval.get("mastery_state", "Needs relearning"),
                "concept_display": mastery_eval.get("mastery_display", f"{int(q_score)}% — {verdict}"),
                "is_mastered": bool(mastery_eval.get("is_mastered", False))
            })

        # 4. Update next review
        if sm2_result:
            self._next_review.update({
                "concept_id": concept_id,
                "next_review_date": next_date,
                "interval_days": interval_d,
                "repetition_count": rep_n,
                "due_status": sm2_result.get("status", "review")
            })

        # Also ensure concept visit is recorded in previous_concepts
        self._archive_concept_visit({
            "id": concept_id,
            "title": concept_title,
            "module_id": self._current_module.get("id"),
            "module_number": self._current_module.get("number"),
            "module_title": self._current_module.get("title")
        })

        return record

    def update_curriculum_mastery(self, curriculum_mastery: Dict[str, Any]) -> None:
        """Update curriculum-wide aggregate mastery statistics."""
        self._current_mastery.update({
            "overall_mastery_percent": float(curriculum_mastery.get("overall_mastery_percent", 0.0)),
            "mastered_count": int(curriculum_mastery.get("mastered_count", 0)),
            "total_concepts": int(curriculum_mastery.get("total_concepts", 0))
        })

    def update_upcoming_reviews(self, queue: List[Dict[str, Any]]) -> None:
        """Update list of upcoming reviews."""
        self._next_review["upcoming_queue"] = list(queue)

    # -------------------------------------------------------------------------
    # Selective Context Retrieval (Zero Token Waste)
    # -------------------------------------------------------------------------
    def retrieve_relevant_context(
        self,
        intent: str = "chat",
        user_query: Optional[str] = None,
        max_history_turns: int = 2
    ) -> Dict[str, Any]:
        """
        Retrieves ONLY the relevant context required for the given task/intent.
        Does NOT dump the entire chat history.

        Args:
            intent: "chat", "recall_question", "evaluation", "hint", or "summary"
            user_query: Optional student prompt / message for relevance filtering
            max_history_turns: Maximum number of recent answers/feedback to retrieve (default: 2)

        Returns:
            Structured dictionary containing only relevant context items.
        """
        current_cid = self._current_concept.get("id")

        # 1. Filter previous concepts: return the most recently completed concepts or prerequisites
        relevant_prev_concepts = []
        if self._previous_concepts:
            # Exclude current concept if present, get last 2 distinct concepts
            seen = set()
            for rec in reversed(self._previous_concepts):
                if rec.concept_id != current_cid and rec.concept_id not in seen:
                    seen.add(rec.concept_id)
                    relevant_prev_concepts.append({
                        "concept_id": rec.concept_id,
                        "title": rec.title,
                        "mastery_level": rec.mastery_level,
                        "mastery_score": rec.mastery_score
                    })
                    if len(relevant_prev_concepts) >= 2:
                        break
            relevant_prev_concepts.reverse()

        # 2. Filter previous answers & feedback:
        # Prioritize answers for the CURRENT concept if any, otherwise the most recent turns
        relevant_attempts: List[RecallAttemptRecord] = []
        if self._previous_answers:
            current_concept_attempts = [
                a for a in self._previous_answers if a.concept_id == current_cid
            ]
            if current_concept_attempts:
                relevant_attempts = current_concept_attempts[-max_history_turns:]
            else:
                relevant_attempts = self._previous_answers[-max_history_turns:]

        # Format compact QA items
        qa_history = [
            {
                "concept_id": a.concept_id,
                "concept_title": a.concept_title,
                "question": a.question_text,
                "student_answer": a.student_answer,
                "verdict": a.verdict,
                "score": a.composite_score,
                "coaching_tip": a.coaching_tip,
                "missing_points": a.missing_concepts
            }
            for a in relevant_attempts
        ]

        # 3. Assemble selective structured context
        context = {
            "subject": self.current_subject,
            "module": self.current_module,
            "current_concept": {
                "id": self._current_concept.get("id"),
                "title": self._current_concept.get("title"),
                "summary": self._current_concept.get("summary"),
                "key_points": self._current_concept.get("key_points", [])[:4],
                "prerequisites": self._current_concept.get("prerequisites", [])
            },
            "mastery": {
                "concept_level": self._current_mastery.get("concept_level"),
                "concept_score": self._current_mastery.get("concept_score"),
                "overall_percent": self._current_mastery.get("overall_mastery_percent"),
                "mastered_count": self._current_mastery.get("mastered_count"),
                "total_concepts": self._current_mastery.get("total_concepts")
            },
            "next_review": {
                "date": self._next_review.get("next_review_date"),
                "interval_days": self._next_review.get("interval_days"),
                "due_status": self._next_review.get("due_status")
            },
            "recent_previous_concepts": relevant_prev_concepts,
            "recent_recall_history": qa_history,
            "intent": intent
        }

        return context

    def format_llm_prompt_context(self, intent: str = "chat", user_message: str = "") -> str:
        """
        Synthesizes a compact, high-density structured prompt context block (under ~150 tokens)
        for injection into LLM system or user prompts.
        """
        ctx = self.retrieve_relevant_context(intent=intent, user_query=user_message)
        subj = ctx["subject"].get("title") or "General Studies"
        mod = ctx["module"].get("title") or (f"Module {ctx['module'].get('number')}" if ctx['module'].get('number') else "Active Module")
        c_title = ctx["current_concept"].get("title") or "Overview"
        c_pts = ctx["current_concept"].get("key_points") or []
        pts_str = "; ".join(c_pts[:3]) if c_pts else (ctx["current_concept"].get("summary") or "Foundational study material.")

        c_level = ctx["mastery"].get("concept_level") or "Learning"
        c_score = ctx["mastery"].get("concept_score") or 0.0
        ov_pct = ctx["mastery"].get("overall_percent") or 0.0
        m_cnt = ctx["mastery"].get("mastered_count") or 0
        tot = ctx["mastery"].get("total_concepts") or 0

        next_rev = ctx["next_review"].get("date") or "Not scheduled yet"
        interval = ctx["next_review"].get("interval_days") or 0

        lines = [
            "[ACTIVE SESSION CONTEXT]",
            f"• Current Subject: {subj}",
            f"• Current Module: {mod}",
            f"• Current Concept: {c_title} (Mastery: {c_level} [{c_score:.1f}%], Next Review: {next_rev} [in {interval}d])",
            f"• Core Concept Principles: {pts_str}"
        ]

        # Prior concepts summary
        prevs = ctx.get("recent_previous_concepts", [])
        if prevs:
            prev_str = ", ".join(f"{p['title']} ({p.get('mastery_level', 'Studied')})" for p in prevs)
            lines.append(f"• Previously Studied Concepts: {prev_str}")
        else:
            lines.append("• Previously Studied Concepts: None (Session start)")

        # Prior answers & feedback summary
        recalls = ctx.get("recent_recall_history", [])
        if recalls:
            last_r = recalls[-1]
            lines.append(
                f"• Last Recall Attempt: Question: \"{last_r['question'][:80]}...\" | "
                f"Answer: \"{last_r['student_answer'][:80]}...\" | "
                f"Verdict: {last_r['verdict']} ({last_r['score']:.0f}%)"
            )
            if last_r.get("missing_points"):
                miss_pts = ", ".join(last_r["missing_points"][:2])
                lines.append(f"• Areas To Strengthen: {miss_pts}")
            if last_r.get("coaching_tip"):
                lines.append(f"• Coaching Note: {last_r['coaching_tip']}")

        lines.append(f"• Overall Progress: {m_cnt}/{tot} concepts mastered ({ov_pct:.1f}%)")

        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # Inspection and Serialization
    # -------------------------------------------------------------------------
    def get_summary(self) -> Dict[str, Any]:
        """Provides a complete snapshot of what EduMentor currently remembers."""
        return {
            "current_subject": self.current_subject,
            "current_module": self.current_module,
            "current_concept": self.current_concept,
            "previous_concepts": self.previous_concepts,
            "previous_answers": self.previous_answers,
            "previous_feedback": self.previous_feedback,
            "current_mastery": self.current_mastery,
            "next_review": self.next_review,
            "counts": {
                "previous_concepts_count": len(self._previous_concepts),
                "previous_answers_count": len(self._previous_answers),
                "previous_feedback_count": len(self._previous_feedback)
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize memory for persistence in SQLite or JSON payloads."""
        return {
            "student_name": self.student_name,
            "current_subject": self._current_subject,
            "current_module": self._current_module,
            "current_concept": self._current_concept,
            "previous_concepts": [c.to_dict() for c in self._previous_concepts],
            "previous_answers": [a.to_dict() for a in self._previous_answers],
            "previous_feedback": self._previous_feedback,
            "current_mastery": self._current_mastery,
            "next_review": self._next_review,
            "last_question_text": self._last_question_text,
            "last_question_grounding": self._last_question_grounding
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationMemory":
        """Deserialize memory from stored session dictionary."""
        mem = cls(student_name=data.get("student_name", "Ashwel"))
        mem._current_subject = dict(data.get("current_subject", {}))
        mem._current_module = dict(data.get("current_module", {}))
        mem._current_concept = dict(data.get("current_concept", {}))

        mem._previous_concepts = [
            ConceptStudyRecord(**c) for c in data.get("previous_concepts", [])
        ]
        mem._previous_answers = [
            RecallAttemptRecord(**a) for a in data.get("previous_answers", [])
        ]
        mem._previous_feedback = list(data.get("previous_feedback", []))
        mem._current_mastery = dict(data.get("current_mastery", {}))
        mem._next_review = dict(data.get("next_review", {}))
        mem._last_question_text = data.get("last_question_text")
        mem._last_question_grounding = data.get("last_question_grounding")
        return mem
