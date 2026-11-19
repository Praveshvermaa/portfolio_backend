
from langchain_core.documents import Document
from qdrant_client import models

from app.rag.vectorstore import vector_store_service


class RetrievalService:

    def __init__(self, top_k: int = 3) -> None:
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        section: str | None = None,
    ) -> list[Document]:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        vector_store = vector_store_service.connect()

        search_filter = None

        if section:
            search_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.section",
                        match=models.MatchValue(value=section),
                    )
                ]
            )

        return vector_store.similarity_search(
            query=query,
            k=self.top_k,
            filter=search_filter,
        )

    def get_retriever(self, section: str | None = None):
        vector_store = vector_store_service.connect()

        search_kwargs = {"k": self.top_k}

        if section:
            search_kwargs["filter"] = models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.section",
                    match=models.MatchValue(value=section),
                )
            ]
        )

        return vector_store.as_retriever(
          search_type="similarity",
          search_kwargs=search_kwargs,
        )


retrieval_service = RetrievalService(top_k=3)
