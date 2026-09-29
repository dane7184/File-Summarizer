import base64
import io
import os

import anthropic
import httpx

from app.models.schemas import SummaryStyle
from app.services.file_extractor import ExtractedFile

PROMPTS = {
    SummaryStyle.bullets: "Summarize this document in 5 to 8 bullet points, then add a one-sentence takeaway.",
    SummaryStyle.short: "Summarize this document in one short paragraph of 3 to 5 sentences.",
    SummaryStyle.detailed: (
        "Write a detailed summary of this document with a short section for each "
        "major topic, followed by a brief conclusion."
    ),
}


MAX_OLLAMA_CHARS = 30_000


class SummarizerError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def _pdf_text(pdf_bytes: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    if not text:
        raise SummarizerError("No extractable text in this PDF (scanned?).", 422)
    return text[:MAX_OLLAMA_CHARS]


def _summarize_ollama(extracted: ExtractedFile, style: SummaryStyle) -> str:
    text = _pdf_text(extracted.pdf_bytes) if extracted.kind == "pdf" else extracted.text[:MAX_OLLAMA_CHARS]
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    try:
        r = httpx.post(
            f"{host}/api/chat",
            json={
                "model": model,
                "stream": False,
                "messages": [
                    {"role": "user", "content": f"<document>\n{text}\n</document>\n\n{PROMPTS[style]}"}
                ],
            },
            timeout=300,
        )
    except httpx.HTTPError:
        raise SummarizerError(f"Could not reach Ollama at {host}. Is it running?")
    if r.status_code != 200:
        raise SummarizerError(f"Ollama error: {r.text[:200]} (try: ollama pull {model})")
    return r.json()["message"]["content"].strip()


def summarize(extracted: ExtractedFile, style: SummaryStyle) -> str:
    if os.getenv("LLM_PROVIDER", "anthropic").lower() == "ollama":
        return _summarize_ollama(extracted, style)

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SummarizerError("Server is missing ANTHROPIC_API_KEY.", 500)

    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    prompt = PROMPTS[style]

    if extracted.kind == "pdf":
        content = [
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": base64.standard_b64encode(extracted.pdf_bytes).decode(),
                },
            },
            {"type": "text", "text": prompt},
        ]
    else:
        content = [
            {
                "type": "text",
                "text": f"<document>\n{extracted.text}\n</document>\n\n{prompt}",
            }
        ]

    try:
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": content}],
        )
    except anthropic.APIStatusError as e:
        raise SummarizerError(f"Claude API error: {e.message}")
    except anthropic.APIConnectionError:
        raise SummarizerError("Could not reach the Claude API.")

    return "".join(b.text for b in msg.content if b.type == "text").strip()
