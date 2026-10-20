"""
Dependency and prerequisite relationship extraction service.
"""

from typing import List, Tuple, Dict, Any


def extract_dependencies(concepts: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """Extract (prerequisite, concept) pairs from extracted concepts list."""
    deps = []
    for c in concepts:
        cid = c["id"]
        for p in c.get("prerequisites", []) or []:
            deps.append((p, cid))
    return deps
