from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel

SourceType = Literal["doc", "chat", "meeting", "github", "email"]


class Document(BaseModel):
    id: str
    source_type: SourceType
    title: str
    author: str
    timestamp: datetime
    url: str
    access_role: str          # public | engineering | finance | exec
    text: str                 # canonical text; ALL offsets refer to this string


class Chunk(BaseModel):
    id: str
    doc_id: str
    idx: int
    text: str
    char_start: int           # offsets into Document.text
    char_end: int


class Evidence(BaseModel):
    source_id: str
    quote: str
    char_start: int
    char_end: int


class DecisionRecord(BaseModel):
    id: str
    decision: str
    topic: str                # canonical slug, grouped by exact match
    alternatives_considered: list[str]
    rationale: str
    participants: list[str]
    date: date
    status: Literal["proposed", "debated", "final", "reversed"]
    evidence: list[Evidence]
    supersedes_id: str | None = None
    access_role: str = "public"
    extraction_confidence: float = 0.0
