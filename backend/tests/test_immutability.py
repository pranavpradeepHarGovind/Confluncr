from fastapi.testclient import TestClient


def test_transactions_are_immutable(client: TestClient):
    acc_id = client.post("/api/v1/accounts", json={"name": "Immutable User"}).json()["id"]

    tx_res = client.post(
        f"/api/v1/accounts/{acc_id}/transactions",
        json={
            "type": "credit",
            "amount": "150.00",
            "description": "Original transaction",
            "reference_id": "IMMUTABLE-REF-1",
        },
    )
    assert tx_res.status_code == 201
    tx_id = tx_res.json()["id"]

    # Attempt PUT on transaction -> must be rejected
    put_res = client.put(
        f"/api/v1/accounts/{acc_id}/transactions/{tx_id}",
        json={"amount": "200.00"},
    )
    assert put_res.status_code in [404, 405]

    # Attempt PATCH on transaction -> must be rejected
    patch_res = client.patch(
        f"/api/v1/accounts/{acc_id}/transactions/{tx_id}",
        json={"amount": "200.00"},
    )
    assert patch_res.status_code in [404, 405]

    # Attempt DELETE on transaction -> must be rejected
    del_res = client.delete(f"/api/v1/accounts/{acc_id}/transactions/{tx_id}")
    assert del_res.status_code in [404, 405]

    # Verify transaction remains untouched in history
    history = client.get(f"/api/v1/accounts/{acc_id}/transactions").json()
    assert len(history["items"]) == 1
    assert history["items"][0]["id"] == tx_id
    assert history["items"][0]["description"] == "Original transaction"
