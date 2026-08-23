from uuid import uuid4

from src.infrastructure.database.user import User
from src.infrastructure.repositories.user_repository import UserRepository


def test_get_by_id(db_session):
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    user = User(
        user_id=user_id,
        email=email,
        password_hash="hashed_password"
    )

    db_session.add(user)
    db_session.commit()

    repository = UserRepository(db_session)

    retrieved_user = repository.get_by_id(user_id)

    assert retrieved_user is not None
    assert retrieved_user.user_id == user_id
    assert retrieved_user.email == email
    assert retrieved_user.password_hash == "hashed_password"


def test_get_by_email(db_session):
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    user = User(
        user_id=user_id,
        email=email,
        password_hash="hashed_password"
    )

    db_session.add(user)
    db_session.commit()

    repository = UserRepository(db_session)

    retrieved_user = repository.get_by_email(email)

    assert retrieved_user is not None
    assert retrieved_user.user_id == user_id
    assert retrieved_user.email == email


def test_create(db_session):
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    user = User(
        user_id=user_id,
        email=email,
        password_hash="hashed_password"
    )

    repository = UserRepository(db_session)

    created_user = repository.create(user)

    db_session.commit()

    assert created_user is user

    retrieved_user = db_session.get(User, user_id)

    assert retrieved_user is not None
    assert retrieved_user.user_id == user_id
    assert retrieved_user.email == email


def test_exists_by_email(db_session):
    email = f"{uuid4()}@example.com"

    user = User(
        user_id=uuid4(),
        email=email,
        password_hash="hashed_password"
    )

    db_session.add(user)
    db_session.commit()

    repository = UserRepository(db_session)

    assert repository.exists_by_email(email) is True
    assert repository.exists_by_email("does_not_exist@example.com") is False