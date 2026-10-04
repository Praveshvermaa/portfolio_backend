from __future__ import annotations

import logging
from typing import Optional

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from app.config import settings
from app.rag.vectorstore import get_vector_store

logger = logging.getLogger(__name__)


def get_retriever(
    k: Optional[int] = None,
    search_type: str = "similarity",
) -> VectorStoreRetriever:
    """
    Returns a VectorStoreRetriever configured with similarity search.
    """
    top_k = k if k is not None else settings.retrieval_k
    vector_store = get_vector_store()

    return vector_store.as_retriever(
        search_type=search_type,
        search_kwargs={"k": top_k},
    )


def retrieve_context(query: str, k: Optional[int] = None) -> list[Document]:
    """
    Directly retrieves relevant documents for a given query string.
    """
    top_k = k if k is not None else settings.retrieval_k
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=top_k)
    return results


retriever = get_retriever()
