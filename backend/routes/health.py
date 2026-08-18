from ..core.app import app
from ..core.config import OLLAMA_BASE_URL, OLLAMA_MODEL


@app.get("/")
def health():
    return {
        "name": "QuizMate AI",
        "status": "ok",
        "ollama": OLLAMA_BASE_URL,
        "model": OLLAMA_MODEL,
    }
