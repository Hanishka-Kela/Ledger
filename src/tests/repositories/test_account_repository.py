from uuid import uuid4

from src.infrastructure.database.user import User as ORMUser
from src.infrastructure.database.account import Account as ORMAccount

from src.infrastructure.repositories.account_repository import AccountRepository

from src.domain.account import Account as DomainAccount
from src.domain.account import AccountType


def test_create(db_session):
    user_id = uuid4()
    account_id = uuid4()

    user = ORMUser(
        user_id=user_id,
        email=f"{uuid4()}@example.com",
        password_hash="hashed_password"
    )

    db_session.add(user)
    db_session.commit()

    account = DomainAccount(
        account_id=account_id,
        owner_id=user_id,
        name="New Savings Account",
        type=AccountType.ASSET
    )

    repository = AccountRepository(db_session)

    created_account = repository.create(account)

    db_session.commit()

    assert created_account is account
    assert isinstance(created_account, DomainAccount)
    assert not isinstance(created_account, ORMAccount)

    orm_account = db_session.get(ORMAccount, account_id)

    assert orm_account is not None
    assert orm_account.account_id == account_id
    assert orm_account.owner_id == user_id
    assert orm_account.name == "New Savings Account"
    assert orm_account.type == AccountType.ASSET


def test_get_by_id(db_session):
    user_id = uuid4()
    account_id = uuid4()
    email = f"{uuid4()}@example.com"

    user = ORMUser(
        user_id=user_id,
        email=email,
        password_hash="hashed_password"
    )

    account = ORMAccount(
        account_id=account_id,
        owner_id=user_id,
        name="Savings Account",
        type=AccountType.ASSET
    )

    db_session.add(user)
    db_session.add(account)
    db_session.commit()

    repository = AccountRepository(db_session)

    retrieved_account = repository.get_by_id(account_id)

    assert retrieved_account is not None
    assert isinstance(retrieved_account, DomainAccount)
    assert not isinstance(retrieved_account, ORMAccount)

    assert retrieved_account.account_id == account_id
    assert retrieved_account.owner_id == user_id
    assert retrieved_account.name == "Savings Account"
    assert retrieved_account.type == AccountType.ASSET


def test_get_by_owner_id(db_session):
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    account_1_id = uuid4()
    account_2_id = uuid4()

    user = ORMUser(
        user_id=user_id,
        email=email,
        password_hash="hashed_password"
    )

    account_1 = ORMAccount(
        account_id=account_1_id,
        owner_id=user_id,
        name="Savings Account",
        type=AccountType.ASSET
    )

    account_2 = ORMAccount(
        account_id=account_2_id,
        owner_id=user_id,
        name="Checking Account",
        type=AccountType.ASSET
    )

    db_session.add(user)
    db_session.add(account_1)
    db_session.add(account_2)
    db_session.commit()

    repository = AccountRepository(db_session)

    accounts = repository.get_by_owner_id(user_id)

    assert len(accounts) == 2

    for account in accounts:
        assert isinstance(account, DomainAccount)
        assert not isinstance(account, ORMAccount)

    account_ids = {account.account_id for account in accounts}

    assert account_1_id in account_ids
    assert account_2_id in account_ids