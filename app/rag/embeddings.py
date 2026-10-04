from __future__ import annotations

from openai import OpenAI

from app.config import settings

from langchain_core.embeddings import Embeddings

class EmbeddingService(Embeddings):

    def __init__(self)->None:
        self._client = OpenAI(
            base_url = settings.pollinations_base_url,
            api_key = settings.openai_api_key
        )

        self.model_name = settings.embedding_model
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:

        if not texts:
            raise ValueError("texts list is empty for embedding!")

        response = self._client.embeddings.create(
            model=self.model_name,
            input=texts
        )

        return [
            item.embedding
            for item in response.data
        ]
    
    def embed_query(self, query: str) -> list[float]:
        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )
        
        response = self._client.embeddings.create(
            model = self.model_name,
            input = query
        )

        return response.data[0].embedding

embedding_service = EmbeddingService()