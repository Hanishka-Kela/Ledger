from uuid import uuid4


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

    assert response.status_code == 201

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

    assert response.status_code == 201

    return response.json()


def fund_asset_account(
    client,
    token: str,
    asset_account_id: str,
    equity_account_id: str,
    amount: int
):
    response = client.post(
        "/transactions/journal",
        headers=auth_headers(token),
        json={
            "description": "Opening capital",
            "entries": [
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
        }
    )

    assert response.status_code == 201

    return response.json()


def test_create_account_requires_authentication(client):
    response = client.post(
        "/accounts",
        json={
            "name": "Cash",
            "account_type": "ASSET"
        }
    )

    assert response.status_code == 401


def test_authenticated_user_can_create_account(client):
    user = signup_user(
        client,
        email="user1@example.com"
    )

    token = login_user(
        client,
        email="user1@example.com"
    )

    response = client.post(
        "/accounts",
        json={
            "name": "Cash",
            "account_type": "ASSET"
        },
        headers=auth_headers(token)
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Cash"
    assert data["type"] == "ASSET"
    assert data["owner_id"] == user["user_id"]
    assert "account_id" in data


def test_authenticated_user_can_get_own_accounts(client):
    user = signup_user(
        client,
        email="user2@example.com"
    )

    token = login_user(
        client,
        email="user2@example.com"
    )

    headers = auth_headers(token)

    create_account(
        client,
        token,
        "Cash",
        "ASSET"
    )

    create_account(
        client,
        token,
        "Expenses",
        "EXPENSE"
    )

    response = client.get(
        "/accounts",
        headers=headers
    )

    assert response.status_code == 200

    accounts = response.json()

    assert len(accounts) == 2

    assert accounts[0]["owner_id"] == user["user_id"]
    assert accounts[1]["owner_id"] == user["user_id"]

    account_names = {
        account["name"]
        for account in accounts
    }

    assert account_names == {
        "Cash",
        "Expenses"
    }


def test_user_cannot_see_another_users_accounts(client):
    user1 = signup_user(
        client,
        email="user3@example.com"
    )

    user2 = signup_user(
        client,
        email="user4@example.com"
    )

    token1 = login_user(
        client,
        email="user3@example.com"
    )

    token2 = login_user(
        client,
        email="user4@example.com"
    )

    create_account(
        client,
        token1,
        "User 1 Cash",
        "ASSET"
    )

    create_account(
        client,
        token2,
        "User 2 Cash",
        "ASSET"
    )

    response = client.get(
        "/accounts",
        headers=auth_headers(token1)
    )

    assert response.status_code == 200

    accounts = response.json()

    assert len(accounts) == 1

    assert accounts[0]["name"] == "User 1 Cash"
    assert accounts[0]["owner_id"] == user1["user_id"]

    assert accounts[0]["owner_id"] != user2["user_id"]


def test_account_with_no_entries_has_zero_balance(client):
    signup_user(
        client,
        email="zero-balance@example.com"
    )

    token = login_user(
        client,
        email="zero-balance@example.com"
    )

    account = create_account(
        client,
        token,
        "Empty Cash",
        "ASSET"
    )

    response = client.get(
        f"/accounts/{account['account_id']}/balance",
        headers=auth_headers(token)
    )

    assert response.status_code == 200

    assert response.json() == {
        "account_id": account["account_id"],
        "balance": 0
    }


def test_funded_asset_account_returns_correct_balance(client):
    signup_user(
        client,
        email="funded-balance@example.com"
    )

    token = login_user(
        client,
        email="funded-balance@example.com"
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

    fund_asset_account(
        client=client,
        token=token,
        asset_account_id=cash["account_id"],
        equity_account_id=equity["account_id"],
        amount=1000
    )

    response = client.get(
        f"/accounts/{cash['account_id']}/balance",
        headers=auth_headers(token)
    )

    assert response.status_code == 200

    assert response.json() == {
        "account_id": cash["account_id"],
        "balance": 1000
    }


def test_balance_reflects_completed_transfer(client):
    signup_user(
        client,
        email="balance-transfer@example.com"
    )

    token = login_user(
        client,
        email="balance-transfer@example.com"
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

    transfer_response = client.post(
        "/transactions",
        headers=auth_headers(token),
        json={
            "source_account_id": source["account_id"],
            "destination_account_id": destination["account_id"],
            "amount": 300,
            "description": "Move cash to bank"
        }
    )

    assert transfer_response.status_code == 201

    source_balance_response = client.get(
        f"/accounts/{source['account_id']}/balance",
        headers=auth_headers(token)
    )

    destination_balance_response = client.get(
        f"/accounts/{destination['account_id']}/balance",
        headers=auth_headers(token)
    )

    assert source_balance_response.status_code == 200
    assert destination_balance_response.status_code == 200

    assert source_balance_response.json() == {
        "account_id": source["account_id"],
        "balance": 700
    }

    assert destination_balance_response.json() == {
        "account_id": destination["account_id"],
        "balance": 300
    }


def test_balance_returns_404_for_missing_account(client):
    signup_user(
        client,
        email="missing-balance@example.com"
    )

    token = login_user(
        client,
        email="missing-balance@example.com"
    )

    missing_account_id = uuid4()

    response = client.get(
        f"/accounts/{missing_account_id}/balance",
        headers=auth_headers(token)
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Account does not exist"
    }


def test_user_cannot_view_another_users_balance(client):
    signup_user(
        client,
        email="balance-owner@example.com"
    )

    signup_user(
        client,
        email="balance-other@example.com"
    )

    owner_token = login_user(
        client,
        email="balance-owner@example.com"
    )

    other_token = login_user(
        client,
        email="balance-other@example.com"
    )

    owner_account = create_account(
        client,
        owner_token,
        "Owner Cash",
        "ASSET"
    )

    response = client.get(
        f"/accounts/{owner_account['account_id']}/balance",
        headers=auth_headers(other_token)
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Not authorized to view account"
    }


def test_balance_requires_authentication(client):
    account_id = uuid4()

    response = client.get(
        f"/accounts/{account_id}/balance"
    )

    assert response.status_code == 401


def test_account_with_no_entries_has_empty_transaction_history(client):
    signup_user(
        client,
        email="empty-history@example.com"
    )

    token = login_user(
        client,
        email="empty-history@example.com"
    )

    account = create_account(
        client,
        token,
        "Empty Account",
        "ASSET"
    )

    response = client.get(
        f"/accounts/{account['account_id']}/transactions",
        headers=auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json() == []


def test_account_transaction_history_returns_related_transactions(client):
    signup_user(
        client,
        email="history@example.com"
    )

    token = login_user(
        client,
        email="history@example.com"
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

    opening_transaction = fund_asset_account(
        client=client,
        token=token,
        asset_account_id=source["account_id"],
        equity_account_id=equity["account_id"],
        amount=1000
    )

    transfer_response = client.post(
        "/transactions",
        headers=auth_headers(token),
        json={
            "source_account_id": source["account_id"],
            "destination_account_id": destination["account_id"],
            "amount": 300,
            "description": "Move cash to bank"
        }
    )

    assert transfer_response.status_code == 201

    transfer_transaction = transfer_response.json()

    response = client.get(
        f"/accounts/{source['account_id']}/transactions",
        headers=auth_headers(token)
    )

    assert response.status_code == 200

    transactions = response.json()

    assert len(transactions) == 2

    transaction_ids = {
        transaction["transaction_id"]
        for transaction in transactions
    }

    assert transaction_ids == {
        opening_transaction["transaction_id"],
        transfer_transaction["transaction_id"]
    }


def test_destination_account_history_contains_received_transfer(client):
    signup_user(
        client,
        email="destination-history@example.com"
    )

    token = login_user(
        client,
        email="destination-history@example.com"
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

    transfer_response = client.post(
        "/transactions",
        headers=auth_headers(token),
        json={
            "source_account_id": source["account_id"],
            "destination_account_id": destination["account_id"],
            "amount": 250,
            "description": "Received transfer"
        }
    )

    assert transfer_response.status_code == 201

    transaction_id = transfer_response.json()["transaction_id"]

    response = client.get(
        f"/accounts/{destination['account_id']}/transactions",
        headers=auth_headers(token)
    )

    assert response.status_code == 200

    transactions = response.json()

    assert len(transactions) == 1
    assert transactions[0]["transaction_id"] == transaction_id
    assert transactions[0]["description"] == "Received transfer"


def test_account_transaction_history_returns_404_for_missing_account(
    client
):
    signup_user(
        client,
        email="missing-history@example.com"
    )

    token = login_user(
        client,
        email="missing-history@example.com"
    )

    account_id = uuid4()

    response = client.get(
        f"/accounts/{account_id}/transactions",
        headers=auth_headers(token)
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Account does not exist"
    }


def test_user_cannot_view_another_users_account_transactions(client):
    signup_user(
        client,
        email="history-owner@example.com"
    )

    signup_user(
        client,
        email="history-other@example.com"
    )

    owner_token = login_user(
        client,
        email="history-owner@example.com"
    )

    other_token = login_user(
        client,
        email="history-other@example.com"
    )

    owner_account = create_account(
        client,
        owner_token,
        "Owner Cash",
        "ASSET"
    )

    response = client.get(
        f"/accounts/{owner_account['account_id']}/transactions",
        headers=auth_headers(other_token)
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Not authorized to view account transactions"
    }


def test_account_transaction_history_requires_authentication(client):
    account_id = uuid4()

    response = client.get(
        f"/accounts/{account_id}/transactions"
    )

    assert response.status_code == 401