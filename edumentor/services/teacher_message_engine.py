"""
Phase 25 — Teacher Message Engine.

Dedicated service for generating friendly, natural system responses with a controlled,
mature AI teacher personality. Eliminates ad-hoc, overly technical, or childish copy.

Example tones:
- Starting: "Alright, let's get into it. 😊"
- Encouragement: "You're getting there."
- Correct: "Exactly! That's the idea."
- Almost correct: "You're really close. There's just one piece missing."
- Wrong: "No worries — this one needs another pass."
- Revision: "Remember this one? Let's see what stuck."
- Mastery: "Now you've got it. That's a solid recall."

Restraint:
- Avoids excessive emojis (maximum of 1 subtle emoji when appropriate, never chains like 🎉🌱🌟).
- Avoids juvenile, childish, or patronizing phrasing.
"""

from typing import Dict, List, Any, Optional
import re


class TeacherMessageEngine:
    """
    Generates controlled-personality teacher messages and feedback across the learning lifecycle.
    """

    # -------------------------------------------------------------------------
    # 7 Core Pedagogical Tone Phrases
    # -------------------------------------------------------------------------
    CANONICAL_TONES = {
        "starting": "Alright, let's get into it. 😊",
        "encouragement": "You're getting there.",
        "correct": "Exactly! That's the idea.",
        "almost_correct": "You're really close. There's just one piece missing.",
        "wrong": "No worries — this one needs another pass.",
        "revision": "Remember this one? Let's see what stuck.",
        "mastery": "Now you've got it. That's a solid recall."
    }

    def __init__(self, default_student_name: str = "Ashwel"):
        self.default_student_name = default_student_name

    def get_canonical_phrase(self, tone_key: str) -> str:
        """Return the exact canonical headline phrase for a tone."""
        return self.CANONICAL_TONES.get(tone_key.lower(), "")

    # -------------------------------------------------------------------------
    # 1. Starting
    # -------------------------------------------------------------------------
    def get_starting_message(
        self,
        concept_title: str,
        summary: Optional[str] = None,
        total_concepts: Optional[int] = None,
        student_name: Optional[str] = None
    ) -> str:
        """
        Starting message when a student opens a module or begins studying.
        Tone: "Alright, let's get into it. 😊"
        """
        lead = self.CANONICAL_TONES["starting"]
        name = student_name or self.default_student_name
        intro = (
            f"Got it, {name}. I've gone through your notes. There are quite a few concepts here, "
            f"so I've arranged them in an order that should make them easier to understand."
        )

        lines = [
            lead,
            "",
            intro,
            "",
            f"Alright, let's start with **{concept_title}**. 😊\n\n"
            f"It's an important foundation for the next few topics, so let's make sure this one is clear first."
        ]

        if summary:
            lines.append(f"\n> **Core Intuition**: {summary}")

        lines.append("\nTake your time and study it from your notes. Let me know when you're ready.")
        return "\n".join(lines).strip()

    # -------------------------------------------------------------------------
    # 2. Encouragement
    # -------------------------------------------------------------------------
    def get_encouragement_message(
        self,
        concept_title: Optional[str] = None,
        context: Optional[str] = None,
        student_name: Optional[str] = None
    ) -> str:
        """
        Encouragement message when student asks for reassurance or is working through a tough concept.
        Tone: "You're getting there."
        """
        lead = self.CANONICAL_TONES["encouragement"]
        if concept_title:
            return f"{lead} Wrestling with **{concept_title}** is how the concept really solidifies. What part feels least clear?"
        elif context:
            return f"{lead} {context}"
        return f"{lead} Take a breath, trust your intuition, and focus on the primary mechanism."

    # -------------------------------------------------------------------------
    # 3. Correct
    # -------------------------------------------------------------------------
    def get_correct_message(
        self,
        concept_title: str,
        strengths: Optional[List[str]] = None,
        actionable_tip: Optional[str] = None,
        student_name: Optional[str] = None
    ) -> str:
        """
        Feedback when student provides an accurate, complete recall answer.
        Tone: "Exactly! That's the idea."
        """
        lead = self.CANONICAL_TONES["correct"]
        lines = [
            f"{lead} Brilliant recall! 😊",
            "",
            f"You've captured the main idea of **{concept_title}** and explained it correctly."
        ]

        if strengths:
            bullets = "\n".join(f"- {s}" for s in strengths[:2])
            lines.extend(["", "**What you nailed**:", bullets])

        if actionable_tip:
            lines.extend(["", f"> **Coaching Tip**: {actionable_tip}"])

        lines.extend(["", "I'd consider this a strong understanding! When you're ready, let's move on to the next concept."])
        return "\n".join(lines).strip()

    # -------------------------------------------------------------------------
    # 4. Almost Correct
    # -------------------------------------------------------------------------
    def get_almost_correct_message(
        self,
        concept_title: str,
        strengths: Optional[List[str]] = None,
        missing_concepts: Optional[List[str]] = None,
        actionable_tip: Optional[str] = None,
        student_name: Optional[str] = None
    ) -> str:
        """
        Feedback when student understands the general idea but missed an essential detail.
        Tone: "You're really close. There's just one piece missing."
        """
        lead = self.CANONICAL_TONES["almost_correct"]
        lines = [
            f"{lead} Really solid effort!",
            "",
            f"You've understood the main idea of **{concept_title}** correctly, but there's one important part missing."
        ]

        if strengths:
            s_bullets = "\n".join(f"- {s}" for s in strengths[:2])
            lines.extend(["", "**What you understood**:", s_bullets])

        if missing_concepts:
            m_bullets = "\n".join(f"- {m}" for m in missing_concepts[:2])
            lines.extend(["", "**What to look over**:", m_bullets])

        if actionable_tip:
            lines.extend(["", f"> **Coaching Tip**: {actionable_tip}"])

        lines.extend(["", "I'd consider this a strong understanding, but not quite mastery yet. Have another look at that part in your notes, and we'll come back to it."])
        return "\n".join(lines).strip()

    # -------------------------------------------------------------------------
    # 5. Wrong / Needs Reinforcement
    # -------------------------------------------------------------------------
    def get_wrong_message(
        self,
        concept_title: str,
        missing_concepts: Optional[List[str]] = None,
        actionable_tip: Optional[str] = None,
        student_name: Optional[str] = None
    ) -> str:
        """
        Feedback when student's answer demonstrates confusion or significant gaps.
        Tone: "No worries — this one needs another pass."
        """
        lead = self.CANONICAL_TONES["wrong"]
        lines = [
            f"{lead} No worries at all — honestly, this is where real learning happens! 🌱",
            "",
            f"The answer doesn't show enough understanding of **{concept_title}** yet. Wrestling with it primes your memory for deeper retention."
        ]

        if missing_concepts:
            m_bullets = "\n".join(f"- {m}" for m in missing_concepts[:2])
            lines.extend(["", "**Key areas to strengthen**:", m_bullets])

        if actionable_tip:
            lines.extend(["", f"> **Coaching Tip**: {actionable_tip}"])

        lines.extend(["", "Go through this topic once more. I've placed this in our adaptive queue so I'll ask you about it again shortly."])
        return "\n".join(lines).strip()

    # -------------------------------------------------------------------------
    # 6. Revision / Resurfacing
    # -------------------------------------------------------------------------
    def get_revision_message(
        self,
        concept_title: str,
        student_name: Optional[str] = None,
        reason: Optional[str] = None,
        style: str = "canonical"
    ) -> str:
        """
        Proactive resurfacing or spaced revision invitation.
        Tone: "Remember this one? Let's see what stuck."
        """
        name = student_name or self.default_student_name
        lead = self.CANONICAL_TONES["revision"]
        if style == "yesterday" or reason == "yesterday":
            return (
                f"Hey {name}, remember {concept_title} from yesterday?\n\n"
                f"{lead} You were almost there last time. Want to give it another try?"
            )
        reason_text = "to keep it sharp in your memory" if not reason else reason
        return (
            f"Hey {name}, {lead}\n\n"
            f"It's time to revisit **{concept_title}** {reason_text}.\n\n"
            f"Want to give it another try?"
        )

    # -------------------------------------------------------------------------
    # 7. Mastery
    # -------------------------------------------------------------------------
    def get_mastery_message(
        self,
        concept_title: str,
        strengths: Optional[List[str]] = None,
        actionable_tip: Optional[str] = None,
        student_name: Optional[str] = None
    ) -> str:
        """
        Feedback when student achieves full concept mastery.
        Tone: "Now you've got it. That's a solid recall."
        """
        lead = self.CANONICAL_TONES["mastery"]
        lines = [
            f"Yes! You've got this one now. 🎉 Let's move on. {lead}",
            "",
            f"You've captured the main idea of **{concept_title}** and explained it thoroughly."
        ]

        if strengths:
            bullets = "\n".join(f"- {s}" for s in strengths[:2])
            lines.extend(["", "**What you nailed**:", bullets])

        if actionable_tip:
            lines.extend(["", f"> **Coaching Tip**: {actionable_tip}"])

        lines.extend(["", "I'd consider this complete mastery! Whenever you're ready, let's keep this momentum going into the next concept."])
        return "\n".join(lines).strip()

    # -------------------------------------------------------------------------
    # Recall Challenge & Progression Messages
    # -------------------------------------------------------------------------
    def get_recall_challenge_message(
        self,
        question_text: str,
        concept_title: Optional[str] = None,
        grounding_explanation: Optional[str] = None
    ) -> str:
        """Active recall challenge presentation."""
        lines = [
            "Perfect. Let's see what you remember. 😊",
            "",
            "**Active Recall Challenge**:",
            f"> *\"{question_text}\"*"
        ]
        if grounding_explanation:
            lines.extend(["", f"*📚 Grounded in notes: \"{grounding_explanation}\"*"])

        lines.extend(["", "Take a deep breath and explain in your own words purely from memory — no peeking at notes!"])
        return "\n".join(lines).strip()

    def get_next_concept_message(
        self,
        concept_title: str,
        summary: Optional[str] = None,
        is_loopback: bool = False
    ) -> str:
        """Transition to next concept or loopback."""
        if is_loopback:
            return (
                f"Let's loop back to **{concept_title}** for a quick refresher. 😊\n\n"
                f"Solidifying this foundational concept now ensures you won't struggle with downstream prerequisites.\n\n"
                f"{('> **Refresher summary**: ' + summary + chr(10) + chr(10)) if summary else ''}"
                f"Take a moment to review your notes. Tell me when you're ready to test your recall again!"
            )
        return (
            f"Alright, let's move forward to **{concept_title}**. 😊\n\n"
            f"It builds right on what we just covered, so let's make sure this one is clear first.\n\n"
            f"{('> **Core Intuition**: ' + summary + chr(10) + chr(10)) if summary else ''}"
            f"Take your time and study it from your notes. Let me know when you're ready."
        )

    def get_curriculum_completed_message(
        self,
        curriculum_title: str,
        student_name: Optional[str] = None
    ) -> str:
        """Curriculum completion celebration (mature, non-infantile)."""
        name = student_name or self.default_student_name
        return (
            f"🎉 **Incredible work, {name}!**\n\n"
            f"You have conquered and actively recalled every single concept in **{curriculum_title}**!\n\n"
            f"All nodes in your knowledge graph are verified. Your retention schedule is primed for long-term memory mastery."
        )

    # -------------------------------------------------------------------------
    # Unified Feedback Dispatcher
    # -------------------------------------------------------------------------
    def generate_recall_feedback(
        self,
        eval_result: Dict[str, Any],
        concept_title: str,
        is_newly_mastered: bool = False,
        student_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate natural feedback for student answer evaluation based on verdict and quality score.

        Returns:
            Dict with:
            - "message": formatted natural feedback text
            - "teacher_state": avatar expression state ("celebration", "correct", "almost_correct", "wrong")
            - "msg_type": message type
            - "expression_state": expression state
            - "tone_category": "mastery", "correct", "almost_correct", or "wrong"
        """
        verdict = eval_result.get("verdict", "")
        q = int(eval_result.get("quality_q", 0))
        strengths = eval_result.get("strengths", [])
        missing = eval_result.get("missing_concepts", eval_result.get("missing_points", []))
        tip = eval_result.get("actionable_tip", "")

        if is_newly_mastered or eval_result.get("is_mastered", False):
            msg = self.get_mastery_message(concept_title, strengths, tip, student_name)
            return {
                "message": msg,
                "teacher_state": "celebration",
                "msg_type": "mastered",
                "expression_state": "celebration",
                "tone_category": "mastery"
            }
        elif verdict == "Correct" or q >= 4:
            msg = self.get_correct_message(concept_title, strengths, tip, student_name)
            return {
                "message": msg,
                "teacher_state": "correct",
                "msg_type": "correct",
                "expression_state": "happy",
                "tone_category": "correct"
            }
        elif verdict == "Almost Correct" or q == 3:
            msg = self.get_almost_correct_message(concept_title, strengths, missing, tip, student_name)
            return {
                "message": msg,
                "teacher_state": "almost_correct",
                "msg_type": "almost_correct",
                "expression_state": "almost_correct",
                "tone_category": "almost_correct"
            }
        else:
            msg = self.get_wrong_message(concept_title, missing, tip, student_name)
            return {
                "message": msg,
                "teacher_state": "wrong",
                "msg_type": "wrong",
                "expression_state": "supportive",
                "tone_category": "wrong"
            }

    # -------------------------------------------------------------------------
    # LLM System Prompt Generator for Free Chat
    # -------------------------------------------------------------------------
    def build_conversational_teacher_prompt(
        self,
        student_name: str,
        context_str: str,
        user_message: str
    ) -> str:
        """
        Constructs system prompt instructing the LLM to speak with the controlled
        teacher personality: warm, academic, direct, without excessive emojis or juvenile language.
        """
        return (
            f"You are EduMentor, a personal, empathetic, academic AI teacher for {student_name}.\n"
            f"Personality Guidelines:\n"
            f"- Sound natural, mature, and supportive — like a great university professor or mentor, NOT a children's app.\n"
            f"- Avoid excessive emojis. Use at most one subtle emoji (like 😊) where natural, or none at all.\n"
            f"- Keep responses concise (under 3 sentences) and focused on conceptual understanding.\n\n"
            f"{context_str}\n\n"
            f"Student message: \"{user_message}\"\n"
            f"Provide a clear, pedagogical response that guides them constructively:"
        )


# Default singleton instance
teacher_message_engine = TeacherMessageEngine()
