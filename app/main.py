from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.config import settings
from app.models.schemas import HealthResponse
from app.services.keep_alive import keep_alive
import asyncio

from app.rag.vectorstore import vector_store_service
from fastapi import FastAPI, HTTPException


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("portfolio-rag")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Portfolio Chatbot Backend...")

    keep_alive_task = asyncio.create_task(keep_alive())

    try:
        vector_store_service.connect()

        client = vector_store_service.get_client()

        collection = client.get_collection(
            collection_name=settings.qdrant_collection
        )

        points_count = collection.points_count or 0

        logger.info(
            "Qdrant collection '%s' connected. Points: %d",
            settings.qdrant_collection,
            points_count,
        )

        if points_count == 0:
            raise RuntimeError(
                "Qdrant collection is empty. "
                "Run the ingestion process before starting the API."
            )

    except Exception:
        logger.exception("Backend startup failed.")

        vector_store_service.close()
        raise

    logger.info("Backend initialization complete.")

    try:
        yield
    finally:
        vector_store_service.close()
        logger.info("Qdrant connection closed.")
        logger.info("Portfolio Chatbot Backend shut down.")


app = FastAPI(
    title="Portfolio RAG Chatbot API",
    description="Backend API for Pravesh Verma's Portfolio Chatbot.",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
       settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "name": "Pravesh Verma - Portfolio Chatbot API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "message": "Portfolio RAG API is running.",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    try:
        client = vector_store_service.get_client()

        collection = client.get_collection(
            collection_name=settings.qdrant_collection
        )

        return HealthResponse(
            status="healthy",
            qdrant_connected=True,
            points_count=collection.points_count or 0,
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

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )