import os
from pathlib import Path
from dotenv import load_dotenv

# Configuration is kept separate from application startup.
load_dotenv()


# ============================================================
# PROJECT PATHS
# ============================================================

# This resolves to the project root when this file lives at:
# <project>/backend/core/config.py
ROOT = Path(__file__).resolve().parents[2]

DB_PATH = ROOT / "quizmate.db"
TOPICS_DIR = ROOT / "data" / "topics"


# ============================================================
# JWT CONFIGURATION
# ============================================================

JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "7G5F7aYahj4QHHNK2aALfFcVNGgtNb1M_TnlYIy43Sg",
)

JWT_ALG = "HS256"


# ============================================================
# FRONTEND CONFIGURATION
# ============================================================

FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:5173",
)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)

GEMINI_EMBED_MODEL = os.getenv(
    "GEMINI_EMBED_MODEL",
    "gemini-embedding-001",
)