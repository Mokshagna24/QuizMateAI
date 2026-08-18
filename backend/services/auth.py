import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Header, HTTPException

from ..core.config import JWT_ALG, JWT_SECRET


def hash_password(
    password: str,
    salt: Optional[bytes] = None,
):
    salt = salt or os.urandom(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        120_000,
    )

    return salt.hex() + ":" + digest.hex()


def verify_password(
    password: str,
    stored: str,
):
    try:
        salt_hex, digest_hex = stored.split(":")

        test = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt_hex),
            120_000,
        )

        return hmac.compare_digest(
            test.hex(),
            digest_hex,
        )

    except Exception:
        return False


def make_token(
    user_id: int,
    email: str,
):
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=12),
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALG,
    )


def current_user(
    authorization: Optional[str] = Header(
        default=None
    ),
):
    if (
        not authorization
        or not authorization.startswith("Bearer ")
    ):
        raise HTTPException(
            status_code=401,
            detail="Please log in.",
        )

    token = authorization.split(
        " ",
        1,
    )[1]

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALG],
        )

        return {
            "id": int(payload["sub"]),
            "email": payload["email"],
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please log in.",
        )
