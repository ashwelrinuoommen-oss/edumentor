"""
Avatar Expression Manager for EduMentor.
Centralized service mapping pedagogical conversation states & message types
to the user-provided AI teacher PNG avatar expressions.
Handles fallback safety, base64 encoding, responsive path resolution, and asset verification.
"""

import os
import json
import base64
import logging
from functools import lru_cache
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Base asset search locations
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CONFIG_PATH = os.path.join(_ROOT_DIR, "config", "teacher_expressions.json")
_ASSET_DIRS = [
    os.path.join(_ROOT_DIR, "assets", "teacher_avatar"),
    os.path.join(_ROOT_DIR, "edumentor", "assets", "teacher_avatar"),
    os.path.join(_ROOT_DIR, "static", "assets", "teacher_avatar"),
]

# Default expression mapping if config file is absent
_DEFAULT_MAPPING = {
    "idle": "teacher_idle.png",
    "greeting": "teacher_greeting.png",
    "hello": "teacher_greeting.png",
    "welcome": "teacher_greeting.png",
    "thinking": "teacher_thinking.png",
    "processing": "teacher_thinking.png",
    "explaining": "teacher_explaining.png",
    "speaking": "teacher_explaining.png",
    "concept": "teacher_explaining.png",
    "listening": "teacher_listening.png",
    "waiting": "teacher_listening.png",
    "studying": "teacher_listening.png",
    "revise": "teacher_listening.png",
    "encouraging": "teacher_encouraging.png",
    "idea": "teacher_encouraging.png",
    "great_idea": "teacher_encouraging.png",
    "correct": "teacher_happy.png",
    "happy": "teacher_happy.png",
    "almost_correct": "teacher_almost_correct.png",
    "almost": "teacher_almost_correct.png",
    "wrong_supportive": "teacher_supportive.png",
    "supportive": "teacher_supportive.png",
    "wrong": "teacher_supportive.png",
    "confused": "teacher_supportive.png",
    "mastered": "teacher_celebration.png",
    "celebration": "teacher_celebration.png",
    "celebrating": "teacher_celebration.png",
    "reminder": "teacher_reminder.png",
    "break": "teacher_reminder.png",
    "complete": "teacher_celebration.png",
    "completed": "teacher_celebration.png",
    "default_fallback": "teacher_idle.png",
}


class AvatarExpressionManager:
    """
    Centralized controller managing AI teacher avatar emotional expressions.
    Guarantees state-based expression synchronization and robust fallback behavior.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or _CONFIG_PATH
        self.mapping = self._load_mapping()
        self.fallback_filename = self.mapping.get("default_fallback", "teacher_idle.png")

    def _load_mapping(self) -> Dict[str, str]:
        """Load JSON mapping with fallback to default dictionary."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        merged = dict(_DEFAULT_MAPPING)
                        merged.update(data)
                        return merged
            except Exception as e:
                logger.warning(f"Could not parse teacher_expressions.json: {e}")
        return dict(_DEFAULT_MAPPING)

    def resolve_filename(self, state_or_message_type: str) -> str:
        """
        Normalize input and return the corresponding PNG filename.
        Never returns empty; falls back gracefully.
        """
        if not state_or_message_type:
            return self.fallback_filename

        clean = str(state_or_message_type).lower().strip().replace(" ", "_")
        # Direct lookup
        if clean in self.mapping:
            return self.mapping[clean]

        # Aliases & common synonyms
        alias_map = {
            "hello": "teacher_greeting.png",
            "welcome": "teacher_greeting.png",
            "asking": "teacher_greeting.png",
            "evaluating": "teacher_thinking.png",
            "idea": "teacher_encouraging.png",
            "great_idea": "teacher_encouraging.png",
            "revise": "teacher_reminder.png",
            "break": "teacher_reminder.png",
            "confused": "teacher_supportive.png",
            "not_quite": "teacher_supportive.png",
            "speaking": "teacher_explaining.png",
        }
        if clean in alias_map:
            return alias_map[clean]

        return self.fallback_filename

    def get_expression(self, state_or_message_type: str) -> str:
        """Return the PNG asset filename for the specified state or message type."""
        return self.resolve_filename(state_or_message_type)

    def get_expression_path(self, state_or_message_type: str) -> str:
        """
        Return the absolute file system path to the PNG expression asset.
        Checks multiple candidate asset directories.
        """
        filename = self.resolve_filename(state_or_message_type)
        for asset_dir in _ASSET_DIRS:
            candidate = os.path.join(asset_dir, filename)
            if os.path.exists(candidate):
                return candidate

        # Fallback file path
        for asset_dir in _ASSET_DIRS:
            candidate = os.path.join(asset_dir, self.fallback_filename)
            if os.path.exists(candidate):
                logger.warning(
                    f"Expression '{state_or_message_type}' resolved to '{filename}' but file not found. Using fallback '{self.fallback_filename}'"
                )
                return candidate

        # Fallback to greeting if idle missing
        for asset_dir in _ASSET_DIRS:
            candidate = os.path.join(asset_dir, "teacher_greeting.png")
            if os.path.exists(candidate):
                return candidate

        return ""

    @lru_cache(maxsize=64)
    def get_expression_base64(self, state_or_message_type: str) -> str:
        """
        Return the base64-encoded PNG data for embedding directly in HTML / SVG.
        Cached in-memory for instant rendering performance.
        """
        path = self.get_expression_path(state_or_message_type)
        if path and os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception as e:
                logger.error(f"Error reading avatar asset {path}: {e}")
        return ""

    def get_expression_url(self, state_or_message_type: str) -> str:
        """Return web-accessible URL path for client-side rendering."""
        filename = self.resolve_filename(state_or_message_type)
        return f"/assets/teacher_avatar/{filename}"


# Global singleton instance for app-wide use
avatar_expression_manager = AvatarExpressionManager()
