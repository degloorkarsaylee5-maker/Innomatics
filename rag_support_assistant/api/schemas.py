from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)


class SourceItem(BaseModel):
    chunk_id: str
    score: float
    page_number: Optional[int]


class QueryResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[SourceItem]
    escalated: bool