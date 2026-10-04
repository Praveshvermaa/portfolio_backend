from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.config import settings
from app.models.schemas import HealthResponse
from app.rag.vectorstore import get_collection_point_count, ingest_portfolio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("portfolio-rag")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle management.
    """
    logger.info("Initializing Portfolio Chatbot Backend...")
    try:
        current_points = get_collection_point_count()
        logger.info("Qdrant collection '%s' points count: %d", settings.qdrant_collection, current_points)
        if current_points == 0:
            logger.info("Collection is empty. Automatically initiating portfolio document ingestion...")
            ingest_portfolio()
            logger.info("Initial ingestion complete. Ready to serve queries.")
    except Exception as e:
        logger.warning("Could not verify or auto-ingest Qdrant collection during startup: %s", e)

    yield

    logger.info("Shutting down Portfolio Chatbot Backend.")


app = FastAPI(
    title="Portfolio RAG Chatbot API",
    description="Backend API for Pravesh Verma's Portfolio Chatbot with RAG and Qdrant vector database.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend applications (Vite default is 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "name": "Pravesh Verma - Portfolio Chatbot API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "chat_endpoint": "/chat/?q={question}",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    try:
        points = get_collection_point_count()
        return HealthResponse(
            status="healthy",
            qdrant_connected=True,
            points_count=points,
            collection=settings.qdrant_collection,
        )
    except Exception as e:
        return HealthResponse(
            status=f"unhealthy: {str(e)}",
            qdrant_connected=False,
            points_count=0,
            collection=settings.qdrant_collection,
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
