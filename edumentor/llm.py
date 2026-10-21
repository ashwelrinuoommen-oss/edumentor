"""
Unified Multi-Provider LLM Client for EduMentor.
Supports OpenAI, Anthropic Claude, Google Gemini, Ollama, and an intelligent Heuristic Demo Mode.
"""

import os
import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from edumentor.utils.error_handler import ERROR_LLM_MSG, EduMentorLLMError


@dataclass
class LLMConfig:
    provider: str = "demo"  # "demo", "openai", "anthropic", "gemini", "ollama"
    model: str = "default"
    api_key: Optional[str] = None
    temperature: float = 0.2
    base_url: Optional[str] = None

    @property
    def model_name(self) -> str:
        return self.model

    @model_name.setter
    def model_name(self, value: str):
        self.model = value

    @property
    def masked_api_key(self) -> str:
        from edumentor.utils.security import mask_api_key
        return mask_api_key(self.api_key)

    def to_safe_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "api_key_configured": bool(self.api_key),
            "api_key_masked": self.masked_api_key,
            "temperature": self.temperature,
            "base_url": self.base_url
        }

    def __repr__(self) -> str:
        key_display = self.masked_api_key if self.api_key else "None"
        return f"LLMConfig(provider='{self.provider}', model='{self.model}', api_key='{key_display}', temperature={self.temperature})"

    def __str__(self) -> str:
        return self.__repr__()



def get_default_config() -> LLMConfig:
    """Read API keys from environment if present, else fallback to demo mode."""
    if os.environ.get("GEMINI_API_KEY"):
        return LLMConfig(provider="gemini", model="gemini-1.5-flash", api_key=os.environ["GEMINI_API_KEY"])
    elif os.environ.get("OPENAI_API_KEY"):
        return LLMConfig(provider="openai", model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"])
    elif os.environ.get("ANTHROPIC_API_KEY"):
        return LLMConfig(provider="anthropic", model="claude-3-5-haiku-20241022", api_key=os.environ["ANTHROPIC_API_KEY"])
    return LLMConfig(provider="demo", model="heuristic-v1")


def test_llm_connection(config: LLMConfig) -> Tuple[bool, str]:
    """
    Test connectivity and credentials for the specified LLMConfig.
    Returns (success: bool, message: str).
    """
    if config.provider == "demo":
        return True, "Demo Mode active: Intelligent Offline Engine ready (zero API key needed)."

    test_prompt = "Respond with 'OK' if you can read this message."
    try:
        response = call_llm(test_prompt, system_prompt="Verify connectivity.", config=config)
        if response == ERROR_LLM_MSG or response.startswith("Error connecting to"):
            return False, response
        return True, f"Successfully connected to {config.provider.upper()} ({config.model or 'default'})!"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


def call_llm(
    prompt: str,
    system_prompt: str = "You are an expert pedagogical AI specializing in concept recall mastery.",
    config: Optional[LLMConfig] = None,
    use_cache: bool = True
) -> str:
    """Call LLM provider and return raw text response with caching to avoid repeated calls."""
    if config is None:
        config = get_default_config()

    from edumentor.ai.llm_cache import llm_cache

    provider = config.provider.lower()
    model = config.model or "default"
    temp = config.temperature

    if use_cache:
        cached = llm_cache.get(provider, model, temp, system_prompt, prompt)
        if cached is not None:
            return cached

    result = _execute_provider_call(provider, config, prompt, system_prompt)

    if use_cache and result and result != ERROR_LLM_MSG:
        llm_cache.set(provider, model, temp, system_prompt, prompt, result)

    return result


def _execute_provider_call(
    provider: str,
    config: LLMConfig,
    prompt: str,
    system_prompt: str
) -> str:
    """Execute raw provider network inference."""
    if provider == "demo":
        return _demo_llm_response(prompt)

    elif provider == "gemini":
        try:
            model_name = config.model if config.model != "default" else "gemini-1.5-flash"
            api_key = config.api_key or os.environ.get("GEMINI_API_KEY", "")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{system_prompt}\n\n{prompt}"}]}
                ],
                "generationConfig": {"temperature": config.temperature}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return ERROR_LLM_MSG

    elif provider in ["openai", "gpt"]:
        try:
            try:
                import openai
                client = openai.OpenAI(api_key=config.api_key, base_url=config.base_url)
                model_name = config.model if config.model != "default" else "gpt-4o-mini"
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=config.temperature
                )
                return response.choices[0].message.content or ""
            except ImportError:
                url = f"{config.base_url or 'https://api.openai.com/v1'}/chat/completions"
                model_name = config.model if config.model != "default" else "gpt-4o-mini"
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": config.temperature
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.api_key or ''}"
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"]
        except Exception:
            return ERROR_LLM_MSG

    elif provider in ["anthropic", "claude"]:
        try:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=config.api_key)
                model_name = config.model if config.model != "default" else "claude-3-5-haiku-20241022"
                response = client.messages.create(
                    model=model_name,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2048,
                    temperature=config.temperature
                )
                return response.content[0].text
            except ImportError:
                url = "https://api.anthropic.com/v1/messages"
                model_name = config.model if config.model != "default" else "claude-3-5-haiku-20241022"
                payload = {
                    "model": model_name,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2048,
                    "temperature": config.temperature
                }
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": config.api_key or "",
                    "anthropic-version": "2023-06-01"
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                with urllib.request.urlopen(req, timeout=35) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["content"][0]["text"]
        except Exception:
            return ERROR_LLM_MSG

    elif provider == "ollama":
        try:
            base_url = config.base_url or "http://localhost:11434"
            model_name = config.model if config.model != "default" else "llama3"
            url = f"{base_url}/api/generate"
            payload = {
                "model": model_name,
                "system": system_prompt,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": config.temperature}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "")
        except Exception:
            return ERROR_LLM_MSG

    return _demo_llm_response(prompt)


def call_llm_json(
    prompt: str,
    system_prompt: str = "You are an expert pedagogical AI. You always respond in valid JSON.",
    config: Optional[LLMConfig] = None,
    schema: Optional[Any] = None,
    validator: Optional[Any] = None,
    max_retries: int = 2,
    fallback_fn: Optional[Any] = None,
    default_fallback: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Call LLM and extract cleanly parsed, schema-validated JSON object or dict.
    Executes through the Phase 37 4-stage pipeline:
      Validation -> Retry -> Fallback -> User-friendly error
    "Never assume the model returns valid JSON."
    """
    from edumentor.ai.fallback_pipeline import execute_ai_pipeline, safe_parse_json

    def _call(attempt: int, prev_err: Optional[str]) -> str:
        curr_prompt = prompt
        if attempt > 1 and prev_err:
            curr_prompt = (
                f"{prompt}\n\n"
                f"IMPORTANT: Your previous output failed validation: {prev_err}. "
                f"Output strictly valid JSON matching the required schema only."
            )
        return call_llm(curr_prompt, system_prompt=system_prompt, config=config)

    res = execute_ai_pipeline(
        operation_name="call_llm_json",
        llm_callable=_call,
        schema=schema,
        validator=validator,
        max_retries=max_retries,
        fallback_fn=fallback_fn,
        default_fallback=default_fallback,
        is_json=True
    )

    if res.success and res.data is not None:
        return res.data

    # If fallback wasn't specified and all retries failed:
    return {"raw": prompt, "error": res.error_message or "Could not parse JSON response"}


def call_llm_with_fallback(
    prompt: str,
    system_prompt: str = "You are an expert pedagogical AI.",
    config: Optional[LLMConfig] = None,
    schema: Optional[Any] = None,
    validator: Optional[Any] = None,
    max_retries: int = 2,
    fallback_fn: Optional[Any] = None,
    default_fallback: Optional[Any] = None,
    is_json: bool = False
) -> Any:
    """
    Call LLM with the universal Phase 37 4-stage fallback pipeline:
      Validation -> Retry -> Fallback -> User-friendly error
    """
    from edumentor.ai.fallback_pipeline import execute_ai_pipeline

    def _call(attempt: int, prev_err: Optional[str]) -> str:
        curr_prompt = prompt
        if attempt > 1 and prev_err:
            curr_prompt = f"{prompt}\n\nPlease correct your previous response: {prev_err}."
        return call_llm(curr_prompt, system_prompt=system_prompt, config=config)

    res = execute_ai_pipeline(
        operation_name="call_llm_with_fallback",
        llm_callable=_call,
        schema=schema,
        validator=validator,
        max_retries=max_retries,
        fallback_fn=fallback_fn,
        default_fallback=default_fallback,
        is_json=is_json
    )

    if res.success:
        return res.data
    return res.error_message or ERROR_LLM_MSG


def _demo_llm_response(prompt: str) -> str:
    """
    Intelligent simulated response for offline/demo evaluation & concept extraction.
    Ensures tests and demos work seamlessly without third-party API keys.
    """
    prompt_lower = prompt.lower()

    # Case 1: Hybrid Evaluation Judge Prompt
    if "evaluate the student's recall" in prompt_lower or "llm-as-judge" in prompt_lower or "student's recall answer" in prompt_lower:
        # Robust extraction of student text and canonical explanation
        student_text = ""
        if "[STUDENT'S RECALL ANSWER]:" in prompt:
            after_marker = prompt.split("[STUDENT'S RECALL ANSWER]:", 1)[1].strip()
            clean = re.sub(r'^(?:"""|\'\'\'|"|\')', '', after_marker).strip()
            if '"""' in clean:
                clean = clean.split('"""', 1)[0].strip()
            elif "'''" in clean:
                clean = clean.split("'''", 1)[0].strip()
            elif "\nEvaluate " in clean:
                clean = clean.split("\nEvaluate ", 1)[0].strip()
            student_text = clean
        elif student_match:
            student_text = student_match.group(1).strip(" \"'\n\r\t")

        canonical_text = ""
        if "[CANONICAL EXPLANATION]:" in prompt:
            after_canon = prompt.split("[CANONICAL EXPLANATION]:", 1)[1].strip()
            if "\n[" in after_canon:
                canonical_text = after_canon.split("\n[", 1)[0].strip()
            else:
                canonical_text = after_canon.strip()
        elif canonical_match:
            canonical_text = canonical_match.group(1)

        if len(student_text) < 12 or any(w in student_text.lower() for w in ["don't know", "idk", "no idea", "pass", "skip", "not sure"]):
            return json.dumps({
                "score": 0,
                "correctness": 0,
                "completeness": 0,
                "missing_points": ["Core operational mechanisms and foundational principles."],
                "misconceptions": [],
                "reasoning": "The student gave a blank response or indicated they did not know the concept.",
                "relevance": 0,
                "verdict": "wrong",
                "conceptual_accuracy": 0,
                "key_point_coverage": 0,
                "misconception_penalty": 0,
                "judge_score": 0,
                "strengths": ["Attempted the active recall exercise."],
                "missing_concepts": ["All core operational mechanisms and principles."],
                "actionable_tip": "Review the primary concept card and try explaining the mechanism in 2 plain sentences."
            })
        
        # Stop-words filtered conceptual vocabulary
        stopwords = {
            "the", "and", "that", "this", "with", "from", "for", "are", "was", "were", "been",
            "have", "has", "had", "will", "would", "can", "could", "should", "what", "when",
            "where", "which", "who", "whom", "whose", "why", "how", "all", "any", "both",
            "each", "few", "more", "most", "other", "some", "such", "than", "too", "very",
            "into", "through", "during", "before", "after", "above", "below", "between",
            "under", "again", "further", "then", "once", "about", "there", "their", "they"
        }
        words_student = set(w for w in re.findall(r"\b[a-zA-Z]{3,}\b", student_text.lower()) if w not in stopwords)
        words_canonical = set(w for w in re.findall(r"\b[a-zA-Z]{3,}\b", canonical_text.lower()) if w not in stopwords)
        
        common = words_student.intersection(words_canonical)
        overlap_ratio = len(common) / max(1, len(words_canonical)) if words_canonical else 0.1
        word_count = len(student_text.split())

        # Calibrated rubric scoring
        if overlap_ratio >= 0.24 or len(common) >= 7:
            # High conceptual mastery: accurate vocabulary and mechanisms
            correctness = min(98.0, 72.0 + overlap_ratio * 38.0)
            completeness = min(96.0, 60.0 + min(22.0, word_count * 0.5) + overlap_ratio * 25.0)
            misconceptions = []
            penalty = 0.0
            reasoning = "The student accurately articulates the core operational mechanism with solid technical precision."
        elif overlap_ratio >= 0.20:
            # Partial understanding: grasps main premise, lacks depth or secondary mechanics
            correctness = round(52.0 + (overlap_ratio - 0.20) * 80.0, 1)
            completeness = round(42.0 + min(24.0, word_count * 0.5), 1)
            misconceptions = []
            penalty = 0.0
            reasoning = "The student understands the high-level concept but omits underlying causal mechanisms."
        else:
            # Low overlap: severe misconception, keyword mismatch, or irrelevant answer
            correctness = round(max(5.0, overlap_ratio * 120.0), 1)
            completeness = round(max(5.0, min(18.0, word_count * 0.3)), 1)
            misconceptions = ["Demonstrates significant conceptual drift or misunderstanding of core mechanics."]
            penalty = 10.0
            reasoning = "The response lacks essential domain concepts or demonstrates fundamental misconceptions."

        raw_score = max(0.0, (0.55 * correctness + 0.45 * completeness) - penalty)
        score = round(max(0.0, min(100.0, raw_score)), 1)
        v_label = "correct" if score >= 75.0 else ("almost_correct" if score >= 55.0 else "wrong")

        return json.dumps({
            "score": score,
            "correctness": round(correctness, 1),
            "completeness": round(completeness, 1),
            "missing_points": [
                "Could elaborate further on edge conditions or trade-offs."
            ] if overlap_ratio >= 0.20 else ["Core operational mechanisms and foundational principles."],
            "misconceptions": misconceptions,
            "reasoning": reasoning,
            "relevance": 95 if overlap_ratio >= 0.20 else 25,
            "verdict": v_label,
            "conceptual_accuracy": round(correctness, 1),
            "key_point_coverage": round(completeness, 1),
            "misconception_penalty": penalty,
            "judge_score": score,
            "strengths": [
                "Captured the fundamental mechanisms in your own words accurately."
            ] if overlap_ratio >= 0.20 else ["Attempted active retrieval."],
            "missing_concepts": [
                "Could elaborate further on edge conditions or trade-offs."
            ],
            "actionable_tip": "Connect this concept directly to how its immediate prerequisite enables it in practice."
        })

    # Case 2: Concept Extraction Prompt
    if "extract key concepts" in prompt_lower or "dependency extraction" in prompt_lower:
        return json.dumps({
            "concepts": [
                {
                    "id": "c1",
                    "title": "Fundamental Prerequisite Concept",
                    "summary": "Core baseline concept needed before advanced ideas.",
                    "canonical_explanation": "The foundational mechanism providing baseline principles.",
                    "key_points": ["Establishes baseline mechanics", "Enables downstream architecture"],
                    "prerequisites": []
                },
                {
                    "id": "c2",
                    "title": "Intermediate Dependent Concept",
                    "summary": "Builds upon fundamental concepts to achieve deeper functionality.",
                    "canonical_explanation": "Extends basic mechanics with adaptive rules.",
                    "key_points": ["Depends on baseline mechanisms", "Introduces dynamic behavior"],
                    "prerequisites": ["c1"]
                }
            ]
        })

    # Case 3: Socratic Hints Generation
    if "socratic hint" in prompt_lower or "progressive hint" in prompt_lower:
        title_m = re.search(r"\[CONCEPT\]:\s*(.*?)(?:\n|$)", prompt, re.IGNORECASE)
        title = title_m.group(1).strip() if title_m else "the concept"
        return json.dumps({
            "hint_tier_1": f"Think of {title} from a high-level real-world perspective: what primary problem is it solving in the system?",
            "hint_tier_2": f"Consider the step-by-step mechanism: what data structure or table is looked up, and what happens next?",
            "hint_tier_3": f"Targeted Guiding Question: What specific failure or bottleneck occurs if {title} is omitted?"
        })

    # Case 4: General AI Teacher Conversational Response
    return (
        "That's a thoughtful question! When studying this concept, consider how it interacts with the system's foundational components. "
        "Take a moment to review the key principles from your notes, and we can explore any specific mechanism that feels unclear. 😊"
    )
