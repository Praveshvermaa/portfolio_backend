from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    openai_api_key: str = Field(min_length=1)

    chunk_size: int = Field(default=500, ge=100, le=5000)
    chunk_overlap: int = Field(default=50, ge=0, le=1000)

    pollinations_base_url: str = Field(
        default="https://gen.pollinations.ai/v1",
        min_length=1,
    )

    embedding_model: str = Field(
        min_length=1,
    )

    llm_model: str = Field(
        default="openai/gpt-5.4-nano",
        min_length=1,
    )

    retrieval_k: int = Field(
        default=4,
        ge=1,
        le=20,
    )

    qdrant_url: str = Field(
        min_length=1,
    )

    qdrant_api_key: str = Field(
        min_length=1,
    )

    qdrant_collection: str = Field(
        default="portfolio",
        min_length=1,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    frontend_url: str = Field(
    default="http://localhost:5173",
    min_length=1,
    )
    backend_url: str = "http://127.0.0.1:8000"
    


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
OPENAI_API_KEY = settings.openai_api_key
