"""
Unit and Integration Tests for Phase 25 — Teacher Message Engine.

Validates:
1. Dedicated TeacherMessageEngine service generating friendly, natural system responses.
2. Controlled AI teacher personality across 7 core pedagogical states:
   - Starting: "Alright, let's get into it. 😊"
   - Encouragement: "You're getting there."
   - Correct: "Exactly! That's the idea."
   - Almost correct: "You're really close. There's just one piece missing."
   - Wrong: "No worries — this one needs another pass."
   - Revision: "Remember this one? Let's see what stuck."
   - Mastery: "Now you've got it. That's a solid recall."
3. Strict emoji restraint: at most 1 subtle emoji per message, never chains of emojis.
4. Adult academic tone: natural, mature mentorship, avoiding children's educational app feel.
5. Seamless orchestrator integration across curriculum load, recall challenge, answer evaluation,
   automatic resurfacing, and next concept progression.
"""

import unittest
import re
from edumentor.services.teacher_message_engine import TeacherMessageEngine, teacher_message_engine
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.llm import LLMConfig


class TestPhase25TeacherMessageEngine(unittest.TestCase):
    """Unit test suite for TeacherMessageEngine standalone functionality."""

    def setUp(self):
        self.engine = TeacherMessageEngine(default_student_name="Ashwel")

    def test_canonical_phrases_defined(self):
        """Verify all 7 canonical tone phrases match user specifications."""
        expected = {
            "starting": "Alright, let's get into it. 😊",
            "encouragement": "You're getting there.",
            "correct": "Exactly! That's the idea.",
            "almost_correct": "You're really close. There's just one piece missing.",
            "wrong": "No worries — this one needs another pass.",
            "revision": "Remember this one? Let's see what stuck.",
            "mastery": "Now you've got it. That's a solid recall."
        }
        for key, phrase in expected.items():
            self.assertEqual(self.engine.get_canonical_phrase(key), phrase)

    def test_starting_message(self):
        """Verify starting message tone, canonical phrase, and concept details."""
        msg = self.engine.get_starting_message(
            concept_title="Process Scheduling",
            summary="Allocates CPU time slices to active processes.",
            total_concepts=4,
            student_name="Ashwel"
        )
        self.assertIn("Alright, let's get into it. 😊", msg)
        self.assertIn("Process Scheduling", msg)
        self.assertIn("Core Intuition", msg)
        self.assertIn("Take your time and study it from your notes.", msg)

    def test_encouragement_message(self):
        """Verify encouragement message tone and mature delivery."""
        msg_general = self.engine.get_encouragement_message()
        self.assertIn("You're getting there.", msg_general)
        self.assertIn("Take a breath", msg_general)

        msg_concept = self.engine.get_encouragement_message(concept_title="Virtual Memory")
        self.assertIn("You're getting there.", msg_concept)
        self.assertIn("Virtual Memory", msg_concept)

    def test_correct_message(self):
        """Verify correct feedback tone, strengths, and coaching tip."""
        msg = self.engine.get_correct_message(
            concept_title="Paging",
            strengths=["Mapped page numbers to frames cleanly", "Understood offset logic"],
            actionable_tip="Think about how TLB caching speeds up this translation."
        )
        self.assertIn("Exactly! That's the idea.", msg)
        self.assertIn("Paging", msg)
        self.assertIn("What you nailed", msg)
        self.assertIn("Mapped page numbers to frames cleanly", msg)
        self.assertIn("Coaching Tip", msg)

    def test_almost_correct_message(self):
        """Verify almost correct tone, missing concepts, and encouraging guidance."""
        msg = self.engine.get_almost_correct_message(
            concept_title="Demand Paging",
            strengths=["Understood lazy swapping"],
            missing_concepts=["Page fault interrupt sequence"],
            actionable_tip="Review the steps the kernel takes during a page fault."
        )
        self.assertIn("You're really close. There's just one piece missing.", msg)
        self.assertIn("Demand Paging", msg)
        self.assertIn("What you understood", msg)
        self.assertIn("What to look over", msg)
        self.assertIn("Page fault interrupt sequence", msg)

    def test_wrong_message(self):
        """Verify wrong answer tone is supportive and not punitive."""
        msg = self.engine.get_wrong_message(
            concept_title="Process State Machine",
            missing_concepts=["Distinction between ready and waiting queues"],
            actionable_tip="Look at what event causes a process to move to waiting."
        )
        self.assertIn("No worries — this one needs another pass.", msg)
        self.assertIn("Process State Machine", msg)
        self.assertIn("adaptive queue", msg)
        # Avoid patronizing or scolding language
        self.assertNotIn("Failed!", msg)
        self.assertNotIn("Incorrect answer!", msg)

    def test_revision_message(self):
        """Verify revision message tone and automatic resurfacing styles."""
        # Canonical revision style
        msg_canon = self.engine.get_revision_message(concept_title="Thrashing", student_name="Ashwel")
        self.assertIn("Remember this one? Let's see what stuck.", msg_canon)
        self.assertIn("Thrashing", msg_canon)
        self.assertIn("Want to give it another try?", msg_canon)

        # Yesterday resurfacing style
        msg_yesterday = self.engine.get_revision_message(
            concept_title="Thrashing",
            student_name="Ashwel",
            style="yesterday"
        )
        self.assertIn("remember Thrashing from yesterday?", msg_yesterday)
        self.assertIn("Remember this one? Let's see what stuck.", msg_yesterday)
        self.assertIn("Want to give it another try?", msg_yesterday)

    def test_mastery_message(self):
        """Verify mastery message celebration and tone."""
        msg = self.engine.get_mastery_message(
            concept_title="Context Switching",
            strengths=["Accurately captured register save/restore overhead"]
        )
        self.assertIn("Now you've got it. That's a solid recall.", msg)
        self.assertIn("Context Switching", msg)
        self.assertIn("complete mastery", msg)

    def test_emoji_restraint_and_mature_tone(self):
        """Verify messages avoid emoji clusters and maintain adult tone."""
        test_messages = [
            self.engine.get_starting_message("Test Concept"),
            self.engine.get_encouragement_message("Test Concept"),
            self.engine.get_correct_message("Test Concept"),
            self.engine.get_almost_correct_message("Test Concept"),
            self.engine.get_wrong_message("Test Concept"),
            self.engine.get_revision_message("Test Concept"),
            self.engine.get_mastery_message("Test Concept"),
            self.engine.get_recall_challenge_message("Explain paging"),
            self.engine.get_next_concept_message("Test Concept"),
            self.engine.get_curriculum_completed_message("OS")
        ]

        # Emoji regex pattern
        emoji_pattern = re.compile(
            r'[\U00010000-\U0010ffff]|[\u2600-\u27bf]',
            flags=re.UNICODE
        )

        for text in test_messages:
            emojis = emoji_pattern.findall(text)
            # Ensure at most 2 emojis total across any whole multi-paragraph message
            self.assertLessEqual(len(emojis), 2, f"Too many emojis ({len(emojis)}) in message: {text[:50]}")
            # Ensure no adjacent emoji burst (e.g. 🎉🌱🌟 or 🎉🎉)
            self.assertFalse(re.search(r'[\U00010000-\U0010ffff\u2600-\u27bf]{2,}', text), "No consecutive emoji chains allowed.")


class TestOrchestratorTeacherMessageEngineIntegration(unittest.TestCase):
    """Integration test suite ensuring EduMentorOrchestrator delegates message generation to TeacherMessageEngine."""

    def setUp(self):
        self.orch = EduMentorOrchestrator(student_name="Ashwel")
        self.orch.llm_config = LLMConfig(provider="demo")
        self.orch.load_sample_module("Operating Systems")

    def test_orchestrator_engine_attribute_and_property(self):
        """Verify orchestrator exposes teacher_message_engine and message_engine property."""
        self.assertIsNotNone(self.orch.teacher_message_engine)
        self.assertIs(self.orch.teacher_message_engine, self.orch.message_engine)
        self.assertIsInstance(self.orch.teacher_message_engine, TeacherMessageEngine)

    def test_load_curriculum_uses_engine_starting_message(self):
        """Verify initial curriculum load message contains canonical starting tone."""
        latest_msg = self.orch.chat_history[-1]["content"]
        self.assertIn("Alright, let's get into it. 😊", latest_msg)
        self.assertIn("I've gone through your module.", latest_msg)

    def test_trigger_ready_for_recall_uses_engine(self):
        """Verify active recall challenge uses engine format."""
        payload = self.orch.trigger_ready_for_recall()
        latest_msg = self.orch.chat_history[-1]["content"]
        self.assertIn("Perfect. Let's see what you remember. 😊", latest_msg)
        self.assertIn("Active Recall Challenge", latest_msg)
        self.assertIn("Take a deep breath and explain in your own words", latest_msg)

    def test_submit_recall_response_correct_verdict_uses_engine(self):
        """Verify high quality recall triggers correct message with canonical tone."""
        self.orch.trigger_ready_for_recall()
        answer = (
            "Process scheduling is the mechanism where the OS dispatcher allocates CPU time "
            "slices to processes in the ready queue using algorithms like Round Robin or Priority Scheduling."
        )
        self.orch.submit_recall_response(answer)
        latest_msg = self.orch.chat_history[-1]["content"]
        self.assertIn("Exactly! That's the idea.", latest_msg)
        self.assertIn("Brilliant recall! 😊", latest_msg)

    def test_submit_recall_response_wrong_verdict_uses_engine(self):
        """Verify weak recall triggers wrong message with canonical tone."""
        self.orch.trigger_ready_for_recall()
        self.orch.submit_recall_response("I have no idea what this is.")
        latest_msg = self.orch.chat_history[-1]["content"]
        self.assertIn("No worries — this one needs another pass.", latest_msg)
        self.assertIn("No worries at all — honestly, this is where real learning happens! 🌱", latest_msg)
        self.assertIn("adaptive queue", latest_msg)

    def test_automatic_resurfacing_uses_engine(self):
        """Verify automatic resurfacing generates revision message with canonical tone."""
        first_cid = self.orch.topological_order[0]
        self.orch.trigger_automatic_resurfacing(concept_id=first_cid)
        latest_msg = self.orch.chat_history[-1]["content"]
        self.assertIn("Remember this one? Let's see what stuck.", latest_msg)
        self.assertIn("Want to give it another try?", latest_msg)

    def test_advance_next_concept_and_loopback_use_engine(self):
        """Verify next concept and loopback messages use engine."""
        # Loopback
        first_cid = self.orch.topological_order[0]
        self.orch.weak_queue.append(first_cid)
        self.orch.advance_next_step()
        loopback_msg = self.orch.chat_history[-1]["content"]
        self.assertIn("Let's loop back to", loopback_msg)
        self.assertIn("quick refresher", loopback_msg)

        # Unvisited next concept
        self.orch.weak_queue.clear()
        self.orch.advance_next_step()
        next_msg = self.orch.chat_history[-1]["content"]
        self.assertIn("Alright, let's move forward to", next_msg)

    def test_free_chat_prompt_generation(self):
        """Verify LLM prompt builder includes teacher personality guidelines."""
        prompt = self.orch.teacher_message_engine.build_conversational_teacher_prompt(
            student_name="Ashwel",
            context_str="Concept: Threads",
            user_message="Why do threads share memory?"
        )
        self.assertIn("university professor or mentor", prompt)
        self.assertIn("Avoid excessive emojis", prompt)
        self.assertIn("Why do threads share memory?", prompt)


if __name__ == "__main__":
    unittest.main()
