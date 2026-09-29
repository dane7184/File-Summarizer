import os
from dataclasses import dataclass
from typing import Optional

MAX_BYTES = 20 * 1024 * 1024
MAX_TEXT_CHARS = 400_000
TEXT_EXTENSIONS = {".txt", ".md"}


class ExtractionError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


@dataclass
class ExtractedFile:
    filename: str
    kind: str  # "pdf" or "text"
    pdf_bytes: Optional[bytes] = None
    text: Optional[str] = None


def extract(filename: str, content_type: Optional[str], data: bytes) -> ExtractedFile:
    """Validate an uploaded file and prepare it for summarizing.

    PDFs are kept as raw bytes (Claude reads PDFs natively, including tables
    and images). Plain-text files are decoded to a string.
    """
    filename = filename or "upload"
    ext = os.path.splitext(filename.lower())[1]

    if not data:
        raise ExtractionError("The uploaded file is empty.")
    if len(data) > MAX_BYTES:
        raise ExtractionError("File is too large (max 20 MB).", 413)

    if ext == ".pdf" or content_type == "application/pdf":
        if b"%PDF" not in data[:1024]:
            raise ExtractionError("This file is not a valid PDF.")
        return ExtractedFile(filename=filename, kind="pdf", pdf_bytes=data)

    if ext in TEXT_EXTENSIONS:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1")
        if not text.strip():
            raise ExtractionError("The text file has no content.")
        if len(text) > MAX_TEXT_CHARS:
            raise ExtractionError(
                f"Text file is too long to summarize (limit {MAX_TEXT_CHARS:,} characters).",
                413,
            )
        return ExtractedFile(filename=filename, kind="text", text=text)

    raise ExtractionError("Unsupported file type. Upload a PDF, .txt or .md file.", 415)
