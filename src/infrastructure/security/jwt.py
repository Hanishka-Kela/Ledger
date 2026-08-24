import jwt

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jwt import (
    ExpiredSignatureError,
    InvalidSignatureError,
    DecodeError
)

from src.infrastructure.config import (
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256",
    )


def verify_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"],
        )

        subject = payload["sub"]

        return UUID(subject)

    except (
        ExpiredSignatureError,
        InvalidSignatureError,
        DecodeError,
        KeyError,
        ValueError,
    ) as exc:
        raise ValueError("Invalid token") from exc