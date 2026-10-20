"""
Hybrid Evaluation Engine for EduMentor.
Combines Semantic Similarity (Sentence-Transformers / TF-IDF Vector Cosine)
with LLM-as-Judge rubric evaluation (Lekshmi-Narayanan et al. 2026, Kazi & Kahanda 2023, GradeOpt 2025).
Prevents keyword gaming and verifies deep conceptual understanding.
"""

import math
import re
from typing import Dict, List, Any, Optional, Tuple
from edumentor.llm import call_llm, call_llm_json, LLMConfig
from edumentor.scheduler import map_score_to_quality, get_quality_label

_ST_MODEL = None


def get_sentence_transformer_model():
    """Load lightweight SentenceTransformer if installed, prioritizing local cache."""
    global _ST_MODEL
    if _ST_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            try:
                _ST_MODEL = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            except Exception:
                _ST_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _ST_MODEL = False
    return _ST_MODEL if _ST_MODEL is not False else None


class VerdictString(str):
    """
    Case-insensitive string representation matching both
    Phase 9 lowercase underscore notation ('almost_correct', 'correct', 'wrong')
    and legacy title case ('Almost Correct', 'Correct', 'Wrong').
    """
    def __eq__(self, other):
        if isinstance(other, str):
            clean_s = self.lower().replace(" ", "_").strip()
            clean_o = other.lower().replace(" ", "_").strip()
            return clean_s == clean_o or super().__eq__(other)
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.lower().replace(" ", "_").strip())


def compute_cosine_similarity(text_a: str, text_b: str) -> float:
    """
    Computes direct vector cosine similarity between reference concept explanation
    and student explanation using sentence-transformers (all-MiniLM-L6-v2).
    Returns float cosine similarity in range [-1.0, 1.0].
    """
    if not text_a or not text_b or not text_a.strip() or not text_b.strip():
        return 0.0

    from edumentor.ai.embedding_cache import embedding_cache

    cached_sim = embedding_cache.get_similarity(text_a, text_b)
    if cached_sim is not None:
        return cached_sim

    st_model = get_sentence_transformer_model()
    if st_model is not None:
        try:
            import numpy as np
            emb1 = embedding_cache.get(text_a.strip())
            emb2 = embedding_cache.get(text_b.strip())

            missing_texts = []
            if emb1 is None:
                missing_texts.append(text_a.strip())
            if emb2 is None and text_b.strip() not in missing_texts:
                missing_texts.append(text_b.strip())

            if missing_texts:
                encoded = st_model.encode(missing_texts)
                for txt, vec in zip(missing_texts, encoded):
                    embedding_cache.set(txt, vec)

            emb1 = embedding_cache.get(text_a.strip())
            emb2 = embedding_cache.get(text_b.strip())

            if emb1 is not None and emb2 is not None:
                norm1 = np.linalg.norm(emb1)
                norm2 = np.linalg.norm(emb2)
                if norm1 > 0 and norm2 > 0:
                    sim = float(np.dot(emb1, emb2) / (norm1 * norm2))
                    embedding_cache.set_similarity(text_a, text_b, sim)
                    return sim
        except Exception:
            pass

    # Fallback to TF-IDF cosine similarity
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        mat = vec.fit_transform([text_a.strip(), text_b.strip()])
        sim = float(cosine_similarity(mat[0:1], mat[1:2])[0][0])
        embedding_cache.set_similarity(text_a, text_b, sim)
        return sim
    except Exception:
        words_a = set(re.findall(r"\w+", text_a.lower()))
        words_b = set(re.findall(r"\w+", text_b.lower()))
        union = words_a.union(words_b)
        sim = float(len(words_a.intersection(words_b)) / len(union)) if union else 0.0
        embedding_cache.set_similarity(text_a, text_b, sim)
        return sim


def compute_semantic_similarity(
    student_answer: str,
    canonical_text: str,
    key_points: Optional[List[str]] = None
) -> float:
    """
    Compute semantic similarity between student response and canonical concept explanation.
    Returns normalized score 0.0 to 100.0, utilizing embedding_cache to avoid repeated computations.
    """
    clean_student = student_answer.strip()
    if not clean_student or len(clean_student.split()) < 3:
        return 0.0

    reference_elements = [canonical_text]
    if key_points:
        reference_elements.extend(key_points)
    reference_corpus = " ".join(reference_elements)

    from edumentor.ai.embedding_cache import embedding_cache

    # Check pair cache first
    cached_score = embedding_cache.get_similarity(clean_student, reference_corpus)
    if cached_score is not None:
        return cached_score

    # 1. Try SentenceTransformers if available with embedding cache
    st_model = get_sentence_transformer_model()
    if st_model is not None:
        try:
            import numpy as np
            emb1 = embedding_cache.get(clean_student)
            emb2 = embedding_cache.get(reference_corpus)

            missing_texts = []
            if emb1 is None:
                missing_texts.append(clean_student)
            if emb2 is None and reference_corpus not in missing_texts:
                missing_texts.append(reference_corpus)

            if missing_texts:
                encoded = st_model.encode(missing_texts)
                for txt, vec in zip(missing_texts, encoded):
                    embedding_cache.set(txt, vec)

            emb1 = embedding_cache.get(clean_student)
            emb2 = embedding_cache.get(reference_corpus)

            if emb1 is not None and emb2 is not None:
                norm1 = np.linalg.norm(emb1)
                norm2 = np.linalg.norm(emb2)
                if norm1 > 0 and norm2 > 0:
                    cosine = float(np.dot(emb1, emb2) / (norm1 * norm2))
                    calibrated = round(max(0.0, min(100.0, (cosine - 0.15) / 0.75 * 100.0)), 1)
                    embedding_cache.set_similarity(clean_student, reference_corpus, calibrated)
                    return calibrated
        except Exception:
            pass

    # 2. Vector Cosine Similarity via TF-IDF & Word n-grams
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english"
        )
        tfidf_matrix = vectorizer.fit_transform([clean_student, reference_corpus])
        tfidf_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
    except Exception:
        s_words = set(re.findall(r"\w+", clean_student.lower()))
        r_words = set(re.findall(r"\w+", reference_corpus.lower()))
        union = s_words.union(r_words)
        tfidf_sim = len(s_words.intersection(r_words)) / len(union) if union else 0.0

    # 3. Key Points Coverage Heuristic
    key_coverage = 0.0
    if key_points:
        s_lower = clean_student.lower()
        matched = 0
        for kp in key_points:
            kp_words = [w for w in re.findall(r"\w+", kp.lower()) if len(w) > 3]
            if any(w in s_lower for w in kp_words):
                matched += 1
        key_coverage = (matched / len(key_points))

    combined = (0.6 * tfidf_sim + 0.4 * key_coverage) * 100.0
    final_score = round(max(0.0, min(100.0, combined)), 1)
    embedding_cache.set_similarity(clean_student, reference_corpus, final_score)
    return final_score


def evaluate_with_llm_judge(
    concept_title: Any = "",
    canonical_explanation: str = "",
    key_points: Optional[List[str]] = None,
    student_answer: str = "",
    llm_config: Optional[LLMConfig] = None,
    concept: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Invoke LLM-as-a-Judge with comprehensive pedagogical rubric.
    Evaluates:
    1. Conceptual correctness (0-100)
    2. Completeness (0-100)
    3. Missing information (missing_points: list of strings)
    4. Misconceptions (misconceptions: list of strings)
    5. Reasoning (reasoning: string)
    6. Relevance (relevance: 0-100)
    """
    if concept is not None or isinstance(concept_title, dict):
        c_dict = concept if concept is not None else concept_title
        concept_title = c_dict.get("title", "")
        canonical_explanation = c_dict.get("canonical_explanation") or c_dict.get("summary", "")
        key_points = c_dict.get("key_points") or c_dict.get("principles", [])

    if key_points is None:
        key_points = []

    key_points_formatted = "\n".join(f"- {kp}" for kp in key_points)

    prompt = f"""
You are an expert pedagogical evaluator. Evaluate the student's active recall of the concept below.

[CONCEPT]: {concept_title}

[CANONICAL EXPLANATION]:
{canonical_explanation}

[KEY PRINCIPLES & CRITERIA]:
{key_points_formatted}

[STUDENT'S RECALL ANSWER]:
\"\"\"{student_answer}\"\"\"

Evaluate the answer strictly on deep conceptual understanding rather than exact keyword repetition across these 6 criteria:
1. `correctness` (0 to 100): Conceptual correctness. Are the mechanisms, causal relationships, and facts accurate?
2. `completeness` (0 to 100): Did the student cover the essential principles, steps, and reasons?
3. `missing_points` (list of strings): What important mechanisms, criteria, or concepts did the student omit?
4. `misconceptions` (list of strings): Any incorrect beliefs, inverted causalities, or false statements (empty list if none).
5. `reasoning` (string): Concise pedagogical explanation of how this score was derived.
6. `relevance` (0 to 100): Topical relevance of the answer to the concept.
7. `strengths` (list of strings): 1 to 3 specific points the student grasped well.
8. `actionable_tip` (string): A concise 1-2 sentence tip to help the student bridge the gap.

Respond in valid JSON format only:
{{
  "correctness": 88,
  "completeness": 76,
  "missing_points": ["CPU allocation", "process selection"],
  "misconceptions": [],
  "reasoning": "The student understands the general purpose of process scheduling but omitted the dispatcher context switch mechanism.",
  "relevance": 95,
  "strengths": ["Accurately identified ready queue management"],
  "actionable_tip": "Remember to explain how the OS dispatcher performs context switches."
}}
"""

    def _heuristic_fallback_judge() -> Dict[str, Any]:
        c_sim = compute_semantic_similarity(student_answer, canonical_explanation, key_points)
        score_est = round(c_sim, 1)
        v_est = "correct" if score_est >= 75.0 else ("almost_correct" if score_est >= 55.0 else "wrong")
        return {
            "correctness": score_est,
            "completeness": max(20.0, round(score_est - 5.0, 1)),
            "reasoning": "Heuristic fallback evaluation based on semantic keyword and n-gram overlap.",
            "missing_points": ["Could elaborate further on edge conditions or mechanism causality."],
            "misconceptions": [],
            "strengths": ["Demonstrated active retrieval effort."],
            "actionable_tip": "Review core mechanism and try recalling the key causality.",
            "relevance": 90.0,
            "verdict": v_est
        }

    from edumentor.ai.fallback_pipeline import execute_ai_pipeline
    from edumentor.ai.schemas import EvaluationJudgeSchema

    pipeline_res = execute_ai_pipeline(
        operation_name="llm_as_judge_recall_eval",
        llm_callable=lambda attempt, prev_err: call_llm(
            prompt if attempt == 1 else f"{prompt}\n\nIMPORTANT: Your previous output failed schema validation: {prev_err}. Output valid JSON matching the schema only.",
            system_prompt="You are a rigorous pedagogical judge assessing active recall understanding. Always output valid JSON.",
            config=llm_config
        ),
        schema=EvaluationJudgeSchema,
        max_retries=2,
        fallback_fn=_heuristic_fallback_judge
    )

    result = pipeline_res.data if pipeline_res.success and isinstance(pipeline_res.data, dict) else _heuristic_fallback_judge()

    correctness = float(result.get("correctness", result.get("conceptual_accuracy", 50.0)))
    completeness = float(result.get("completeness", result.get("key_point_coverage", 50.0)))
    missing_points = result.get("missing_points", result.get("missing_concepts", []))
    if not isinstance(missing_points, list):
        missing_points = [str(missing_points)] if missing_points else []

    misconceptions = result.get("misconceptions", [])
    if not isinstance(misconceptions, list):
        misconceptions = [str(misconceptions)] if misconceptions else []

    reasoning = str(result.get("reasoning", "Evaluated based on conceptual correctness and coverage."))
    relevance = float(result.get("relevance", 95.0))
    tip = result.get("actionable_tip", "Review core mechanism and try recalling the key causality.")

    strengths = result.get("strengths", [])
    if not isinstance(strengths, list):
        strengths = [str(strengths)] if strengths else ["Demonstrated recall effort."]

    # Derived composite judge score
    penalty = min(30.0, len(misconceptions) * 10.0)
    judge_score = max(0.0, min(100.0, (0.55 * correctness + 0.45 * completeness) - penalty))

    # Calculate overall score and verdict for direct judge consumers
    if judge_score >= 75.0:
        verdict = VerdictString("correct")
    elif judge_score >= 55.0:
        verdict = VerdictString("almost_correct")
    else:
        verdict = VerdictString("wrong")

    return {
        "score": int(round(judge_score)),
        "verdict": verdict,
        "judge_score": round(judge_score, 1),
        "correctness": round(correctness, 1),
        "completeness": round(completeness, 1),
        "missing_points": missing_points,
        "misconceptions": misconceptions,
        "reasoning": reasoning,
        "relevance": round(relevance, 1),
        "conceptual_accuracy": round(correctness, 1),
        "key_point_coverage": round(completeness, 1),
        "misconception_penalty": round(penalty, 1),
        "strengths": strengths,
        "missing_concepts": missing_points,
        "actionable_tip": tip
    }


def evaluate_recall(
    concept: Dict[str, Any],
    student_answer: str,
    weight_similarity: float = 0.35,
    weight_judge: float = 0.65,
    llm_config: Optional[LLMConfig] = None
) -> Dict[str, Any]:
    """
    Master Hybrid Evaluation function (Phase 9 Core Engine).
    Synthesizes sentence-transformers vector cosine similarity (35%)
    and LLM-as-a-judge rubric evaluation (65%) into final evaluation score.
    Returns structured JSON schema matching Phase 9 specification.
    """
    clean_ans = student_answer.strip()
    words = clean_ans.split()

    title = concept.get("title", "Concept")
    canonical = concept.get("canonical_explanation") or concept.get("summary", "")
    key_points = concept.get("key_points") or concept.get("principles", [])

    # Edge Case: Blank or extremely short response
    if len(words) < 5 or clean_ans.lower() in ["idk", "i don't know", "skip", "pass", "no idea"]:
        verdict = VerdictString("wrong")
        blank_details = {
            "score": 0,
            "correctness": 0,
            "completeness": 0,
            "missing_points": ["All primary mechanisms and foundational principles."],
            "misconceptions": [],
            "reasoning": "No active recall provided. Student gave a blank or 'I don't know' response.",
            "relevance": 0,
            "verdict": verdict,
            "concept_id": concept.get("id"),
            "concept_title": title,
            "composite_score": 0.0,
            "semantic_score": 0.0,
            "semantic_similarity_score": 0.0,
            "llm_score": 0.0,
            "judge_score": 0.0,
            "quality_q": 0,
            "quality_label": "Complete Blank (<20%)",
            "quality_description": "No active recall provided. Scheduled for immediate re-learning.",
            "conceptual_accuracy": 0.0,
            "key_point_coverage": 0.0,
            "misconception_penalty": 0.0,
            "strengths": ["Recognized need for review."],
            "missing_concepts": ["All primary mechanisms."],
            "actionable_tip": "Re-read the concept summary and attempt to explain the fundamental purpose from memory."
        }
        blank_details["hybrid_evaluation"] = {
            "correctness": 0,
            "completeness": 0,
            "missing_points": blank_details["missing_points"],
            "misconceptions": [],
            "reasoning": blank_details["reasoning"],
            "relevance": 0
        }
        return blank_details

    # 1. Semantic Similarity Signal (sentence-transformers cosine similarity)
    sim_score = compute_semantic_similarity(clean_ans, canonical, key_points)

    # 2. LLM-as-a-Judge Signal
    judge_result = evaluate_with_llm_judge(title, canonical, key_points, clean_ans, llm_config)
    judge_score = judge_result["judge_score"]

    # 3. Hybrid Engine Synthesis
    composite = round((weight_similarity * sim_score) + (weight_judge * judge_score), 1)
    composite = max(0.0, min(100.0, composite))

    # 4. Map to SM-2 Quality
    q = map_score_to_quality(composite)
    label, desc = get_quality_label(q)

    # Verdict label
    if composite >= 75.0:
        verdict = VerdictString("correct")
    elif composite >= 55.0:
        verdict = VerdictString("almost_correct")
    else:
        verdict = VerdictString("wrong")

    return {
        # Primary Phase 9 structured JSON fields
        "score": int(round(composite)),
        "correctness": int(round(judge_result["correctness"])),
        "completeness": int(round(judge_result["completeness"])),
        "missing_points": judge_result["missing_points"],
        "misconceptions": judge_result["misconceptions"],
        "reasoning": judge_result["reasoning"],
        "relevance": int(round(judge_result["relevance"])),
        "verdict": verdict,

        # Extended integration fields for SM-2 and UI components
        "concept_id": concept.get("id"),
        "concept_title": title,
        "composite_score": composite,
        "semantic_score": sim_score,
        "semantic_similarity_score": sim_score,
        "llm_score": judge_score,
        "judge_score": judge_score,
        "hybrid_evaluation": judge_result,
        "quality_q": q,
        "quality_label": label,
        "quality_description": desc,
        "conceptual_accuracy": judge_result["correctness"],
        "key_point_coverage": judge_result["completeness"],
        "misconception_penalty": judge_result["misconception_penalty"],
        "strengths": judge_result["strengths"],
        "missing_concepts": judge_result["missing_points"],
        "actionable_tip": judge_result["actionable_tip"]
    }


def evaluate_hybrid_answer(
    student_answer: str = "",
    reference_explanation: str = "",
    concept_title: str = "",
    key_points: Optional[List[str]] = None,
    llm_config: Optional[LLMConfig] = None,
    weight_semantic: float = 0.35,
    weight_llm: float = 0.65,
    concept: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Phase 9 Core Research Contribution:
    Evaluates student answer via the two-stage hybrid pipeline:
      Student Answer
           ↓
      ┌───────────────┐
      │ Semantic      │ (sentence-transformers cosine similarity)
      └───────┬───────┘
              │
              ├───────────────┐
              ↓               ↓
      sentence-transformers  LLM Judge (correctness, completeness, missing_points,
              │               │          misconceptions, reasoning, relevance)
              └───────┬───────┘
                      ↓
                Hybrid Engine
                      ↓
               Final Evaluation
    """
    if concept is not None:
        concept_dict = concept
    else:
        concept_dict = {
            "title": concept_title or "Target Concept",
            "canonical_explanation": reference_explanation,
            "key_points": key_points or []
        }
    return evaluate_recall(
        concept=concept_dict,
        student_answer=student_answer,
        weight_similarity=weight_semantic,
        weight_judge=weight_llm,
        llm_config=llm_config
    )


def generate_socratic_hints(
    concept_title: str,
    canonical_explanation: str,
    key_points: List[str],
    llm_config: Optional[LLMConfig] = None
) -> Dict[str, str]:
    """Generate 3 tiers of progressive Socratic scaffolding hints."""
    key_points_str = "\n".join(f"- {kp}" for kp in key_points)
    prompt = f"""
Generate 3 tiers of progressive Socratic scaffolding hints for a student trying to recall this concept:
[CONCEPT]: {concept_title}
[CANONICAL]: {canonical_explanation}
[KEY POINTS]:
{key_points_str}

Tier 1: High-level intuition or real-world analogy.
Tier 2: Specific operational step or core mechanism.
Tier 3: Targeted guiding question that unlocks the exact principle.

Respond in JSON format:
{{
  "hint_tier_1": "...",
  "hint_tier_2": "...",
  "hint_tier_3": "..."
}}
"""
    def _fallback_socratic_hints() -> Dict[str, str]:
        return {
            "hint_tier_1": f"Think about why {concept_title} is necessary in the broader system architecture.",
            "hint_tier_2": f"Consider the step-by-step mechanism and what components or state are modified.",
            "hint_tier_3": f"What specific problem arises if {concept_title} fails or is omitted completely?"
        }

    from edumentor.ai.fallback_pipeline import execute_ai_pipeline
    from edumentor.ai.schemas import SocraticHintsSchema

    pipeline_res = execute_ai_pipeline(
        operation_name="generate_socratic_hints",
        llm_callable=lambda attempt, prev_err: call_llm(
            prompt if attempt == 1 else f"{prompt}\n\nIMPORTANT: Previous attempt failed validation: {prev_err}. Output valid JSON matching schema only.",
            system_prompt="You are an expert pedagogical AI. Always output valid JSON.",
            config=llm_config
        ),
        schema=SocraticHintsSchema,
        max_retries=2,
        fallback_fn=_fallback_socratic_hints
    )

    hints = pipeline_res.data if pipeline_res.success and isinstance(pipeline_res.data, dict) else _fallback_socratic_hints()
    return hints
