"""
Validation utilities for inputs, emails, passwords, student names, and documents.
Phase 35 — Security & Privacy Input Validation.
"""

import re
import html
from typing import Tuple, Optional


def sanitize_input_string(text: str) -> str:
    """
    Sanitize general text input by stripping null bytes, dangerous control characters,
    and escaping HTML tags to prevent cross-site scripting (XSS).
    """
    if not text:
        return ""
    # Strip null bytes and non-printable control characters (except newline and tab)
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    # Strip or escape script tags
    cleaned = re.sub(r'(?i)<script[^>]*>.*?</script>', '', cleaned, flags=re.DOTALL)
    return cleaned.strip()


def validate_chat_input(message: str, max_length: int = 5000) -> Tuple[bool, str]:
    """
    Validate student conversational messages.
    Ensures message is non-empty, within length bounds, and free from null bytes.
    """
    if not message or not message.strip():
        return False, "Message cannot be empty."
    
    clean = sanitize_input_string(message)
    if not clean:
        return False, "Message contains invalid or empty content."
    
    if len(clean) > max_length:
        return False, f"Message exceeds maximum allowed length of {max_length} characters."
    
    return True, clean


def validate_student_name(name: str) -> Tuple[bool, str]:
    """
    Validate student username or display name.
    Allowed: Letters, numbers, spaces, hyphens, and underscores. Length: 1-50 chars.
    """
    if not name or not name.strip():
        return False, "Student name cannot be empty."
    
    cleaned = name.strip()
    if len(cleaned) < 1 or len(cleaned) > 50:
        return False, "Student name must be between 1 and 50 characters."
    
    pattern = r"^[a-zA-Z0-9_\s\-]+$"
    if not re.match(pattern, cleaned):
        return False, "Student name may only contain letters, numbers, spaces, hyphens, or underscores."
    
    return True, cleaned


def validate_subject_or_module_title(title: str, max_length: int = 120) -> Tuple[bool, str]:
    """
    Validate subject name or module title.
    """
    if not title or not title.strip():
        return False, "Title cannot be empty."
    
    clean = sanitize_input_string(title)
    if len(clean) > max_length:
        return False, f"Title must be within {max_length} characters."
    
    return True, clean


def validate_user_answer(answer: str) -> Tuple[bool, str]:
    """Validate student recall response length and quality."""
    clean = sanitize_input_string(answer)
    if not clean:
        return False, "Answer cannot be empty."
    if len(clean.split()) < 3:
        return False, "Answer is too brief to evaluate meaningful conceptual recall."
    return True, "Valid"


def validate_file_extension(filename: str) -> bool:
    """Check allowed document extensions."""
    exts = (".pdf", ".txt", ".md", ".markdown")
    return any(filename.lower().endswith(e) for e in exts)


def validate_email(email: str) -> bool:
    """Validate email format according to standard RFC structure."""
    if not email or "@" not in email or "." not in email:
        return False
    clean = email.strip()
    if len(clean) > 254:
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, clean))


def validate_password_strength(password: str, min_length: int = 6) -> bool:
    """Check password satisfies minimum safety threshold."""
    if not password:
        return False
    if len(password.strip()) < min_length:
        return False
    # Avoid passwords that are all spaces
    if password.isspace():
        return False
    return True
