from sqlalchemy.orm import configure_mappers

from src.infrastructure.database.user import User
from src.infrastructure.database.account import Account
from src.infrastructure.database.transaction import Transaction
from src.infrastructure.database.entry import Entry


def test_orm_models():
    configure_mappers()

    assert User.__tablename__ == "users"
    assert Account.__tablename__ == "accounts"
    assert Transaction.__tablename__ == "transactions"
    assert Entry.__tablename__ == "entries"


def test_user_account_relationship():
    assert User.accounts.property.back_populates == "owner"
    assert Account.owner.property.back_populates == "accounts"


def test_transaction_entry_relationship():
    assert Transaction.entries.property.back_populates == "transaction"
    assert Entry.transaction.property.back_populates == "entries"


def test_account_entry_relationship():
    assert Account.entries.property.back_populates == "account"
    assert Entry.account.property.back_populates == "entries"