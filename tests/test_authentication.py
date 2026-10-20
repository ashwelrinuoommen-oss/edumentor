"""
Unit and Integration Tests for Phase 1 Authentication.
Verifies:
- Login with email or username and password
- Sign Up with Name, Email, Password, Confirm Password, and optional 'What are you studying?'
- Forgot password & password reset
- Dynamic student name resolution from user profile (no hardcoded name)
"""

import os
import tempfile
import unittest

from edumentor.database.database import init_db
from edumentor.database.repository import EduMentorRepository
from edumentor.orchestrator import EduMentorOrchestrator
from edumentor.utils.security import hash_password, verify_password
from edumentor.utils.validators import validate_email, validate_password_strength


class TestAuthenticationPhase1(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        init_db(self.temp_db.name)
        self.repo = EduMentorRepository(db_path=self.temp_db.name)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_signup_creates_profile_with_dynamic_name(self):
        # Register a student with a custom name
        custom_name = "Kavya"
        custom_email = "kavya@university.edu"
        user = self.repo.create_user(
            username=custom_name,
            email=custom_email,
            password="SecurePassword456!",
            studying="Distributed Systems"
        )
        self.assertEqual(user.username, custom_name)
        self.assertEqual(user.email, custom_email)
        self.assertEqual(user.studying, "Distributed Systems")

        # Verify password was hashed securely (not plain text)
        self.assertNotEqual(user.password_hash, "SecurePassword456!")
        self.assertTrue(verify_password("SecurePassword456!", user.password_hash))

    def test_login_authentication_by_email_and_username(self):
        # Create student profile
        self.repo.create_user(
            username="Ashwel",
            email="ashwel@edumentor.ai",
            password="MySecretPassword123",
            studying="Operating Systems"
        )

        # Login via email
        user_by_email = self.repo.authenticate_user("ashwel@edumentor.ai", "MySecretPassword123")
        self.assertIsNotNone(user_by_email)
        self.assertEqual(user_by_email.username, "Ashwel")

        # Login via username
        user_by_username = self.repo.authenticate_user("Ashwel", "MySecretPassword123")
        self.assertIsNotNone(user_by_username)
        self.assertEqual(user_by_username.email, "ashwel@edumentor.ai")

        # Incorrect password fails
        bad_auth = self.repo.authenticate_user("ashwel@edumentor.ai", "WrongPassword")
        self.assertIsNone(bad_auth)

        # Unknown user fails
        unknown_auth = self.repo.authenticate_user("nobody@edumentor.ai", "Pass123")
        self.assertIsNone(unknown_auth)

    def test_forgot_password_reset_flow(self):
        self.repo.create_user(
            username="Rohan",
            email="rohan@study.org",
            password="OldPassword123"
        )

        # Reset password
        reset_success = self.repo.reset_password("rohan@study.org", "BrandNewPassword789")
        self.assertTrue(reset_success)

        # Old password no longer works
        old_login = self.repo.authenticate_user("rohan@study.org", "OldPassword123")
        self.assertIsNone(old_login)

        # New password works
        new_login = self.repo.authenticate_user("rohan@study.org", "BrandNewPassword789")
        self.assertIsNotNone(new_login)
        self.assertEqual(new_login.username, "Rohan")

        # Reset for non-existent email returns False
        unknown_reset = self.repo.reset_password("nonexistent@domain.com", "SomePass")
        self.assertFalse(unknown_reset)

    def test_orchestrator_dynamic_student_name_greeting(self):
        # Authenticated student Maya
        maya_user = self.repo.create_user(
            username="Maya Lin",
            email="maya.lin@domain.edu",
            password="MayaPassWord123",
            studying="Machine Learning"
        )

        # Initialize orchestrator with the authenticated student's profile name
        orch = EduMentorOrchestrator(student_name=maya_user.username)
        orch.initialize_home()

        self.assertEqual(orch.student_name, "Maya Lin")
        self.assertIn("Welcome back, Maya Lin!", orch.chat_history[0]["content"])
        self.assertNotIn("Ashwel", orch.chat_history[0]["content"])

    def test_input_validators(self):
        self.assertTrue(validate_email("student@university.edu"))
        self.assertFalse(validate_email("not-an-email"))
        self.assertTrue(validate_password_strength("ValidPass123"))
        self.assertFalse(validate_password_strength("short"))


if __name__ == "__main__":
    unittest.main()
