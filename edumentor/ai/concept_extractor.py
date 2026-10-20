"""
Concept extraction AI service.
"""

from typing import Dict, List, Any, Optional
from edumentor.ai.llm_client import LLMConfig
from edumentor.extractor import extract_concepts_from_text


def extract_concepts(raw_text: str, curriculum_title: str = "Notes", llm_config: Optional[LLMConfig] = None) -> List[Dict[str, Any]]:
    """Extract atomic concepts from study material."""
    result = extract_concepts_from_text(raw_text, curriculum_title=curriculum_title, llm_config=llm_config)
    if isinstance(result, tuple):
        return result[0]
    elif isinstance(result, dict):
        return result.get("concepts", [])
    return []

