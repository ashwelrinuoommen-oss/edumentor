"""
Unit and Verification Tests for Phase 27 — Main Interface Visual Design.

Validates:
1. Exact 7-color palette from design specification:
   - Background: #050608
   - Surface:    #0D1117
   - Cyan:       #25D8E8
   - Violet:     #8B5CF6
   - Text:       #F5F7FA
   - Muted:      #9AA4B2
   - Border:     #27303B
2. Typography: Geist Sans and Inter.
3. Presence of Phase 26 Avatar stem tree connector and status pill classes in CSS.
"""

import os
import re
import unittest


class TestPhase27VisualDesignSystem(unittest.TestCase):
    """Test suite ensuring exact palette and typography compliance."""

    @classmethod
    def setUpClass(cls):
        cls.css_path = os.path.join(os.path.dirname(__file__), "..", "static", "css", "style.css")
        with open(cls.css_path, "r", encoding="utf-8") as f:
            cls.css_content = f.read()

        cls.html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

    def test_exact_seven_palette_colors_in_css_variables(self):
        """Verify the exact 7-color palette hex codes are defined in CSS variables."""
        required_palette = {
            "--bg-canvas": "#050608",
            "--bg-surface": "#0D1117",
            "--accent-cyan": "#25D8E8",
            "--accent-violet": "#8B5CF6",
            "--text-primary": "#F5F7FA",
            "--text-muted": "#9AA4B2",
            "--border-subtle": "#27303B"
        }
        for var_name, hex_code in required_palette.items():
            pattern = rf"{re.escape(var_name)}\s*:\s*{re.escape(hex_code)}"
            self.assertRegex(
                self.css_content,
                re.compile(pattern, re.IGNORECASE),
                f"Expected CSS variable {var_name} to be defined as {hex_code}"
            )

    def test_typography_includes_geist_and_inter(self):
        """Verify typography in style.css and index.html loads and applies Geist and Inter."""
        # Check CSS font imports and variables
        self.assertIn("Geist", self.css_content)
        self.assertIn("Inter", self.css_content)
        self.assertIn("--font-main", self.css_content)
        self.assertRegex(self.css_content, r"--font-main\s*:\s*['\"]Geist['\"],\s*['\"]Inter['\"]")

        # Check HTML font links
        self.assertIn("family=Geist", self.html_content)
        self.assertIn("family=Inter", self.html_content)

    def test_avatar_stem_connector_css_classes(self):
        """Verify Phase 26 avatar stem branch connector CSS rules exist."""
        required_classes = [
            ".avatar-stem-col",
            ".avatar-connector-stem",
            ".avatar-branch-curve",
            ".chat-row.status-notice",
            ".status-pill"
        ]
        for cls in required_classes:
            self.assertIn(cls, self.css_content, f"Missing required CSS class {cls}")

    def test_teacher_message_component_palette_consistency(self):
        """Verify Python teacher_message component reflects the exact design system colors."""
        comp_path = os.path.join(os.path.dirname(__file__), "..", "edumentor", "components", "teacher_message.py")
        with open(comp_path, "r", encoding="utf-8") as f:
            comp_content = f.read()

        for hex_code in ["#050608", "#0D1117", "#25D8E8", "#8B5CF6", "#F5F7FA", "#9AA4B2", "#27303B"]:
            self.assertIn(hex_code, comp_content, f"Component missing palette token {hex_code}")
        self.assertIn("Geist", comp_content)
        self.assertIn("Inter", comp_content)


if __name__ == "__main__":
    unittest.main()
