def signup_user(client, email: str, password: str = "Password123!"):
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


def login_user(client, email: str, password: str = "Password123!"):
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

    assert response.status_code == 200

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