from uuid import uuid4

import pytest
from sqlalchemy import func, select

from src.infrastructure.database.entry import Entry as ORMEntry
from src.infrastructure.database.transaction import Transaction as ORMTransaction
from src.infrastructure.repositories.entry_repository import EntryRepository


def signup_user(
    client,
    email: str,
    password: str = "Password123!"
):
    response = client.post(
        "/auth/signup",
        json={
            "email": email,
            "password": password,
            "confirm_password": password
        }
    )

    assert response.status_code == 200

    return response.json()


def login_user(
    client,
    email: str,
    password: str = "Password123!"
):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def auth_headers(token: str):
    return {
        "Authorization": f"Bearer {token}"
    }


def create_account(
    client,
    token: str,
    name: str,
    account_type: str
):
    response = client.post(
        "/accounts",
        headers=auth_headers(token),
        json={
            "name": name,
            "account_type": account_type
        }
    )

    assert response.status_code == 200

    return response.json()


def create_journal(
    client,
    token: str,
    description: str,
    entries: list[dict]
):
    response = client.post(
        "/transactions/journal",
        headers=auth_headers(token),
        json={
            "description": description,
            "entries": entries
        }
    )

    return response


def fund_asset_account(
    client,
    token: str,
    asset_account_id: str,
    equity_account_id: str,
    amount: int
):
    response = create_journal(
        client=client,
        token=token,
        description="Opening capital",
        entries=[
            {
                "account_id": asset_account_id,
                "type": "DEBIT",
                "amount": amount
            },
            {
                "account_id": equity_account_id,
                "type": "CREDIT",
                "amount": amount
            }
        ]
    )

    assert response.status_code == 200

    return response.json()


def test_journal_transaction_success(client):
    signup_user(
        client,
        "journal-success@example.com"
    )

    token = login_user(
        client,
        "journal-success@example.com"
    )

    cash = create_account(
        client,
        token,
        "Cash",
        "ASSET"
    )

    equity = create_account(
        client,
        token,
        "Owner Equity",
        "EQUITY"
    )

    response = create_journal(
        client=client,
        token=token,
        description="Owner capital",
        entries=[
            {
                "account_id": cash["account_id"],
                "type": "DEBIT",
                "amount": 1000
            },
            {
                "account_id": equity["account_id"],
                "type": "CREDIT",
                "amount": 1000
            }
        ]
    )

    assert response.status_code == 200

    data = response.json()

    assert data["description"] == "Owner capital"
    assert len(data["entries"]) == 2

    assert data["entries"][0]["account_id"] == cash["account_id"]
    assert data["entries"][0]["type"] == "DEBIT"
    assert data["entries"][0]["amount"] == 1000

    assert data["entries"][1]["account_id"] == equity["account_id"]
    assert data["entries"][1]["type"] == "CREDIT"
    assert data["entries"][1]["amount"] == 1000

    assert (
        data["entries"][0]["transaction_id"]
        == data["transaction_id"]
    )

    assert (
        data["entries"][1]["transaction_id"]
        == data["transaction_id"]
    )


def test_normal_asset_transfer_success(client):
    signup_user(
        client,
        "transfer-success@example.com"
    )

    token = login_user(
        client,
        "transfer-success@example.com"
    )

    source = create_account(
        client,
        token,
        "Cash",
        "ASSET"
    )

    destination = create_account(
        client,
        token,
        "Bank",
        "ASSET"
    )

    equity = create_account(
        client,
        token,
        "Owner Equity",
        "EQUITY"
    )

    fund_asset_account(
        client=client,
        token=token,
        asset_account_id=source["account_id"],
        equity_account_id=equity["account_id"],
        amount=1000
    )

    response = client.post(
        "/transactions",
        headers=auth_headers(token),
        json={
            "source_account_id": source["account_id"],
            "destination_account_id": destination["account_id"],
            "amount": 300,
            "description": "Move cash to bank"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["description"] == "Move cash to bank"
    assert len(data["entries"]) == 2

    source_entry = data["entries"][0]
    destination_entry = data["entries"][1]

    assert source_entry["account_id"] == source["account_id"]
    assert source_entry["type"] == "CREDIT"
    assert source_entry["amount"] == 300

    assert destination_entry["account_id"] == destination["account_id"]
    assert destination_entry["type"] == "DEBIT"
    assert destination_entry["amount"] == 300


def test_cross_user_transfer_success(client):
    signup_user(
        client,
        "sender@example.com"
    )

    signup_user(
        client,
        "receiver@example.com"
    )

    sender_token = login_user(
        client,
        "sender@example.com"
    )

    receiver_token = login_user(
        client,
        "receiver@example.com"
    )

    sender_cash = create_account(
        client,
        sender_token,
        "Sender Cash",
        "ASSET"
    )

    sender_equity = create_account(
        client,
        sender_token,
        "Sender Equity",
        "EQUITY"
    )

    receiver_cash = create_account(
        client,
        receiver_token,
        "Receiver Cash",
        "ASSET"
    )

    fund_asset_account(
        client=client,
        token=sender_token,
        asset_account_id=sender_cash["account_id"],
        equity_account_id=sender_equity["account_id"],
        amount=1000
    )

    response = client.post(
        "/transactions",
        headers=auth_headers(sender_token),
        json={
            "source_account_id": sender_cash["account_id"],
            "destination_account_id": receiver_cash["account_id"],
            "amount": 250,
            "description": "Pay second user"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["entries"][0]["account_id"]
        == sender_cash["account_id"]
    )

    assert data["entries"][0]["type"] == "CREDIT"

    assert (
        data["entries"][1]["account_id"]
        == receiver_cash["account_id"]
    )

    assert data["entries"][1]["type"] == "DEBIT"


def test_user_cannot_spend_from_another_users_account(client):
    signup_user(
        client,
        "owner@example.com"
    )

    signup_user(
        client,
        "attacker@example.com"
    )

    owner_token = login_user(
        client,
        "owner@example.com"
    )

    attacker_token = login_user(
        client,
        "attacker@example.com"
    )

    owner_cash = create_account(
        client,
        owner_token,
        "Owner Cash",
        "ASSET"
    )

    owner_equity = create_account(
        client,
        owner_token,
        "Owner Equity",
        "EQUITY"
    )

    attacker_cash = create_account(
        client,
        attacker_token,
        "Attacker Cash",
        "ASSET"
    )

    fund_asset_account(
        client=client,
        token=owner_token,
        asset_account_id=owner_cash["account_id"],
        equity_account_id=owner_equity["account_id"],
        amount=1000
    )

    response = client.post(
        "/transactions",
        headers=auth_headers(attacker_token),
        json={
            "source_account_id": owner_cash["account_id"],
            "destination_account_id": attacker_cash["account_id"],
            "amount": 100,
            "description": "Unauthorized transfer"
        }
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Not authorized to use source account"
    }


def test_transaction_rejects_missing_source_account(client):
    signup_user(
        client,
        "missing-source@example.com"
    )

    token = login_user(
        client,
        "missing-source@example.com"
    )

    destination = create_account(
        client,
        token,
        "Destination",
        "ASSET"
    )

    response = client.post(
        "/transactions",
        headers=auth_headers(token),
        json={
            "source_account_id": str(uuid4()),
            "destination_account_id": destination["account_id"],
            "amount": 100,
            "description": "Missing source"
        }
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Source account does not exist"
    }


def test_transaction_rejects_missing_destination_account(client):
    signup_user(
        client,
        "missing-destination@example.com"
    )

    token = login_user(
        client,
        "missing-destination@example.com"
    )

    source = create_account(
        client,
        token,
        "Cash",
        "ASSET"
    )

    equity = create_account(
        client,
        token,
        "Equity",
        "EQUITY"
    )

    fund_asset_account(
        client=client,
        token=token,
        asset_account_id=source["account_id"],
        equity_account_id=equity["account_id"],
        amount=1000
    )

    response = client.post(
        "/transactions",
        headers=auth_headers(token),
        json={
            "source_account_id": source["account_id"],
            "destination_account_id": str(uuid4()),
            "amount": 100,
            "description": "Missing destination"
        }
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Destination account does not exist"
    }


def test_transaction_rejects_insufficient_funds(client):
    signup_user(
        client,
        "insufficient@example.com"
    )

    token = login_user(
        client,
        "insufficient@example.com"
    )

    source = create_account(
        client,
        token,
        "Cash",
        "ASSET"
    )

    destination = create_account(
        client,
        token,
        "Bank",
        "ASSET"
    )

    response = client.post(
        "/transactions",
        headers=auth_headers(token),
        json={
            "source_account_id": source["account_id"],
            "destination_account_id": destination["account_id"],
            "amount": 100,
            "description": "Too much"
        }
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Insufficient funds"
    }


def test_journal_rejects_unbalanced_entries(client):
    signup_user(
        client,
        "unbalanced@example.com"
    )

    token = login_user(
        client,
        "unbalanced@example.com"
    )

    cash = create_account(
        client,
        token,
        "Cash",
        "ASSET"
    )

    equity = create_account(
        client,
        token,
        "Equity",
        "EQUITY"
    )

    response = create_journal(
        client=client,
        token=token,
        description="Broken journal",
        entries=[
            {
                "account_id": cash["account_id"],
                "type": "DEBIT",
                "amount": 1000
            },
            {
                "account_id": equity["account_id"],
                "type": "CREDIT",
                "amount": 500
            }
        ]
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Journal transaction is not balanced"
    }


def test_transaction_requires_authentication(client):
    response = client.post(
        "/transactions",
        json={
            "source_account_id": str(uuid4()),
            "destination_account_id": str(uuid4()),
            "amount": 100,
            "description": "Unauthorized"
        }
    )

    assert response.status_code == 401


def test_failed_transaction_rolls_back_all_database_changes(
    client,
    db_session,
    monkeypatch
):
    signup_user(
        client,
        "rollback@example.com"
    )

    token = login_user(
        client,
        "rollback@example.com"
    )

    source = create_account(
        client,
        token,
        "Cash",
        "ASSET"
    )

    destination = create_account(
        client,
        token,
        "Bank",
        "ASSET"
    )

    equity = create_account(
        client,
        token,
        "Equity",
        "EQUITY"
    )

    fund_asset_account(
        client=client,
        token=token,
        asset_account_id=source["account_id"],
        equity_account_id=equity["account_id"],
        amount=1000
    )

    transaction_count_before = db_session.scalar(
        select(func.count()).select_from(
            ORMTransaction
        )
    )

    entry_count_before = db_session.scalar(
        select(func.count()).select_from(
            ORMEntry
        )
    )

    original_create = EntryRepository.create

    call_count = {
        "value": 0
    }

    def failing_create(self, entry):
        call_count["value"] += 1

        if call_count["value"] == 2:
            raise RuntimeError(
                "Simulated entry persistence failure"
            )

        return original_create(
            self,
            entry
        )

    monkeypatch.setattr(
        EntryRepository,
        "create",
        failing_create
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated entry persistence failure"
    ):
        client.post(
            "/transactions",
            headers=auth_headers(token),
            json={
                "source_account_id": source["account_id"],
                "destination_account_id": destination["account_id"],
                "amount": 300,
                "description": "Should rollback"
            }
        )

    transaction_count_after = db_session.scalar(
        select(func.count()).select_from(
            ORMTransaction
        )
    )

    entry_count_after = db_session.scalar(
        select(func.count()).select_from(
            ORMEntry
        )
    )

    assert (
        transaction_count_after
        == transaction_count_before
    )

    assert (
        entry_count_after
        == entry_count_before
    )