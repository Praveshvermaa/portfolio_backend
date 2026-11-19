import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest
from app.services.chat_service import chat_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/stream")
def stream_chat(request: ChatRequest):

    def event_generator():
        try:
            for chunk in chat_service.chat_stream(request.query):
                data = json.dumps({"token": chunk})
                yield f"data: {data}\n\n"

        except Exception:
            logger.exception("Error while generating chatbot response.")

            error_data = json.dumps({
                "error": "Sorry, something went wrong while generating the response."
            })

            yield f"event: error\ndata: {error_data}\n\n"

        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )