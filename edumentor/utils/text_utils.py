"""
Text processing and normalization utilities.
"""

import re
from typing import List, Set


def clean_text(text: str) -> str:
    """Normalize whitespace and strip unprintable characters."""
    if not text:
        return ""
    cleaned = re.sub(r"[ \t]+", " ", text)
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)
    return cleaned.strip()


def extract_keywords(text: str, min_len: int = 4) -> Set[str]:
    """Extract unique lowercase keywords for heuristic matching."""
    words = re.findall(r"\b[a-zA-Z]{" + str(min_len) + r",}\b", text.lower())
    stopwords = {"this", "that", "with", "from", "have", "more", "also", "when", "then", "into", "some"}
    return set(w for w in words if w not in stopwords)


def clean_html_for_markdown(html_str: str) -> str:
    """
    Strips leading and trailing whitespace from each line and eliminates empty lines.
    This guarantees that markdown parsers (like markdown-it used in Streamlit)
    never interpret indented HTML or lines following empty lines as indented code blocks (<pre><code>).
    """
    if not html_str:
        return ""
    lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    return "\n".join(lines)
