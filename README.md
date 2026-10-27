# VaultFlow — Account & Transaction Management System

A production-quality, high-concurrency **Account & Transaction Management System** built with **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL**, **Alembic**, **Pydantic V2**, and a modern **React 18 + TypeScript + Tailwind CSS** frontend.

---

## 1. System Architecture

The codebase follows strict clean architecture and separation of concerns:

```
Routes (API Layer)
       │
       ▼
Services (Business Logic & Transactions)
       │
       ▼
Repositories (Row-level Locking & Queries)
       │
       ▼
Database Engine (PostgreSQL / Constraints)
```

- **Routes (`backend/app/api/v1/`)**: Fast, typed route controllers defining HTTP request/response models, status codes (201, 400, 404, 409, 422), and OpenAPI documentation.
- **Services (`backend/app/services/`)**: Enforces financial business logic, atomic transaction coordination, and deadlock-free locking sequences.
- **Repositories (`backend/app/repositories/`)**: Encapsulates database queries, row locking (`with_for_update()`), pagination, and immutable record insertion.
- **Models & Schemas (`backend/app/models/`, `backend/app/schemas/`)**: SQLAlchemy declarative models with PostgreSQL constraints and Pydantic V2 schemas with Decimal validation.

---

## 2. Core Data Integrity Guarantees

Financial data integrity is the highest priority:

1. **Exact Decimal Arithmetic (Never Floats)**:
   - Money is persisted as `NUMERIC(18, 2)` in PostgreSQL and manipulated strictly as Python `decimal.Decimal`.
   - Quantized to 2 decimal places to prevent floating-point rounding errors.
2. **Concurrency & Race Condition Prevention**:
   - Every balance modification executes inside a PostgreSQL database transaction with **row-level locking** (`SELECT ... FOR UPDATE`).
   - Dual-layer protection: In addition to service-level checks, a PostgreSQL table constraint `CHECK (balance >= 0)` guarantees at the database engine level that no race condition or bug can ever drive a balance negative.
3. **Atomic Operations & Rollback**:
   - Transaction insertion and balance updates occur within the same atomic transaction.
   - Any failure (insufficient funds, duplicate reference, network drop) causes a complete rollback leaving account balances 100% unchanged.
4. **Idempotency & Duplicate Reference Rejection**:
   - Database-level unique constraint `UNIQUE (account_id, reference_id)` prevents double-charging or duplicate submissions.
   - Duplicate attempts fail with `409 Conflict` and return a standardized error response.
5. **Deadlock-Free Cross-Account Transfers**:
   - Transfers lock both participating accounts in deterministic lexicographical order (`sorted([source_id, dest_id])`).
   - Bidirectional concurrent transfers (e.g. A → B and B → A simultaneously) acquire locks in the exact same order, completely eliminating database deadlocks.
6. **Immutable Ledger Entries**:
   - The transaction log is append-only. No `PUT`, `PATCH`, or `DELETE` endpoints exist.

---

## 3. Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic V2, Alembic |
| **Database** | PostgreSQL 16 (with Row-Level Locks & Check Constraints) |
| **Frontend** | React 18, TypeScript, Tailwind CSS, Lucide Icons, Vite |
| **Testing** | Pytest, Pytest-Cov, HTTPX, Concurrent ThreadPool |
| **DevOps** | Docker Compose, Multi-stage Docker builds, Nginx |

---

## 4. Quickstart Guide

### Option A: Run with Docker Compose (Recommended)

Make sure Docker Desktop is running, then run:

```bash
docker compose up --build
```

- **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Option B: Run Locally (Development)

#### 1. Start PostgreSQL
```bash
docker run -d --name confluncr-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=confluncr -p 5432:5432 postgres:16-alpine
```

#### 2. Start Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

#### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173).

---

## 5. Verification of the Assessment Example

**Requirement**: Credit 100 + 50, Debit 30 + 20 → Balance 100.

This requirement is verified in `backend/tests/test_transactions.py::test_credit_and_debit_balance_flow_example`:

1. Account initialized: `$0.00`
2. Credit `100.00` (Ref: `REF-C1`) → Balance: `$100.00`
3. Credit `50.00` (Ref: `REF-C2`) → Balance: `$150.00`
4. Debit `30.00` (Ref: `REF-D1`) → Balance: `$120.00`
5. Debit `20.00` (Ref: `REF-D2`) → Balance: `$100.00`
6. Final verified balance: **`$100.00`** (Status: **PASSED**)

---

## 6. Test Suite & Coverage

The test suite covers unit logic, integration endpoints, row locking, and high concurrency on PostgreSQL:

```bash
cd backend
.venv\Scripts\pytest --cov=app -v tests
```

### Actual Test Results (23 Passed, 0 Failed, 90% Code Coverage):

```
tests/test_accounts.py::test_create_account_success PASSED
tests/test_accounts.py::test_create_account_empty_name PASSED
tests/test_accounts.py::test_create_account_whitespace_only PASSED
tests/test_accounts.py::test_get_account_by_id PASSED
tests/test_accounts.py::test_get_non_existent_account PASSED
tests/test_accounts.py::test_list_accounts PASSED
tests/test_concurrency.py::test_concurrent_debits_prevent_overdraft PASSED
tests/test_concurrency.py::test_concurrent_transfers_no_deadlock PASSED
tests/test_immutability.py::test_transactions_are_immutable PASSED
tests/test_pagination.py::test_paginated_history_and_sorting PASSED
tests/test_pagination.py::test_pagination_invalid_parameters PASSED
tests/test_transactions.py::test_credit_and_debit_balance_flow_example PASSED
tests/test_transactions.py::test_insufficient_funds_rejection PASSED
tests/test_transactions.py::test_duplicate_reference_id_rejected PASSED
tests/test_transactions.py::test_same_reference_id_different_accounts_allowed PASSED
tests/test_transactions.py::test_invalid_negative_or_zero_amount PASSED
tests/test_transactions.py::test_invalid_more_than_two_decimal_places PASSED
tests/test_transactions.py::test_direct_transactions_endpoint PASSED
tests/test_transfers.py::test_atomic_transfer_success PASSED
tests/test_transfers.py::test_transfer_insufficient_funds_rollback PASSED
tests/test_transfers.py::test_transfer_to_same_account_rejected PASSED
tests/test_transfers.py::test_transfer_to_non_existent_account PASSED
tests/test_transfers.py::test_duplicate_transfer_reference_rejected PASSED

Coverage Total: 90%
```

---

## 7. API Specification & Sample Requests

### 1. Create Account
- **Endpoint**: `POST /api/v1/accounts`
- **Status Code**: `201 Created`
- **Payload**:
```json
{
  "name": "Acme Treasury"
}
```
- **Response**:
```json
{
  "id": "b9688432-841f-4b08-8e6f-fb9f82d4eb72",
  "name": "Acme Treasury",
  "balance": "0.00",
  "created_at": "2026-10-27T19:50:00Z",
  "updated_at": "2026-10-27T19:50:00Z"
}
```

### 2. Retrieve Account
- **Endpoint**: `GET /api/v1/accounts/{account_id}`
- **Status Code**: `200 OK` (or `404 Not Found`)

### 3. Credit / Debit Transaction
- **Endpoint**: `POST /api/v1/accounts/{account_id}/transactions`
- **Status Code**: `201 Created`
- **Payload**:
```json
{
  "type": "credit",
  "amount": "100.00",
  "description": "Initial funding",
  "reference_id": "REF-INIT-001"
}
```
- **Response**:
```json
{
  "id": "97d3967a-115f-4bf1-bf63-82502753a3eb",
  "account_id": "b9688432-841f-4b08-8e6f-fb9f82d4eb72",
  "type": "credit",
  "amount": "100.00",
  "description": "Initial funding",
  "reference_id": "REF-INIT-001",
  "balance_after": "100.00",
  "created_at": "2026-10-27T19:50:05Z"
}
```

### 4. Paginated Transaction History
- **Endpoint**: `GET /api/v1/accounts/{account_id}/transactions?page=1&limit=10`
- **Status Code**: `200 OK`
- **Response**:
```json
{
  "items": [
    {
      "id": "97d3967a-115f-4bf1-bf63-82502753a3eb",
      "account_id": "b9688432-841f-4b08-8e6f-fb9f82d4eb72",
      "type": "credit",
      "amount": "100.00",
      "description": "Initial funding",
      "reference_id": "REF-INIT-001",
      "balance_after": "100.00",
      "created_at": "2026-10-27T19:50:05Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "limit": 10,
    "total_records": 1,
    "total_pages": 1
  }
}
```

### 5. Atomic Transfer Between Accounts (Bonus)
- **Endpoint**: `POST /api/v1/transfers`
- **Status Code**: `201 Created`
- **Payload**:
```json
{
  "source_account_id": "b9688432-841f-4b08-8e6f-fb9f82d4eb72",
  "destination_account_id": "d13543d4-2821-4f1d-b8d9-3617be88bb82",
  "amount": "40.00",
  "description": "Invoice payment #492",
  "reference_id": "TRF-INV-492"
}
```

### Standardized Error Format
```json
{
  "error": {
    "code": "INSUFFICIENT_FUNDS",
    "message": "Insufficient balance. Current balance is 20.00, but 50.00 is required.",
    "details": {
      "current_balance": "20.00",
      "required_amount": "50.00"
    }
  }
}
```

---

## 8. Assumptions & Design Decisions

1. **UUIDv4 for Primary Keys**:
   - Accounts and Transactions use random UUIDs instead of auto-incrementing integers to prevent enumeration attacks and preserve privacy in multi-tenant environments.
2. **Snapshotting `balance_after`**:
   - Each transaction stores an immutable `balance_after` snapshot. This provides immediate auditability and reconciliation without having to recompute historic event logs.
3. **Deterministic Lock Ordering**:
   - Transfers lock `min(source_id, dest_id)` followed by `max(source_id, dest_id)` to mathematically eliminate cyclic lock dependency (deadlocks).
4. **Per-Account Reference Scoping**:
   - `reference_id` uniqueness is scoped per account (`UNIQUE(account_id, reference_id)`). This accommodates real-world bank feeds where different clients might use identical reference numbering schemas (e.g. `INV-001`).

---

## 9. Remaining Limitations & Future Hardening

1. **Distributed Event Streaming**:
   - In ultra-high-throughput systems, integrating an event log (such as Kafka or Debezium CDC) would enable asynchronous ledger broadcasting to downstream analytics and fraud detection systems.
2. **Multi-Currency Support**:
   - The current schema assumes a single base currency (USD). A multi-currency extension would add an ISO 4217 currency column (`USD`, `EUR`, `GBP`) and enforce single-currency account isolation or foreign exchange conversion services.
3. **Distributed Rate Limiting**:
   - Redis-based token bucket rate limiting could be introduced at the API gateway layer to prevent denial-of-service attempts.
