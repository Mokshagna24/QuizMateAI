from datetime import datetime

from fastapi import Depends, HTTPException

from ..core.app import app
from ..db.database import get_db
from ..services.auth import current_user


@app.post("/api/feedback")
def submit_feedback(
    feedback: dict,
    user=Depends(current_user),
):
    experience = str(
        feedback.get("experience", "")
    ).strip()

    usefulness = str(
        feedback.get("usefulness", "")
    ).strip()

    improvement = str(
        feedback.get("improvement", "")
    ).strip()

    # ========================================================
    # VALIDATION
    # ========================================================

    valid_experience = {
        "Excellent",
        "Good",
        "Average",
        "Poor",
    }

    valid_usefulness = {
        "Yes",
        "Somewhat",
        "No",
    }

    if experience not in valid_experience:
        raise HTTPException(
            status_code=400,
            detail="Invalid experience rating.",
        )

    if usefulness not in valid_usefulness:
        raise HTTPException(
            status_code=400,
            detail="Invalid usefulness value.",
        )

    # ========================================================
    # SAVE FEEDBACK
    # ========================================================

    con = get_db()

    try:

        con.execute(
            """
            INSERT INTO feedback(
                user_id,
                experience,
                usefulness,
                improvement,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                experience,
                usefulness,
                improvement,
                datetime.utcnow().isoformat(),
            ),
        )

        con.commit()

    finally:
        con.close()

    return {
        "message": "Thank you for your feedback!"
    }