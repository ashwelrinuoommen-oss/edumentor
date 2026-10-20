"""
Ingestion service managing notes parsing, PDF extraction, and curriculum creation.
"""

from typing import Dict, List, Tuple, Any, Optional
from edumentor.utils.pdf_utils import extract_text_from_pdf
from edumentor.ai.concept_extractor import extract_concepts
from edumentor.ai.dependency_extractor import extract_dependencies
from edumentor.ai.llm_client import LLMConfig
from edumentor.samples import SAMPLE_CURRICULA


class IngestionService:
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.llm_config = llm_config

    def process_pdf(self, pdf_bytes: bytes, filename: str = "Notes.pdf") -> Dict[str, Any]:
        """Extract text from PDF and produce structured concepts and dependencies."""
        doc_title, text = extract_text_from_pdf(pdf_bytes)
        title = doc_title if doc_title and doc_title != "Uploaded PDF Notes" else filename.replace(".pdf", "")
        return self.process_text(text, title=title)

    def process_text(self, text: str, title: str = "Notes") -> Dict[str, Any]:
        """Extract concepts from raw text notes."""
        concepts = extract_concepts(text, curriculum_title=title, llm_config=self.llm_config)
        if not concepts:
            # Fallback to curated benchmark
            return self.get_sample_curriculum("Operating Systems")
        deps = extract_dependencies(concepts)
        return {
            "title": title,
            "concepts": concepts,
            "dependencies": deps
        }

    def get_sample_curriculum(self, module_name: str) -> Dict[str, Any]:
        """Retrieve one of the pre-curated curricula."""
        matched = None
        for k, v in SAMPLE_CURRICULA.items():
            if module_name.lower() in k.lower():
                matched = v
                break
        if not matched:
            matched = list(SAMPLE_CURRICULA.values())[0]

        deps = list(matched.get("dependencies", []))
        if not deps:
            for c in matched["concepts"]:
                for p in c.get("prerequisites", []) or []:
                    deps.append((p, c["id"]))

        return {
            "title": matched["title"],
            "concepts": matched["concepts"],
            "dependencies": deps
        }
