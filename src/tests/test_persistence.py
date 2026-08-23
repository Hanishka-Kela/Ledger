from uuid import uuid4
from datetime import datetime, timezone

from src.infrastructure.database.user import User
from src.infrastructure.database.account import Account
from src.infrastructure.database.transaction import Transaction
from src.infrastructure.database.entry import Entry
from src.domain.account import AccountType
from src.domain.entry import EntryType


def test_create_and_retrieve_user(db_session):
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    user = User(
        user_id=user_id,
        email=email,
        password_hash="hashed_password"
    )

    db_session.add(user)
    db_session.commit()

    retrieved_user = db_session.get(User, user_id)

    assert retrieved_user is not None
    assert retrieved_user.user_id == user_id
    assert retrieved_user.email == email
    assert retrieved_user.password_hash == "hashed_password"


def test_create_user_and_account(db_session):
    user_id = uuid4()
    account_id = uuid4()
    email = f"{uuid4()}@example.com"

    user = User(
        user_id=user_id,
        email=email,
        password_hash="hashed_password"
    )

    account = Account(
        account_id=account_id,
        owner_id=user_id,
        name="My Savings",
        type=AccountType.ASSET
    )

    db_session.add(user)
    db_session.add(account)
    db_session.commit()

    retrieved_account = db_session.get(Account, account_id)

    assert retrieved_account is not None
    assert retrieved_account.owner_id == user_id
    assert retrieved_account.name == "My Savings"
    assert retrieved_account.type == AccountType.ASSET

    assert retrieved_account.owner.user_id == user_id
    assert retrieved_account.owner.email == email


def test_create_transaction_with_entries(db_session):
    user_id = uuid4()
    email = f"{uuid4()}@example.com"

    alice_account_id = uuid4()
    bob_account_id = uuid4()

    transaction_id = uuid4()
    debit_entry_id = uuid4()
    credit_entry_id = uuid4()

    user = User(
        user_id=user_id,
        email=email,
        password_hash="hashed_password"
    )

    alice_account = Account(
        account_id=alice_account_id,
        owner_id=user_id,
        name="Alice Account",
        type=AccountType.ASSET
    )

    bob_account = Account(
        account_id=bob_account_id,
        owner_id=user_id,
        name="Bob Account",
        type=AccountType.ASSET
    )

    transaction = Transaction(
        transaction_id=transaction_id,
        timestamp=datetime.now(timezone.utc),
        description="Alice pays Bob",
    )

    debit_entry = Entry(
        entry_id=debit_entry_id,
        transaction_id=transaction_id,
        account_id=bob_account_id,
        type=EntryType.DEBIT,
        amount=20000
    )

    credit_entry = Entry(
        entry_id=credit_entry_id,
        transaction_id=transaction_id,
        account_id=alice_account_id,
        type=EntryType.CREDIT,
        amount=20000
    )

    db_session.add(user)
    db_session.add(alice_account)
    db_session.add(bob_account)
    db_session.add(transaction)
    db_session.add(debit_entry)
    db_session.add(credit_entry)

    db_session.commit()

    retrieved_transaction = db_session.get(
        Transaction,
        transaction_id
    )

    assert retrieved_transaction is not None
    assert retrieved_transaction.description == "Alice pays Bob"
    assert len(retrieved_transaction.entries) == 2

    entries = retrieved_transaction.entries

    assert any(
        entry.account_id == bob_account_id
        and entry.type == EntryType.DEBIT
        and entry.amount == 20000
        for entry in entries
    )

    assert any(
        entry.account_id == alice_account_id
        and entry.type == EntryType.CREDIT
        and entry.amount == 20000
        for entry in entries
    )