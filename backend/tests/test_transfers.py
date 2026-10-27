import uuid
from decimal import Decimal
from fastapi.testclient import TestClient


def test_atomic_transfer_success(client: TestClient):
    # Setup Alice with 200.00 and Bob with 50.00
    a1 = client.post("/api/v1/accounts", json={"name": "Alice"}).json()["id"]
    a2 = client.post("/api/v1/accounts", json={"name": "Bob"}).json()["id"]

    client.post(
        f"/api/v1/accounts/{a1}/transactions",
        json={
            "type": "credit",
            "amount": "200.00",
            "description": "Alice Initial",
            "reference_id": "ALICE-INIT",
        },
    )
    client.post(
        f"/api/v1/accounts/{a2}/transactions",
        json={
            "type": "credit",
            "amount": "50.00",
            "description": "Bob Initial",
            "reference_id": "BOB-INIT",
        },
    )

    # Transfer 75.00 from Alice to Bob
    transfer_res = client.post(
        "/api/v1/transfers",
        json={
            "source_account_id": a1,
            "destination_account_id": a2,
            "amount": "75.00",
            "description": "Rent share",
            "reference_id": "TRF-RENT-001",
        },
    )
    assert transfer_res.status_code == 201
    t_data = transfer_res.json()
    assert t_data["transfer_reference"] == "TRF-RENT-001"
    assert Decimal(str(t_data["source_transaction"]["balance_after"])) == Decimal("125.00")
    assert Decimal(str(t_data["destination_transaction"]["balance_after"])) == Decimal("125.00")

    # Verify Alice's balance
    alice = client.get(f"/api/v1/accounts/{a1}").json()
    assert Decimal(str(alice["balance"])) == Decimal("125.00")

    # Verify Bob's balance
    bob = client.get(f"/api/v1/accounts/{a2}").json()
    assert Decimal(str(bob["balance"])) == Decimal("125.00")


def test_transfer_insufficient_funds_rollback(client: TestClient):
    # Alice has 30.00, Bob has 10.00
    a1 = client.post("/api/v1/accounts", json={"name": "Alice Broke"}).json()["id"]
    a2 = client.post("/api/v1/accounts", json={"name": "Bob Waiting"}).json()["id"]

    client.post(
        f"/api/v1/accounts/{a1}/transactions",
        json={
            "type": "credit",
            "amount": "30.00",
            "description": "Alice Funds",
            "reference_id": "ALICE-30",
        },
    )
    client.post(
        f"/api/v1/accounts/{a2}/transactions",
        json={
            "type": "credit",
            "amount": "10.00",
            "description": "Bob Funds",
            "reference_id": "BOB-10",
        },
    )

    # Try transferring 50.00 (Alice only has 30.00)
    res = client.post(
        "/api/v1/transfers",
        json={
            "source_account_id": a1,
            "destination_account_id": a2,
            "amount": "50.00",
            "description": "Overdraft Transfer",
            "reference_id": "TRF-FAIL-01",
        },
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "INSUFFICIENT_FUNDS"

    # Both balances must be exactly unchanged!
    alice = client.get(f"/api/v1/accounts/{a1}").json()
    bob = client.get(f"/api/v1/accounts/{a2}").json()
    assert Decimal(str(alice["balance"])) == Decimal("30.00")
    assert Decimal(str(bob["balance"])) == Decimal("10.00")


def test_transfer_to_same_account_rejected(client: TestClient):
    a1 = client.post("/api/v1/accounts", json={"name": "Self Transfer User"}).json()["id"]

    res = client.post(
        "/api/v1/transfers",
        json={
            "source_account_id": a1,
            "destination_account_id": a1,
            "amount": "10.00",
            "description": "Self transfer",
            "reference_id": "TRF-SELF",
        },
    )
    assert res.status_code == 422


def test_transfer_to_non_existent_account(client: TestClient):
    a1 = client.post("/api/v1/accounts", json={"name": "Valid Account"}).json()["id"]
    fake_id = str(uuid.uuid4())

    res = client.post(
        "/api/v1/transfers",
        json={
            "source_account_id": a1,
            "destination_account_id": fake_id,
            "amount": "10.00",
            "description": "Transfer to ghost",
            "reference_id": "TRF-GHOST",
        },
    )
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "ACCOUNT_NOT_FOUND"


def test_duplicate_transfer_reference_rejected(client: TestClient):
    a1 = client.post("/api/v1/accounts", json={"name": "Sender"}).json()["id"]
    a2 = client.post("/api/v1/accounts", json={"name": "Receiver"}).json()["id"]

    client.post(
        f"/api/v1/accounts/{a1}/transactions",
        json={
            "type": "credit",
            "amount": "500.00",
            "description": "Initial",
            "reference_id": "INIT-500",
        },
    )

    # First transfer
    r1 = client.post(
        "/api/v1/transfers",
        json={
            "source_account_id": a1,
            "destination_account_id": a2,
            "amount": "50.00",
            "description": "Transfer 1",
            "reference_id": "TRANSFER-DUP-01",
        },
    )
    assert r1.status_code == 201

    # Second transfer with same reference
    r2 = client.post(
        "/api/v1/transfers",
        json={
            "source_account_id": a1,
            "destination_account_id": a2,
            "amount": "50.00",
            "description": "Transfer 2 with same ref",
            "reference_id": "TRANSFER-DUP-01",
        },
    )
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "DUPLICATE_REFERENCE_ID"

    # Sender should have only 1 deduction of 50.00 -> 450.00
    sender = client.get(f"/api/v1/accounts/{a1}").json()
    assert Decimal(str(sender["balance"])) == Decimal("450.00")
