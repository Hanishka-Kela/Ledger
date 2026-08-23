from uuid import uuid4
from datetime import datetime, timezone

from src.infrastructure.database.user import User
from src.infrastructure.database.account import Account
from src.infrastructure.database.transaction import Transaction
from src.infrastructure.database.entry import Entry

from src.infrastructure.repositories.transaction_repository import TransactionRepository

from src.domain.account import AccountType
from src.domain.entry import EntryType


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

    repository = TransactionRepository(db_session)

    retrieved_transaction = repository.get_by_id(transaction_id)

    assert retrieved_transaction is not None
    assert retrieved_transaction.transaction_id == transaction_id
    assert retrieved_transaction.description == "Test transaction"


def test_get_entries(db_session):
    user_id = uuid4()
    account_id = uuid4()
    transaction_id = uuid4()
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

    transaction = Transaction(
        transaction_id=transaction_id,
        timestamp=datetime.now(timezone.utc),
        description="Alice pays Bob"
    )

    entry_1 = Entry(
        entry_id=entry_1_id,
        transaction_id=transaction_id,
        account_id=account_id,
        type=EntryType.DEBIT,
        amount=20000
    )

    entry_2 = Entry(
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

    entry_ids = {entry.entry_id for entry in entries}

    assert entry_1_id in entry_ids
    assert entry_2_id in entry_ids