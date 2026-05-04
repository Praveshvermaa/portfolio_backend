from fastapi import APIRouter 
from fastapi.responses import StreamingResponse
from app.services.rag import ask 

router = APIRouter()

@router.get("/")
async def chat(q:str):
    return StreamingResponse(
        await ask(q), 
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "Content-Encoding": "identity",
            "X-Content-Type-Options": "nosniff"
        }
    )
