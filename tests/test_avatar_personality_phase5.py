"""
Tests for Phase 5 — AI Teacher Personality and Avatar System.
Verifies the friendly, intelligent, calm, encouraging, slightly playful, academic female AI teacher persona,
along with all 11 avatar states, transitions, non-robotic dialogue, and celebration/reminder triggers.
"""

import unittest
from edumentor.components.teacher_avatar import (
    get_avatar_state_config,
    build_teacher_svg,
    get_available_avatar_states,
    get_teacher_avatar_svg
)
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.llm import LLMConfig


class TestAvatarPersonalityPhase5(unittest.TestCase):
    """Test suite for Phase 5 AI Teacher Persona and 11 Avatar States."""

    def setUp(self):
        self.orch = EduMentorOrchestrator(student_name="Ashwel")
        self.orch.llm_config = LLMConfig(provider="demo")

    def test_all_11_avatar_states_configuration(self):
        """Verify all 11 required avatar states return rich visual configurations."""
        expected_states = [
            "idle", "greeting", "thinking", "explaining", "waiting",
            "encouraging", "correct", "almost_correct", "wrong",
            "celebrating", "reminder"
        ]
        available = get_available_avatar_states()
        self.assertEqual(sorted(expected_states), sorted(available))

        for state in expected_states:
            cfg = get_avatar_state_config(state)
            self.assertIn("halo_color1", cfg)
            self.assertIn("halo_color2", cfg)
            self.assertIn("border_color", cfg)
            self.assertIn("badge_text", cfg)
            self.assertIn("mouth_type", cfg)
            self.assertIn("eyes_type", cfg)
            self.assertIn("halo_anim", cfg)

            # Generate SVG and verify tags
            svg = build_teacher_svg(cfg, size=86)
            self.assertTrue(svg.startswith("<svg") or "<svg" in svg)
            self.assertIn("</svg>", svg)
            # Verify academic glasses vector
            self.assertIn("<rect", svg)
            self.assertIn(cfg["glasses_accent"], svg)

    def test_mastered_alias_resolves_to_celebrating(self):
        """Verify 'mastered' state alias correctly resolves to celebrating."""
        mastered_cfg = get_avatar_state_config("mastered")
        celebrating_cfg = get_avatar_state_config("celebrating")
        self.assertEqual(mastered_cfg["badge_text"], celebrating_cfg["badge_text"])
        self.assertEqual(mastered_cfg["halo_color1"], celebrating_cfg["halo_color1"])
        self.assertEqual(mastered_cfg["mouth_type"], "joyful")

    def test_avatar_helper_functions(self):
        """Verify get_teacher_avatar_svg helper generates complete SVG for states."""
        svg_thinking = get_teacher_avatar_svg("thinking", size=90)
        self.assertIn("svg", svg_thinking)
        self.assertIn("#A78BFA", svg_thinking)  # thinking accent

        svg_correct = get_teacher_avatar_svg("correct", size=90)
        self.assertIn("#10B981", svg_correct)  # correct emerald accent

        svg_wrong = get_teacher_avatar_svg("wrong", size=90)
        self.assertIn("#FB7185", svg_wrong)  # wrong supportive rose accent

    def test_subtle_restrained_animations(self):
        """Verify subtle, restrained animation requirements for idle, thinking, speaking, correct, and mastered."""
        # 1. Idle: small breathing motion
        idle_cfg = get_avatar_state_config("idle")
        self.assertIn("avatarBreathe", idle_cfg["head_anim"])
        self.assertEqual(idle_cfg["mouth_anim"], "none")

        # 2. Thinking: slight head movement (thoughtful tilt, not spinning)
        thinking_cfg = get_avatar_state_config("thinking")
        self.assertIn("avatarThinkingHead", thinking_cfg["head_anim"])
        self.assertNotIn("Spin", thinking_cfg["halo_anim"])

        # 3. Speaking / Explaining: subtle mouth animation
        explaining_cfg = get_avatar_state_config("explaining")
        self.assertIn("avatarSpeakingMouth", explaining_cfg["mouth_anim"])
        self.assertIn("avatarSpeakingHead", explaining_cfg["head_anim"])

        # Speaking alias resolves cleanly
        speaking_cfg = get_avatar_state_config("speaking")
        self.assertEqual(speaking_cfg["badge_text"], explaining_cfg["badge_text"])
        self.assertIn("avatarSpeakingMouth", speaking_cfg["mouth_anim"])

        # 4. Correct: small positive expression that settles (finite forwards play, doesn't bounce constantly)
        correct_cfg = get_avatar_state_config("correct")
        self.assertIn("avatarCorrectSettle", correct_cfg["head_anim"])
        self.assertIn("1 forwards", correct_cfg["head_anim"])

        # 5. Mastered / Celebrating: brief celebration that settles (finite forwards play)
        celebrating_cfg = get_avatar_state_config("celebrating")
        self.assertIn("avatarBriefCelebrate", celebrating_cfg["head_anim"])
        self.assertIn("1 forwards", celebrating_cfg["head_anim"])

        # SVG contains animated groups and embedded defs style
        svg = build_teacher_svg(explaining_cfg, size=86)
        self.assertIn('<g class="avatar-head"', svg)
        self.assertIn('<g class="avatar-mouth"', svg)
        self.assertIn("@keyframes avatarSpeakingMouth", svg)
        self.assertIn("@keyframes avatarBreathe", svg)

    def test_orchestrator_initial_and_ingestion_states(self):
        """Verify teacher state initializes to greeting and transitions to thinking upon notes upload."""
        payload = self.orch.initialize_home()
        self.assertEqual(self.orch.teacher_state, "greeting")
        self.assertEqual(payload["teacher_state"], "greeting")

        # Ingesting notes switches teacher avatar to thinking state
        self.orch.ingest_notes_text(
            "Operating Systems note: Process Scheduling allocates CPU time slices. Threads share memory space.",
            title="OS Module"
        )
        # Note: after curriculum is loaded, teacher explains intro or enters waiting state for student to study notes
        self.assertIn(self.orch.teacher_state, ["explaining", "waiting"])

    def test_canonical_intro_dialogue_and_explaining_state(self):
        """Verify the exact canonical introductory phrase requested by the user is used."""
        concepts = [
            {
                "id": "c1",
                "title": "Process Scheduling",
                "summary": "Core mechanism allocating CPU time slices.",
                "canonical_explanation": "Operating system scheduling ensures equitable CPU utilization.",
                "key_points": ["CPU scheduling", "Context switching", "Ready queue"],
                "prerequisites": []
            },
            {
                "id": "c2",
                "title": "Threads & Concurrency",
                "summary": "Execution units sharing memory address space.",
                "canonical_explanation": "Threads enable concurrent execution within a single process address space.",
                "key_points": ["Shared memory", "Race conditions"],
                "prerequisites": ["c1"]
            }
        ]
        self.orch.load_curriculum("Operating Systems", concepts, [("c1", "c2")])
        self.assertIn(self.orch.teacher_state, ["explaining", "waiting"])

        latest_msg = self.orch.chat_history[-1]["content"]
        
        # Verify friendly academic persona - NOT robotic
        self.assertNotIn("🤖 SYSTEM:", latest_msg)
        self.assertIn("Alright, let's start with **Process Scheduling**. 😊", latest_msg)
        self.assertIn("It's an important foundation for the next few topics, so let's make sure this one is clear first.", latest_msg)
        self.assertIn("Take your time and study it from your notes. Let me know when you're ready.", latest_msg)

    def test_recall_prompt_encouraging_state(self):
        """Verify triggering recall sets teacher state to encouraging with warm academic prompt."""
        self.orch.load_sample_module("Operating Systems")
        self.orch.trigger_ready_for_recall()

        self.assertEqual(self.orch.teacher_state, "encouraging")
        self.assertEqual(self.orch.state, "WAITING_RECALL")

        latest_msg = self.orch.chat_history[-1]["content"]
        self.assertNotIn("🤖 SYSTEM:", latest_msg)
        self.assertTrue(
            "Perfect. Let's see what you remember." in latest_msg or
            "Awesome, you've got this!" in latest_msg
        )
        self.assertIn("Active Recall Challenge", latest_msg)


    def test_recall_evaluation_avatar_states_and_tone(self):
        """Verify evaluation outcomes update avatar state to correct, almost_correct, and wrong."""
        self.orch.load_sample_module("Operating Systems")
        self.orch.trigger_ready_for_recall()

        # 1. Correct Answer (score >= 80, q >= 4) -> 'correct' state
        strong_answer = (
            "Process scheduling is how the OS CPU scheduler selects processes from the ready queue "
            "to allocate CPU execution time, maximizing throughput and minimizing latency through context switching."
        )
        self.orch.submit_recall_response(strong_answer)
        self.assertIn(self.orch.teacher_state, ["correct", "almost_correct"])
        self.assertNotIn("🤖 SYSTEM:", self.orch.chat_history[-1]["content"])
        self.assertTrue(
            "Brilliant recall! 😊" in self.orch.chat_history[-1]["content"] or
            "Really solid effort!" in self.orch.chat_history[-1]["content"]
        )

        # 2. Blank / Wrong Answer (q < 3) -> 'wrong' state with supportive expression
        self.orch.trigger_ready_for_recall()
        self.orch.submit_recall_response("I don't know anything about this.")
        self.assertEqual(self.orch.teacher_state, "wrong")

        wrong_msg = self.orch.chat_history[-1]["content"]
        self.assertNotIn("🤖 SYSTEM:", wrong_msg)
        # Supportive expression rather than disappointment
        self.assertIn("No worries at all — honestly, this is where real learning happens! 🌱", wrong_msg)
        self.assertIn("adaptive queue", wrong_msg)

    def test_loopback_and_celebrating_states(self):
        """Verify weak loopback triggers encouraging state, and curriculum completion triggers celebrating."""
        self.orch.load_sample_module("Operating Systems")
        
        # Inject weak concept into queue
        first_cid = self.orch.topological_order[0]
        self.orch.weak_queue.append(first_cid)
        
        self.orch.advance_next_step()
        self.assertEqual(self.orch.teacher_state, "encouraging")
        self.assertIn("Let's loop back to", self.orch.chat_history[-1]["content"])

        # Complete all concepts with quality >= 3
        self.orch.weak_queue.clear()
        for cid in self.orch.topological_order:
            self.orch.concepts[cid]["last_quality_score"] = 4
            self.orch.concepts[cid]["total_reviews"] = 1

        self.orch.advance_next_step()
        self.assertEqual(self.orch.teacher_state, "celebrating")
        self.assertEqual(self.orch.state, "MASTERED")
        self.assertIn("🎉", self.orch.chat_history[-1]["content"])
        self.assertIn("conquered and actively recalled every single concept", self.orch.chat_history[-1]["content"])

    def test_reminder_trigger_state(self):
        """Verify spaced repetition review alert triggers reminder teacher state."""
        self.orch.load_sample_module("Operating Systems")
        first_cid = self.orch.topological_order[0]
        
        payload = self.orch.trigger_reminder(first_cid)
        self.assertEqual(self.orch.teacher_state, "reminder")
        self.assertEqual(payload["teacher_state"], "reminder")
        self.assertIn("Spaced Repetition Due", payload["system_message"])


if __name__ == "__main__":
    unittest.main()
