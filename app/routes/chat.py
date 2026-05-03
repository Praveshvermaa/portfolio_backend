from fastapi import APIRouter 
from fastapi.responses import StreamingResponse
from app.services.rag import ask 

router = APIRouter()

@router.get("/")
def chat(q:str):
    return StreamingResponse(ask(q), media_type="text/plain")
