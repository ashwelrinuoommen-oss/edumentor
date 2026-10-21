"""
Dependency and prerequisite relationship extraction service.
"""

from typing import List, Tuple, Dict, Any


def extract_dependencies(concepts: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """
    Extract and validate (prerequisite, concept) pairs from extracted concepts list.
    Ensures prerequisite targets exist, prevents self-loops, resolves title-to-ID mappings,
    and deduplicates relationships.
    """
    if not concepts:
        return []

    valid_ids = {c["id"] for c in concepts if "id" in c}
    title_to_id = {c["title"].strip().lower(): c["id"] for c in concepts if "title" in c and "id" in c}

    deps: List[Tuple[str, str]] = []
    seen = set()

    for c in concepts:
        cid = c.get("id")
        if not cid:
            continue

        raw_prereqs = c.get("prerequisites", []) or []
        for p in raw_prereqs:
            target_p = None
            if p in valid_ids:
                target_p = p
            elif isinstance(p, str) and p.strip().lower() in title_to_id:
                target_p = title_to_id[p.strip().lower()]

            if target_p and target_p != cid:
                pair = (target_p, cid)
                if pair not in seen:
                    seen.add(pair)
                    deps.append(pair)

    return deps
