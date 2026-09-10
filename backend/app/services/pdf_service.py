"""Extract text from PDF files using PyMuPDF."""
import pymupdf  # PyMuPDF (modern import name; replaces deprecated `fitz`)


def extract_text_from_pdf(path: str) -> str:
    """Return concatenated text from all pages of a PDF.

    Falls back to an empty string if the document has no extractable text
    (e.g. a scanned image-only PDF).
    """
    text_parts: list[str] = []
    with pymupdf.open(path) as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return _clean(" ".join(text_parts))


def _clean(text: str) -> str:
    # Normalise whitespace; keep it simple and robust.
    return " ".join(text.split())
