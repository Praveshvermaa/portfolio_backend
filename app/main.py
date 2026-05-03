from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.services.rag import load_data 

import os

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

@app.on_event("startup")
def startup():
    load_data()


app.include_router(chat_router,prefix="/chat") 
