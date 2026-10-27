import uuid
from decimal import Decimal
from fastapi.testclient import TestClient


def test_create_account_success(client: TestClient):
    response = client.post("/api/v1/accounts", json={"name": "Alice Cooper"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Alice Cooper"
    assert Decimal(str(data["balance"])) == Decimal("0.00")
    assert "created_at" in data
    assert "updated_at" in data


def test_create_account_empty_name(client: TestClient):
    response = client.post("/api/v1/accounts", json={"name": ""})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_create_account_whitespace_only(client: TestClient):
    response = client.post("/api/v1/accounts", json={"name": "   "})
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_get_account_by_id(client: TestClient):
    # 1. Create account
    create_res = client.post("/api/v1/accounts", json={"name": "Bob Dylan"})
    assert create_res.status_code == 201
    account_id = create_res.json()["id"]

    # 2. Retrieve account
    get_res = client.get(f"/api/v1/accounts/{account_id}")
    assert get_res.status_code == 200
    acc_data = get_res.json()
    assert acc_data["id"] == account_id
    assert acc_data["name"] == "Bob Dylan"
    assert Decimal(str(acc_data["balance"])) == Decimal("0.00")


def test_get_non_existent_account(client: TestClient):
    random_id = str(uuid.uuid4())
    res = client.get(f"/api/v1/accounts/{random_id}")
    assert res.status_code == 404
    data = res.json()
    assert data["error"]["code"] == "ACCOUNT_NOT_FOUND"


def test_list_accounts(client: TestClient):
    client.post("/api/v1/accounts", json={"name": "User 1"})
    client.post("/api/v1/accounts", json={"name": "User 2"})

    res = client.get("/api/v1/accounts")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 2
