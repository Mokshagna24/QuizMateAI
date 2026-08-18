from fastapi import Depends

from ..core.app import app
from ..db.database import get_db
from ..services.auth import current_user


@app.get("/api/results")
def results(
    user=Depends(current_user),
):

    con = get_db()

    rows = [
        dict(row)
        for row in con.execute(
            """
            SELECT
                topic,
                score,
                total,
                difficulty,
                created_at
            FROM results
            WHERE user_id=?
            ORDER BY id DESC
            """,
            (user["id"],),
        ).fetchall()
    ]

    con.close()

    return rows
