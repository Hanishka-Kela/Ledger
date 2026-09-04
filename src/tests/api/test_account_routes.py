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

    client.post(
        "/accounts",
        json={
            "name": "Cash",
            "account_type": "ASSET"
        },
        headers=headers
    )

    client.post(
        "/accounts",
        json={
            "name": "Expenses",
            "account_type": "EXPENSE"
        },
        headers=headers
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

    headers1 = auth_headers(token1)
    headers2 = auth_headers(token2)

    client.post(
        "/accounts",
        json={
            "name": "User 1 Cash",
            "account_type": "ASSET"
        },
        headers=headers1
    )

    client.post(
        "/accounts",
        json={
            "name": "User 2 Cash",
            "account_type": "ASSET"
        },
        headers=headers2
    )

    response = client.get(
        "/accounts",
        headers=headers1
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