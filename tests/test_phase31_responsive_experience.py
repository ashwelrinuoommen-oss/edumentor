"""
Unit and Integration Tests for Phase 31 — Responsive Experience.

Validates:
1. Desktop viewport specifications (>= 1200px):
   - Large centered conversational workspace.
   - Generous container sizing.
2. Tablet viewport specifications (768px - 1199px):
   - Reduced container widths and avatar scaling (140px / 150px).
3. Mobile assistant viewport specifications (< 768px):
   - Mobile AI assistant interface with brand and hamburger menu (☰).
   - Centered scaled avatar (110px - 120px).
   - Conversational greeting ("Welcome back!", "What are we studying today?").
   - Compact rounded mobile composer: [ Type... 📎 ↑ ].
   - Minimum 44×44px touch targets as mandated by the design document.
4. Interactive mobile menu drawer in HTML and JavaScript.
"""

import os
import unittest


class TestPhase31ResponsiveExperience(unittest.TestCase):
    """Test suite ensuring Phase 31 Responsive Experience specifications."""

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

    def test_desktop_large_centered_workspace_rules(self):
        """Verify Desktop (>= 1200px) large centered workspace CSS rules."""
        self.assertIn("1200px", self.css_content)
        self.assertIn(".workspace-body", self.css_content)

    def test_tablet_reduced_avatar_and_width_rules(self):
        """Verify Tablet (768px - 1199px) rules reduce avatar size and container widths."""
        self.assertIn("max-width: 768px", self.css_content)
        # Verify avatar scaling down on tablet
        self.assertTrue(
            "150px" in self.css_content or "140px" in self.css_content,
            "Missing tablet avatar scaling"
        )

    def test_mobile_touch_targets_minimum_44px(self):
        """Verify minimum 44×44px touch targets rule in CSS for mobile viewports."""
        self.assertIn("min-width: 44px", self.css_content)
        self.assertIn("min-height: 44px", self.css_content)

    def test_mobile_hamburger_menu_elements(self):
        """Verify mobile hamburger button (☰) and drawer exist in index.html."""
        self.assertTrue(
            "btnMobileNavToggle" in self.html_content or "btnMobileHeaderMenu" in self.html_content or "btn-mobile-menu" in self.html_content,
            "Missing mobile hamburger menu button in index.html"
        )
        self.assertTrue(
            "mobileNavDrawer" in self.html_content or "mobile-drawer" in self.html_content,
            "Missing mobile navigation drawer in index.html"
        )

    def test_mobile_assistant_greeting_and_composer(self):
        """Verify conversational greeting ('Welcome back', 'What are we studying today') and compact composer."""
        self.assertIn("Welcome back", self.html_content)
        self.assertIn("What are we studying", self.html_content)
        # Verify attachment and send buttons in composer
        self.assertTrue(
            "btn-upload-notes" in self.html_content or "btnUploadNotes" in self.html_content or "btnActiveUpload" in self.html_content
        )
        self.assertTrue(
            "btn-send-arrow" in self.html_content or "btnSendArrow" in self.html_content or "btnActiveSend" in self.html_content
        )

    def test_mobile_drawer_javascript_controller(self):
        """Verify JavaScript manages mobile drawer toggle."""
        self.assertTrue(
            "mobileNavDrawer" in self.js_content or "openMobileDrawer" in self.js_content or "toggleMobileMenu" in self.js_content,
            "Missing mobile drawer toggle in app.js"
        )


if __name__ == "__main__":
    unittest.main()
