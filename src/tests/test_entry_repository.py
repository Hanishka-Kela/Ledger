from uuid import uuid4

from src.infrastructure.database.user import User
from src.infrastructure.database.account import Account
from src.infrastructure.database.transaction import Transaction
from src.infrastructure.database.entry import Entry
from src.infrastructure.repositories.entry_repository import EntryRepository

from src.domain.account import AccountType
from src.domain.entry import EntryType

from datetime import datetime, timezone


def test_get_by_id(db_session):
    user_id = uuid4()
    account_id = uuid4()
    transaction_id = uuid4()
    entry_id = uuid4()

    user = User(
        user_id=user_id,
        email=f"{uuid4()}@example.com",
        password_hash="hashed_password"
    )

    account = Account(
        account_id=account_id,
        owner_id=user_id,
        name="Savings Account",
        type=AccountType.ASSET
    )

    transaction = Transaction(
        transaction_id=transaction_id,
        timestamp=datetime.now(timezone.utc),
        description="Test transaction"
    )

    entry = Entry(
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

    user = User(
        user_id=user_id,
        email=f"{uuid4()}@example.com",
        password_hash="hashed_password"
    )

    account = Account(
        account_id=account_id,
        owner_id=user_id,
        name="Savings Account",
        type=AccountType.ASSET
    )

    transaction_1 = Transaction(
        transaction_id=transaction_1_id,
        timestamp=datetime.now(timezone.utc),
        description="Transaction 1"
    )

    transaction_2 = Transaction(
        transaction_id=transaction_2_id,
        timestamp=datetime.now(timezone.utc),
        description="Transaction 2"
    )

    entry_1 = Entry(
        entry_id=entry_1_id,
        transaction_id=transaction_1_id,
        account_id=account_id,
        type=EntryType.DEBIT,
        amount=20000
    )

    entry_2 = Entry(
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

    entry_ids = {entry.entry_id for entry in entries}

    assert entry_1_id in entry_ids
    assert entry_2_id in entry_ids