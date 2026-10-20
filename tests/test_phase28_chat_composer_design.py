"""
Unit and Integration Tests for Phase 28 — Chat Composer Design.

Validates:
1. Floating rounded container structure (border-radius: 20px, #0D1117, #27303B).
2. The exact default prompt placeholder: "Ask EduMentor anything about your learning".
3. Action elements:
   - "＋ Upload notes" button
   - "↑" Send button
4. Processing state:
   - 📄 Document header with filename
   - "Processing your notes..." status message
   - Progress bar with percentage readout (e.g. 82%)
5. Palette compliance: #050608, #0D1117, #25D8E8, #8B5CF6, #F5F7FA, #9AA4B2, #27303B.
6. CSS and Web client classes in style.css and index.html.
"""

import os
import re
import unittest
from edumentor.components.upload_zone import (
    render_floating_composer,
    render_composer_processing_card,
    get_composer_css,
    DEFAULT_COMPOSER_PLACEHOLDER
)


class TestPhase28ChatComposerDesign(unittest.TestCase):
    """Test suite ensuring Phase 28 Chat Composer specifications."""

    @classmethod
    def setUpClass(cls):
        cls.css_path = os.path.join(os.path.dirname(__file__), "..", "static", "css", "style.css")
        with open(cls.css_path, "r", encoding="utf-8") as f:
            cls.css_content = f.read()

        cls.html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

        cls.comp_path = os.path.join(os.path.dirname(__file__), "..", "edumentor", "components", "upload_zone.py")
        with open(cls.comp_path, "r", encoding="utf-8") as f:
            cls.comp_content = f.read()

    def test_default_prompt_placeholder(self):
        """Verify the exact prompt placeholder: 'Ask EduMentor anything about your learning'."""
        self.assertEqual(DEFAULT_COMPOSER_PLACEHOLDER, "Ask EduMentor anything about your learning")
        self.assertIn("Ask EduMentor anything about your learning", self.comp_content)

    def test_floating_rounded_container_specifications(self):
        """Verify floating rounded container with border-radius: 20px and palette tokens."""
        css = get_composer_css()
        self.assertIn("border-radius: 20px", css)
        self.assertIn("#0D1117", css)
        self.assertIn("#27303B", css)
        self.assertIn(".floating-composer", css)

    def test_composer_action_buttons(self):
        """Verify presence of '＋ Upload notes' and '↑' send button in component."""
        self.assertIn("Upload notes", self.comp_content)
        self.assertIn("＋", self.comp_content)
        self.assertIn("↑", self.comp_content)

    def test_composer_processing_card_structure(self):
        """Verify processing card renders 📄 filename, status text, and progress bar with 82%."""
        card_html = render_composer_processing_card(
            filename="Operating Systems Module 1.pdf",
            progress_pct=82,
            status_text="Processing your notes..."
        )
        self.assertIn("Operating Systems Module 1.pdf", card_html)
        self.assertIn("Processing your notes...", card_html)
        self.assertIn("82%", card_html)
        self.assertIn("📄", card_html)
        self.assertIn("linear-gradient", card_html)
        self.assertIn("#25D8E8", card_html)

    def test_web_style_css_phase28_classes(self):
        """Verify Phase 28 CSS rules exist in style.css for web client."""
        for cls_name in [
            ".floating-composer",
            ".btn-upload-notes",
            ".btn-send-arrow",
            ".composer-processing-card",
            ".composer-progress-fill"
        ]:
            self.assertIn(cls_name, self.css_content, f"Missing {cls_name} in style.css")

    def test_index_html_phase28_composer_elements(self):
        """Verify index.html contains Phase 28 floating composer and processing view."""
        self.assertIn("floating-composer", self.html_content)
        self.assertIn("Ask EduMentor anything about your learning", self.html_content)
        self.assertIn("btnUploadNotes", self.html_content)
        self.assertIn("btnSendArrow", self.html_content)
        self.assertIn("composerProcessingView", self.html_content)


if __name__ == "__main__":
    unittest.main()
