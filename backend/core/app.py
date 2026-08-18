from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import FRONTEND_ORIGIN

app = FastAPI(
    title="QuizMate AI API",
    version="1.0.0",
)

origins = [
    o.strip()
    for o in FRONTEND_ORIGIN.split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
