"""
Phase 36: Error Handling & Conversational Crash Prevention Test Suite.
Verifies that:
1. The conversational experience never abruptly crashes.
2. KeyError (e.g. KeyError: concept_id) or general processing errors show:
   "Hmm, something went wrong while processing that. Give me another moment and I'll try again."
3. Upload errors (corrupted PDF, unreadable pages, extraction failures) show:
   "I couldn't read that file properly. Try uploading the PDF again or send a text-based PDF."
4. LLM errors (API timeouts, network drops, provider failures) show:
   "I'm having trouble thinking through that one right now. Let's try again."
5. Session state machine recovers cleanly after errors without getting stuck.
6. FastAPI endpoints (/api/chat, /api/upload) and global exception handler return controlled friendly messages.
"""

import os
import io
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from server import app
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.llm import LLMConfig, call_llm
from edumentor.utils.error_handler import (
    ERROR_PROCESSING_MSG,
    ERROR_UPLOAD_MSG,
    ERROR_LLM_MSG,
    EduMentorError,
    EduMentorProcessingError,
    EduMentorUploadError,
    EduMentorLLMError,
    resolve_friendly_error,
    is_llm_error,
    is_upload_error,
)
from edumentor.extractor import extract_text_from_pdf


class TestPhase36ErrorHandling(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.orch = EduMentorOrchestrator(student_name="TestAshwel")
        self.orch.initialize_home()

    def test_canonical_error_constants_exact_wording(self):
        """Verify the exact wording of all 3 Phase 36 error messages."""
        self.assertEqual(
            ERROR_PROCESSING_MSG,
            "Hmm, something went wrong while processing that. Give me another moment and I'll try again."
        )
        self.assertEqual(
            ERROR_UPLOAD_MSG,
            "I couldn't read that file properly. Try uploading the PDF again or send a text-based PDF."
        )
        self.assertEqual(
            ERROR_LLM_MSG,
            "I'm having trouble thinking through that one right now. Let's try again."
        )

    def test_error_classification_helpers(self):
        """Verify is_llm_error and is_upload_error correctly categorize exceptions."""
        self.assertTrue(is_llm_error(EduMentorLLMError()))
        self.assertTrue(is_llm_error(Exception("Gemini connection error: timed out")))
        self.assertTrue(is_llm_error(Exception("OpenAI rate limit exceeded")))
        self.assertFalse(is_llm_error(KeyError("concept_id")))

        self.assertTrue(is_upload_error(EduMentorUploadError()))
        self.assertTrue(is_upload_error(Exception("pdfplumber corrupted PDF structure")))
        self.assertFalse(is_upload_error(KeyError("concept_id")))

    def test_resolve_friendly_error_mapping(self):
        """Verify resolve_friendly_error maps exceptions to the exact 3 specified messages."""
        # 1. General processing / KeyError
        self.assertEqual(
            resolve_friendly_error(KeyError("concept_id")),
            ERROR_PROCESSING_MSG
        )
        self.assertEqual(
            resolve_friendly_error(AttributeError("'NoneType' object has no attribute 'get'")),
            ERROR_PROCESSING_MSG
        )

        # 2. Upload errors
        self.assertEqual(
            resolve_friendly_error(EduMentorUploadError()),
            ERROR_UPLOAD_MSG
        )
        self.assertEqual(
            resolve_friendly_error(Exception("Failed to extract text from PDF"), context="upload"),
            ERROR_UPLOAD_MSG
        )

        # 3. LLM errors
        self.assertEqual(
            resolve_friendly_error(EduMentorLLMError()),
            ERROR_LLM_MSG
        )
        self.assertEqual(
            resolve_friendly_error(Exception("Anthropic API connection failed"), context="llm"),
            ERROR_LLM_MSG
        )

    def test_keyerror_concept_id_in_chat_shows_processing_message(self):
        """
        Verify that instead of crashing with:
        KeyError: concept_id
        EduMentor shows:
        "Hmm, something went wrong while processing that. Give me another moment and I'll try again."
        """
        self.orch.load_sample_module("Operating Systems")

        # Force an unexpected KeyError during conversational processing
        with patch.object(self.orch.memory, "format_llm_prompt_context", side_effect=KeyError("concept_id")):
            payload = self.orch.handle_user_chat("Can you explain how this concept works?")
            
            # The app did not crash!
            self.assertIsInstance(payload, dict)
            self.assertEqual(payload["status"], "ok")
            
            # The assistant message contains the exact specified friendly message
            last_message = self.orch.chat_history[-1]
            self.assertEqual(last_message["role"], "assistant")
            self.assertEqual(last_message["content"], ERROR_PROCESSING_MSG)
            self.assertEqual(payload.get("system_message"), ERROR_PROCESSING_MSG)

    def test_general_processing_exception_never_crashes_chat(self):
        """Verify unexpected runtime exceptions in handle_user_chat return ERROR_PROCESSING_MSG."""
        self.orch.load_sample_module("Operating Systems")

        with patch.object(self.orch.teacher_message_engine, "build_conversational_teacher_prompt", side_effect=ValueError("Unexpected processing failure")):
            payload = self.orch.handle_user_chat("Tell me more about threads.")
            
            self.assertIsInstance(payload, dict)
            last_message = self.orch.chat_history[-1]
            self.assertEqual(last_message["content"], ERROR_PROCESSING_MSG)

    def test_llm_error_in_chat_shows_llm_message(self):
        """
        For LLM errors:
        "I'm having trouble thinking through that one right now. Let's try again."
        """
        self.orch.load_sample_module("Operating Systems")

        with patch("edumentor.orchestrator.call_llm", side_effect=EduMentorLLMError()):
            payload = self.orch.handle_user_chat("What is the difference between paging and segmentation?")
            
            self.assertIsInstance(payload, dict)
            last_message = self.orch.chat_history[-1]
            self.assertEqual(last_message["role"], "assistant")
            self.assertEqual(last_message["content"], ERROR_LLM_MSG)
            self.assertEqual(payload.get("system_message"), ERROR_LLM_MSG)

    def test_call_llm_provider_exception_returns_llm_message(self):
        """Verify call_llm returns ERROR_LLM_MSG when external API call fails."""
        gemini_config = LLMConfig(provider="gemini", api_key="test_dummy_key")
        
        with patch("urllib.request.urlopen", side_effect=Exception("API request timed out")):
            response = call_llm("Explain virtual memory", config=gemini_config)
            self.assertEqual(response, ERROR_LLM_MSG)

    def test_upload_corrupt_pdf_shows_upload_error_message(self):
        """
        For upload errors:
        "I couldn't read that file properly. Try uploading the PDF again or send a text-based PDF."
        """
        # Valid header but corrupt/truncated body that causes pdfplumber to fail
        corrupt_pdf_bytes = b"%PDF-1.4\ncorrupt binary junk that cannot be parsed as valid xref or pages\n%%EOF"

        with self.assertRaises(EduMentorUploadError) as ctx:
            self.orch.ingest_pdf(corrupt_pdf_bytes, filename="CorruptLecture.pdf")

        self.assertEqual(str(ctx.exception), ERROR_UPLOAD_MSG)
        # Verify friendly message was also appended to chat history
        self.assertEqual(self.orch.chat_history[-1]["content"], ERROR_UPLOAD_MSG)

    def test_extract_text_from_pdf_corrupt_raises_upload_error(self):
        """Verify extract_text_from_pdf raises EduMentorUploadError for corrupt input."""
        corrupt_bytes = b"%PDF-1.4\nnot_valid_pdf_stream\n"
        with self.assertRaises(EduMentorUploadError) as ctx:
            extract_text_from_pdf(corrupt_bytes)
        self.assertEqual(str(ctx.exception), ERROR_UPLOAD_MSG)

    def test_conversation_continues_after_error_without_deadlock(self):
        """Verify that after an error occurs, the conversational loop continues normally on subsequent turns."""
        self.orch.load_sample_module("Operating Systems")

        # Turn 1: Incur an error
        with patch.object(self.orch.memory, "format_llm_prompt_context", side_effect=KeyError("concept_id")):
            payload1 = self.orch.handle_user_chat("Trigger error")
            self.assertEqual(self.orch.chat_history[-1]["content"], ERROR_PROCESSING_MSG)

        # Turn 2: Subsequent message must work cleanly without getting stuck
        payload2 = self.orch.handle_user_chat("I'm ready")
        self.assertIsInstance(payload2, dict)
        self.assertIn("WAITING", str(payload2["state"]))
        self.assertIsNotNone(self.orch.last_recall_question)

    def test_trigger_ready_for_recall_error_resilience(self):
        """Verify trigger_ready_for_recall catches unexpected exceptions and returns friendly error."""
        self.orch.load_sample_module("Operating Systems")

        with patch.object(self.orch, "generate_recall_question", side_effect=KeyError("concept_id")):
            payload = self.orch.trigger_ready_for_recall()
            self.assertIsInstance(payload, dict)
            self.assertEqual(self.orch.chat_history[-1]["content"], ERROR_PROCESSING_MSG)

    def test_submit_recall_response_error_resilience(self):
        """Verify submit_recall_response catches unexpected exceptions and returns friendly error."""
        self.orch.load_sample_module("Operating Systems")
        self.orch.trigger_ready_for_recall()

        with patch("edumentor.orchestrator.evaluate_recall", side_effect=KeyError("missing_eval_key")):
            payload = self.orch.submit_recall_response("Virtual memory translates virtual to physical.")
            self.assertIsInstance(payload, dict)
            self.assertEqual(self.orch.chat_history[-1]["content"], ERROR_PROCESSING_MSG)

    def test_advance_next_step_error_resilience(self):
        """Verify advance_next_step catches unexpected exceptions and returns friendly error."""
        self.orch.load_sample_module("Operating Systems")

        with patch.object(self.orch.state_machine, "transition_to", side_effect=RuntimeError("State transition bug")):
            payload = self.orch.advance_next_step()
            self.assertIsInstance(payload, dict)
            self.assertEqual(self.orch.chat_history[-1]["content"], ERROR_PROCESSING_MSG)

    def test_fastapi_chat_endpoint_never_crashes(self):
        """Verify /api/chat returns HTTP 200 with friendly message even if an exception escapes."""
        with patch.object(self.orch, "handle_user_chat", side_effect=KeyError("concept_id")):
            # Inject mock into server module orchestrator
            import server
            orig = server.orchestrator
            server.orchestrator = self.orch
            try:
                res = self.client.post("/api/chat", json={"message": "Can you explain this?"})
                self.assertEqual(res.status_code, 200)
                data = res.json()
                self.assertEqual(data.get("system_message"), ERROR_PROCESSING_MSG)
            finally:
                server.orchestrator = orig

    def test_fastapi_upload_endpoint_returns_upload_error_message(self):
        """Verify /api/upload returns HTTP 400 with ERROR_UPLOAD_MSG when PDF is corrupt."""
        corrupt_pdf_bytes = b"%PDF-1.4\ncorrupt binary junk\n%%EOF"
        files = {"file": ("unreadable.pdf", corrupt_pdf_bytes, "application/pdf")}
        res = self.client.post("/api/upload", files=files)
        
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertEqual(data.get("detail"), ERROR_UPLOAD_MSG)

    def test_fastapi_modules_upload_returns_upload_error_message(self):
        """Verify /api/modules/upload returns HTTP 400 with ERROR_UPLOAD_MSG when file is unreadable."""
        corrupt_pdf_bytes = b"%PDF-1.4\ncorrupt binary junk\n%%EOF"
        files = {"file": ("module_broken.pdf", corrupt_pdf_bytes, "application/pdf")}
        data = {"subject_title": "Operating Systems", "module_title": "Module 3"}
        res = self.client.post("/api/modules/upload", files=files, data=data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json().get("detail"), ERROR_UPLOAD_MSG)

    def test_global_exception_handler_returns_friendly_messages(self):
        """Verify global_exception_handler maps unhandled server exceptions to Phase 36 messages."""
        # 1. General KeyError -> ERROR_PROCESSING_MSG
        res = resolve_friendly_error(KeyError("concept_id"))
        self.assertEqual(res, ERROR_PROCESSING_MSG)

        # 2. Upload error -> ERROR_UPLOAD_MSG
        res_upload = resolve_friendly_error(EduMentorUploadError())
        self.assertEqual(res_upload, ERROR_UPLOAD_MSG)

        # 3. LLM error -> ERROR_LLM_MSG
        res_llm = resolve_friendly_error(EduMentorLLMError())
        self.assertEqual(res_llm, ERROR_LLM_MSG)

    def test_app_js_contains_phase36_error_handling(self):
        """Verify static/js/app.js contains Phase 36 friendly error strings and appendAssistantMessage."""
        app_js_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "js", "app.js")
        with open(app_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check appendAssistantMessage is implemented
        self.assertIn("function appendAssistantMessage", content)

        # Check friendly messages in app.js
        self.assertIn("Hmm, something went wrong while processing that. Give me another moment and I'll try again.", content)
        self.assertIn("I couldn't read that file properly. Try uploading the PDF again or send a text-based PDF.", content)


if __name__ == "__main__":
    unittest.main()
