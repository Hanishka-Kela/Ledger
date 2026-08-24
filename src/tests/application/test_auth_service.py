from uuid import uuid4

import pytest

from src.application.auth_service import AuthService
from src.domain.user import User as DomainUser
from src.infrastructure.database.user import User as ORMUser
from src.infrastructure.repositories.user_repository import UserRepository


def test_signup(db_session):
    email = f"{uuid4()}@example.com"
    password = "password123"

    user_repository = UserRepository(db_session)

    service = AuthService(
        user_repository=user_repository
    )

    user = service.signup(
        email=email,
        password=password,
        confirm_password=password
    )

    assert isinstance(user, DomainUser)

    assert user.email == email
    assert user.password_hash != password

    db_session.commit()

    orm_user = db_session.get(
        ORMUser,
        user.user_id
    )

    assert orm_user is not None
    assert orm_user.user_id == user.user_id
    assert orm_user.email == email
    assert orm_user.password_hash == user.password_hash


def test_signup_passwords_do_not_match(db_session):
    email = f"{uuid4()}@example.com"

    user_repository = UserRepository(db_session)

    service = AuthService(
        user_repository=user_repository
    )

    with pytest.raises(ValueError, match="Passwords don't match"):
        service.signup(
            email=email,
            password="password123",
            confirm_password="differentpassword"
        )


def test_signup_email_already_exists(db_session):
    email = f"{uuid4()}@example.com"

    existing_user = ORMUser(
        user_id=uuid4(),
        email=email,
        password_hash="existing_hash"
    )

    db_session.add(existing_user)
    db_session.commit()

    user_repository = UserRepository(db_session)

    service = AuthService(
        user_repository=user_repository
    )

    with pytest.raises(ValueError, match="User already exists"):
        service.signup(
            email=email,
            password="password123",
            confirm_password="password123"
        )


def test_signup_password_can_be_verified(db_session):
    email = f"{uuid4()}@example.com"
    password = "password123"

    user_repository = UserRepository(db_session)

    service = AuthService(
        user_repository=user_repository
    )

    user = service.signup(
        email=email,
        password=password,
        confirm_password=password
    )

    db_session.commit()

    orm_user = db_session.get(
        ORMUser,
        user.user_id
    )

    assert orm_user is not None

    from src.infrastructure.security.password import verify_password

    assert verify_password(
        password,
        orm_user.password_hash
    ) is True
