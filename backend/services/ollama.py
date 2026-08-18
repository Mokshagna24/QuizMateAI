import requests
from fastapi import HTTPException

from ..core.config import (
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_MODEL,
    OLLAMA_MODEL,
)


def ollama_post(
    endpoint: str,
    payload: dict,
    timeout: int = 180,
):
    url = f"{OLLAMA_BASE_URL}{endpoint}"

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Ollama is not running. "
                "Start Ollama and make sure the required "
                "models are installed."
            ),
        )

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail=(
                "Ollama took too long to respond. "
                "Please try again."
            ),
        )

    except requests.exceptions.HTTPError as e:
        detail = ""

        try:
            detail = response.json().get(
                "error",
                "",
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=502,
            detail=(
                f"Ollama API error: "
                f"{detail or str(e)}"
            ),
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama request failed: {str(e)}",
        )


def call_ai(prompt: str):
    print(
        "\n========== OLLAMA DEBUG =========="
    )

    print(
        "OLLAMA URL:",
        OLLAMA_BASE_URL,
    )

    print(
        "LLM MODEL:",
        OLLAMA_MODEL,
    )

    print(
        "EMBED MODEL:",
        OLLAMA_EMBED_MODEL,
    )

    print(
        "PROMPT LENGTH:",
        len(prompt),
    )

    payload = {
        "model": OLLAMA_MODEL,

        "messages": [
            {
                "role": "system",
                "content": (
                    "You are QuizMate AI. "
                    "Follow the user's instructions exactly. "
                    "Return valid JSON when requested. "
                    "Do not return markdown."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],

        "stream": False,

        "format": "json",

        "options": {
            "temperature": 0.2,
        },
    }

    data = ollama_post(
        "/api/chat",
        payload,
        timeout=300,
    )

    result = (
        data
        .get("message", {})
        .get("content", "")
    )

    print(
        "OLLAMA SUCCESS:",
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
                "Ollama returned an empty response."
            ),
        )

    return result
