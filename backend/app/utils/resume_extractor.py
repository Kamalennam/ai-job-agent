import re
from pathlib import Path

import fitz
import pdfplumber

PARSER_VERSION = "pymupdf-1.24"

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text using PyMuPDF, with pdfplumber fallback."""
    text = _extract_with_pymupdf(file_path)
    if text.strip():
        return _normalize_text(text)

    text = _extract_with_pdfplumber(file_path)
    return _normalize_text(text)


def _extract_with_pymupdf(file_path: Path) -> str:
    with fitz.open(file_path) as document:
        return "\n".join(page.get_text() for page in document)


def _extract_with_pdfplumber(file_path: Path) -> str:
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def _normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned.strip()


def extract_contact_hints(text: str) -> dict[str, str | None]:
    email_match = EMAIL_PATTERN.search(text)
    phone_match = PHONE_PATTERN.search(text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    name = lines[0] if lines else None

    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0).strip() if phone_match else None,
    }
