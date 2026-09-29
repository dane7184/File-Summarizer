from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.schemas import SummarizeResponse, SummaryStyle
from app.services.file_extractor import MAX_BYTES, ExtractionError, extract
from app.services.summarizer import SummarizerError, summarize

router = APIRouter()


@router.post("/summarize", response_model=SummarizeResponse)
def summarize_file(
    file: UploadFile = File(...),
    style: SummaryStyle = Form(SummaryStyle.bullets),
):
    data = file.file.read(MAX_BYTES + 1)

    try:
        extracted = extract(file.filename or "", file.content_type, data)
        summary = summarize(extracted, style)
    except (ExtractionError, SummarizerError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    return SummarizeResponse(summary=summary, filename=extracted.filename)
