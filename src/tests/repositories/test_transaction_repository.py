from uuid import uuid4
from datetime import datetime, timezone

from src.domain.transaction import Transaction as DomainTransaction
from src.domain.entry import Entry as DomainEntry
from src.domain.account import AccountType
from src.domain.entry import EntryType

from src.infrastructure.database.user import User as ORMUser
from src.infrastructure.database.account import Account as ORMAccount
from src.infrastructure.database.transaction import Transaction as ORMTransaction
from src.infrastructure.database.entry import Entry as ORMEntry

from src.infrastructure.repositories.transaction_repository import (
    TransactionRepository
)


def test_get_by_id(db_session):
    user_id = uuid4()
    account_id = uuid4()
    transaction_id = uuid4()
    entry_id = uuid4()

    user = ORMUser(
        user_id=user_id,
        email=f"{uuid4()}@example.com",
        password_hash="hashed_password"
    )

    account = ORMAccount(
        account_id=account_id,
        owner_id=user_id,
        name="Savings Account",
        type=AccountType.ASSET
    )

    transaction = ORMTransaction(
        transaction_id=transaction_id,
        timestamp=datetime.now(timezone.utc),
        description="Test transaction"
    )

    entry = ORMEntry(
        entry_id=entry_id,
        transaction_id=transaction_id,
        account_id=account_id,
        type=EntryType.DEBIT,
        amount=20000
    )

    db_session.add(user)
    db_session.add(account)
    db_session.add(transaction)
    db_session.add(entry)
    db_session.commit()

    repository = TransactionRepository(db_session)

    retrieved_transaction = repository.get_by_id(transaction_id)

    assert retrieved_transaction is not None
    assert isinstance(retrieved_transaction, DomainTransaction)
    assert not isinstance(retrieved_transaction, ORMTransaction)

    assert retrieved_transaction.transaction_id == transaction_id
    assert retrieved_transaction.description == "Test transaction"

    assert len(retrieved_transaction.entries) == 1
    assert isinstance(retrieved_transaction.entries[0], DomainEntry)
    assert not isinstance(retrieved_transaction.entries[0], ORMEntry)


def test_get_entries(db_session):
    user_id = uuid4()
    account_id = uuid4()
    transaction_id = uuid4()
    entry_1_id = uuid4()
    entry_2_id = uuid4()

    user = ORMUser(
        user_id=user_id,
        email=f"{uuid4()}@example.com",
        password_hash="hashed_password"
    )

    account = ORMAccount(
        account_id=account_id,
        owner_id=user_id,
        name="Savings Account",
        type=AccountType.ASSET
    )

    transaction = ORMTransaction(
        transaction_id=transaction_id,
        timestamp=datetime.now(timezone.utc),
        description="Alice pays Bob"
    )

    entry_1 = ORMEntry(
        entry_id=entry_1_id,
        transaction_id=transaction_id,
        account_id=account_id,
        type=EntryType.DEBIT,
        amount=20000
    )

    entry_2 = ORMEntry(
        entry_id=entry_2_id,
        transaction_id=transaction_id,
        account_id=account_id,
        type=EntryType.CREDIT,
        amount=20000
    )

    db_session.add(user)
    db_session.add(account)
    db_session.add(transaction)
    db_session.add(entry_1)
    db_session.add(entry_2)
    db_session.commit()

    repository = TransactionRepository(db_session)

    entries = repository.get_entries(transaction_id)

    assert len(entries) == 2

    for entry in entries:
        assert isinstance(entry, DomainEntry)
        assert not isinstance(entry, ORMEntry)

    entry_ids = {entry.entry_id for entry in entries}

    assert entry_1_id in entry_ids
    assert entry_2_id in entry_ids


def test_create(db_session):
    transaction_id = uuid4()

    transaction = DomainTransaction(
        transaction_id=transaction_id,
        timestamp=datetime.now(timezone.utc),
        description="Test transaction",
        entries=[]
    )

    repository = TransactionRepository(db_session)

    created_transaction = repository.create(transaction)

    db_session.commit()

    assert created_transaction is transaction
    assert isinstance(created_transaction, DomainTransaction)
    assert not isinstance(created_transaction, ORMTransaction)

    orm_transaction = db_session.get(
        ORMTransaction,
        transaction_id
    )

    assert orm_transaction is not None
    assert orm_transaction.transaction_id == transaction_id
    assert orm_transaction.description == "Test transaction"