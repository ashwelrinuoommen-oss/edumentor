"""
PDF Processing utilities using pdfplumber for EduMentor.
"""

import io
from typing import Tuple, Optional


def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[str, str]:
    """
    Extract title and text content from PDF bytes using pdfplumber.
    Returns (document_title, extracted_text).
    """
    extracted_text = []
    title = "Uploaded PDF Notes"

    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    extracted_text.append(text)
                    if page_idx == 0:
                        lines = [l.strip() for l in text.split("\n") if l.strip()]
                        if lines:
                            title = lines[0][:80]
    except Exception as e:
        from edumentor.utils.error_handler import ERROR_UPLOAD_MSG, EduMentorUploadError
        raise EduMentorUploadError(ERROR_UPLOAD_MSG) from e

    full_text = "\n\n".join(extracted_text).strip()
    return title, full_text


async def async_extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[str, str]:
    """
    Extract title and text content from PDF bytes asynchronously
    offloading CPU and disk I/O to a background thread pool.
    """
    import asyncio
    return await asyncio.to_thread(extract_text_from_pdf, pdf_bytes)
