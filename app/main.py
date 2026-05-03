from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.services.rag import load_data 
import os
import asyncio
import httpx

app = FastAPI()

# Secure CORS: Only allow localhost in development mode
ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "production":
    origins = ["https://portfolio2-0-vert-beta.vercel.app"]
else:
    origins = [
        "https://portfolio2-0-vert-beta.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

async def keep_alive():
    """Background task to ping the server and keep it awake."""
    url = "https://portfolio-backend-kix6.onrender.com/health"
    await asyncio.sleep(10) # Wait for server to start
    async with httpx.AsyncClient() as client:
        while True:
            try:
                await client.get(url)
                # print("Self-ping successful")
            except Exception as e:
                pass
            await asyncio.sleep(300) # 5 minutes

@app.on_event("startup")
async def startup():
    load_data()
    asyncio.create_task(keep_alive())

@app.get("/health")
def health_check():
    return {"status": "alive"}

app.include_router(chat_router,prefix="/chat") 
