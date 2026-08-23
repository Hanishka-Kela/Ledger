from uuid import uuid4

from src.domain.user import User as DomainUser
from src.infrastructure.database.user import User as ORMUser
from src.infrastructure.repositories.user_repository import UserRepository


def test_get_by_id(db_session):
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    user = ORMUser(
        user_id=user_id,
        email=email,
        password_hash="hashed_password"
    )

    db_session.add(user)
    db_session.commit()

    repository = UserRepository(db_session)

    retrieved_user = repository.get_by_id(user_id)

    assert retrieved_user is not None
    assert isinstance(retrieved_user, DomainUser)
    assert not isinstance(retrieved_user, ORMUser)

    assert retrieved_user.user_id == user_id
    assert retrieved_user.email == email
    assert retrieved_user.password_hash == "hashed_password"


def test_get_by_email(db_session):
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    user = ORMUser(
        user_id=user_id,
        email=email,
        password_hash="hashed_password"
    )

    db_session.add(user)
    db_session.commit()

    repository = UserRepository(db_session)

    retrieved_user = repository.get_by_email(email)

    assert retrieved_user is not None
    assert isinstance(retrieved_user, DomainUser)
    assert not isinstance(retrieved_user, ORMUser)

    assert retrieved_user.user_id == user_id
    assert retrieved_user.email == email


def test_create(db_session):
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    user = DomainUser(
        user_id=user_id,
        email=email,
        password_hash="hashed_password"
    )

    repository = UserRepository(db_session)

    created_user = repository.create(user)

    db_session.commit()

    assert created_user is user
    assert isinstance(created_user, DomainUser)

    orm_user = db_session.get(ORMUser, user_id)

    assert orm_user is not None
    assert orm_user.user_id == user_id
    assert orm_user.email == email
    assert orm_user.password_hash == "hashed_password"


def test_exists_by_email(db_session):
    email = f"{uuid4()}@example.com"

    user = ORMUser(
        user_id=uuid4(),
        email=email,
        password_hash="hashed_password"
    )

    db_session.add(user)
    db_session.commit()

    repository = UserRepository(db_session)

    assert repository.exists_by_email(email) is True
    assert repository.exists_by_email("does_not_exist@example.com") is False