"""
Comprehensive test suite for EduMentor Phases 11, 12, 13, and 14:
- Phase 11: Qualitative Feedback Prioritization & Semantic Accessible Badges
- Phase 12: Mastery Engine 5-Tier Scale & Stored Concept Attributes
- Phase 13: Confidence Tracking & Metacognitive Adaptive Calibration
- Phase 14: SM-2 Spaced Repetition Calibration
"""

import unittest
from datetime import date, datetime
from edumentor.scheduler import calculate_sm2, calculate_phase14_sm2
from edumentor.services.mastery_service import MasteryService, MASTERY_STATE_METADATA
from edumentor.orchestrator import EduMentorOrchestrator


class TestPhases11To14(unittest.TestCase):
    def setUp(self):
        self.orch = EduMentorOrchestrator(student_name="Ashwel")

    # =========================================================================
    # PHASE 11 TESTS: Feedback Hierarchy & Accessible Semantic Badges
    # =========================================================================
    def test_phase11_semantic_badge_formatting(self):
        """Verify score is formatted with semantic state e.g. '82% — Strong understanding'."""
        self.assertEqual(MasteryService.format_mastery_badge(82), "82% — Strong understanding")
        self.assertEqual(MasteryService.format_mastery_badge(95), "95% — Mastered")
        self.assertEqual(MasteryService.format_mastery_badge(68), "68% — Partial understanding")
        self.assertEqual(MasteryService.format_mastery_badge(52), "52% — Developing")
        self.assertEqual(MasteryService.format_mastery_badge(30), "30% — Needs relearning")

    def test_phase11_mastery_indicators_not_color_alone(self):
        """Verify each state has an explicit textual label and icon, avoiding color-only indicators."""
        for state_name, meta in MASTERY_STATE_METADATA.items():
            self.assertIn("label", meta)
            self.assertIn("icon", meta)
            self.assertIn("badge_display", meta)
            self.assertTrue(len(meta["icon"]) >= 1)
            self.assertEqual(meta["label"], state_name)
            # Must include icon + label
            self.assertIn(meta["icon"], meta["badge_display"])
            self.assertIn(meta["label"], meta["badge_display"])

    # =========================================================================
    # PHASE 12 TESTS: 5-Tier Mastery Scale & Stored Concept Attributes
    # =========================================================================
    def test_phase12_exact_five_tier_scale(self):
        """
        Verify exact 5-tier bands:
          0–39   Needs relearning
          40–59  Developing
          60–74  Partial understanding
          75–89  Strong understanding
          90–100 Mastered
        """
        # 0–39 Needs relearning
        self.assertEqual(MasteryService.get_mastery_state(0), "Needs relearning")
        self.assertEqual(MasteryService.get_mastery_state(25), "Needs relearning")
        self.assertEqual(MasteryService.get_mastery_state(39), "Needs relearning")

        # 40–59 Developing
        self.assertEqual(MasteryService.get_mastery_state(40), "Developing")
        self.assertEqual(MasteryService.get_mastery_state(50), "Developing")
        self.assertEqual(MasteryService.get_mastery_state(59), "Developing")

        # 60–74 Partial understanding
        self.assertEqual(MasteryService.get_mastery_state(60), "Partial understanding")
        self.assertEqual(MasteryService.get_mastery_state(70), "Partial understanding")
        self.assertEqual(MasteryService.get_mastery_state(74), "Partial understanding")

        # 75–89 Strong understanding
        self.assertEqual(MasteryService.get_mastery_state(75), "Strong understanding")
        self.assertEqual(MasteryService.get_mastery_state(82), "Strong understanding")
        self.assertEqual(MasteryService.get_mastery_state(89), "Strong understanding")

        # 90–100 Mastered
        self.assertEqual(MasteryService.get_mastery_state(90), "Mastered")
        self.assertEqual(MasteryService.get_mastery_state(98), "Mastered")
        self.assertEqual(MasteryService.get_mastery_state(100), "Mastered")

    def test_phase12_stored_attributes_on_concept(self):
        """
        Verify every concept persistently stores:
        mastery_score, attempt_count, confidence, last_attempt, next_review
        """
        self.orch.load_sample_module("Operating Systems")
        cid = self.orch.current_concept_id
        c = self.orch.concepts[cid]

        # Check initial values
        self.assertIn("mastery_score", c)
        self.assertIn("attempt_count", c)
        self.assertIn("confidence", c)
        self.assertIn("last_attempt", c)
        self.assertIn("next_review", c)

        # Trigger recall and submit answer
        self.orch.trigger_ready_for_recall()
        answer = "A process is an active executing instance of a computer program with its own memory space."
        self.orch.submit_recall_response(answer)

        # Check updated stored attributes
        updated_c = self.orch.concepts[cid]
        self.assertGreater(updated_c["mastery_score"], 0)
        self.assertEqual(updated_c["attempt_count"], 1)
        self.assertIsNotNone(updated_c["last_attempt"])
        self.assertIsNotNone(updated_c["next_review"])
        self.assertIn("mastery_state", updated_c)

    # =========================================================================
    # PHASE 13 TESTS: Confidence Tracking & Adaptive Metacognitive Calibration
    # =========================================================================
    def test_phase13_confidence_prompt_and_storage(self):
        """Verify that after answering, confidence is prompted and stored separately from correctness."""
        self.orch.load_sample_module("Operating Systems")
        cid = self.orch.current_concept_id
        self.orch.trigger_ready_for_recall()

        res = self.orch.submit_recall_response("A process has code and data.")
        self.assertTrue(self.orch.awaiting_confidence)
        self.assertIn("How confident were you about that answer?", res["system_message"])
        self.assertIn("confidence_options", res)
        self.assertEqual(res["confidence_options"], ["Not very confident", "Somewhat confident", "Very confident"])

        # Store confidence
        calib_res = self.orch.record_student_confidence("Somewhat confident")
        c = self.orch.concepts[cid]
        self.assertEqual(c["confidence"], "Somewhat confident")
        self.assertFalse(self.orch.awaiting_confidence)
        self.assertIn("confidence", c)
        self.assertIn("last_quality_score", c)  # Stored separately from quality/score

    def test_phase13_adaptive_overconfidence_detection(self):
        """
        Confidence: Very confident, Actual score: low (e.g. 38%)
        EduMentor responds:
        'Interesting — you were quite confident there. Let's revisit this one later so we can make sure it really sticks.'
        """
        calibration = MasteryService.analyze_confidence_calibration(
            confidence="Very confident",
            score=38.0,
            quality=2,
            concept_title="Virtual Memory"
        )
        self.assertEqual(calibration["calibration_state"], "overconfident")
        self.assertEqual(
            calibration["dialogue"],
            "Interesting — you were quite confident there. Let's revisit this one later so we can make sure it really sticks."
        )

    def test_phase13_adaptive_underconfidence_coaching(self):
        """Confidence: Not very confident, Actual score: high (e.g. 88%) -> supportive coaching."""
        calibration = MasteryService.analyze_confidence_calibration(
            confidence="Not very confident",
            score=88.0,
            quality=4,
            concept_title="Processes"
        )
        self.assertEqual(calibration["calibration_state"], "underconfident")
        self.assertIn("Trust your intuition more", calibration["dialogue"])

    def test_phase13_orchestrator_confidence_chat_routing(self):
        """Verify student typing confidence into chat is processed by calibration."""
        self.orch.load_sample_module("Operating Systems")
        self.orch.trigger_ready_for_recall()
        self.orch.submit_recall_response("A process is a program in execution.")
        self.assertTrue(self.orch.awaiting_confidence)

        # Student replies with confidence
        res = self.orch.handle_user_chat("I was very confident about that answer!")
        c = self.orch.concepts[self.orch.current_concept_id]
        self.assertEqual(c["confidence"], "Very confident")
        self.assertFalse(self.orch.awaiting_confidence)

    # =========================================================================
    # PHASE 14 TESTS: SM-2 Spaced Repetition Calibration
    # =========================================================================
    def test_phase14_sm2_progression(self):
        """
        Verify Phase 14 SM-2 intervals:
        1st successful recall -> Review tomorrow (1 day)
        2nd successful recall -> Review in 3 days (3 days)
        3rd successful recall -> Review in 7 days (7 days)
        Strong repeated recall -> Review in 14 days (14 days)
        """
        ref = date(2026, 9, 10)

        # 1st successful recall
        r1 = calculate_phase14_sm2(quality_q=4, repetition=0, ease_factor=2.5, reference_date=ref)
        self.assertEqual(r1["repetition"], 1)
        self.assertEqual(r1["interval"], 1)
        self.assertEqual(r1["next_review"], "2026-09-11")

        # 2nd successful recall
        r2 = calculate_phase14_sm2(quality_q=4, repetition=1, ease_factor=2.5, reference_date=ref)
        self.assertEqual(r2["repetition"], 2)
        self.assertEqual(r2["interval"], 3)
        self.assertEqual(r2["next_review"], "2026-09-13")

        # 3rd successful recall
        r3 = calculate_phase14_sm2(quality_q=5, repetition=2, ease_factor=2.6, reference_date=ref)
        self.assertEqual(r3["repetition"], 3)
        self.assertEqual(r3["interval"], 7)
        self.assertEqual(r3["next_review"], "2026-09-17")

        # Strong repeated recall (4th)
        r4 = calculate_phase14_sm2(quality_q=5, repetition=3, ease_factor=2.7, reference_date=ref)
        self.assertEqual(r4["repetition"], 4)
        self.assertEqual(r4["interval"], 14)
        self.assertEqual(r4["next_review"], "2026-09-24")

    def test_phase14_weak_answers_reduce_interval(self):
        """Verify weak answers (quality < 3) reduce the review interval."""
        # Previous interval was 14 days; weak answer should reduce it
        r_weak = calculate_phase14_sm2(
            quality_q=2,
            repetition=3,
            ease_factor=2.5,
            current_interval=14,
            reference_date=date(2026, 9, 10)
        )
        self.assertEqual(r_weak["repetition"], 0)
        self.assertLess(r_weak["interval"], 14)
        self.assertEqual(r_weak["interval"], 7)  # 14 // 2
        self.assertEqual(r_weak["status"], "weak")

        # If current interval was 1 or 0, it stays 1
        r_weak_base = calculate_phase14_sm2(
            quality_q=1,
            repetition=1,
            ease_factor=2.5,
            current_interval=1,
            reference_date=date(2026, 9, 10)
        )
        self.assertEqual(r_weak_base["interval"], 1)

    def test_phase14_stored_keys_presence(self):
        """Verify ease_factor, interval, repetition, and next_review are returned."""
        res = calculate_phase14_sm2(quality_q=4, repetition=0)
        self.assertIn("ease_factor", res)
        self.assertIn("interval", res)
        self.assertIn("repetition", res)
        self.assertIn("next_review", res)


if __name__ == "__main__":
    unittest.main()
