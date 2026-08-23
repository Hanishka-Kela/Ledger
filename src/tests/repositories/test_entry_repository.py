from uuid import uuid4
from datetime import datetime, timezone

from src.domain.entry import Entry as DomainEntry
from src.domain.account import AccountType
from src.domain.entry import EntryType

from src.infrastructure.database.user import User as ORMUser
from src.infrastructure.database.account import Account as ORMAccount
from src.infrastructure.database.transaction import Transaction as ORMTransaction
from src.infrastructure.database.entry import Entry as ORMEntry

from src.infrastructure.repositories.entry_repository import EntryRepository


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

    repository = EntryRepository(db_session)

    retrieved_entry = repository.get_by_id(entry_id)

    assert retrieved_entry is not None
    assert isinstance(retrieved_entry, DomainEntry)
    assert not isinstance(retrieved_entry, ORMEntry)

    assert retrieved_entry.entry_id == entry_id
    assert retrieved_entry.transaction_id == transaction_id
    assert retrieved_entry.account_id == account_id
    assert retrieved_entry.type == EntryType.DEBIT
    assert retrieved_entry.amount == 20000


def test_get_by_account_id(db_session):
    user_id = uuid4()
    account_id = uuid4()
    transaction_1_id = uuid4()
    transaction_2_id = uuid4()
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

    transaction_1 = ORMTransaction(
        transaction_id=transaction_1_id,
        timestamp=datetime.now(timezone.utc),
        description="Transaction 1"
    )

    transaction_2 = ORMTransaction(
        transaction_id=transaction_2_id,
        timestamp=datetime.now(timezone.utc),
        description="Transaction 2"
    )

    entry_1 = ORMEntry(
        entry_id=entry_1_id,
        transaction_id=transaction_1_id,
        account_id=account_id,
        type=EntryType.DEBIT,
        amount=20000
    )

    entry_2 = ORMEntry(
        entry_id=entry_2_id,
        transaction_id=transaction_2_id,
        account_id=account_id,
        type=EntryType.CREDIT,
        amount=5000
    )

    db_session.add(user)
    db_session.add(account)
    db_session.add(transaction_1)
    db_session.add(transaction_2)
    db_session.add(entry_1)
    db_session.add(entry_2)
    db_session.commit()

    repository = EntryRepository(db_session)

    entries = repository.get_by_account_id(account_id)

    assert len(entries) == 2

    for entry in entries:
        assert isinstance(entry, DomainEntry)
        assert not isinstance(entry, ORMEntry)

    entry_ids = {entry.entry_id for entry in entries}

    assert entry_1_id in entry_ids
    assert entry_2_id in entry_ids


def test_create(db_session):
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

    db_session.add(user)
    db_session.add(account)
    db_session.add(transaction)
    db_session.commit()

    entry = DomainEntry(
        entry_id=entry_id,
        transaction_id=transaction_id,
        account_id=account_id,
        type=EntryType.DEBIT,
        amount=20000
    )

    repository = EntryRepository(db_session)

    created_entry = repository.create(entry)

    db_session.commit()

    assert created_entry is entry
    assert isinstance(created_entry, DomainEntry)
    assert not isinstance(created_entry, ORMEntry)

    orm_entry = db_session.get(
        ORMEntry,
        entry_id
    )

    assert orm_entry is not None
    assert orm_entry.entry_id == entry_id
    assert orm_entry.transaction_id == transaction_id
    assert orm_entry.account_id == account_id
    assert orm_entry.type == EntryType.DEBIT
    assert orm_entry.amount == 20000