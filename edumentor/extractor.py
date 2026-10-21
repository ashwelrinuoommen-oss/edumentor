"""
Document ingestion, detailed hierarchical concept extraction, and dependency mapping engine for EduMentor.
Supports PDF extraction via pdfplumber with page tracking, plain text notes, and LLM-driven structured extraction.
Guarantees source-grounded topic segregation: Major Topics -> Detailed Subtopics -> Named Entities / Algorithms -> Definitions.
"""

import io
import os
import re
import json
import urllib.request
import urllib.parse
from html.parser import HTMLParser
import html
from typing import Dict, List, Tuple, Any, Optional

from edumentor.llm import call_llm, call_llm_json, LLMConfig
from edumentor.utils.error_handler import ERROR_UPLOAD_MSG, EduMentorUploadError


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


def extract_pdf_pages_and_text(file_bytes_or_path: Any) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extract text and structured page metadata from a PDF file using pdfplumber.
    Returns: (combined_clean_text, list_of_pages)
    Where list_of_pages is [{"page_number": int, "text": str, "char_count": int}].
    Detects scanned or image-only PDFs with no extractable text.
    """
    import pdfplumber

    pages_data: List[Dict[str, Any]] = []
    text_parts: List[str] = []
    total_chars = 0

    try:
        fp = io.BytesIO(file_bytes_or_path) if isinstance(file_bytes_or_path, bytes) else file_bytes_or_path
        with pdfplumber.open(fp) as pdf:
            if not pdf.pages:
                raise EduMentorUploadError("The uploaded PDF file contains no readable pages.")

            for page_idx, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                clean_page = _clean_watermark_lines(page_text).strip()
                if clean_page:
                    text_parts.append(clean_page)
                    total_chars += len(clean_page)
                pages_data.append({
                    "page_number": page_idx + 1,
                    "text": clean_page,
                    "char_count": len(clean_page)
                })

        # Scanned / Image-only PDF detection
        if total_chars < 30 and len(pages_data) >= 1:
            raise EduMentorUploadError(
                "This PDF appears to be scanned or contains image-only pages with no extractable text. "
                "EduMentor requires selectable digital text to analyze study concepts. "
                "Please upload a PDF with selectable text or copy-paste your lecture notes."
            )

    except EduMentorUploadError:
        raise
    except Exception as exc:
        raise EduMentorUploadError(ERROR_UPLOAD_MSG) from exc

    full_text = "\n\n".join(text_parts)
    return full_text, pages_data


def extract_text_from_pdf(file_bytes_or_path: Any) -> str:
    """Extract full clean text from a PDF file using pdfplumber."""
    full_text, _ = extract_pdf_pages_and_text(file_bytes_or_path)
    return full_text


async def async_extract_text_from_pdf(file_bytes_or_path: Any) -> str:
    """Extract full clean text from a PDF file asynchronously offloading I/O to a worker thread."""
    import asyncio
    return await asyncio.to_thread(extract_text_from_pdf, file_bytes_or_path)


async def async_extract_concepts_from_text(*args, **kwargs) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]:
    """Asynchronously extract atomic concepts and dependencies from notes text."""
    import asyncio
    return await asyncio.to_thread(extract_concepts_from_text, *args, **kwargs)


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


# -----------------------------------------------------------------------------
# KNOWN CS & TECHNICAL ALGORITHM & ENTITY SIGNATURES FOR ACCURATE EXTRACTION
# -----------------------------------------------------------------------------
KNOWN_TECHNICAL_TERMS = [
    # OS Scheduling
    "First-Come First-Served", "FCFS", "Shortest Job First", "SJF", "Round Robin",
    "Priority Scheduling", "Multilevel Queue Scheduling", "Multilevel Feedback Queue", "MLFQ",
    "Completely Fair Scheduler", "CFS",
    # OS Concurrency & Deadlocks
    "Critical Section", "Peterson's Algorithm", "Test-and-Set", "Compare-and-Swap",
    "Semaphores", "Mutex", "Monitors", "Dining Philosophers", "Producer-Consumer",
    "Banker's Algorithm", "Resource Allocation Graph", "Two-Phase Locking",
    # OS Memory Management
    "Paging", "Segmentation", "Page Table", "Inverted Page Table", "Translation Lookaside Buffer", "TLB",
    "First-In First-Out", "FIFO", "Least Recently Used", "LRU", "Optimal Page Replacement", "OPT",
    "Clock Algorithm", "Second-Chance Algorithm", "Least Frequently Used", "LFU", "Working Set Model",
    # Machine Learning & AI
    "Linear Regression", "Logistic Regression", "Decision Trees", "Information Gain", "Gini Impurity",
    "Random Forest", "Gradient Boosting", "XGBoost", "Support Vector Machines", "SVM", "Kernel Trick",
    "K-Nearest Neighbors", "KNN", "Naive Bayes", "K-Means Clustering", "Hierarchical Clustering",
    "Principal Component Analysis", "PCA", "Feedforward Neural Networks", "Backpropagation",
    "Convolutional Neural Networks", "CNN", "Recurrent Neural Networks", "RNN", "LSTM", "GRU",
    "Transformer Architecture", "Self-Attention", "Multi-Head Attention",
    # Data Structures & Algorithms
    "Binary Search Tree", "AVL Tree", "Red-Black Tree", "B-Tree", "B+ Tree",
    "Dijkstra's Algorithm", "Bellman-Ford Algorithm", "Floyd-Warshall", "A* Search",
    "Breadth-First Search", "BFS", "Depth-First Search", "DFS", "Topological Sort",
    "Kruskal's Algorithm", "Prim's Algorithm", "Dynamic Programming", "Divide and Conquer"
]


def _extract_definitions_from_text(text: str) -> Dict[str, str]:
    """Scan text for explicit definition sentence patterns."""
    definitions = {}
    pattern = re.compile(
        r"(?:^|\.\s+|\n+)([A-Z][a-zA-Z0-9\s\-]{2,45})\s+(?:is defined as|refers to|is a mechanism (?:that|for)|is an algorithm (?:that|for)|is a method (?:that|for)|is a technique (?:that|for)|is the process of)\s+([^.\n]{15,220}\.)",
        re.MULTILINE
    )
    for match in pattern.finditer(text):
        term = match.group(1).strip()
        defn = match.group(0).strip().lstrip(".\n ")
        if 3 <= len(term) <= 50 and term not in definitions:
            definitions[term.lower()] = defn
    return definitions


def _extract_heuristic_title(lines: List[str], doc_title: str, idx: int) -> Tuple[str, List[str]]:
    """Extracts a clean, human-readable concept title from section lines."""
    non_empty = [l.strip() for l in lines if l.strip()]
    if not non_empty:
        return f"{doc_title} - Concept {idx+1}", []

    # 1. Explicit header markers in first 4 lines
    for i, line in enumerate(non_empty[:4]):
        m = re.match(
            r"^(?:#{1,4}\s*|[0-9]+(?:\.[0-9]+)*[\.\:\-\s]+|module\s+[0-9]+\s*[\:\-\s]*|unit\s+[0-9]+\s*[\:\-\s]*|chapter\s+[0-9]+\s*[\:\-\s]*)(.+)$",
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


def _find_source_page_for_text(target_text: str, pages_data: Optional[List[Dict[str, Any]]]) -> Optional[str]:
    """Find the specific PDF page number where target_text or concept title appears."""
    if not pages_data:
        return None
    target_clean = re.sub(r'[^a-zA-Z0-9]', '', target_text.lower())
    if len(target_clean) < 4:
        return None

    matched_pages = []
    for p in pages_data:
        p_clean = re.sub(r'[^a-zA-Z0-9]', '', p.get("text", "").lower())
        if target_clean in p_clean:
            matched_pages.append(p.get("page_number"))

    if not matched_pages:
        return None
    if len(matched_pages) == 1:
        return f"Page {matched_pages[0]}"
    return f"Pages {matched_pages[0]}-{matched_pages[-1]}"


def _heuristic_concept_extractor(
    text: str,
    doc_title: str,
    pages_data: Optional[List[Dict[str, Any]]] = None
) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]:
    """
    Intelligent heuristic fallback supporting detailed topic segregation without artificial limits:
    - Identifies major topics and detailed subtopics.
    - Identifies specific named representations, algorithms, types, and methods.
    - Captures definitions explicitly present in notes.
    - Maps prerequisite relationships into a valid acyclic DAG.
    - Preserves source PDF page numbers when available.
    """
    clean_title = clean_doc_title(doc_title)
    cleaned_text = _clean_watermark_lines(text)
    known_defs = _extract_definitions_from_text(cleaned_text)

    # 1. Identify Major Topics / Chapters / Modules
    major_split_pattern = re.compile(
        r"(?=(?:^|\n)(?:#{1,2}\s+|module\s+[0-9]+|unit\s+[0-9]+|chapter\s+[0-9]+|[0-9]+\.0\s+|[A-Z\s]{5,45}\n))",
        re.IGNORECASE
    )
    raw_major_blocks = major_split_pattern.split(cleaned_text)
    major_blocks = [b.strip() for b in raw_major_blocks if len(b.strip()) > 40]
    if not major_blocks:
        major_blocks = [cleaned_text]

    extracted_concepts: List[Dict[str, Any]] = []
    dependencies: List[Tuple[str, str]] = []
    seen_ids = set()
    prev_concept_id: Optional[str] = None

    for m_idx, block in enumerate(major_blocks):
        # Determine Major Topic Heading
        first_line = block.splitlines()[0].strip().lstrip("#*- 0123456789.:")
        if 3 <= len(first_line) <= 65 and not first_line.endswith("."):
            major_topic_name = first_line
        else:
            major_topic_name = f"{clean_title} - Section {m_idx + 1}"

        # 2. Break Major Topic into Specific Subtopics
        sub_split_pattern = re.compile(
            r"\n(?=#{2,4}\s+|[0-9]+(?:\.[0-9]+)+\s+|[A-Z][A-Za-z0-9\s\-]{2,40}:|\n\s*[\*\-•]\s+[A-Z][A-Za-z0-9\s]{2,40}:)",
            re.IGNORECASE
        )
        sub_sections = sub_split_pattern.split(block)
        sub_sections = [s.strip() for s in sub_sections if len(s.strip()) > 35]
        if not sub_sections:
            sub_sections = [s.strip() for s in block.split("\n\n") if len(s.strip()) > 50]

        # Process each subtopic in this major topic (no artificial 6-topic truncation!)
        for s_idx, sec in enumerate(sub_sections):
            lines = [l.strip() for l in sec.split("\n") if l.strip()]
            title, rem_lines = _extract_heuristic_title(lines, major_topic_name, s_idx)
            summary, canonical, key_pts = _extract_heuristic_points(rem_lines, title)

            # Discover specific named entities (algorithms, representations, models) in this subtopic
            named_entities = []
            sec_lower = sec.lower()
            for term in KNOWN_TECHNICAL_TERMS:
                if term.lower() in sec_lower:
                    named_entities.append(term)

            # Match explicit definitions present in text
            definitions_found = []
            for term_key, defn_val in known_defs.items():
                if term_key in title.lower() or term_key in sec_lower:
                    definitions_found.append(defn_val)

            # Resolve source page location if pages_data available
            source_page = _find_source_page_for_text(title, pages_data)
            if not source_page and named_entities:
                source_page = _find_source_page_for_text(named_entities[0], pages_data)

            cid = f"node_{re.sub(r'[^a-zA-Z0-9_]', '_', title.lower())[:24]}_{len(extracted_concepts) + 1}"
            if cid in seen_ids:
                cid = f"{cid}_{len(extracted_concepts) + 1}"
            seen_ids.add(cid)

            # Construct active recall challenge question
            if named_entities and len(named_entities) > 1:
                prompt_q = f"In your own words, what is {title}, and how do its mechanisms (such as {', '.join(named_entities[:2])}) operate?"
            else:
                prompt_q = f"In your own words, what is {title} and what are its key requirements and principles?"

            concept_record = {
                "id": cid,
                "title": title,
                "major_topic": major_topic_name,
                "subtopic": title,
                "summary": summary,
                "canonical_explanation": canonical[:800],
                "key_points": key_pts,
                "named_entities": named_entities[:5],
                "named_types_or_methods": named_entities[:5],
                "definitions": definitions_found[:3],
                "source_page": source_page or "Uploaded Notes",
                "source_location": source_page or "Uploaded Notes",
                "order_index": len(extracted_concepts) + 1,
                "status": "not_started",
                "prompt_question": prompt_q,
                "note_chunks": [sec[:1200]],
                "prerequisites": [prev_concept_id] if prev_concept_id else []
            }

            extracted_concepts.append(concept_record)

            if prev_concept_id:
                dependencies.append((prev_concept_id, cid))
            prev_concept_id = cid

    return extracted_concepts, dependencies


def _chunk_text_with_context(text: str, chunk_size: int = 8000, overlap: int = 1000) -> List[Dict[str, Any]]:
    """
    Split long document text into manageable chunks with overlap,
    preserving sentence boundaries and multi-page technical context.
    """
    if len(text) <= chunk_size:
        return [{"chunk_index": 0, "text": text, "start_char": 0, "end_char": len(text)}]

    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            # Try to break at paragraph or newline boundary
            break_pt = text.rfind("\n\n", start + chunk_size - 1200, end)
            if break_pt != -1:
                end = break_pt
            else:
                # Fallback to period or space
                break_pt = text.rfind(". ", start + chunk_size - 600, end)
                if break_pt != -1:
                    end = break_pt + 1

        chunk_str = text[start:end].strip()
        if chunk_str:
            chunks.append({
                "chunk_index": idx,
                "text": chunk_str,
                "start_char": start,
                "end_char": end
            })
            idx += 1

        if end >= len(text):
            break
        start = max(start + 1, end - overlap)

    return chunks


def extract_concepts_from_text(
    raw_text: str,
    doc_title: str = "Uploaded Notes",
    llm_config: Optional[LLMConfig] = None,
    curriculum_title: Optional[str] = None,
    pages_data: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]:
    """
    Extract detailed hierarchical atomic concepts and prerequisite learning dependencies.
    Supports long notes via context-preserving chunking, merging, and deduplication.
    Grounded in actual source text — preserves named representations, algorithms, definitions, and page numbers.
    Returns (concepts_list, dependencies_list).
    """
    doc_title = curriculum_title or doc_title
    clean_text = raw_text.strip()
    if len(clean_text) < 50:
        return [], []

    # In demo/offline mode, parse genuine concepts directly from student notes using the intelligent heuristic engine
    if not llm_config or getattr(llm_config, "provider", "demo") == "demo":
        return _heuristic_concept_extractor(clean_text, doc_title, pages_data=pages_data)

    from edumentor.ai.fallback_pipeline import execute_ai_pipeline
    from edumentor.ai.schemas import ConceptExtractionSchema
    from edumentor.llm import call_llm

    def _fallback_extractor():
        return _heuristic_concept_extractor(clean_text, doc_title, pages_data=pages_data)

    # Long document support: chunk and extract across chunks with overlap
    chunks = _chunk_text_with_context(clean_text, chunk_size=8000, overlap=1000)
    all_extracted_concepts: List[Dict[str, Any]] = []
    all_dependencies: List[Tuple[str, str]] = []
    seen_titles = set()
    prev_chunk_last_id: Optional[str] = None

    for c_info in chunks:
        chunk_text = c_info["text"]
        prompt = f"""
You are an expert cognitive curriculum designer and professor.
Analyze the following section of student study notes and extract the detailed atomic concepts and prerequisite dependencies.

[DOCUMENT TITLE]: {doc_title}

[STUDENT NOTES CONTENT]:
\"\"\"{chunk_text}\"\"\"

CRITICAL INSTRUCTIONS:
1. Do NOT produce vague, generic topic names (e.g. do not just say "Memory", "Scheduling", "Representation", "Learning").
2. Extract the SPECIFIC named algorithms, representations, models, types, and methods actually covered in the material (e.g. "LRU vs FIFO Page Replacement", "Round Robin CPU Scheduling", "Two-Phase Locking Protocol", "Support Vector Machines with RBF Kernel").
3. For every concept, provide:
   - `id`: a short snake_case identifier (e.g. "lru_page_replacement")
   - `major_topic`: the overarching subject area (e.g. "Memory Management")
   - `title`: the specific, concise concept title
   - `named_types_or_methods`: list of actual algorithm/type/method names from the notes
   - `definitions`: explicit definitions supported by the notes
   - `summary`: 1-sentence high-level summary
   - `canonical_explanation`: clear, authoritative explanation (2-4 sentences) defining mechanics
   - `key_points`: 3-4 essential criteria/principles required to understand it
   - `prompt_question`: active recall question testing the concept without revealing the answer
   - `prerequisites`: list of concept `id`s from this set that must be understood first
4. Ensure dependencies form a valid Directed Acyclic Graph (DAG).

Respond in valid JSON format matching this schema:
{{
  "concepts": [
    {{
      "id": "concept_a",
      "major_topic": "Major Subject Area",
      "title": "Specific Concept A Title",
      "named_types_or_methods": ["Method 1", "Method 2"],
      "definitions": ["Concept A is defined as..."],
      "summary": "Brief summary",
      "canonical_explanation": "Detailed explanation",
      "key_points": ["Principle 1", "Principle 2", "Principle 3"],
      "prompt_question": "Explain Concept A in your own words, focusing on its core mechanisms.",
      "prerequisites": []
    }}
  ]
}}
"""
        pipeline_res = execute_ai_pipeline(
            operation_name="concept_extraction_chunk",
            llm_callable=lambda attempt, prev_err, p=prompt: call_llm(
                p if attempt == 1 else f"{p}\n\nIMPORTANT: Output valid JSON with 'concepts' list matching schema only.",
                system_prompt="You are an expert curriculum designer. Always output strict JSON.",
                config=llm_config
            ),
            schema=ConceptExtractionSchema,
            max_retries=2,
            fallback_fn=None
        )

        if pipeline_res.success and isinstance(pipeline_res.data, dict) and "concepts" in pipeline_res.data:
            chunk_concepts = pipeline_res.data.get("concepts", [])
            for c in chunk_concepts:
                t_lower = c.get("title", "").strip().lower()
                if not t_lower or t_lower in seen_titles:
                    continue
                seen_titles.add(t_lower)
                all_extracted_concepts.append(c)

    if not all_extracted_concepts:
        return _heuristic_concept_extractor(clean_text, doc_title, pages_data=pages_data)

    # Deduplicate, assign order index, and resolve page references
    final_concepts: List[Dict[str, Any]] = []
    seen_ids = set()

    for idx, c in enumerate(all_extracted_concepts):
        cid = c.get("id") or f"concept_{idx+1}"
        cid = re.sub(r"[^a-zA-Z0-9_]", "_", str(cid).lower())
        if cid in seen_ids:
            cid = f"{cid}_{idx+1}"
        seen_ids.add(cid)

        title = c.get("title", f"Concept {idx+1}").strip()
        major_topic = c.get("major_topic") or doc_title
        summary = c.get("summary", "").strip()
        explanation = c.get("canonical_explanation", summary).strip()
        key_points = c.get("key_points", [])
        if isinstance(key_points, str):
            key_points = [k.strip() for k in key_points.split("\n") if k.strip()]

        named_ents = c.get("named_types_or_methods") or c.get("named_entities", [])
        if isinstance(named_ents, str):
            named_ents = [named_ents]
        definitions = c.get("definitions", [])
        if isinstance(definitions, str):
            definitions = [definitions]

        source_loc = _find_source_page_for_text(title, pages_data) or "Uploaded Notes"

        prompt_q = c.get("prompt_question") or f"In your own words, what is {title} and how does it work?"

        matched_paras = [p.strip() for p in clean_text.split("\n\n") if title.lower() in p.lower() and len(p.strip()) > 30]
        note_chunks = matched_paras[:3] if matched_paras else ([explanation] if explanation else [summary])

        concept_obj = {
            "id": cid,
            "title": title,
            "major_topic": major_topic,
            "subtopic": title,
            "summary": summary,
            "canonical_explanation": explanation,
            "key_points": key_pts if 'key_pts' in locals() else key_points,
            "named_entities": named_ents,
            "named_types_or_methods": named_ents,
            "definitions": definitions,
            "source_page": source_loc,
            "source_location": source_loc,
            "order_index": idx + 1,
            "status": "not_started",
            "prompt_question": prompt_q,
            "note_chunks": note_chunks,
            "prerequisites": [str(p) for p in c.get("prerequisites", [])]
        }
        final_concepts.append(concept_obj)

        for prereq in c.get("prerequisites", []):
            clean_prereq = re.sub(r"[^a-zA-Z0-9_]", "_", str(prereq).lower())
            all_dependencies.append((clean_prereq, cid))

    # Link adjacent concepts if graph is sparse
    if not all_dependencies and len(final_concepts) > 1:
        for i in range(len(final_concepts) - 1):
            all_dependencies.append((final_concepts[i]["id"], final_concepts[i+1]["id"]))

    valid_deps = [(p, c) for p, c in all_dependencies if p in seen_ids and c in seen_ids and p != c]
    return final_concepts, valid_deps
