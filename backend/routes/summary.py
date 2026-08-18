from fastapi import Depends, HTTPException

from ..core.app import app
from ..core.config import OLLAMA_MODEL
from ..schemas.models import SummaryRequest
from ..services.auth import current_user
from ..services.json_utils import parse_ai_json
from ..services.ollama import call_ai, ollama_post


@app.post("/api/summary")
def summary(
    req: SummaryRequest,
    user=Depends(current_user),
):

    text = req.text.strip()

    if len(text) < 20:

        raise HTTPException(
            status_code=400,
            detail=(
                "Document text is too short "
                "to summarize."
            ),
        )

    prompt = f"""
You are QuizMate AI.

Summarize ONLY the document below.

SUMMARY STYLE:
{req.mode}

IMPORTANT:

1. Use only information from the document.
2. Do not invent facts.
3. The summary must not be empty.
4. Make the summary useful for studying.
5. Return ONLY valid JSON.
6. Do not return markdown.
7. Do not return ```json.

Return EXACTLY:

{{
  "summary": "Your complete summary here."
}}

DOCUMENT:

<DOCUMENT>
{text[:40000]}
</DOCUMENT>
"""

    try:

        raw = call_ai(
            prompt
        )

        parsed = parse_ai_json(
            raw
        )

        if not isinstance(
            parsed,
            dict,
        ):

            raise ValueError(
                "Summary response is not a JSON object."
            )

        summary_text = str(
            parsed.get(
                "summary",
                "",
            )
        ).strip()

        # ====================================================
        # IMPORTANT FALLBACK
        # ====================================================

        if not summary_text:

            print(
                "SUMMARY JSON WAS EMPTY. "
                "Retrying without JSON mode."
            )

            fallback_payload = {
                "model": OLLAMA_MODEL,

                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a document summarization "
                            "assistant. Summarize only the supplied "
                            "document. Do not invent information."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"""
Summarize this document.

Style:
{req.mode}

Document:
{text[:40000]}
""",
                    },
                ],

                "stream": False,

                "options": {
                    "temperature": 0.2,
                },
            }

            fallback_data = ollama_post(
                "/api/chat",
                fallback_payload,
                timeout=300,
            )

            summary_text = (
                fallback_data
                .get("message", {})
                .get("content", "")
                .strip()
            )

        if not summary_text:

            raise HTTPException(
                status_code=502,
                detail=(
                    "Ollama returned an empty summary."
                ),
            )

        print(
            "SUMMARY SUCCESS:",
            len(summary_text),
            "characters",
        )

        return {
            "summary": summary_text
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            "SUMMARY ERROR:",
            repr(e),
        )

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=502,
            detail=(
                "Failed to generate document summary."
            ),
        )
