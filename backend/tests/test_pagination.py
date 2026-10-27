import time
from decimal import Decimal
from fastapi.testclient import TestClient


def test_paginated_history_and_sorting(client: TestClient):
    # 1. Create account
    acc_id = client.post("/api/v1/accounts", json={"name": "Pagination User"}).json()["id"]

    # 2. Add 7 transactions with distinct references
    for i in range(1, 8):
        res = client.post(
            f"/api/v1/accounts/{acc_id}/transactions",
            json={
                "type": "credit",
                "amount": f"{i * 10}.00",
                "description": f"Deposit #{i}",
                "reference_id": f"PAG-REF-{i}",
            },
        )
        assert res.status_code == 201

    # 3. Query page 1 with limit 3
    p1 = client.get(f"/api/v1/accounts/{acc_id}/transactions?page=1&limit=3")
    assert p1.status_code == 200
    d1 = p1.json()
    assert d1["pagination"]["current_page"] == 1
    assert d1["pagination"]["limit"] == 3
    assert d1["pagination"]["total_records"] == 7
    assert d1["pagination"]["total_pages"] == 3
    assert len(d1["items"]) == 3
    # Check latest-first: items[0] should be deposit #7
    assert d1["items"][0]["reference_id"] == "PAG-REF-7"
    assert d1["items"][1]["reference_id"] == "PAG-REF-6"
    assert d1["items"][2]["reference_id"] == "PAG-REF-5"

    # 4. Query page 2 with limit 3
    p2 = client.get(f"/api/v1/accounts/{acc_id}/transactions?page=2&limit=3")
    assert p2.status_code == 200
    d2 = p2.json()
    assert d2["pagination"]["current_page"] == 2
    assert len(d2["items"]) == 3
    assert d2["items"][0]["reference_id"] == "PAG-REF-4"
    assert d2["items"][1]["reference_id"] == "PAG-REF-3"
    assert d2["items"][2]["reference_id"] == "PAG-REF-2"

    # 5. Query page 3 with limit 3
    p3 = client.get(f"/api/v1/accounts/{acc_id}/transactions?page=3&limit=3")
    assert p3.status_code == 200
    d3 = p3.json()
    assert d3["pagination"]["current_page"] == 3
    assert len(d3["items"]) == 1
    assert d3["items"][0]["reference_id"] == "PAG-REF-1"


def test_pagination_invalid_parameters(client: TestClient):
    acc_id = client.post("/api/v1/accounts", json={"name": "Bad Pagination User"}).json()["id"]

    # page < 1
    r_bad_page = client.get(f"/api/v1/accounts/{acc_id}/transactions?page=0&limit=10")
    assert r_bad_page.status_code == 422

    # limit < 1
    r_bad_limit = client.get(f"/api/v1/accounts/{acc_id}/transactions?page=1&limit=0")
    assert r_bad_limit.status_code == 422

    # limit > 100
    r_limit_too_high = client.get(f"/api/v1/accounts/{acc_id}/transactions?page=1&limit=101")
    assert r_limit_too_high.status_code == 422
