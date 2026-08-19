from ..core.app import app

from ..core.config import (
    GEMINI_MODEL,
)


@app.get("/")
def health():

    return {
        "name": "QuizMate AI",
        "status": "ok",
        "provider": "Gemini",
        "model": GEMINI_MODEL,
    }