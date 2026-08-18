import sqlite3

from fastapi import HTTPException

from ..core.app import app
from ..db.database import get_db
from ..schemas.models import AuthIn, TokenOut
from ..services.auth import (
    hash_password,
    make_token,
    verify_password,
)


@app.post(
    "/api/auth/register",
    response_model=TokenOut,
)
def register(
    req: AuthIn,
):

    if (
        not req.name
        or len(req.password) < 6
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Name and password "
                "(6+ characters) are required."
            ),
        )

    email = req.email.strip().lower()

    con = get_db()

    try:

        cur = con.execute(
            """
            INSERT INTO users(
                name,
                email,
                password_hash
            )
            VALUES(?,?,?)
            """,
            (
                req.name.strip(),
                email,
                hash_password(
                    req.password
                ),
            ),
        )

        con.commit()

        user_id = cur.lastrowid

    except sqlite3.IntegrityError:

        con.close()

        raise HTTPException(
            status_code=409,
            detail=(
                "An account with this "
                "email already exists."
            ),
        )

    finally:

        try:
            con.close()
        except Exception:
            pass

    return {
        "token": make_token(
            user_id,
            email,
        ),
        "user": {
            "id": user_id,
            "name": req.name.strip(),
            "email": email,
        },
    }


# ============================================================
# AUTH LOGIN
# ============================================================

@app.post(
    "/api/auth/login",
    response_model=TokenOut,
)
def login(
    req: AuthIn,
):

    email = req.email.strip().lower()

    con = get_db()

    row = con.execute(
        """
        SELECT *
        FROM users
        WHERE email=?
        """,
        (email,),
    ).fetchone()

    con.close()

    if (
        not row
        or not verify_password(
            req.password,
            row["password_hash"],
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    return {
        "token": make_token(
            row["id"],
            row["email"],
        ),
        "user": {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
        },
    }
