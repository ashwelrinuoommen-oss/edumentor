"""
Document ingestion and concept/dependency extraction engine.
Supports PDF extraction via pdfplumber, plain text notes, and LLM-driven structured extraction.
"""

import io
import os
import re
import json
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from typing import Dict, List, Tuple, Any, Optional
from edumentor.llm import call_llm, call_llm_json, LLMConfig


class SimpleHTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
        self.in_script = False
        self.in_style = False
        self.in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t in ("script", "noscript"):
            self.in_script = True
        elif t == "style":
            self.in_style = True
        elif t == "title":
            self.in_title = True
        elif t in ("p", "h1", "h2", "h3", "h4", "li", "div", "br", "tr"):
            self.fed.append("\n")

    def handle_endtag(self, tag):
        t = tag.lower()
        if t in ("script", "noscript"):
            self.in_script = False
        elif t == "style":
            self.in_style = False
        elif t == "title":
            self.in_title = False
        elif t in ("p", "h1", "h2", "h3", "h4", "li", "div", "tr"):
            self.fed.append("\n")

    def handle_data(self, data):
        if self.in_script or self.in_style:
            return
        if self.in_title:
            self.title += data.strip() + " "
        else:
            self.fed.append(data)

    def get_data(self) -> Tuple[str, str]:
        raw = "".join(self.fed)
        clean = re.sub(r"[ \t]+", " ", raw)
        clean = re.sub(r"\n\s*\n", "\n\n", clean).strip()
        title = self.title.strip() or "Web Notes"
        return title, clean


import html


def extract_text_from_url(url: str, timeout: int = 20) -> Tuple[str, str]:
    """
    Fetch and extract clean readable text and page title from a web URL.
    Returns (page_title, text_content).
    Raises ValueError on network or parse failures.
    """
    clean_url = url.strip()
    if not clean_url:
        raise ValueError("URL cannot be empty.")
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url

    try:
        req = urllib.request.Request(
            clean_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,text/plain"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("content-type", "").lower()
            charset = "utf-8"
            if "charset=" in content_type:
                charset = content_type.split("charset=")[-1].split(";")[0].strip().strip("\"'")
            raw_bytes = resp.read()
            try:
                html_text = raw_bytes.decode(charset, errors="replace")
            except Exception:
                html_text = raw_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        raise ValueError(f"Failed to fetch content from URL '{clean_url}': {str(e)}")

    parser = SimpleHTMLTextExtractor()
    parser.feed(html_text)
    title, text = parser.get_data()
    title = html.unescape(title).strip() or "Web Article Notes"
    text = html.unescape(text).strip()

    if not text:
        raise ValueError("Could not extract readable text from the provided webpage.")

    return title, text


def extract_text_from_pdf(file_bytes_or_path: Any) -> str:
    """Extract full clean text from a PDF file using pdfplumber."""
    import pdfplumber
    from edumentor.utils.error_handler import ERROR_UPLOAD_MSG, EduMentorUploadError

    text_parts = []
    try:
        if isinstance(file_bytes_or_path, (str, bytes, io.BytesIO)):
            fp = io.BytesIO(file_bytes_or_path) if isinstance(file_bytes_or_path, bytes) else file_bytes_or_path
            with pdfplumber.open(fp) as pdf:
                for page_idx, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text.strip())
    except Exception as exc:
        raise EduMentorUploadError(ERROR_UPLOAD_MSG) from exc

    return "\n\n".join(text_parts)


async def async_extract_text_from_pdf(file_bytes_or_path: Any) -> str:
    """Extract full clean text from a PDF file asynchronously offloading I/O to a worker thread."""
    import asyncio
    return await asyncio.to_thread(extract_text_from_pdf, file_bytes_or_path)


async def async_extract_concepts_from_text(*args, **kwargs) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]:
    """Asynchronously extract atomic concepts and dependencies from notes text."""
    import asyncio
    return await asyncio.to_thread(extract_concepts_from_text, *args, **kwargs)


def extract_concepts_from_text(
    raw_text: str,
    doc_title: str = "Uploaded Notes",
    llm_config: Optional[LLMConfig] = None,
    curriculum_title: Optional[str] = None,
    **kwargs
) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]:
    """
    Extract atomic concepts and prerequisite dependencies from raw text using LLM.
    Returns (concepts_list, dependencies_list).
    """
    doc_title = curriculum_title or doc_title
    clean_text = raw_text.strip()
    if len(clean_text) < 50:
        return [], []

    # Truncate to reasonable context window if exceptionally long
    truncated_text = clean_text[:12000]

    prompt = f"""
You are an expert cognitive curriculum designer.
Analyze the following student study notes and extract the core atomic concepts and their prerequisite learning dependencies.

[DOCUMENT TITLE]: {doc_title}

[STUDENT NOTES CONTENT]:
\"\"\"{truncated_text}\"\"\"

Instructions:
1. Identify 3 to 8 distinct, atomic concepts present in these notes.
2. For each concept, provide:
   - `id`: a short snake_case identifier (e.g. "virtual_memory", "paging")
   - `title`: concise human-readable concept title
   - `summary`: 1-sentence high-level summary
   - `canonical_explanation`: a clear, authoritative explanation (2-4 sentences) defining the core mechanics
   - `key_points`: a list of 3-4 essential criteria/principles required for a student to truly understand it
   - `prompt_question`: an active recall question testing the concept without giving away the answer
   - `prerequisites`: a list of concept `id`s from THIS extracted set that must be learned BEFORE this concept
3. Ensure prerequisite dependencies form a Directed Acyclic Graph (avoid circular dependencies).

Respond in valid JSON format matching this schema:
{{
  "concepts": [
    {{
      "id": "concept_a",
      "title": "Concept A Title",
      "summary": "Brief summary",
      "canonical_explanation": "Detailed explanation",
      "key_points": ["Principle 1", "Principle 2", "Principle 3"],
      "prompt_question": "Explain Concept A in your own words, focusing on its core mechanisms.",
      "prerequisites": []
    }},
    {{
      "id": "concept_b",
      "title": "Concept B Title",
      "summary": "Brief summary",
      "canonical_explanation": "Detailed explanation",
      "key_points": ["Principle 1", "Principle 2"],
      "prompt_question": "How does Concept B operate, and how does it rely on Concept A?",
      "prerequisites": ["concept_a"]
    }}
  ]
}}
"""

    # In demo/offline mode, parse genuine concepts directly from student notes using the heuristic engine
    if not llm_config or getattr(llm_config, "provider", "demo") == "demo":
        return _heuristic_concept_extractor(clean_text, doc_title)

    from edumentor.ai.fallback_pipeline import execute_ai_pipeline
    from edumentor.ai.schemas import ConceptExtractionSchema
    from edumentor.llm import call_llm

    def _fallback_extractor():
        return _heuristic_concept_extractor(clean_text, doc_title)

    pipeline_res = execute_ai_pipeline(
        operation_name="concept_extraction",
        llm_callable=lambda attempt, prev_err: call_llm(
            prompt if attempt == 1 else f"{prompt}\n\nIMPORTANT: Previous attempt failed validation: {prev_err}. Output valid JSON with 'concepts' list matching schema only.",
            system_prompt="You are an expert curriculum designer. Always output strict JSON.",
            config=llm_config
        ),
        schema=ConceptExtractionSchema,
        max_retries=2,
        fallback_fn=_fallback_extractor
    )

    if pipeline_res.fallback_used and isinstance(pipeline_res.data, tuple):
        return pipeline_res.data

    if pipeline_res.success and isinstance(pipeline_res.data, dict) and "concepts" in pipeline_res.data:
        concepts_raw = pipeline_res.data.get("concepts", [])
    else:
        return _heuristic_concept_extractor(clean_text, doc_title)

    extracted_concepts: List[Dict[str, Any]] = []
    dependencies: List[Tuple[str, str]] = []
    seen_ids = set()

    for i, c in enumerate(concepts_raw):
        cid = c.get("id") or f"concept_{i+1}"
        cid = re.sub(r"[^a-zA-Z0-9_]", "_", str(cid).lower())
        if cid in seen_ids:
            cid = f"{cid}_{i+1}"
        seen_ids.add(cid)

        title = c.get("title", f"Concept {i+1}").strip()
        summary = c.get("summary", "").strip()
        explanation = c.get("canonical_explanation", summary).strip()
        key_points = c.get("key_points", [])
        if isinstance(key_points, str):
            key_points = [k.strip() for k in key_points.split("\n") if k.strip()]

        # Collect relevant note chunks from student notes
        note_chunks = c.get("note_chunks", [])
        if not note_chunks:
            matched_paras = [p.strip() for p in clean_text.split("\n\n") if title.lower() in p.lower() and len(p.strip()) > 30]
            if matched_paras:
                note_chunks = matched_paras[:3]
            else:
                note_chunks = [explanation] if explanation else [summary]

        extracted_concepts.append({
            "id": cid,
            "title": title,
            "summary": summary,
            "canonical_explanation": explanation,
            "key_points": key_points,
            "prompt_question": prompt_q,
            "note_chunks": note_chunks
        })

        for prereq in c.get("prerequisites", []):
            clean_prereq = re.sub(r"[^a-zA-Z0-9_]", "_", str(prereq).lower())
            dependencies.append((clean_prereq, cid))

    # Filter dependencies so only valid concept IDs exist
    valid_deps = [(p, c) for p, c in dependencies if p in seen_ids and c in seen_ids and p != c]

    return extracted_concepts, valid_deps



def clean_doc_title(title: str) -> str:
    """Clean filename noise like .pdf, ktunotes.in, etc."""
    cleaned = re.sub(r"\.(pdf|txt|md)$", "", title, flags=re.IGNORECASE)
    cleaned = re.sub(r"[\._\-]*(?:ktunotes(?:\.in)?|notes|slides|lecture)[\._\-]*", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[\s_]+", " ", cleaned).strip()
    return cleaned or title


def _clean_watermark_lines(text: str) -> str:
    """Filter out web scrapers, university watermarks, and page counter lines."""
    lines = []
    wm = re.compile(
        r"(ktunotes(?:\.in)?|downloaded from|www\.\w+|https?://|page\s+\d+\s*(?:of\s*\d+)?$|all rights reserved)",
        re.IGNORECASE
    )
    for line in text.splitlines():
        s = line.strip()
        if wm.search(s) and len(s) < 80:
            continue
        lines.append(line)
    return "\n".join(lines)


def _extract_heuristic_title(lines: List[str], doc_title: str, idx: int) -> Tuple[str, List[str]]:
    """Extracts a clean, human-readable concept title from section lines."""
    non_empty = [l.strip() for l in lines if l.strip()]
    if not non_empty:
        return f"{doc_title} - Concept {idx+1}", []

    # 1. Look for explicit header markers in first 4 lines
    for i, line in enumerate(non_empty[:4]):
        m = re.match(
            r"^(?:#{1,4}\s*|[0-9]+(?:\.[0-9]+)*[\.\:\-\s]+|module\s+[0-9]+\s*[\:\-\s]*|unit\s+[0-9]+\s*[\:\-\s]*)(.+)$",
            line,
            re.IGNORECASE
        )
        if m:
            cand = m.group(1).strip().strip(":#*- ")
            if 3 <= len(cand) <= 75 and not cand.endswith("."):
                return cand, non_empty[i+1:]

    # 2. Look for title-like line in first 4 lines (UPPERCASE or Title Case, length 4 to 75, no period)
    for i, line in enumerate(non_empty[:4]):
        cand = re.sub(r"^[\*\-•#\s]+", "", line).strip().strip(":#*- ")
        if 3 <= len(cand) <= 75 and not cand.endswith("."):
            if cand.isupper() or any(w.istitle() for w in cand.split()) or ":" in cand:
                if ":" in cand and len(cand) > 35:
                    cand = cand.split(":")[0].strip()
                return cand, non_empty[i+1:]

    # 3. Look for split before punctuation on first line
    first = non_empty[0]
    split_parts = re.split(r"[:\-\–—\(\.]", first)
    if split_parts and 4 <= len(split_parts[0].strip()) <= 55:
        return split_parts[0].strip(), non_empty[1:]

    # 4. Truncate first line cleanly at word boundary
    words = first.split()
    cand = " ".join(words[:6]).strip().rstrip(".,;:")
    if 4 <= len(cand) <= 55:
        return cand, non_empty[1:]

    return f"{doc_title} - Part {idx+1}", non_empty[1:]


def _extract_heuristic_points(lines: List[str], title: str) -> Tuple[str, str, List[str]]:
    """Extracts summary, canonical explanation, and key points from section content."""
    bullets = []
    paragraphs = []
    bullet_re = re.compile(r"^[\*\-•\–]\s*|^\d+[\.\)]\s*")

    for l in lines:
        s = l.strip()
        if not s:
            continue
        if bullet_re.match(s):
            clean_b = bullet_re.sub("", s).strip()
            if clean_b and len(clean_b) > 8:
                bullets.append(clean_b)
        else:
            paragraphs.append(s)

    summary_text = " ".join(paragraphs[:2]) if paragraphs else (bullets[0] if bullets else title)
    summary = summary_text[:140] + ("..." if len(summary_text) > 140 else "")
    canonical = "\n\n".join(paragraphs[:3]) if paragraphs else "\n".join(bullets[:4])

    key_points = bullets[:4]
    if len(key_points) < 2:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", " ".join(paragraphs)) if len(s.strip()) > 15]
        key_points = sentences[:3]
    if not key_points:
        key_points = [
            f"Core principle: {title}",
            "Key operational mechanisms and definition",
            "Applications and structural relationships"
        ]

    return summary, canonical, key_points


def _heuristic_concept_extractor(text: str, doc_title: str) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]:
    """
    Intelligent heuristic fallback: splits text into sections by headings, paragraphs,
    or bullet groups and constructs an ordered learning sequence with realistic concepts.
    """
    clean_title = clean_doc_title(doc_title)
    cleaned_text = _clean_watermark_lines(text)

    # Look for markdown, numbered, colon-delimited, module/unit, or uppercase headings
    sections = re.split(
        r"\n(?=#{1,3}\s+|[0-9]+[\.\)]\s+|module\s+[0-9]+|unit\s+[0-9]+|[A-Z][A-Za-z0-9\s]{2,40}:|\n[A-Z\s]{4,45}\n)",
        cleaned_text,
        flags=re.IGNORECASE
    )
    sections = [s.strip() for s in sections if len(s.strip()) > 30]

    if len(sections) < 2:
        # Split by double newline paragraphs
        sections = [s.strip() for s in cleaned_text.split("\n\n") if len(s.strip()) > 50]

    # Limit to top 6 concepts for optimal pedagogical pacing
    sections = sections[:6]

    concepts = []
    dependencies = []
    prev_id = None

    for i, sec in enumerate(sections):
        lines = [l.strip() for l in sec.split("\n") if l.strip()]
        title, rem_lines = _extract_heuristic_title(lines, clean_title, i)
        summary, canonical, key_pts = _extract_heuristic_points(rem_lines, title)

        cid = f"node_{re.sub(r'[^a-zA-Z0-9_]', '_', title.lower())[:20]}_{i+1}"

        concepts.append({
            "id": cid,
            "title": title,
            "summary": summary,
            "canonical_explanation": canonical[:600],
            "key_points": key_pts,
            "prompt_question": f"In your own words, what is {title} and what are its key requirements and principles?",
            "note_chunks": [sec]
        })

        if prev_id:
            dependencies.append((prev_id, cid))
        prev_id = cid

    return concepts, dependencies
