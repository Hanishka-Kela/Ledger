from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from src.infrastructure.config import SECRET_KEY
from src.infrastructure.security.jwt import (
    create_access_token,
    verify_access_token,
)


def test_create_access_token_returns_string():
    user_id = uuid4()

    token = create_access_token(user_id)

    assert isinstance(token, str)


def test_verify_access_token_returns_correct_user_id():
    user_id = uuid4()

    token = create_access_token(user_id)

    result = verify_access_token(token)

    assert result == user_id


def test_token_contains_expiration():
    user_id = uuid4()

    token = create_access_token(user_id)

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=["HS256"],
    )

    assert "exp" in payload


def test_token_cannot_be_verified_with_wrong_secret():
    user_id = uuid4()

    token = create_access_token(user_id)

    wrong_secret = "wrong-secret-that-is-32-bytes!!!"

    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(
            token,
            wrong_secret,
            algorithms=["HS256"],
        )


def test_expired_token_is_rejected():
    user_id = uuid4()

    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="Invalid token"):
        verify_access_token(token)


def test_token_without_subject_is_rejected():
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="Invalid token"):
        verify_access_token(token)


def test_token_with_invalid_user_id_is_rejected():
    payload = {
        "sub": "not-a-valid-uuid",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="Invalid token"):
        verify_access_token(token)