"""
Phase 42 — MVP Scope Boundaries & Deferred Features Governance Test Suite

Validates that all 9 features specified by Phase 42 are strictly kept OUT of the MVP:
1. Voice input
2. Handwritten OCR
3. Math solving
4. Programming/code evaluation
5. Live video teacher
6. Multiplayer learning
7. Social features
8. Complex gamification
9. Leaderboards

These can come later.
"""

import unittest
from fastapi.testclient import TestClient

from server import app
from edumentor.scope import (
    DEFERRED_MVP_FEATURES,
    MVP_CORE_FEATURES,
    FeatureDeferredError,
    is_feature_enabled,
    get_deferred_features,
    get_deferred_feature_keys,
    get_deferred_feature_names,
    get_mvp_manifest
)


class TestPhase42MVPFeaturesScope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # -------------------------------------------------------------------------
    # TEST 1: CATALOG OF 9 DEFERRED FEATURES
    # -------------------------------------------------------------------------
    def test_all_nine_features_explicitly_cataloged_as_deferred(self):
        """Verify the exact 9 features specified by Phase 42 are recorded as deferred."""
        expected_names = [
            "Voice input",
            "Handwritten OCR",
            "Math solving",
            "Programming/code evaluation",
            "Live video teacher",
            "Multiplayer learning",
            "Social features",
            "Complex gamification",
            "Leaderboards"
        ]
        
        actual_names = get_deferred_feature_names()
        for name in expected_names:
            self.assertIn(name, actual_names, f"Expected '{name}' to be cataloged as deferred for post-MVP")

        self.assertEqual(len(DEFERRED_MVP_FEATURES), 9, "Phase 42 catalog must contain exactly 9 deferred features")

    def test_deferred_features_attributes(self):
        """Verify every deferred feature has enabled=False, status='deferred_post_mvp', and reason."""
        for key, feat in DEFERRED_MVP_FEATURES.items():
            self.assertFalse(feat["enabled"], f"Deferred feature '{key}' must have enabled=False")
            self.assertEqual(feat["status"], "deferred_post_mvp", f"Feature '{key}' must be 'deferred_post_mvp'")
            self.assertEqual(feat["phase"], 42, f"Feature '{key}' must reference Phase 42")
            self.assertTrue(len(feat["reason"]) > 10, f"Feature '{key}' must provide an architectural reason")
            self.assertTrue(len(feat["mvp_alternative"]) > 5, f"Feature '{key}' must describe current MVP alternative")

    # -------------------------------------------------------------------------
    # TEST 2: FEATURE GATE ENFORCEMENT
    # -------------------------------------------------------------------------
    def test_is_feature_enabled_returns_false_for_all_deferred(self):
        """Verify is_feature_enabled returns False for all 9 deferred features across formatting styles."""
        keys = get_deferred_feature_keys()
        for k in keys:
            self.assertFalse(is_feature_enabled(k), f"Feature gate should return False for '{k}'")
            # Test hyphenated and title cases
            self.assertFalse(is_feature_enabled(k.replace("_", "-")))
            self.assertFalse(is_feature_enabled(k.replace("_", " ")))

    def test_is_feature_enabled_returns_true_for_mvp_core(self):
        """Verify is_feature_enabled returns True for actual active MVP features."""
        core_keys = ["chat_workspace", "pdf_markdown_ingestion", "concept_prerequisite_dag", "supermemo_sm2"]
        for ck in core_keys:
            self.assertTrue(is_feature_enabled(ck), f"Core MVP feature '{ck}' should be enabled")

    def test_feature_deferred_error_exception(self):
        """Verify FeatureDeferredError includes descriptive messaging."""
        exc = FeatureDeferredError("voice_input")
        self.assertEqual(exc.feature_key, "voice_input")
        self.assertIn("Voice input", exc.message)
        self.assertIn("deferred post-MVP", exc.message)

    # -------------------------------------------------------------------------
    # TEST 3: REST API ENDPOINTS FOR SCOPE AND FEATURE GOVERNANCE
    # -------------------------------------------------------------------------
    def test_api_scope_endpoint_returns_manifest(self):
        """Verify GET /api/scope returns complete manifesto with 9 deferred features."""
        res = self.client.get("/api/scope")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        manifest = data["manifest"]
        self.assertEqual(manifest["phase"], 42)
        self.assertEqual(manifest["deferred_feature_count"], 9)
        self.assertGreaterEqual(manifest["mvp_core_count"], 5)
        self.assertEqual(manifest["status"], "enforced")

    def test_api_features_deferred_endpoint(self):
        """Verify GET /api/features/deferred returns the 9 features."""
        res = self.client.get("/api/features/deferred")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["total_deferred"], 9)
        names = [f["name"] for f in data["deferred_features"]]
        self.assertIn("Leaderboards", names)
        self.assertIn("Voice input", names)
        self.assertIn("Live video teacher", names)

    def test_api_feature_status_query_deferred_returns_501(self):
        """Verify querying any of the 9 deferred features via API returns 501 Not Implemented."""
        for key in get_deferred_feature_keys():
            res = self.client.get(f"/api/features/{key}")
            self.assertEqual(
                res.status_code, 501,
                f"Deferred feature '{key}' must return HTTP 501 Not Implemented, got {res.status_code}"
            )
            body = res.json()
            self.assertEqual(body["status"], "deferred_post_mvp")
            self.assertFalse(body["enabled"])
            self.assertIn("post-MVP", body["message"])

    def test_api_feature_status_query_active_returns_200(self):
        """Verify querying active MVP core feature returns 200."""
        res = self.client.get("/api/features/chat_workspace")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["status"], "active_mvp")
        self.assertTrue(body["enabled"])

    def test_api_feature_status_query_unknown_returns_404(self):
        """Verify querying non-existent feature returns 404."""
        res = self.client.get("/api/features/telepathic_knowledge_download")
        self.assertEqual(res.status_code, 404)

    # -------------------------------------------------------------------------
    # TEST 4: VERIFY ABSENCE OF PREMATURE / POLLUTING DEFERRED ROUTES
    # -------------------------------------------------------------------------
    def test_no_premature_voice_routes(self):
        """Verify no premature voice recording API routes are exposed."""
        res = self.client.post("/api/voice/transcribe")
        self.assertIn(res.status_code, [404, 405])

    def test_no_premature_leaderboard_routes(self):
        """Verify no global competitive leaderboard API routes exist in MVP."""
        res = self.client.get("/api/leaderboards")
        self.assertIn(res.status_code, [404, 405])

    def test_no_premature_multiplayer_routes(self):
        """Verify no multiplayer or collaborative room routes exist in MVP."""
        res = self.client.get("/api/multiplayer/rooms")
        self.assertIn(res.status_code, [404, 405])

    def test_no_premature_social_feed_routes(self):
        """Verify no social feed or followers API routes exist in MVP."""
        res = self.client.get("/api/social/feed")
        self.assertIn(res.status_code, [404, 405])

    def test_no_premature_code_execution_routes(self):
        """Verify no programming code execution sandbox exists in MVP."""
        res = self.client.post("/api/code/execute")
        self.assertIn(res.status_code, [404, 405])


if __name__ == "__main__":
    unittest.main()
