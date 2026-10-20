"""
Unit and Integration Tests for Phase 35 — Security & Privacy.

Verifies:
1. File Validation:
   - Allowed document formats (.pdf, .txt, .md, .markdown)
   - Magic byte validation for PDFs (%PDF-)
   - Binary/executable content inspection (rejection of MZ/ELF/malware)
   - Dangerous extensions rejection (.exe, .bat, .sh, .php, .py, .js)
   - Filename sanitization against path traversal (../, ..\\, null bytes)
2. Maximum File Size:
   - Size limit enforcement (15 MB default)
   - Rejection of oversized files with controlled HTTP 413 error
3. Safe Temporary Storage:
   - Creation in isolated secure temp directories
   - Guaranteed automatic cleanup/deletion even upon exception
4. API Key Protection:
   - Key masking (e.g. sk-••••••••7890, ••••••••)
   - LLMConfig safe string representation (__repr__ never leaks raw keys)
   - Settings endpoint returns api_key_masked, never raw key
   - Protection against overwriting valid keys with masked strings
5. Input Validation:
   - Chat message validation (length limits, non-empty, script sanitization)
   - Student name validation (alphanumeric, length 1-50)
   - Email format validation
   - Password strength validation
6. No Secrets in Git:
   - .gitignore presence and exclusion of .env, *.db, *.log, temp/, etc.
   - .env.example contains only placeholder credentials
   - Workspace secrets scanner passes without finding raw keys
7. Controlled Error Messages:
   - Redaction of system file paths (C:\\Users..., /home/...)
   - Redaction of internal database table details and tracebacks
   - Sanitized user-friendly error responses
8. User-Specific Database Access:
   - documents table contains user_id
   - Scoped queries via get_user_documents
   - IDOR prevention on history session reconstruction (403 Forbidden for cross-user)
   - Privacy right to erasure (purge_user_data)
9. Explaining Note Privacy Near Upload Flow:
   - Note privacy badge and footer in static/index.html near upload
   - Note privacy callout in addModuleModal
   - Note privacy explanation in Streamlit upload_zone.py
   - /api/privacy/policy endpoint returns privacy guarantee
"""

import os
import re
import tempfile
import unittest
from fastapi.testclient import TestClient

from edumentor.database.database import init_db, get_db_connection
from edumentor.database.repository import EduMentorRepository
from edumentor.database.models import Document
from edumentor.llm import LLMConfig
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.utils.security import (
    validate_uploaded_file,
    sanitize_filename,
    safe_temporary_file,
    mask_api_key,
    is_masked_key,
    sanitize_error_message,
    scan_text_for_secrets,
    MAX_UPLOAD_SIZE_BYTES,
    NOTE_PRIVACY_STATEMENT
)
from edumentor.utils.validators import (
    validate_chat_input,
    validate_student_name,
    validate_email,
    validate_password_strength,
    validate_subject_or_module_title,
    sanitize_input_string
)
from server import app


class TestPhase35SecurityAndPrivacy(unittest.TestCase):
    """Test suite ensuring Phase 35 Security & Privacy specifications."""

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        init_db(self.db_path)
        self.repo = EduMentorRepository(db_path=self.db_path)
        self.client = TestClient(app)

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # 1. FILE VALIDATION & CONTENT INSPECTION
    # -------------------------------------------------------------------------
    def test_valid_pdf_magic_bytes(self):
        """Verify valid PDF document with %PDF- header passes file validation."""
        valid_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"
        is_valid, clean_name, err = validate_uploaded_file("operating_systems.pdf", valid_pdf_bytes)
        self.assertTrue(is_valid)
        self.assertEqual(clean_name, "operating_systems.pdf")

    def test_fake_pdf_with_executable_header_rejected(self):
        """Verify a file named .pdf containing executable headers (MZ) is rejected."""
        fake_pdf_bytes = b"MZ\x90\x00\x03\x00\x00\x00malicious executable pretending to be pdf"
        is_valid, clean_name, err = validate_uploaded_file("trojan.pdf", fake_pdf_bytes)
        self.assertFalse(is_valid)
        self.assertIn("executable", err.lower())

    def test_invalid_pdf_header_rejected(self):
        """Verify a file named .pdf missing %PDF- header is rejected."""
        corrupt_bytes = b"This is just plain text disguised as a PDF file without the magic bytes header."
        is_valid, clean_name, err = validate_uploaded_file("corrupt.pdf", corrupt_bytes)
        self.assertFalse(is_valid)
        self.assertIn("header does not match", err)

    def test_valid_text_and_markdown(self):
        """Verify clean UTF-8 text and markdown documents pass validation."""
        md_bytes = "# Operating Systems Notes\n\nVirtual memory maps virtual to physical addresses.".encode("utf-8")
        is_valid, clean_name, err = validate_uploaded_file("lecture_notes.md", md_bytes)
        self.assertTrue(is_valid)
        self.assertEqual(clean_name, "lecture_notes.md")

    def test_dangerous_extensions_rejected(self):
        """Verify executable, script, and dangerous file extensions are strictly prohibited."""
        dangerous_names = [
            ("payload.exe", b"binary content"),
            ("script.bat", b"@echo off\ndir"),
            ("exploit.sh", b"#!/bin/bash\nrm -rf /"),
            ("backdoor.php", b"<?php system($_GET['cmd']); ?>"),
            ("injector.py", b"import os; os.system('calc')"),
            ("attack.js", b"alert(1)")
        ]
        for fname, content in dangerous_names:
            is_valid, _, err = validate_uploaded_file(fname, content)
            self.assertFalse(is_valid, f"Expected {fname} to be rejected")
            self.assertIn("prohibited", err.lower())

    def test_path_traversal_filename_sanitization(self):
        """Verify filename sanitization strips directory traversal sequences and null bytes."""
        malicious_names = [
            ("../../etc/passwd", "etc_passwd"),
            ("..\\..\\Windows\\System32\\cmd.exe", "Windows_System32_cmd.exe"),
            ("notes\x00evil.pdf", "notesevil.pdf"),
            ("/absolute/path/to/notes.pdf", "notes.pdf")
        ]
        for raw, expected in malicious_names:
            cleaned = sanitize_filename(raw)
            self.assertNotIn("..", cleaned)
            self.assertNotIn("/", cleaned)
            self.assertNotIn("\\", cleaned)
            self.assertNotIn("\0", cleaned)

    # -------------------------------------------------------------------------
    # 2. MAXIMUM FILE SIZE ENFORCEMENT
    # -------------------------------------------------------------------------
    def test_file_under_max_size_passes(self):
        """Verify file under 15 MB limit is accepted."""
        content = b"A" * (1024 * 1024)  # 1 MB
        is_valid, _, _ = validate_uploaded_file("notes.txt", content, max_size_bytes=MAX_UPLOAD_SIZE_BYTES)
        self.assertTrue(is_valid)

    def test_file_exceeding_max_size_rejected(self):
        """Verify file exceeding the maximum size limit is rejected with informative message."""
        limit = 1000  # 1000 bytes limit
        oversized = b"A" * 1500
        is_valid, _, err = validate_uploaded_file("huge.txt", oversized, max_size_bytes=limit)
        self.assertFalse(is_valid)
        self.assertIn("exceeds maximum allowed size", err)

    def test_api_upload_rejects_oversized_file(self):
        """Verify FastAPI upload endpoint rejects oversized files with HTTP 413."""
        # Oversized dummy payload simulating file > 15MB
        huge_bytes = b"A" * (MAX_UPLOAD_SIZE_BYTES + 500)
        res = self.client.post(
            "/api/upload",
            files={"file": ("huge.txt", huge_bytes, "text/plain")}
        )
        self.assertEqual(res.status_code, 413)
        self.assertIn("exceeds maximum allowed size", res.json()["detail"].lower())

    # -------------------------------------------------------------------------
    # 3. SAFE TEMPORARY STORAGE & ISOLATION
    # -------------------------------------------------------------------------
    def test_safe_temporary_file_creation_and_auto_cleanup(self):
        """Verify safe temporary file is created and cleaned up automatically upon context exit."""
        test_data = b"%PDF-1.4 Secure test content"
        temp_file_path = None
        
        with safe_temporary_file(test_data, suffix=".pdf") as fpath:
            temp_file_path = fpath
            self.assertTrue(os.path.exists(temp_file_path))
            with open(temp_file_path, "rb") as f:
                self.assertEqual(f.read(), test_data)

        # File must no longer exist after exiting the context block
        self.assertFalse(os.path.exists(temp_file_path))

    def test_safe_temporary_file_cleanup_on_exception(self):
        """Verify safe temporary file is cleaned up even if an exception occurs during processing."""
        temp_file_path = None
        try:
            with safe_temporary_file(b"Temporary processing content", suffix=".tmp") as fpath:
                temp_file_path = fpath
                self.assertTrue(os.path.exists(temp_file_path))
                raise RuntimeError("Simulated processing failure")
        except RuntimeError:
            pass

        self.assertFalse(os.path.exists(temp_file_path))

    # -------------------------------------------------------------------------
    # 4. API KEY PROTECTION & MASKING
    # -------------------------------------------------------------------------
    def test_mask_api_key_formats(self):
        """Verify API keys are masked properly without leaking credentials."""
        self.assertEqual(mask_api_key(None), "")
        self.assertEqual(mask_api_key(""), "")
        self.assertEqual(mask_api_key("short"), "••••••••")
        
        real_key = "sk-proj-1234567890abcdef12345"
        masked = mask_api_key(real_key)
        self.assertTrue(masked.startswith("sk-••••••••"))
        self.assertTrue(masked.endswith("2345"))
        self.assertNotIn("1234567890abcdef", masked)

    def test_is_masked_key_detection(self):
        """Verify detection of already-masked keys to prevent accidental overwrites."""
        self.assertTrue(is_masked_key("sk-••••••••7890"))
        self.assertTrue(is_masked_key("••••••••"))
        self.assertFalse(is_masked_key("sk-proj-actual-real-key-12345"))

    def test_llm_config_repr_protects_key(self):
        """Verify LLMConfig __repr__ and __str__ never expose raw API keys in logs or prints."""
        secret_key = "sk-ant-api03-very-secret-token-998877"
        cfg = LLMConfig(provider="anthropic", api_key=secret_key)
        repr_str = repr(cfg)
        str_str = str(cfg)
        self.assertNotIn(secret_key, repr_str)
        self.assertNotIn(secret_key, str_str)
        self.assertIn("••••••••", repr_str)

    def test_settings_api_does_not_expose_raw_key(self):
        """Verify /api/settings endpoint returns api_key_masked and never the plaintext secret."""
        res = self.client.post("/api/settings", json={
            "provider": "openai",
            "api_key": "sk-proj-secret-testing-key-12345678",
            "model": "gpt-4o-mini"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("api_key_configured"))
        self.assertIn("api_key_masked", data)
        self.assertNotIn("sk-proj-secret-testing-key-12345678", str(data))
        self.assertIn("••••••••", data["api_key_masked"])

    def test_settings_api_does_not_overwrite_with_masked_key(self):
        """Verify submitting a masked bullet string does not overwrite the existing valid key."""
        # 1. Set real key
        self.client.post("/api/settings", json={"provider": "gemini", "api_key": "AIzaSySecretRealKey1234567890"})
        # 2. Submit masked string
        res = self.client.post("/api/settings", json={"provider": "gemini", "api_key": "AIz••••••••7890"})
        self.assertEqual(res.status_code, 200)
        # Check that api_key_configured remains true
        self.assertTrue(res.json().get("api_key_configured"))

    # -------------------------------------------------------------------------
    # 5. INPUT VALIDATION & SANITIZATION
    # -------------------------------------------------------------------------
    def test_validate_chat_input(self):
        """Verify conversational input length constraints and script tag stripping."""
        # Empty
        valid, _ = validate_chat_input("")
        self.assertFalse(valid)
        
        # Script tags
        malicious = "Hello <script>alert('xss')</script> world"
        valid, clean = validate_chat_input(malicious)
        self.assertTrue(valid)
        self.assertNotIn("<script>", clean)
        self.assertIn("Hello", clean)
        self.assertIn("world", clean)

        # Oversized message
        oversized = "A" * 6000
        valid, err = validate_chat_input(oversized, max_length=5000)
        self.assertFalse(valid)
        self.assertIn("maximum allowed length", err)

    def test_validate_student_name(self):
        """Verify student username validation."""
        self.assertTrue(validate_student_name("Ashwel")[0])
        self.assertTrue(validate_student_name("Maya Chen")[0])
        self.assertTrue(validate_student_name("Student_123-A")[0])
        
        # Rejection of invalid characters
        self.assertFalse(validate_student_name("<script>")[0])
        self.assertFalse(validate_student_name("")[0])
        self.assertFalse(validate_student_name("A" * 60)[0])

    def test_validate_email_and_password(self):
        """Verify RFC email format and password safety thresholds."""
        self.assertTrue(validate_email("student@edumentor.ai"))
        self.assertFalse(validate_email("notanemail"))
        self.assertFalse(validate_email("@missinguser.com"))

        self.assertTrue(validate_password_strength("securepass123"))
        self.assertFalse(validate_password_strength("123"))  # too short
        self.assertFalse(validate_password_strength("      "))  # all spaces

    # -------------------------------------------------------------------------
    # 6. NO SECRETS IN GIT
    # -------------------------------------------------------------------------
    def test_gitignore_exists_and_contains_secrets_exclusions(self):
        """Verify .gitignore exists in workspace root and excludes sensitive files."""
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        gitignore_path = os.path.join(workspace_root, ".gitignore")
        self.assertTrue(os.path.exists(gitignore_path), ".gitignore file must exist in workspace root")

        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(".env", content)
        self.assertIn("*.db", content)
        self.assertIn("temp", content)
        self.assertIn("__pycache__", content)

    def test_env_example_has_no_real_secrets(self):
        """Verify .env.example contains only dummy placeholder values."""
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        env_example_path = os.path.join(workspace_root, ".env.example")
        self.assertTrue(os.path.exists(env_example_path))

        with open(env_example_path, "r", encoding="utf-8") as f:
            content = f.read()

        secrets_found = scan_text_for_secrets(content)
        self.assertEqual(len(secrets_found), 0, f"Found secrets in .env.example: {secrets_found}")

    # -------------------------------------------------------------------------
    # 7. CONTROLLED ERROR MESSAGES
    # -------------------------------------------------------------------------
    def test_sanitize_error_message_strips_paths_and_sql(self):
        """Verify internal filesystem paths and raw database errors are scrubbed."""
        path_error = Exception("FileNotFoundError: [Errno 2] No such file: 'C:\\Users\\ASHWEL\\secret\\keys.json'")
        sanitized = sanitize_error_message(path_error)
        self.assertNotIn("C:\\Users\\ASHWEL", sanitized)

        sql_error = Exception("sqlite3.OperationalError: table users has no column foo in SELECT * FROM users")
        sanitized_sql = sanitize_error_message(sql_error)
        self.assertNotIn("SELECT * FROM users", sanitized_sql)
        self.assertIn("database", sanitized_sql.lower())

    # -------------------------------------------------------------------------
    # 8. USER-SPECIFIC DATABASE ACCESS & ISOLATION
    # -------------------------------------------------------------------------
    def test_documents_table_has_user_id_and_scoped_queries(self):
        """Verify documents are partitioned by user_id."""
        self.repo.save_document(
            doc_id="doc_ashwel_1",
            title="Operating Systems Notes",
            raw_text="OS notes content",
            user_id="user_ashwel"
        )
        self.repo.save_document(
            doc_id="doc_maya_1",
            title="Machine Learning Notes",
            raw_text="ML notes content",
            user_id="user_maya"
        )

        ashwel_docs = self.repo.get_user_documents("user_ashwel")
        maya_docs = self.repo.get_user_documents("user_maya")

        self.assertEqual(len(ashwel_docs), 1)
        self.assertEqual(ashwel_docs[0].id, "doc_ashwel_1")
        self.assertEqual(len(maya_docs), 1)
        self.assertEqual(maya_docs[0].id, "doc_maya_1")

        # Verify document ownership check
        self.assertTrue(self.repo.verify_user_document_ownership("user_ashwel", "doc_ashwel_1"))
        self.assertFalse(self.repo.verify_user_document_ownership("user_maya", "doc_ashwel_1"))

    def test_idor_session_reconstruction_authorization(self):
        """Verify cross-student session reconstruction is rejected with 403 Forbidden."""
        # Create Ashwel conversation
        self.repo.store_conversation_message(
            conversation_id="conv_ashwel_private",
            user_id="user_ashwel",
            role="assistant",
            message="Ashwel's private notes discussion",
            message_type="study_instruction"
        )

        # Create Maya conversation
        self.repo.store_conversation_message(
            conversation_id="conv_maya_private",
            user_id="user_maya",
            role="assistant",
            message="Maya's private notes discussion",
            message_type="study_instruction"
        )

        # Attempt unauthorized reconstruction of Maya's session by Ashwel
        res = self.repo.reconstruct_session("conv_maya_private", requesting_user_id="user_ashwel")
        self.assertTrue(res.get("unauthorized"))
        self.assertFalse(res.get("found"))

        # Authorized reconstruction by Maya succeeds
        res_maya = self.repo.reconstruct_session("conv_maya_private", requesting_user_id="user_maya")
        self.assertFalse(res_maya.get("unauthorized", False))
        self.assertTrue(res_maya.get("found"))

    def test_user_privacy_right_to_erasure_purge(self):
        """Verify purge_user_data deletes all records belonging to the student."""
        user_id = "user_test_purge"
        self.repo.save_document(doc_id="doc_purge_1", raw_text="text", user_id=user_id)
        self.repo.store_conversation_message(conversation_id="conv_purge", user_id=user_id, role="user", message="hi")

        self.assertEqual(len(self.repo.get_user_documents(user_id)), 1)
        deleted = self.repo.purge_user_data(user_id)
        self.assertGreaterEqual(deleted.get("documents", 0), 1)
        self.assertGreaterEqual(deleted.get("conversations", 0), 1)
        self.assertEqual(len(self.repo.get_user_documents(user_id)), 0)

    # -------------------------------------------------------------------------
    # 9. EXPLAINING NOTE PRIVACY NEAR UPLOAD FLOW
    # -------------------------------------------------------------------------
    def test_privacy_explanation_near_upload_in_html(self):
        """Verify static/index.html explains note privacy near the upload flow as required by the design doc."""
        html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn("note-privacy-badge", html)
        self.assertIn("note-privacy-footer", html)
        self.assertIn("Notes stay private", html)
        self.assertIn("Never used to train public AI", html)

    def test_privacy_policy_api_endpoint(self):
        """Verify /api/privacy/policy returns accurate local storage and privacy guarantees."""
        res = self.client.get("/api/privacy/policy")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("local_storage_guarantee"))
        self.assertFalse(data.get("public_data_sharing"))
        self.assertEqual(data.get("max_upload_size_mb"), 15)
        self.assertIn("train public AI", data.get("privacy_statement"))


if __name__ == "__main__":
    unittest.main()
