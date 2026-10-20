"""
Phase 42 — MVP Scope Boundaries & Deferred Features Governance.

Defines the explicit boundary between the MVP Core Feature Set and
features intentionally kept OUT of the MVP for post-MVP releases.

Out of Scope / Deferred for MVP:
1. Voice input
2. Handwritten OCR
3. Math solving
4. Programming/code evaluation
5. Live video teacher
6. Multiplayer learning
7. Social features
8. Complex gamification
9. Leaderboards
"""

from typing import Dict, Any, List, Optional


# Exact list of 9 features excluded from MVP per Phase 42 specification
DEFERRED_MVP_FEATURES: Dict[str, Dict[str, Any]] = {
    "voice_input": {
        "key": "voice_input",
        "name": "Voice input",
        "category": "Audio & Speech",
        "status": "deferred_post_mvp",
        "enabled": False,
        "phase": 42,
        "reason": "Keep MVP focused on text-based active memory retrieval and deliberate thought formulation without audio distraction.",
        "mvp_alternative": "Text-based conversational chat composer with keyboard accessibility."
    },
    "handwritten_ocr": {
        "key": "handwritten_ocr",
        "name": "Handwritten OCR",
        "category": "Computer Vision",
        "status": "deferred_post_mvp",
        "enabled": False,
        "phase": 42,
        "reason": "MVP prioritizes clean digital PDF and Markdown note ingestion pipelines.",
        "mvp_alternative": "PDF lecture slides, book chapters, and Markdown text file uploads."
    },
    "math_solving": {
        "key": "math_solving",
        "name": "Math solving",
        "category": "Symbolic Computation",
        "status": "deferred_post_mvp",
        "enabled": False,
        "phase": 42,
        "reason": "MVP evaluates conceptual mastery and semantic understanding rather than symbolic computation engines.",
        "mvp_alternative": "Socratic conceptual questions evaluating core principles and mechanisms."
    },
    "programming_code_evaluation": {
        "key": "programming_code_evaluation",
        "name": "Programming/code evaluation",
        "category": "Code Execution Sandbox",
        "status": "deferred_post_mvp",
        "enabled": False,
        "phase": 42,
        "reason": "MVP evaluates architectural mental models and concept comprehension rather than executing test suites or syntax parsers.",
        "mvp_alternative": "Explaining concepts, algorithm intuition, and architectural trade-offs."
    },
    "live_video_teacher": {
        "key": "live_video_teacher",
        "name": "Live video teacher",
        "category": "Streaming Media",
        "status": "deferred_post_mvp",
        "enabled": False,
        "phase": 42,
        "reason": "MVP uses a fast, lightweight, and responsive SVG teacher avatar with glowing emotional state indicators.",
        "mvp_alternative": "SVG glowing avatar with 5 emotional states (neutral, encouraging, thinking, celebrating, compassionate)."
    },
    "multiplayer_learning": {
        "key": "multiplayer_learning",
        "name": "Multiplayer learning",
        "category": "Collaborative Sync",
        "status": "deferred_post_mvp",
        "enabled": False,
        "phase": 42,
        "reason": "EduMentor is intentionally structured as an intimate, distraction-free personal 1-on-1 AI companion.",
        "mvp_alternative": "Personalized 1-on-1 AI study companion workspace."
    },
    "social_features": {
        "key": "social_features",
        "name": "Social features",
        "category": "Social Network",
        "status": "deferred_post_mvp",
        "enabled": False,
        "phase": 42,
        "reason": "Eliminates social feed distractions, notification spam, and peer comparison anxiety to protect deep focus.",
        "mvp_alternative": "Private learning history, individual retention curve, and mastery analytics."
    },
    "complex_gamification": {
        "key": "complex_gamification",
        "name": "Complex gamification",
        "category": "Game Mechanics",
        "status": "deferred_post_mvp",
        "enabled": False,
        "phase": 42,
        "reason": "Design Doc Principle: Keep the interface calm and spacious, making progress feel intelligent rather than gamified (no loot boxes, coins, or arbitrary XP grind).",
        "mvp_alternative": "Mastery radar, retention percentages, SM-2 interval progress, and subtle progress rings."
    },
    "leaderboards": {
        "key": "leaderboards",
        "name": "Leaderboards",
        "category": "Competitive Ranking",
        "status": "deferred_post_mvp",
        "enabled": False,
        "phase": 42,
        "reason": "Active recall mastery is personal growth against one's own forgetting curve, not a competitive zero-sum ranking.",
        "mvp_alternative": "Personal mastery depth tiers (Tier 0 primitives → Tier 1 core → Tier 2 advanced)."
    }
}


# Core MVP Feature Manifesto
MVP_CORE_FEATURES: Dict[str, Dict[str, Any]] = {
    "chat_workspace": {
        "name": "Chat Workspace",
        "status": "active_mvp",
        "enabled": True,
        "description": "Unified conversational study workspace where talk, upload, study, and recall all happen."
    },
    "pdf_markdown_ingestion": {
        "name": "PDF & Markdown Ingestion",
        "status": "active_mvp",
        "enabled": True,
        "description": "Extract text, chunk notes, and isolate academic sections."
    },
    "concept_prerequisite_dag": {
        "name": "Concept Prerequisite DAG",
        "status": "active_mvp",
        "enabled": True,
        "description": "Directed Acyclic Graph generation with cycle resolution and topological sequencing."
    },
    "active_recall_generator": {
        "name": "Active Recall Question Generator",
        "status": "active_mvp",
        "enabled": True,
        "description": "Multi-tier difficulty questions testing generative memory."
    },
    "hybrid_two_pillar_evaluation": {
        "name": "Two-Pillar Hybrid Evaluation",
        "status": "active_mvp",
        "enabled": True,
        "description": "Semantic Vector Cosine Similarity (40%) + LLM-as-Judge Rubric (60%)."
    },
    "supermemo_sm2": {
        "name": "SuperMemo SM-2 Spaced Repetition",
        "status": "active_mvp",
        "enabled": True,
        "description": "Scientific review interval calculation with automatic resurfacing for weak concepts."
    },
    "svg_avatar": {
        "name": "Responsive SVG Teacher Avatar",
        "status": "active_mvp",
        "enabled": True,
        "description": "Dynamic visual avatar expressing five emotional states without heavy video streaming."
    },
    "privacy_first_architecture": {
        "name": "Privacy-First Architecture",
        "status": "active_mvp",
        "enabled": True,
        "description": "Scoped SQLite user access, input sanitization, and data purge rights."
    },
    "telemetry_funnel": {
        "name": "Product Events & Learning Funnel Telemetry",
        "status": "active_mvp",
        "enabled": True,
        "description": "Event logging for full student conversion journey (import -> recall -> mastery)."
    }
}


class FeatureDeferredError(Exception):
    """Raised when an attempt is made to access a deferred post-MVP feature."""
    def __init__(self, feature_key: str):
        feature_info = DEFERRED_MVP_FEATURES.get(feature_key, {
            "name": feature_key,
            "reason": "This feature is planned for a future post-MVP release."
        })
        self.feature_key = feature_key
        self.feature_name = feature_info.get("name", feature_key)
        self.reason = feature_info.get("reason", "This feature is excluded from the MVP.")
        self.message = f"Feature '{self.feature_name}' is deferred post-MVP. {self.reason}"
        super().__init__(self.message)


def is_feature_enabled(feature_key: str) -> bool:
    """
    Check if a given feature key is enabled in current MVP scope.
    Returns False for all 9 deferred features.
    """
    normalized_key = feature_key.strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")
    if normalized_key in DEFERRED_MVP_FEATURES:
        return False
    if normalized_key in MVP_CORE_FEATURES:
        return True
    return False


def get_deferred_features() -> List[Dict[str, Any]]:
    """Return all 9 features deferred post-MVP."""
    return list(DEFERRED_MVP_FEATURES.values())


def get_deferred_feature_keys() -> List[str]:
    """Return list of keys for the 9 deferred features."""
    return list(DEFERRED_MVP_FEATURES.keys())


def get_deferred_feature_names() -> List[str]:
    """Return human-readable names of the 9 deferred features."""
    return [f["name"] for f in DEFERRED_MVP_FEATURES.values()]


def get_mvp_manifest() -> Dict[str, Any]:
    """
    Return complete MVP scope manifest, explicitly separating active
    MVP capabilities from post-MVP deferred roadmap items.
    """
    return {
        "phase": 42,
        "phase_name": "MVP Scope Boundaries & Deferred Features Governance",
        "product": "EduMentor",
        "philosophy": "Concept → Recall → Mastery",
        "design_rule": "Keep interface calm, spacious, and focused on active recall rather than gamification or external distraction.",
        "mvp_core_count": len(MVP_CORE_FEATURES),
        "deferred_feature_count": len(DEFERRED_MVP_FEATURES),
        "mvp_core_features": MVP_CORE_FEATURES,
        "deferred_features": DEFERRED_MVP_FEATURES,
        "status": "enforced"
    }
