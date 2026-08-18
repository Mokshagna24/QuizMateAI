import os
from pathlib import Path
from dotenv import load_dotenv

# Configuration is kept separate from application startup.
load_dotenv()

# This resolves to the project root when this file lives at:
# <project>/backend/core/config.py
ROOT = Path(__file__).resolve().parents[2]

DB_PATH = ROOT / "quizmate.db"
TOPICS_DIR = ROOT / "data" / "topics"

JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "7G5F7aYahj4QHHNK2aALfFcVNGgtNb1M_TnlYIy43Sg",
)

JWT_ALG = "HS256"

FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:5173",
)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
).rstrip("/")

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:latest",
)

OLLAMA_EMBED_MODEL = os.getenv(
    "OLLAMA_EMBED_MODEL",
    "nomic-embed-text:latest",
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)