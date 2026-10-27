import concurrent.futures
from decimal import Decimal
from fastapi.testclient import TestClient


def test_concurrent_debits_prevent_overdraft(client: TestClient):
    """
    Spawns 10 concurrent threads each attempting to debit 20.00 from an account
    with an initial balance of 100.00 (Total attempted: 200.00).
    Uses real PostgreSQL row-level locking (FOR UPDATE).
    Exactly 5 must succeed (status 201) and 5 must fail with 400 Insufficient Funds.
    The final balance must be strictly 0.00, never negative.
    """
    # 1. Setup account and fund with 100.00
    acc_res = client.post("/api/v1/accounts", json={"name": "Concurrent Debit Target"})
    assert acc_res.status_code == 201
    account_id = acc_res.json()["id"]

    fund_res = client.post(
        f"/api/v1/accounts/{account_id}/transactions",
        json={
            "type": "credit",
            "amount": "100.00",
            "description": "Initial Funding 100",
            "reference_id": "INIT-FUND-CONC",
        },
    )
    assert fund_res.status_code == 201

    results = []

    def make_debit(thread_idx: int):
        resp = client.post(
            f"/api/v1/accounts/{account_id}/transactions",
            json={
                "type": "debit",
                "amount": "20.00",
                "description": f"Concurrent debit from worker {thread_idx}",
                "reference_id": f"CONC-DEBIT-THREAD-{thread_idx}",
            },
        )
        return resp.status_code, resp.json()

    # 2. Execute 10 requests concurrently across 10 worker threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_debit, i) for i in range(10)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    successes = [r for r in results if r[0] == 201]
    failures = [r for r in results if r[0] == 400]

    assert len(successes) == 5, f"Expected 5 successes, got {len(successes)}"
    assert len(failures) == 5, f"Expected 5 failures, got {len(failures)}"

    for status_code, data in failures:
        assert data["error"]["code"] == "INSUFFICIENT_FUNDS"

    # 3. Verify final balance is strictly 0.00
    final_acc = client.get(f"/api/v1/accounts/{account_id}").json()
    assert Decimal(str(final_acc["balance"])) == Decimal("0.00")


def test_concurrent_transfers_no_deadlock(client: TestClient):
    """
    Tests bidirectional concurrent transfers between Account A and Account B.
    Deterministic row locking prevents deadlocks.
    Total system balance (A + B) must remain perfectly preserved.
    """
    a = client.post("/api/v1/accounts", json={"name": "Concurrent Alice"}).json()["id"]
    b = client.post("/api/v1/accounts", json={"name": "Concurrent Bob"}).json()["id"]

    client.post(
        f"/api/v1/accounts/{a}/transactions",
        json={"type": "credit", "amount": "100.00", "description": "Init A", "reference_id": "A-INIT"},
    )
    client.post(
        f"/api/v1/accounts/{b}/transactions",
        json={"type": "credit", "amount": "100.00", "description": "Init B", "reference_id": "B-INIT"},
    )

    def transfer_worker(src, dst, amount, ref):
        res = client.post(
            "/api/v1/transfers",
            json={
                "source_account_id": src,
                "destination_account_id": dst,
                "amount": amount,
                "description": f"Transfer {ref}",
                "reference_id": ref,
            },
        )
        return res.status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        # Alice -> Bob (4 transfers)
        for i in range(4):
            futures.append(executor.submit(transfer_worker, a, b, "10.00", f"TRF-A-TO-B-{i}"))
        # Bob -> Alice (4 transfers)
        for i in range(4):
            futures.append(executor.submit(transfer_worker, b, a, "10.00", f"TRF-B-TO-A-{i}"))

        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # All transfers should complete successfully without deadlocks
    assert all(code == 201 for code in results)

    # Invariant: Total money in the system must remain exactly 200.00
    acc_a = client.get(f"/api/v1/accounts/{a}").json()
    acc_b = client.get(f"/api/v1/accounts/{b}").json()
    total_balance = Decimal(str(acc_a["balance"])) + Decimal(str(acc_b["balance"]))
    assert total_balance == Decimal("200.00")
