import uuid
from decimal import Decimal
from fastapi.testclient import TestClient


def test_credit_and_debit_balance_flow_example(client: TestClient):
    """
    Explicit test of user requirement:
    Credit 100 + 50, Debit 30 + 20 -> Balance 100
    """
    # 1. Create account
    res = client.post("/api/v1/accounts", json={"name": "Assessment Example Account"})
    assert res.status_code == 201
    account_id = res.json()["id"]

    # 2. Credit 100
    res_c1 = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={
            "type": "credit",
            "amount": "100.00",
            "description": "Initial Deposit",
            "reference_id": "REF-C1",
        },
    )
    assert res_c1.status_code == 201
    assert Decimal(str(res_c1.json()["balance_after"])) == Decimal("100.00")

    # 3. Credit 50
    res_c2 = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={
            "type": "credit",
            "amount": "50.00",
            "description": "Second Deposit",
            "reference_id": "REF-C2",
        },
    )
    assert res_c2.status_code == 201
    assert Decimal(str(res_c2.json()["balance_after"])) == Decimal("150.00")

    # 4. Debit 30
    res_d1 = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={
            "type": "debit",
            "amount": "30.00",
            "description": "Bill Payment 1",
            "reference_id": "REF-D1",
        },
    )
    assert res_d1.status_code == 201
    assert Decimal(str(res_d1.json()["balance_after"])) == Decimal("120.00")

    # 5. Debit 20
    res_d2 = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={
            "type": "debit",
            "amount": "20.00",
            "description": "Bill Payment 2",
            "reference_id": "REF-D2",
        },
    )
    assert res_d2.status_code == 201
    assert Decimal(str(res_d2.json()["balance_after"])) == Decimal("100.00")

    # 6. Verify final account balance is exactly 100.00
    final_res = client.get(f"/api/v1/accounts/{account_id}")
    assert final_res.status_code == 200
    assert Decimal(str(final_res.json()["balance"])) == Decimal("100.00")


def test_insufficient_funds_rejection(client: TestClient):
    # Create account with balance 0.00
    res = client.post("/api/v1/accounts", json={"name": "Low Balance User"})
    account_id = res.json()["id"]

    # Attempt debit of 50.00
    debit_res = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={
            "type": "debit",
            "amount": "50.00",
            "description": "Attempted Overdraft",
            "reference_id": "REF-FAIL-1",
        },
    )
    assert debit_res.status_code == 400
    data = debit_res.json()
    assert data["error"]["code"] == "INSUFFICIENT_FUNDS"

    # Verify balance was NOT modified (atomic failure)
    acc = client.get(f"/api/v1/accounts/{account_id}").json()
    assert Decimal(str(acc["balance"])) == Decimal("0.00")


def test_duplicate_reference_id_rejected(client: TestClient):
    res = client.post("/api/v1/accounts", json={"name": "Idempotency Test User"})
    account_id = res.json()["id"]

    # First transaction
    tx1 = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={
            "type": "credit",
            "amount": "75.00",
            "description": "First Attempt",
            "reference_id": "DUP-REF-100",
        },
    )
    assert tx1.status_code == 201

    # Second transaction with SAME reference_id
    tx2 = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={
            "type": "credit",
            "amount": "75.00",
            "description": "Duplicate Attempt",
            "reference_id": "DUP-REF-100",
        },
    )
    assert tx2.status_code == 409
    data = tx2.json()
    assert data["error"]["code"] == "DUPLICATE_REFERENCE_ID"

    # Verify balance was NOT doubled
    acc = client.get(f"/api/v1/accounts/{account_id}").json()
    assert Decimal(str(acc["balance"])) == Decimal("75.00")


def test_same_reference_id_different_accounts_allowed(client: TestClient):
    # Reference uniqueness is per-account
    u1 = client.post("/api/v1/accounts", json={"name": "User One"}).json()["id"]
    u2 = client.post("/api/v1/accounts", json={"name": "User Two"}).json()["id"]

    res1 = client.post(
        f"/api/v1/accounts/{u1}/transactions",
        json={
            "type": "credit",
            "amount": "50.00",
            "description": "Salary",
            "reference_id": "SALARY-OCT-2026",
        },
    )
    assert res1.status_code == 201

    res2 = client.post(
        f"/api/v1/accounts/{u2}/transactions",
        json={
            "type": "credit",
            "amount": "50.00",
            "description": "Salary",
            "reference_id": "SALARY-OCT-2026",
        },
    )
    assert res2.status_code == 201


def test_invalid_negative_or_zero_amount(client: TestClient):
    res = client.post("/api/v1/accounts", json={"name": "Validation Tester"})
    account_id = res.json()["id"]

    # Zero amount
    r_zero = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={
            "type": "credit",
            "amount": "0.00",
            "description": "Zero deposit",
            "reference_id": "REF-ZERO",
        },
    )
    assert r_zero.status_code == 422

    # Negative amount
    r_neg = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={
            "type": "credit",
            "amount": "-50.00",
            "description": "Negative deposit",
            "reference_id": "REF-NEG",
        },
    )
    assert r_neg.status_code == 422


def test_invalid_more_than_two_decimal_places(client: TestClient):
    res = client.post("/api/v1/accounts", json={"name": "Decimal Tester"})
    account_id = res.json()["id"]

    # 3 decimal places
    r = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={
            "type": "credit",
            "amount": "10.005",
            "description": "Sub-cent deposit",
            "reference_id": "REF-FRACTION",
        },
    )
    assert r.status_code == 422


def test_direct_transactions_endpoint(client: TestClient):
    acc_id = client.post("/api/v1/accounts", json={"name": "Direct Tx User"}).json()["id"]

    r = client.post(
        "/api/v1/transactions",
        json={
            "account_id": acc_id,
            "type": "credit",
            "amount": "200.00",
            "description": "Direct deposit via /transactions",
            "reference_id": "DIRECT-TX-1",
        },
    )
    assert r.status_code == 201
    assert Decimal(str(r.json()["balance_after"])) == Decimal("200.00")
