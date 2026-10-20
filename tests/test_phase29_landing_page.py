"""
Unit and Integration Tests for Phase 29 — Product Preview / Landing Page.

Validates:
1. Complete 8-section homepage structure:
   - Navigation
   - Hero
   - Product Preview
   - How It Works
   - Adaptive Learning
   - Trust / Outcomes
   - Final CTA
   - Footer
2. The exact headline:
   "Turn Your Notes Into a Path From Concept to Recall to Mastery"
3. The exact CTAs:
   - "Start Learning Free"
   - "See How It Works"
4. Visual design compliance with the 7-color palette:
   #050608, #0D1117, #25D8E8, #8B5CF6, #F5F7FA, #9AA4B2, #27303B.
5. CSS classes and responsive rules for landing elements in style.css.
6. JavaScript state management showing landing page when unauthenticated.
"""

import os
import unittest


class TestPhase29LandingPage(unittest.TestCase):
    """Test suite ensuring Phase 29 Landing Page specifications."""

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

    def test_all_eight_homepage_sections_exist(self):
        """Verify all 8 design document sections are present in index.html."""
        # 1. Navigation
        self.assertTrue(
            "landing-nav" in self.html_content or "landingNav" in self.html_content or "nav class" in self.html_content,
            "Missing Navigation section in landing page"
        )
        # 2. Hero
        self.assertTrue(
            "landing-hero" in self.html_content or "landingHero" in self.html_content,
            "Missing Hero section in landing page"
        )
        # 3. Product Preview
        self.assertTrue(
            "product-preview" in self.html_content or "productPreview" in self.html_content,
            "Missing Product Preview section in landing page"
        )
        # 4. How It Works
        self.assertTrue(
            "how-it-works" in self.html_content or "howItWorks" in self.html_content,
            "Missing How It Works section in landing page"
        )
        # 5. Adaptive Learning
        self.assertTrue(
            "adaptive-learning" in self.html_content or "adaptiveLearning" in self.html_content,
            "Missing Adaptive Learning section in landing page"
        )
        # 6. Trust / Outcomes
        self.assertTrue(
            "trust-outcomes" in self.html_content or "trustOutcomes" in self.html_content or "trust" in self.html_content,
            "Missing Trust / Outcomes section in landing page"
        )
        # 7. Final CTA
        self.assertTrue(
            "final-cta" in self.html_content or "finalCta" in self.html_content,
            "Missing Final CTA section in landing page"
        )
        # 8. Footer
        self.assertTrue(
            "landing-footer" in self.html_content or "<footer" in self.html_content,
            "Missing Footer section in landing page"
        )

    def test_exact_headline_content(self):
        """Verify the exact headline: 'Turn Your Notes Into a Path From Concept to Recall to Mastery'."""
        self.assertIn(
            "Turn Your Notes Into a Path From Concept to Recall to Mastery",
            self.html_content,
            "Exact headline missing from index.html"
        )

    def test_exact_cta_texts(self):
        """Verify the presence of 'Start Learning Free' and 'See How It Works'."""
        self.assertIn("Start Learning Free", self.html_content, "Missing 'Start Learning Free' CTA")
        self.assertIn("See How It Works", self.html_content, "Missing 'See How It Works' CTA")

    def test_css_classes_exist_for_landing_page(self):
        """Verify CSS classes for Phase 29 exist in style.css."""
        for cls_name in [
            ".landing-stage",
            ".landing-nav",
            ".landing-hero",
            ".hero-art-ribbons",
            ".product-preview-section",
            ".how-it-works-section",
            ".adaptive-learning-section",
            ".trust-outcomes-section",
            ".final-cta-section",
            ".landing-footer"
        ]:
            self.assertIn(cls_name, self.css_content, f"Missing CSS rule {cls_name} in style.css")

    def test_palette_token_usage_in_landing_css(self):
        """Verify palette colors #050608, #0D1117, #25D8E8, #8B5CF6, #27303B in style.css."""
        self.assertIn("#050608", self.css_content)
        self.assertIn("#0D1117", self.css_content)
        self.assertIn("#25D8E8", self.css_content)
        self.assertIn("#8B5CF6", self.css_content)
        self.assertIn("#27303B", self.css_content)

    def test_javascript_landing_integration(self):
        """Verify app.js manages landing stage display and transitions."""
        self.assertIn("landingStage", self.js_content)
        self.assertIn("showLandingStage", self.js_content)


if __name__ == "__main__":
    unittest.main()
