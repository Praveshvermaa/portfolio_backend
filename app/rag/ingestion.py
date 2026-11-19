
from langchain_core.documents import Document
from qdrant_client import models

from app.config import settings
from app.rag.vectorstore import vector_store_service


class IngestionService:

    def ingest(self, documents: list[Document]) -> list[str]:
        if not documents:
            raise ValueError("No documents provided for ingestion.")

        client = vector_store_service.get_client()

      
        client.delete(
            collection_name=settings.qdrant_collection,
            points_selector=models.FilterSelector(
                filter=models.Filter(must=[])
            ),
            wait=True,
        )
        print("Previous documents and embedding deleted")

        vector_store = vector_store_service.connect()

       
        stored_ids = vector_store.add_documents(
            documents=documents,
        )

        return stored_ids


ingestion_service = IngestionService()
