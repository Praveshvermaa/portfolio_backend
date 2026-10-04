from __future__ import annotations

import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest, ChatResponse, IngestResponse
from app.services.chat_service import chat_service
from app.rag.vectorstore import ingest_portfolio, get_collection_point_count

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("", response_class=StreamingResponse)
@router.get("/", response_class=StreamingResponse)
async def chat_stream_get(q: str = Query(..., min_length=1, description="Question for Pravesh's portfolio chatbot")):
    """
    GET streaming endpoint called by the frontend Chatbot component.
    Streams plain text tokens in real time.
    """
    clean_q = q.strip()
    if not clean_q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'q' cannot be empty.",
        )

    return StreamingResponse(
        chat_service.stream_response(clean_q),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse)
async def chat_post(request: ChatRequest):
    """
    Standard JSON POST endpoint returning full answer and source sections.
    """
    clean_query = request.query.strip()
    if not clean_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty.",
        )

    result = await chat_service.get_response(clean_query)
    return ChatResponse(
        query=clean_query,
        answer=result.get("answer", ""),
        sources=result.get("sources", []),
    )


@router.post("/stream", response_class=StreamingResponse)
async def chat_post_stream(request: ChatRequest):
    """
    POST streaming endpoint taking JSON body.
    """
    clean_query = request.query.strip()
    if not clean_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty.",
        )

    return StreamingResponse(
        chat_service.stream_response(clean_query),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/ingest", response_model=IngestResponse)
async def trigger_ingestion():
    """
    Re-ingests the portfolio document into Qdrant vector database.
    """
    try:
        count = ingest_portfolio()
        total = get_collection_point_count()
        return IngestResponse(
            status="success",
            chunks_ingested=count,
            total_points=total,
        )
    except Exception as e:
        logger.error("Failed to ingest portfolio: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}",
        )
