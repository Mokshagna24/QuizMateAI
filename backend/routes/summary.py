from fastapi import Depends, HTTPException

from ..core.app import app
from ..schemas.models import SummaryRequest
from ..services.auth import current_user
from ..services.json_utils import parse_ai_json
from ..services.gemini import call_ai


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
        # GEMINI FALLBACK
        # ====================================================

        if not summary_text:

            print(
                "SUMMARY JSON WAS EMPTY. "
                "Retrying with Gemini."
            )

            fallback_prompt = f"""
You are a document summarization assistant.

Summarize ONLY the supplied document.

SUMMARY STYLE:
{req.mode}

IMPORTANT:

1. Use only information from the document.
2. Do not invent information.
3. Create a useful summary for studying.
4. Return ONLY valid JSON.
5. Do not return markdown.
6. Do not return ```json.

Return EXACTLY:

{{
  "summary": "Your complete summary here."
}}

DOCUMENT:

<DOCUMENT>
{text[:40000]}
</DOCUMENT>
"""

            fallback_raw = call_ai(
                fallback_prompt
            )

            fallback_parsed = parse_ai_json(
                fallback_raw
            )

            if isinstance(
                fallback_parsed,
                dict,
            ):

                summary_text = str(
                    fallback_parsed.get(
                        "summary",
                        "",
                    )
                ).strip()

        if not summary_text:

            raise HTTPException(
                status_code=502,
                detail=(
                    "Gemini returned an empty summary."
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