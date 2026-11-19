
from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode

from app.config import settings
from app.rag.embeddings import embedding_service


class VectorStoreService:
    """Manages connection to the existing Qdrant collection."""

    EXPECTED_DIMENSION = 1536
    VECTOR_NAME = "Dense"
    SPARSE_VECTOR_NAME = "Sparse"
    EXPECTED_DISTANCE = models.Distance.COSINE

    def __init__(self) -> None:
        self._client: QdrantClient | None = None
        self._vector_store: QdrantVectorStore | None = None

    def connect(self) -> QdrantVectorStore:
        if self._vector_store is not None:
            return self._vector_store

        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30,
        )

        try:
            if not client.collection_exists(settings.qdrant_collection):
                raise ValueError(
                    f"Collection '{settings.qdrant_collection}' does not exist."
                )

            collection = client.get_collection(
                collection_name=settings.qdrant_collection
            )

            # Validate Dense vector configuration
            vectors = collection.config.params.vectors

            if not isinstance(vectors, dict):
                raise ValueError(
                    "Expected named vectors, but found an unnamed vector."
                )

            if self.VECTOR_NAME not in vectors:
                raise ValueError(
                    f"Named vector '{self.VECTOR_NAME}' not found. "
                    f"Available vectors: {list(vectors.keys())}"
                )

            vector_config = vectors[self.VECTOR_NAME]

            if vector_config.size != self.EXPECTED_DIMENSION:
                raise ValueError(
                    f"Dimension mismatch: expected {self.EXPECTED_DIMENSION}, "
                    f"found {vector_config.size}."
                )

            if vector_config.distance != self.EXPECTED_DISTANCE:
                raise ValueError(
                    f"Distance mismatch: expected COSINE, "
                    f"found {vector_config.distance}."
                )

            # Validate Sparse vector configuration
            sparse_vectors = collection.config.params.sparse_vectors

            if not sparse_vectors or self.SPARSE_VECTOR_NAME not in sparse_vectors:
                raise ValueError(
                    f"Named sparse vector '{self.SPARSE_VECTOR_NAME}' "
                    "not found in collection."
                )

            # Initialize local Sparse embedding model
            sparse_embedding = FastEmbedSparse(
                model_name="Qdrant/bm25"
            )

            # Initialize Hybrid vector store
            vector_store = QdrantVectorStore(
                client=client,
                collection_name=settings.qdrant_collection,
                embedding=embedding_service,
                sparse_embedding=sparse_embedding,
                retrieval_mode=RetrievalMode.HYBRID,
                vector_name=self.VECTOR_NAME,
                sparse_vector_name=self.SPARSE_VECTOR_NAME,
            )

            self._client = client
            self._vector_store = vector_store

            return vector_store

        except Exception:
            client.close()
            raise

    def get_client(self) -> QdrantClient:
        if self._client is None:
            self.connect()

        assert self._client is not None
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()

        self._client = None
        self._vector_store = None


vector_store_service = VectorStoreService()
