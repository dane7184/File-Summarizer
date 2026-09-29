from enum import Enum

from pydantic import BaseModel


class SummaryStyle(str, Enum):
    bullets = "bullets"
    short = "short"
    detailed = "detailed"


class SummarizeResponse(BaseModel):
    summary: str
    filename: str
