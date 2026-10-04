from __future__ import annotations

import logging
from typing import AsyncIterator, Dict, Any

from app.rag.chain import stream_rag_chain, get_answer_with_sources, arun_rag_chain

logger = logging.getLogger(__name__)


class ChatService:
    """
    Orchestrates RAG chat operations for both streaming and non-streaming requests.
    """

    async def get_response(self, question: str) -> Dict[str, Any]:
        """
        Processes a user question and returns the answer alongside source references.
        """
        try:
            return await get_answer_with_sources(question)
        except Exception as e:
            logger.error("Error generating response for question '%s': %s", question, e, exc_info=True)
            return {
                "question": question,
                "answer": "I'm sorry, I encountered an error while processing your request. Please try again or reach out to Pravesh directly.",
                "sources": [],
                "context_documents": [],
            }

    async def stream_response(self, question: str) -> AsyncIterator[str]:
        """
        Streams answer tokens chunk-by-chunk for conversational real-time response.
        """
        try:
            async for token in stream_rag_chain(question):
                yield token
        except Exception as e:
            logger.error("Error streaming response for question '%s': %s", question, e, exc_info=True)
            yield "\n[Error: Unable to complete response. Please check your backend connection.]"


chat_service = ChatService()
