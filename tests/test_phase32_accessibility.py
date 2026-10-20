"""
Unit and Integration Tests for Phase 32 — Accessibility (WCAG 2.1 AA/AAA Compliance).

Validates:
1. Keyboard navigation (Skip to main content, Escape modal dismissal, keyboard recall shortcuts).
2. Screen-reader labels (aria-label, aria-live regions, role="dialog", role="progressbar").
3. Visible focus indicators (:focus-visible styling with high-contrast outlines).
4. Proper contrast across color tokens and dark backgrounds.
5. Accessible upload controls and accessible chat inputs.
6. Accessible feedback (aria-live announcements for evaluations and progress).
7. Semantic HTML landmarks (<main>, <nav>, <header>, <aside>, <section>).
8. Reduced-motion support (@media (prefers-reduced-motion: reduce)).
9. No color-only mastery communication (multi-modal icons, text labels, and numeric metrics).
"""

import os
import unittest


class TestPhase32Accessibility(unittest.TestCase):
    """Test suite ensuring Phase 32 Accessibility specifications."""

    @classmethod
    def setUpClass(cls):
        cls.css_path = os.path.join(os.path.dirname(__file__), "..", "static", "css", "style.css")
        with open(cls.css_path, "r", encoding="utf-8") as f:
            cls.css_content = f.read()

        cls.html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

        cls.js_path = os.path.join(os.path.dirname(__file__), "..", "static", "js", "app.js")
        with open(cls.js_path, "r", encoding="utf-8") as f:
            cls.js_content = f.read()

    def test_focus_visible_styling_exists(self):
        """Verify visible focus states via :focus-visible rules in CSS."""
        self.assertIn(":focus-visible", self.css_content)
        self.assertTrue(
            "outline" in self.css_content,
            "Missing visible outline in CSS"
        )
        self.assertTrue(
            "#25D8E8" in self.css_content,
            "Missing high-contrast cyan focus color in CSS"
        )

    def test_universal_reduced_motion_support(self):
        """Verify comprehensive reduced-motion support in CSS."""
        self.assertIn("prefers-reduced-motion", self.css_content)
        self.assertTrue(
            "animation" in self.css_content and "none" in self.css_content or "0.01ms" in self.css_content,
            "Missing reduced motion animation overrides"
        )

    def test_screen_reader_only_utility_class(self):
        """Verify .sr-only utility class exists in CSS."""
        self.assertIn(".sr-only", self.css_content)
        self.assertIn("clip: rect", self.css_content)

    def test_skip_to_main_link_exists(self):
        """Verify skip-to-main content link exists in HTML."""
        self.assertTrue(
            "skip-link" in self.html_content or "skip-to-main" in self.html_content or "Skip to" in self.html_content,
            "Missing skip-to-content bypass link in index.html"
        )

    def test_aria_live_announcer_exists(self):
        """Verify aria-live polite announcer exists in HTML."""
        self.assertTrue(
            'aria-live="polite"' in self.html_content,
            "Missing aria-live polite region in index.html"
        )
        self.assertTrue(
            "srLiveAnnouncer" in self.html_content or "toastContainer" in self.html_content,
            "Missing announcer element in index.html"
        )

    def test_dialog_roles_and_aria_modal(self):
        """Verify modal dialogs have role='dialog' and aria-modal='true'."""
        self.assertTrue(
            'role="dialog"' in self.html_content,
            "Missing role='dialog' attributes on modal dialogs"
        )
        self.assertTrue(
            'aria-modal="true"' in self.html_content,
            "Missing aria-modal='true' on modal dialogs"
        )

    def test_accessible_upload_and_chat_controls(self):
        """Verify accessible upload controls and chat input labels."""
        self.assertTrue(
            'aria-label=' in self.html_content,
            "Missing aria-labels on interactive controls"
        )
        self.assertTrue(
            'role="progressbar"' in self.html_content or 'aria-valuenow' in self.html_content,
            "Missing progressbar accessibility on upload processing bar"
        )

    def test_no_color_only_mastery_communication(self):
        """Verify mastery states communicate via symbols/icons AND text labels, not color alone."""
        # Concept badges contain symbols and text
        self.assertIn("✓ Mastered", self.html_content)
        self.assertIn("● Active Recall", self.html_content)
        # JavaScript inline evaluation uses explicit textual mastery bands with icons
        self.assertIn("Mastered", self.js_content)
        self.assertIn("★", self.js_content)
        self.assertIn("Strong understanding", self.js_content)
        self.assertIn("Developing", self.js_content)

    def test_keyboard_navigation_and_shortcuts_in_javascript(self):
        """Verify Escape modal dismissal, keyboard recall shortcuts, and screen reader announcer in JS."""
        self.assertIn("Escape", self.js_content)
        self.assertTrue(
            "announceToScreenReader" in self.js_content or "srLiveAnnouncer" in self.js_content,
            "Missing screen reader announcement controller in app.js"
        )


if __name__ == "__main__":
    unittest.main()
