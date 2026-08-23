from uuid import uuid4

import pytest

from src.application.account_service import AccountService

from src.domain.account import Account as DomainAccount
from src.domain.account import AccountType

from src.infrastructure.database.user import User as ORMUser
from src.infrastructure.database.account import Account as ORMAccount

from src.infrastructure.repositories.user_repository import UserRepository
from src.infrastructure.repositories.account_repository import AccountRepository


def test_get_user_accounts(db_session):
    user_id = uuid4()

    user = ORMUser(
        user_id=user_id,
        email=f"{uuid4()}@example.com",
        password_hash="hashed_password"
    )

    account_1 = ORMAccount(
        account_id=uuid4(),
        owner_id=user_id,
        name="Savings Account",
        type=AccountType.ASSET
    )

    account_2 = ORMAccount(
        account_id=uuid4(),
        owner_id=user_id,
        name="Checking Account",
        type=AccountType.ASSET
    )

    db_session.add(user)
    db_session.add(account_1)
    db_session.add(account_2)
    db_session.commit()

    user_repository = UserRepository(db_session)
    account_repository = AccountRepository(db_session)

    service = AccountService(
        user_repository=user_repository,
        account_repository=account_repository
    )

    accounts = service.get_user_accounts(user_id)

    assert len(accounts) == 2

    assert all(
        isinstance(account, DomainAccount)
        for account in accounts
    )

    account_names = {account.name for account in accounts}

    assert "Savings Account" in account_names
    assert "Checking Account" in account_names


def test_get_user_accounts_user_not_found(db_session):
    user_id = uuid4()

    user_repository = UserRepository(db_session)
    account_repository = AccountRepository(db_session)

    service = AccountService(
        user_repository=user_repository,
        account_repository=account_repository
    )

    with pytest.raises(ValueError, match="User not Found"):
        service.get_user_accounts(user_id)


def test_create_account(db_session):
    user_id = uuid4()

    user = ORMUser(
        user_id=user_id,
        email=f"{uuid4()}@example.com",
        password_hash="hashed_password"
    )

    db_session.add(user)
    db_session.commit()

    user_repository = UserRepository(db_session)
    account_repository = AccountRepository(db_session)

    service = AccountService(
        user_repository=user_repository,
        account_repository=account_repository
    )

    account = service.create_account(
        user_id=user_id,
        name="New Savings Account",
        account_type=AccountType.ASSET
    )

    db_session.commit()

    assert isinstance(account, DomainAccount)

    assert account.owner_id == user_id
    assert account.name == "New Savings Account"
    assert account.type == AccountType.ASSET

    orm_account = db_session.get(
        ORMAccount,
        account.account_id
    )

    assert orm_account is not None
    assert orm_account.account_id == account.account_id
    assert orm_account.owner_id == user_id
    assert orm_account.name == "New Savings Account"
    assert orm_account.type == AccountType.ASSET


def test_create_account_user_not_found(db_session):
    user_id = uuid4()

    user_repository = UserRepository(db_session)
    account_repository = AccountRepository(db_session)

    service = AccountService(
        user_repository=user_repository,
        account_repository=account_repository
    )

    with pytest.raises(ValueError, match="User not found"):
        service.create_account(
            user_id=user_id,
            name="New Savings Account",
            account_type=AccountType.ASSET
        )