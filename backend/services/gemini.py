from fastapi import HTTPException
from google import genai
from google.genai import types

from ..core.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)


# ============================================================
# GEMINI CLIENT
# ============================================================

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# CALL GEMINI
# ============================================================

def call_ai(
    prompt: str,
):
    """
    Send a prompt to Gemini and return the generated text.

    This keeps the same call_ai() interface used by
    question_validation.py.
    """

    if not prompt or not prompt.strip():
        raise ValueError(
            "Prompt cannot be empty."
        )

    print(
        "\n========== GEMINI DEBUG =========="
    )

    print(
        "LLM MODEL:",
        GEMINI_MODEL,
    )

    print(
        "PROMPT LENGTH:",
        len(prompt),
    )

    try:

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are QuizMate AI. "
                    "Follow the user's instructions exactly. "
                    "Return valid JSON when requested. "
                    "Do not return markdown."
                ),
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )

    except Exception as exc:

        print(
            "GEMINI ERROR:",
            repr(exc),
        )

        print(
            "==================================\n"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                f"Gemini API request failed: {str(exc)}"
            ),
        )

    result = ""

    try:
        result = response.text or ""
    except Exception:
        result = ""

    print(
        "GEMINI SUCCESS:",
        bool(result),
    )

    print(
        "RESPONSE LENGTH:",
        len(result),
    )

    print(
        "RESPONSE PREVIEW:",
        result[:1000],
    )

    print(
        "==================================\n"
    )

    if not result.strip():
        raise HTTPException(
            status_code=502,
            detail=(
                "Gemini returned an empty response."
            ),
        )

    return result.strip()