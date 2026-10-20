"""
Security, file validation, API key protection, and privacy helpers for EduMentor.
Phase 35 — Security & Privacy.
"""

import os
import re
import io
import shutil
import hashlib
import secrets
import tempfile
from contextlib import contextmanager
from typing import Tuple, Optional, List, Dict, Any, Generator

# -----------------------------------------------------------------------------
# 1. FILE UPLOAD CONSTRAINTS & LIMITS
# -----------------------------------------------------------------------------
# Default maximum file size: 15 MB (configurable via MAX_UPLOAD_SIZE_MB env var)
_env_mb = os.environ.get("MAX_UPLOAD_SIZE_MB", "15")
try:
    MAX_UPLOAD_SIZE_MB = int(_env_mb)
except ValueError:
    MAX_UPLOAD_SIZE_MB = 15

MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

ALLOWED_FILE_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown"}

DANGEROUS_FILE_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".sh", ".php", ".py", ".pyw", ".js", ".vbs",
    ".dll", ".ps1", ".jar", ".html", ".htm", ".svg", ".scr", ".com", ".msi",
    ".apk", ".elf", ".bin", ".reg", ".wsf", ".cpl"
}

# Magic bytes signatures
PDF_MAGIC_BYTES = b"%PDF-"
PE_EXECUTABLE_MAGIC = b"MZ"
ELF_EXECUTABLE_MAGIC = b"\x7fELF"

# Note Privacy Guarantee statement emphasized by the design doc
NOTE_PRIVACY_STATEMENT = (
    "Your notes stay private. Uploaded study material is processed locally in your session, "
    "stored securely in your student database, and never shared or used to train public AI models."
)


# -----------------------------------------------------------------------------
# 2. FILENAME SANITIZATION & PATH TRAVERSAL DEFENSE
# -----------------------------------------------------------------------------
def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename against path traversal attacks (../, ..\\), null bytes,
    and control characters. Preserves extension and base name.
    """
    if not filename:
        return "uploaded_notes.pdf"
    
    # Strip null bytes and control characters
    cleaned = filename.replace("\0", "").strip()
    
    # Extract only the base name (strip directory paths)
    cleaned = os.path.basename(cleaned)
    cleaned = cleaned.replace("\\", "/").split("/")[-1]
    
    # Remove directory traversal patterns
    cleaned = re.sub(r"\.\.+[/]?", "", cleaned)
    
    # Remove unsafe characters while preserving letters, digits, spaces, dots, hyphens, underscores
    cleaned = re.sub(r'[^a-zA-Z0-9._\s-]', '_', cleaned)
    
    # Strip leading/trailing dots or spaces
    cleaned = cleaned.strip(". ")
    
    if not cleaned:
        return "uploaded_notes.pdf"
    
    return cleaned[:120]  # Cap filename length


# -----------------------------------------------------------------------------
# 3. COMPREHENSIVE FILE VALIDATION & CONTENT INSPECTION
# -----------------------------------------------------------------------------
def validate_uploaded_file(
    filename: str,
    content: bytes,
    max_size_bytes: int = MAX_UPLOAD_SIZE_BYTES
) -> Tuple[bool, str, str]:
    """
    Validate uploaded study notes for:
    1. Maximum file size
    2. Allowed document extension (.pdf, .txt, .md, .markdown)
    3. Explicit rejection of executable/script extensions
    4. Magic bytes content inspection (PDF %PDF- header, executable MZ/ELF rejection)
    5. Text encoding validity for text files

    Returns:
        (is_valid: bool, sanitized_filename: str, error_message: str)
    """
    clean_name = sanitize_filename(filename)
    
    # 1. Size Validation
    if not content or len(content) == 0:
        return False, clean_name, "The uploaded file is empty. Please provide notes with study content."
    
    if len(content) > max_size_bytes:
        size_mb = len(content) / (1024 * 1024)
        limit_mb = max_size_bytes / (1024 * 1024)
        return False, clean_name, (
            f"File exceeds maximum allowed size of {limit_mb:.0f} MB (uploaded file is {size_mb:.1f} MB). "
            "Please upload a smaller document."
        )

    # 2. Extension Validation
    _, ext = os.path.splitext(clean_name.lower())
    if not ext:
        return False, clean_name, "File has no file extension. Allowed formats: PDF (.pdf) or text (.txt, .md)."
    
    if ext in DANGEROUS_FILE_EXTENSIONS:
        return False, clean_name, (
            f"Executable or script file type '{ext}' is strictly prohibited for security. "
            "Please upload notes in PDF (.pdf) or text (.txt, .md) format."
        )
    
    if ext not in ALLOWED_FILE_EXTENSIONS:
        return False, clean_name, (
            f"Unsupported file format '{ext}'. EduMentor supports study notes in "
            "PDF (.pdf) or Markdown / plain text (.md, .txt) format."
        )

    # 3. Magic Header & Binary Content Inspection
    # Immediate rejection if file has executable headers regardless of extension
    header_preview = content[:16]
    if header_preview.startswith(PE_EXECUTABLE_MAGIC) or header_preview.startswith(ELF_EXECUTABLE_MAGIC):
        return False, clean_name, "File content is an executable binary and was rejected for security."

    if ext == ".pdf":
        # Must contain %PDF- in the first 1024 bytes
        first_kb = content[:1024]
        if PDF_MAGIC_BYTES not in first_kb:
            return False, clean_name, (
                "Invalid PDF document format. The file header does not match standard PDF specifications."
            )
    elif ext in {".txt", ".md", ".markdown"}:
        # Must be valid decodable text without excessive binary characters or null bytes
        if b"\0" in content:
            return False, clean_name, "Text file contains invalid binary null bytes and was rejected."
        try:
            decoded = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                decoded = content.decode("latin-1")
            except Exception:
                return False, clean_name, "Unable to decode text file. Please ensure UTF-8 encoding."
        
        # Check ratio of printable text
        if decoded:
            non_printable = sum(1 for ch in decoded if ord(ch) < 32 and ch not in "\n\r\t")
            if non_printable / len(decoded) > 0.10:
                return False, clean_name, "File appears to be a binary file rather than plain text notes."

    return True, clean_name, "File validation passed."


# -----------------------------------------------------------------------------
# 4. SAFE TEMPORARY STORAGE WITH GUARANTEED CLEANUP
# -----------------------------------------------------------------------------
@contextmanager
def safe_temporary_file(
    content: bytes,
    suffix: str = ".tmp",
    prefix: str = "edumentor_safe_"
) -> Generator[str, None, None]:
    """
    Safely write content to an isolated temporary file with a secure random name.
    Guarantees that the temporary file is deleted upon exit, even if exceptions occur.
    """
    temp_dir = tempfile.mkdtemp(prefix="edumentor_sec_")
    rand_id = secrets.token_hex(8)
    temp_path = os.path.join(temp_dir, f"{prefix}{rand_id}{suffix}")
    
    try:
        with open(temp_path, "wb") as f:
            f.write(content)
        yield temp_path
    finally:
        # Secure cleanup
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


# -----------------------------------------------------------------------------
# 5. API KEY PROTECTION & MASKING
# -----------------------------------------------------------------------------
def mask_api_key(api_key: Optional[str]) -> str:
    """
    Mask sensitive API key strings for secure UI display and logging.
    Example: 'sk-ant-api03-abcdef1234567890' -> 'sk-••••••••7890'
    """
    if not api_key:
        return ""
    clean = api_key.strip()
    if not clean:
        return ""
    if len(clean) <= 8:
        return "••••••••"
    
    prefix = clean[:3]
    suffix = clean[-4:]
    return f"{prefix}••••••••{suffix}"


def is_masked_key(key: Optional[str]) -> bool:
    """Detect if an incoming API key string is already masked (bullet points)."""
    if not key:
        return False
    return "••" in key or "••••" in key


# -----------------------------------------------------------------------------
# 6. PASSWORD HASHING (SALTED SHA-256)
# -----------------------------------------------------------------------------
def hash_password(password: str, salt: str = "edumentor_salt") -> str:
    """Salted SHA-256 password hash for local desktop authentication."""
    return hashlib.sha256(f"{salt}_{password}".encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed: str, salt: str = "edumentor_salt") -> bool:
    """Verify password against salted hash."""
    return hash_password(plain_password, salt) == hashed


# -----------------------------------------------------------------------------
# 7. CONTROLLED ERROR MESSAGES & INFORMATION LEAKAGE DEFENSE
# -----------------------------------------------------------------------------
def sanitize_error_message(
    exc: Exception,
    default_msg: str = "An error occurred while processing your request. Please try again."
) -> str:
    """
    Strips internal system paths (C:\\Users..., /home/...), SQL query fragments,
    and raw python exception classes from user-facing error messages.
    """
    raw = str(exc).strip()
    if not raw:
        return default_msg

    # Redact Windows / Unix file paths
    scrubbed = re.sub(r'[A-Za-z]:\\[^:\n\r\t]+', '[internal path]', raw)
    scrubbed = re.sub(r'/(?:Users|home|tmp|var|etc)[^\s:\n\r]+', '[internal path]', scrubbed)
    
    # Redact raw SQL errors
    if "syntax error" in scrubbed.lower() or "sqlite3" in scrubbed.lower() or "table " in scrubbed.lower():
        return "A database storage error occurred. Please try again."
    
    # Redact API key like strings
    scrubbed = re.sub(r'sk-[a-zA-Z0-9_\-]{15,}', '[REDACTED_API_KEY]', scrubbed)
    scrubbed = re.sub(r'AIza[a-zA-Z0-9_\-]{30,}', '[REDACTED_API_KEY]', scrubbed)

    # If message is overly verbose or raw python trace, return safe fallback
    if len(scrubbed) > 200 or "Traceback" in scrubbed or "line " in scrubbed:
        return default_msg

    return scrubbed


# -----------------------------------------------------------------------------
# 8. NO SECRETS IN GIT SCANNER
# -----------------------------------------------------------------------------
SECRET_PATTERNS = [
    (r"sk-[a-zA-Z0-9_\-]{20,}", "OpenAI / Claude API Key"),
    (r"AIzaSy[a-zA-Z0-9_\-]{33}", "Google Gemini / Cloud API Key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"-----BEGIN (?:RSA )?PRIVATE KEY-----", "Private Cryptographic Key"),
    (r"(?i)password\s*=\s*['\"][^'\"]{8,}['\"]", "Hardcoded Password")
]


def scan_text_for_secrets(text: str) -> List[str]:
    """Scan arbitrary text content for live secrets or tokens."""
    found = []
    for pattern, label in SECRET_PATTERNS:
        matches = re.findall(pattern, text)
        for m in matches:
            # Skip obvious test / example placeholders
            if "your_" in m.lower() or "example" in m.lower() or "placeholder" in m.lower():
                continue
            found.append(f"{label}: {m[:6]}...")
    return found


def scan_workspace_for_secrets(workspace_root: str) -> List[Dict[str, Any]]:
    """Scan tracked workspace files and config templates to verify no secrets exist."""
    results = []
    exclude_dirs = {".git", "__pycache__", ".pytest_cache", "node_modules", ".gemini", "brain"}
    
    for root, dirs, files in os.walk(workspace_root):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for fname in files:
            # Check .env.example, source files, md files
            if fname.endswith((".py", ".example", ".md", ".json", ".html", ".js")):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    secrets_found = scan_text_for_secrets(content)
                    if secrets_found:
                        results.append({
                            "file": os.path.relpath(fpath, workspace_root),
                            "secrets": secrets_found
                        })
                except Exception:
                    pass
    return results
