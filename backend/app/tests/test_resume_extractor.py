import tempfile
from pathlib import Path

import fitz

from app.utils.resume_extractor import extract_contact_hints, extract_text_from_pdf


def test_extract_text_from_pdf():
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / "sample.pdf"
        document = fitz.open()
        page = document.new_page()
        page.insert_text((72, 72), "Jane Developer\njane@example.com\n+1 555 123 4567")
        document.save(pdf_path)
        document.close()

        text = extract_text_from_pdf(pdf_path)
        hints = extract_contact_hints(text)

        assert "Jane Developer" in text
        assert hints["email"] == "jane@example.com"
        assert hints["phone"] is not None
