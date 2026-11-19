from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User question to the chatbot",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Query cannot be empty or whitespace only.")

        return value

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What projects has Pravesh built?"
            }
        }


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: list[str] = Field(
        default_factory=list,
        description="Sections referenced in the context",
    )


class IngestResponse(BaseModel):
    status: str
    chunks_ingested: int
    total_points: int


class HealthResponse(BaseModel):
    status: str
    qdrant_connected: bool
    points_count: int
    collection: str