from uuid import uuid4

from src.infrastructure.database import init_db
from src.infrastructure.database.session import SessionLocal
from src.infrastructure.database.user import User
from src.infrastructure.database.account import Account
from src.infrastructure.repositories.account_repository import AccountRepository
from src.domain.account import AccountType


def test_get_by_id():
    user_id = uuid4()
    account_id = uuid4()
    email = f"{uuid4()}@example.com"

    with SessionLocal() as session:
        user = User(
            user_id=user_id,
            email=email,
            password_hash="hashed_password"
        )

        account = Account(
            account_id=account_id,
            owner_id=user_id,
            name="Savings Account",
            type=AccountType.ASSET
        )

        session.add(user)
        session.add(account)
        session.commit()

    with SessionLocal() as session:
        repository = AccountRepository(session)

        retrieved_account = repository.get_by_id(account_id)

        assert retrieved_account is not None
        assert retrieved_account.account_id == account_id
        assert retrieved_account.owner_id == user_id
        assert retrieved_account.name == "Savings Account"
        assert retrieved_account.type == AccountType.ASSET


def test_get_by_owner_id():
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    account_1_id = uuid4()
    account_2_id = uuid4()

    with SessionLocal() as session:
        user = User(
            user_id=user_id,
            email=email,
            password_hash="hashed_password"
        )

        account_1 = Account(
            account_id=account_1_id,
            owner_id=user_id,
            name="Savings Account",
            type=AccountType.ASSET
        )

        account_2 = Account(
            account_id=account_2_id,
            owner_id=user_id,
            name="Checking Account",
            type=AccountType.ASSET
        )

        session.add(user)
        session.add(account_1)
        session.add(account_2)
        session.commit()

    with SessionLocal() as session:
        repository = AccountRepository(session)

        accounts = repository.get_by_owner_id(user_id)

        assert len(accounts) == 2

        account_ids = {account.account_id for account in accounts}

        assert account_1_id in account_ids
        assert account_2_id in account_ids

