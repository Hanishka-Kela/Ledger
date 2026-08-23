from uuid import uuid4

from src.infrastructure.database import init_db
from src.infrastructure.database.session import SessionLocal
from src.infrastructure.database.user import User
from src.infrastructure.repositories.user_repository import UserRepository


def test_get_by_id():
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    with SessionLocal() as session:
        user = User(
            user_id=user_id,
            email=email,
            password_hash="hashed_password"
        )

        session.add(user)
        session.commit()

    with SessionLocal() as session:
        repository = UserRepository(session)

        retrieved_user = repository.get_by_id(user_id)

        assert retrieved_user is not None
        assert retrieved_user.user_id == user_id
        assert retrieved_user.email == email


def test_get_by_email():
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    with SessionLocal() as session:
        user = User(
            user_id=user_id,
            email=email,
            password_hash="hashed_password"
        )

        session.add(user)
        session.commit()

    with SessionLocal() as session:
        repository = UserRepository(session)

        retrieved_user = repository.get_by_email(email)

        assert retrieved_user is not None
        assert retrieved_user.user_id == user_id
        assert retrieved_user.email == email


def test_create():
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    with SessionLocal() as session:
        repository = UserRepository(session)

        user = User(
            user_id=user_id,
            email=email,
            password_hash="hashed_password"
        )

        created_user = repository.create(user)

        session.commit()

        assert created_user is user

    with SessionLocal() as session:
        retrieved_user = session.get(User, user_id)

        assert retrieved_user is not None
        assert retrieved_user.email == email


def test_exists_by_email():
    email = f"{uuid4()}@example.com"

    with SessionLocal() as session:
        user = User(
            user_id=uuid4(),
            email=email,
            password_hash="hashed_password"
        )

        session.add(user)
        session.commit()

    with SessionLocal() as session:
        repository = UserRepository(session)

        assert repository.exists_by_email(email) is True
        assert repository.exists_by_email("does_not_exist@example.com") is False
