from __future__ import annotations

import logging
from pathlib import Path
from functools import lru_cache
from typing import Optional

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import settings
from app.rag.embeddings import embedding_service
from app.rag.loader import document_loader
from app.rag.splitter import document_splitter

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    """
    Returns a cached QdrantClient instance with extended timeout for cloud operations.
    """
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        timeout=120.0,
    )


def _detect_vector_name(client: QdrantClient, collection_name: str) -> str:
    """
    Detects the vector name used in the Qdrant collection.
    Defaults to 'Dense' if present, or first named vector, or empty string.
    """
    try:
        if client.collection_exists(collection_name):
            collection_info = client.get_collection(collection_name)
            vectors = collection_info.config.params.vectors
            if isinstance(vectors, dict):
                if "Dense" in vectors:
                    return "Dense"
                elif vectors:
                    return next(iter(vectors.keys()))
    except Exception as e:
        logger.warning("Failed to detect vector name for collection %s: %s", collection_name, e)
    return "Dense"


def ensure_collection_exists(client: QdrantClient, collection_name: str, vector_size: int = 1536) -> None:
    """
    Ensures that the collection exists in Qdrant with appropriate vector configuration.
    """
    if not client.collection_exists(collection_name):
        logger.info("Collection '%s' does not exist. Creating it now...", collection_name)
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "Dense": qmodels.VectorParams(
                    size=vector_size,
                    distance=qmodels.Distance.COSINE,
                )
            },
        )


@lru_cache(maxsize=1)
def get_vector_store() -> QdrantVectorStore:
    """
    Returns a configured QdrantVectorStore instance.
    """
    client = get_qdrant_client()
    ensure_collection_exists(client, settings.qdrant_collection)
    vector_name = _detect_vector_name(client, settings.qdrant_collection)

    return QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection,
        embedding=embedding_service,
        vector_name=vector_name,
        validate_embeddings=False,
    )


def get_collection_point_count() -> int:
    """
    Returns current number of points in the configured collection.
    """
    client = get_qdrant_client()
    if not client.collection_exists(settings.qdrant_collection):
        return 0
    return client.get_collection(settings.qdrant_collection).points_count or 0


def ingest_documents(
    documents: list[Document],
    clear_existing: bool = False,
    batch_size: int = 5,
) -> list[str]:
    """
    Ingests given documents into Qdrant vector store in safe batches.
    """
    if not documents:
        logger.warning("No documents to ingest.")
        return []

    client = get_qdrant_client()
    ensure_collection_exists(client, settings.qdrant_collection)

    if clear_existing:
        logger.info("Clearing existing points in collection '%s'", settings.qdrant_collection)
        client.delete(
            collection_name=settings.qdrant_collection,
            points_selector=qmodels.FilterSelector(filter=qmodels.Filter()),
        )

    vector_store = get_vector_store()
    all_ids: list[str] = []

    for i in range(0, len(documents), batch_size):
        batch = documents[i : i + batch_size]
        logger.info(
            "Ingesting batch %d to %d of %d documents...",
            i + 1,
            min(i + batch_size, len(documents)),
            len(documents),
        )
        batch_ids = vector_store.add_documents(batch)
        all_ids.extend(batch_ids)

    logger.info("Successfully ingested %d documents into Qdrant", len(all_ids))
    return all_ids


def ingest_portfolio(
    file_path: str | Path = "data/documents/portfolio.txt",
    clear_existing: bool = True,
    batch_size: int = 5,
) -> int:
    """
    Loads portfolio file, splits it into section-wise chunks, and ingests into Qdrant.
    Returns the number of chunks ingested.
    """
    path = Path(file_path)
    if not path.is_absolute():
        base_dir = Path(__file__).resolve().parent.parent.parent
        resolved_path = base_dir / path
        if resolved_path.exists():
            path = resolved_path

    logger.info("Loading document from: %s", path)
    docs = document_loader.load(path)
    chunks = document_splitter.split(docs)
    logger.info("Split document into %d chunks", len(chunks))

    ingest_documents(chunks, clear_existing=clear_existing, batch_size=batch_size)
    return len(chunks)


vector_store = get_vector_store()
