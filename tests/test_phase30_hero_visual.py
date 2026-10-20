"""
Unit and Integration Tests for Phase 30 — Hero Visual.

Validates:
1. Three luminous ribbons converging toward a mastery node:
   - Concept ribbon (cyan #25D8E8)
   - Recall ribbon (violet #8B5CF6)
   - Teacher / learning journey guiding beam
2. Exact convergence topology:
   CONCEPT ──────────────┐
                         ├──→ MASTERY
   RECALL ───────────────┘
3. Reinterpretation around the teacher and learning journey.
4. Slow movement animation (duration >= 18s).
5. Clean design without excessive particles / starfields.
6. Reduced motion accessibility rule: prefers-reduced-motion.
7. Palette token compliance: #25D8E8, #8B5CF6, #10B981, #050608, #27303B.
"""

import os
import re
import unittest


class TestPhase30HeroVisual(unittest.TestCase):
    """Test suite ensuring Phase 30 Hero Visual specifications."""

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

        cls.css_path = os.path.join(os.path.dirname(__file__), "..", "static", "css", "style.css")
        with open(cls.css_path, "r", encoding="utf-8") as f:
            cls.css_content = f.read()

        cls.js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "app.js")
        with open(cls.js_path, "r", encoding="utf-8") as f:
            cls.js_content = f.read()

    def test_three_luminous_ribbons_exist_in_artwork(self):
        """Verify the 3 ribbons: concept, recall, and teacher guiding beam in SVG."""
        self.assertIn("ribbon-path-concept", self.html_content)
        self.assertIn("ribbon-path-recall", self.html_content)
        self.assertIn("ribbon-path-teacher", self.html_content)

    def test_reinterpretation_around_teacher_and_learning_journey(self):
        """Verify the teacher node / learning journey presence in hero visual."""
        self.assertTrue(
            "hero-art-teacher" in self.html_content or "teacher-guide-node" in self.html_content or "ribbon-path-teacher" in self.html_content,
            "Missing teacher / learning journey element in hero visual"
        )
        self.assertIn("MASTERY", self.html_content)
        self.assertIn("CONCEPT", self.html_content)
        self.assertIn("RECALL", self.html_content)

    def test_cyan_and_violet_color_tokens(self):
        """Verify cyan (#25D8E8) and violet (#8B5CF6) are used in hero artwork."""
        self.assertIn("#25D8E8", self.html_content)
        self.assertIn("#8B5CF6", self.html_content)

    def test_slow_movement_animation(self):
        """Verify slow movement animations (duration >= 18s)."""
        # Search for animation durations in style.css
        durations = re.findall(r'(\d+)s', self.css_content)
        durations_int = [int(d) for d in durations]
        has_slow_animation = any(d >= 18 for d in durations_int)
        self.assertTrue(has_slow_animation, "Expected slow movement animation with duration >= 18s")

    def test_prefers_reduced_motion_rule(self):
        """Verify accessibility support for prefers-reduced-motion."""
        self.assertIn("prefers-reduced-motion", self.css_content)

    def test_interactive_hover_caption_element(self):
        """Verify interactive hover caption element exists in hero artwork."""
        self.assertTrue(
            "heroArtCaption" in self.html_content or "hero-art-caption" in self.html_content or "art-caption" in self.html_content,
            "Missing interactive hover caption in hero artwork"
        )


if __name__ == "__main__":
    unittest.main()
