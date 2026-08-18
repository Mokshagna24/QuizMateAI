from datetime import datetime, timezone

from fastapi import Depends, HTTPException

from ..core.app import app
from ..db.database import get_db
from ..schemas.models import QuizOut, QuizRequest, SubmitRequest
from ..services.auth import current_user
from ..services.quiz_generation import generate_questions
from ..services.scoring import score_questions


@app.post(
    "/api/quiz/generate",
    response_model=QuizOut,
)
def quiz_generate(
    req: QuizRequest,
    user=Depends(current_user),
):

    questions = generate_questions(
        req
    )

    return {
        "questions": questions
    }


# ============================================================
# SUBMIT QUIZ
# ============================================================

@app.post("/api/quiz/submit")
def quiz_submit(
    req: SubmitRequest,
    user=Depends(current_user),
):

    try:

        if not req.questions:
            raise HTTPException(
                status_code=400,
                detail="No quiz questions supplied.",
            )

        if not isinstance(
            req.answers,
            dict,
        ):
            raise HTTPException(
                status_code=400,
                detail="Answers must be an object.",
            )

        print(
            "\n========== QUIZ SUBMIT =========="
        )

        print(
            "USER ID:",
            user["id"],
        )

        print(
            "SOURCE:",
            req.source_name,
        )

        print(
            "QUESTION COUNT:",
            len(req.questions),
        )

        print(
            "ANSWER COUNT:",
            len(req.answers),
        )

        print(
            "ANSWERS:",
            req.answers,
        )

        score = score_questions(
            req.questions,
            req.answers,
        )

        total = len(
            req.questions
        )

        con = get_db()

        con.execute(
            """
            INSERT INTO results(
                user_id,
                topic,
                score,
                total,
                difficulty,
                created_at
            )
            VALUES(?,?,?,?,?,?)
            """,
            (
                user["id"],
                req.source_name,
                score,
                total,
                req.difficulty,
                datetime.now(
                    timezone.utc
                ).isoformat(),
            ),
        )

        con.commit()
        con.close()

        percentage = (
            round(
                score / total * 100
            )
            if total
            else 0
        )

        print(
            "SCORE:",
            score,
            "/",
            total,
        )

        print(
            "PERCENTAGE:",
            percentage,
        )

        print(
            "=================================\n"
        )

        return {
            "score": score,
            "total": total,
            "percentage": percentage,
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            "\n========== QUIZ SUBMIT ERROR =========="
        )

        print(
            "ERROR:",
            repr(e),
        )

        import traceback

        traceback.print_exc()

        print(
            "========================================\n"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Quiz submission failed: {str(e)}"
            ),
        )
