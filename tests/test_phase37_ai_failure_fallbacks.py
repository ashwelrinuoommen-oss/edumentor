"""
Test Suite for Phase 37 — AI Failure Fallbacks.
Verifies the universal 4-stage pipeline for all AI operations:
  Validation -> Retry -> Fallback -> User-friendly error

Validates:
- Schema validation against strict schemas.
- Never assuming model returns valid JSON (handling markdown fences, trailing commas, single quotes, preamble, truncation).
- Automatic retry on schema or parse failure.
- Deterministic heuristic fallbacks for all AI operations.
- User-friendly error messages when all else fails.
"""

import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from edumentor.ai.schemas import (
    BaseSchema,
    ConceptExtractionSchema,
    QuestionGenerationSchema,
    EvaluationJudgeSchema,
    SocraticHintsSchema,
    ConversationalReplySchema,
    validate_schema,
    SchemaValidationError
)

from edumentor.ai.fallback_pipeline import (
    safe_parse_json,
    AIPipelineResult,
    execute_ai_pipeline
)

from edumentor.llm import LLMConfig, call_llm_json, call_llm_with_fallback
from edumentor.evaluation import evaluate_with_llm_judge, generate_socratic_hints
from edumentor.extractor import extract_concepts_from_text
from edumentor.ai.question_generator import generate_recall_question
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.utils.error_handler import ERROR_LLM_MSG, ERROR_PROCESSING_MSG


class TestPhase37AIFailureFallbacks(unittest.TestCase):

    # -------------------------------------------------------------------------
    # 1. JSON ROBUSTNESS ("Never assume the model returns valid JSON")
    # -------------------------------------------------------------------------
    def test_safe_parse_json_markdown_fences(self):
        """Verify markdown code blocks with and without json tag are parsed cleanly."""
        text = "```json\n{\"question\": \"What is paging?\", \"difficulty_level\": \"easy\"}\n```"
        parsed, err = safe_parse_json(text)
        self.assertIsNone(err)
        self.assertEqual(parsed["question"], "What is paging?")
        self.assertEqual(parsed["difficulty_level"], "easy")

        text_bare_fence = "```\n{\"correctness\": 90, \"completeness\": 80}\n```"
        parsed2, err2 = safe_parse_json(text_bare_fence)
        self.assertIsNone(err2)
        self.assertEqual(parsed2["correctness"], 90)

    def test_safe_parse_json_trailing_commas(self):
        """Verify trailing commas in objects and arrays are healed."""
        text = '{"items": [1, 2, 3,], "metadata": {"status": "ok",},}'
        parsed, err = safe_parse_json(text)
        self.assertIsNone(err)
        self.assertEqual(parsed["items"], [1, 2, 3])
        self.assertEqual(parsed["metadata"]["status"], "ok")

    def test_safe_parse_json_single_quotes(self):
        """Verify single-quoted JSON keys and values are parsed."""
        text = "{'title': 'Virtual Memory', 'concepts': ['paging', 'segmentation']}"
        parsed, err = safe_parse_json(text)
        self.assertIsNone(err)
        self.assertEqual(parsed["title"], "Virtual Memory")
        self.assertEqual(len(parsed["concepts"]), 2)

    def test_safe_parse_json_preamble_and_postamble(self):
        """Verify conversational filler before and after JSON structure is ignored."""
        text = (
            "Certainly! Here is the evaluation JSON according to your schema:\n\n"
            "{\"correctness\": 82, \"completeness\": 75, \"reasoning\": \"Good response.\"}\n\n"
            "Let me know if you need any adjustments!"
        )
        parsed, err = safe_parse_json(text)
        self.assertIsNone(err)
        self.assertEqual(parsed["correctness"], 82)
        self.assertEqual(parsed["completeness"], 75)

    def test_safe_parse_json_python_literals(self):
        """Verify Python literals (True, False, None) are coerced to valid JSON."""
        text = '{"grounded_in_notes": True, "active": False, "extra": None}'
        parsed, err = safe_parse_json(text)
        self.assertIsNone(err)
        self.assertTrue(parsed["grounded_in_notes"])
        self.assertFalse(parsed["active"])
        self.assertIsNone(parsed["extra"])

    def test_safe_parse_json_truncated_auto_healing(self):
        """Verify truncated JSON with missing closing braces is auto-healed."""
        text = '{"title": "Deadlock", "summary": "Circular wait among processes"'
        parsed, err = safe_parse_json(text)
        self.assertIsNone(err)
        self.assertEqual(parsed["title"], "Deadlock")
        self.assertEqual(parsed["summary"], "Circular wait among processes")

    def test_safe_parse_json_garbage_returns_error(self):
        """Verify non-JSON garbage returns error without raising an exception."""
        text = "I am an AI and I cannot generate this response."
        parsed, err = safe_parse_json(text)
        self.assertIsNone(parsed)
        self.assertIsNotNone(err)

    # -------------------------------------------------------------------------
    # 2. SCHEMA VALIDATION TESTS
    # -------------------------------------------------------------------------
    def test_concept_extraction_schema_validation(self):
        """Verify ConceptExtractionSchema accepts valid formats and rejects invalid."""
        valid_data = {
            "concepts": [
                {
                    "title": "Process Scheduling",
                    "summary": "Allocating CPU time to processes.",
                    "canonical_explanation": "The OS scheduler switches execution context.",
                    "key_points": ["Ready queue", "Dispatcher context switch"],
                    "prerequisites": ["Process State"]
                }
            ]
        }
        ok, err, norm = ConceptExtractionSchema.validate(valid_data)
        self.assertTrue(ok)
        self.assertIsNone(err)
        self.assertEqual(norm["concepts"][0]["id"], "c_1")

        # Invalid: missing concepts list
        ok, err, _ = ConceptExtractionSchema.validate({"status": "no concepts"})
        self.assertFalse(ok)
        self.assertIn("Expected 'concepts' list", err)

        # Invalid: empty concepts list
        ok, err, _ = ConceptExtractionSchema.validate({"concepts": []})
        self.assertFalse(ok)
        self.assertIn("must not be empty", err)

        # Invalid: concept missing title
        ok, err, _ = ConceptExtractionSchema.validate({"concepts": [{"summary": "No title"}]})
        self.assertFalse(ok)
        self.assertIn("missing valid 'title'", err)

    def test_question_generation_schema_validation(self):
        """Verify QuestionGenerationSchema validates length and presence."""
        valid_q = {
            "question": "How does a translation lookaside buffer accelerate virtual address translation?",
            "difficulty_level": "hard"
        }
        ok, err, norm = QuestionGenerationSchema.validate(valid_q)
        self.assertTrue(ok)
        self.assertIsNone(err)
        self.assertEqual(norm["difficulty_level"], "hard")

        # Too short question
        short_q = {"question": "What is OS?"}
        ok, err, _ = QuestionGenerationSchema.validate(short_q)
        self.assertFalse(ok)
        self.assertIn("Question too short", err)

        # Missing question
        no_q = {"difficulty_level": "easy"}
        ok, err, _ = QuestionGenerationSchema.validate(no_q)
        self.assertFalse(ok)
        self.assertIn("Missing or invalid 'question'", err)

    def test_evaluation_judge_schema_validation(self):
        """Verify EvaluationJudgeSchema validates numerical bounds and criteria."""
        valid_eval = {
            "correctness": 88.5,
            "completeness": 72.0,
            "reasoning": "Accurate explanation of paging.",
            "missing_points": ["TLB hit ratio"],
            "strengths": ["Clear understanding of page tables"]
        }
        ok, err, norm = EvaluationJudgeSchema.validate(valid_eval)
        self.assertTrue(ok)
        self.assertEqual(norm["verdict"], "correct")
        self.assertEqual(norm["correctness"], 88.5)

        # Out of bounds score
        bad_score = {"correctness": 125, "completeness": 50}
        ok, err, _ = EvaluationJudgeSchema.validate(bad_score)
        self.assertFalse(ok)
        self.assertIn("out of bounds", err)

        # Missing correctness
        missing_c = {"completeness": 50}
        ok, err, _ = EvaluationJudgeSchema.validate(missing_c)
        self.assertFalse(ok)
        self.assertIn("Missing required field 'correctness'", err)

    def test_socratic_hints_schema_validation(self):
        """Verify SocraticHintsSchema ensures all 3 tiers are present and adequate."""
        valid_hints = {
            "hint_tier_1": "Think of virtual memory as an abstraction over physical RAM.",
            "hint_tier_2": "Consider what happens during a page fault exception.",
            "hint_tier_3": "What specific hardware structure translates the virtual page number?"
        }
        ok, err, norm = SocraticHintsSchema.validate(valid_hints)
        self.assertTrue(ok)
        self.assertEqual(norm["hint_tier_1"], valid_hints["hint_tier_1"])

        # Missing tier 2
        bad_hints = {
            "hint_tier_1": "Think of virtual memory as an abstraction.",
            "hint_tier_3": "What specific hardware structure translates?"
        }
        ok, err, _ = SocraticHintsSchema.validate(bad_hints)
        self.assertFalse(ok)
        self.assertIn("hint_tier_2", err)

    def test_conversational_reply_schema_validation(self):
        """Verify ConversationalReplySchema validates text and filters error banners."""
        valid_text = "That's a great question about thread synchronization! Let's explore mutexes."
        ok, err, norm = ConversationalReplySchema.validate(valid_text)
        self.assertTrue(ok)
        self.assertEqual(norm, valid_text)

        # Rejects leaked exception trace
        bad_text = "Traceback (most recent call last):\n  File 'server.py', line 12\nKeyError: concept_id"
        ok, err, _ = ConversationalReplySchema.validate(bad_text)
        self.assertFalse(ok)
        self.assertIn("Detected raw Python exception trace", err)

    # -------------------------------------------------------------------------
    # 3. THE 4-STAGE PIPELINE: Validation -> Retry -> Fallback -> User-friendly error
    # -------------------------------------------------------------------------
    def test_pipeline_stage1_validation_success(self):
        """Verify pipeline returns on Stage 1 (Validation) if first LLM response is valid."""
        llm_mock = MagicMock(return_value='{"question": "How does mutex locking prevent race conditions?", "difficulty_level": "medium"}')

        result = execute_ai_pipeline(
            operation_name="test_op",
            llm_callable=lambda attempt, prev: llm_mock(),
            schema=QuestionGenerationSchema,
            max_retries=2
        )

        self.assertTrue(result.success)
        self.assertEqual(result.stage, "validation")
        self.assertEqual(result.attempts, 1)
        self.assertFalse(result.fallback_used)
        self.assertEqual(result["difficulty_level"], "medium")

    def test_pipeline_stage2_retry_success(self):
        """Verify pipeline retries upon invalid JSON / schema error and succeeds on attempt 2."""
        call_count = 0

        def simulated_llm(attempt, prev_err):
            nonlocal call_count
            call_count += 1
            if attempt == 1:
                # Malformed output missing 'question'
                return '{"wrong_field": "oops"}'
            else:
                # Fixed valid output on retry
                return '{"question": "How does mutex locking prevent race conditions?", "difficulty_level": "medium"}'

        result = execute_ai_pipeline(
            operation_name="test_op_retry",
            llm_callable=simulated_llm,
            schema=QuestionGenerationSchema,
            max_retries=2
        )

        self.assertTrue(result.success)
        self.assertEqual(result.stage, "retry")
        self.assertEqual(result.attempts, 2)
        self.assertFalse(result.fallback_used)
        self.assertEqual(call_count, 2)
        self.assertEqual(len(result.errors), 1)

    def test_pipeline_stage3_fallback_execution(self):
        """Verify that when all retries are exhausted, the fallback function is executed."""
        call_count = 0

        def always_broken_llm(attempt, prev_err):
            nonlocal call_count
            call_count += 1
            return "Sorry, I am unable to output JSON today."

        def fallback_fn():
            return {
                "question": "Can you explain the difference between a process and a thread in your own words?",
                "difficulty_level": "easy",
                "grounded_in_notes": True
            }

        result = execute_ai_pipeline(
            operation_name="test_op_fallback",
            llm_callable=always_broken_llm,
            schema=QuestionGenerationSchema,
            max_retries=2,
            fallback_fn=fallback_fn
        )

        self.assertTrue(result.success)
        self.assertEqual(result.stage, "fallback")
        self.assertTrue(result.fallback_used)
        self.assertEqual(result.attempts, 3)  # 1 initial + 2 retries
        self.assertEqual(call_count, 3)
        self.assertIn("process and a thread", result["question"])

    def test_pipeline_stage4_user_friendly_error(self):
        """Verify that if both LLM retries and fallback fail, a user-friendly error is returned."""
        def broken_llm(attempt, prev_err):
            return "Broken response"

        def broken_fallback():
            raise RuntimeError("Fallback also failed!")

        result = execute_ai_pipeline(
            operation_name="test_op_error",
            llm_callable=broken_llm,
            schema=QuestionGenerationSchema,
            max_retries=1,
            fallback_fn=broken_fallback,
            user_friendly_error=ERROR_LLM_MSG
        )

        self.assertFalse(result.success)
        self.assertEqual(result.stage, "error")
        self.assertEqual(result.error_message, ERROR_LLM_MSG)

    # -------------------------------------------------------------------------
    # 4. APPLICATION-WIDE AI OPERATIONS INTEGRATION
    # -------------------------------------------------------------------------
    def test_concept_extraction_falls_back_to_heuristic_on_malformed_llm(self):
        """Verify extract_concepts_from_text falls back to heuristic engine when LLM returns invalid JSON."""
        study_notes = (
            "OPERATING SYSTEMS NOTES\n\n"
            "Process Management\n"
            "A process is a program in execution. It contains program counter, stack, and data section.\n\n"
            "CPU Scheduling\n"
            "The CPU scheduler selects from among the processes in memory that are ready to execute."
        )

        # Mock LLM returning broken garbage
        with patch("edumentor.extractor.call_llm", return_value="Here are concepts: 1. Process 2. CPU"):
            concepts, deps = extract_concepts_from_text(study_notes, curriculum_title="OS")
            
            self.assertIsInstance(concepts, list)
            self.assertGreater(len(concepts), 0)
            # The heuristic extractor extracted concepts safely!
            first_title = concepts[0]["title"].lower()
            self.assertTrue("process" in first_title or "operating" in first_title or "cpu" in first_title)

    def test_question_generator_falls_back_to_heuristic_on_malformed_llm(self):
        """Verify generate_recall_question returns a grounded question even if LLM fails validation."""
        concept = {
            "id": "c_vm",
            "title": "Virtual Memory",
            "canonical_explanation": "Virtual memory separates user logical memory from physical memory using paging.",
            "note_chunks": ["Virtual memory separates user logical memory from physical memory using paging."]
        }
        
        gemini_config = LLMConfig(provider="gemini", api_key="dummy_key")

        # Mock call_llm returning unparseable text
        with patch("edumentor.llm.call_llm", return_value="Invalid non-JSON question"):
            question = generate_recall_question(concept, llm_config=gemini_config)

            self.assertIsInstance(question, str)
            self.assertGreater(len(question), 15)
            self.assertIn("Virtual Memory", question)

    def test_recall_judge_falls_back_to_heuristic_on_malformed_llm(self):
        """Verify evaluate_with_llm_judge falls back to semantic heuristic when LLM returns garbage."""
        concept = {
            "title": "Virtual Memory",
            "canonical_explanation": "Virtual memory provides an illusion of large contiguous memory using paging.",
            "key_points": ["Paging", "Page table", "Address translation"]
        }
        student_answer = "Virtual memory allows the computer to use hard disk space as RAM using paging."
        gemini_config = LLMConfig(provider="gemini", api_key="dummy_key")

        with patch("edumentor.llm.call_llm", return_value="Not valid JSON judge"):
            eval_result = evaluate_with_llm_judge(
                concept_title=concept,
                student_answer=student_answer,
                llm_config=gemini_config
            )

            self.assertIsInstance(eval_result, dict)
            self.assertIn("score", eval_result)
            self.assertIn("verdict", eval_result)
            self.assertIn("reasoning", eval_result)
            self.assertGreater(eval_result["score"], 0)

    def test_socratic_hints_falls_back_to_templates_on_malformed_llm(self):
        """Verify generate_socratic_hints falls back to progressive templates on LLM failure."""
        gemini_config = LLMConfig(provider="gemini", api_key="dummy_key")

        with patch("edumentor.llm.call_llm", return_value="{'incomplete_hints': true}"):
            hints = generate_socratic_hints(
                concept_title="Mutex Locking",
                canonical_explanation="A mutex guarantees mutual exclusion in critical sections.",
                key_points=["acquire", "release"],
                llm_config=gemini_config
            )

            self.assertIsInstance(hints, dict)
            self.assertIn("hint_tier_1", hints)
            self.assertIn("hint_tier_2", hints)
            self.assertIn("hint_tier_3", hints)
            self.assertIn("Mutex Locking", hints["hint_tier_1"])

    def test_chat_conversational_reply_falls_back_gracefully_on_llm_failure(self):
        """Verify handle_user_chat uses conversational fallback when LLM provider drops connection."""
        orch = EduMentorOrchestrator(student_name="Test Student")
        orch.initialize_home()
        orch.load_sample_module("Operating Systems")

        # Simulate LLM returning error message
        with patch("edumentor.orchestrator.call_llm", return_value=ERROR_LLM_MSG):
            payload = orch.handle_user_chat("Can you explain how threads work?")

            self.assertIsInstance(payload, dict)
            last_message = orch.chat_history[-1]
            self.assertEqual(last_message["role"], "assistant")
            self.assertEqual(last_message["content"], ERROR_LLM_MSG)

    def test_call_llm_json_pipeline_integration(self):
        """Verify call_llm_json uses the Phase 37 pipeline and returns data cleanly."""
        mock_output = '```json\n{"status": "ok", "count": 42}\n```'
        with patch("edumentor.llm.call_llm", return_value=mock_output):
            result = call_llm_json("Return status")
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["count"], 42)


if __name__ == "__main__":
    unittest.main()
