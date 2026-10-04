from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User question to the chatbot")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What projects has Pravesh built?"
            }
        }


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[str] = Field(default_factory=list, description="Sections referenced in the context")


class IngestResponse(BaseModel):
    status: str
    chunks_ingested: int
    total_points: int


class HealthResponse(BaseModel):
    status: str
    qdrant_connected: bool
    points_count: int
    collection: str
