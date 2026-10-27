from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_account_service, get_transaction_service
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService
from app.schemas.account import AccountCreate, AccountResponse
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.schemas.common import PaginatedResponse, ErrorResponse

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
    description="Creates a new account with a mandatory name and an initial balance of zero.",
    responses={
        201: {"model": AccountResponse, "description": "Account created successfully"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def create_account(
    account_in: AccountCreate,
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    account = service.create_account(name=account_in.name)
    return AccountResponse.model_validate(account)


@router.get(
    "",
    response_model=List[AccountResponse],
    status_code=status.HTTP_200_OK,
    summary="List all accounts",
    description="Returns a list of all accounts registered in the system.",
)
def list_accounts(
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(100, ge=1, le=500, description="Limit"),
    service: AccountService = Depends(get_account_service),
) -> List[AccountResponse]:
    accounts = service.list_accounts(skip=skip, limit=limit)
    return [AccountResponse.model_validate(acc) for acc in accounts]


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve an account",
    description="Fetches account details and current balance by account ID.",
    responses={
        200: {"model": AccountResponse, "description": "Account details retrieved"},
        404: {"model": ErrorResponse, "description": "Account not found"},
    },
)
def get_account(
    account_id: UUID,
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    account = service.get_account(account_id)
    return AccountResponse.model_validate(account)


@router.post(
    "/{account_id}/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a transaction for an account",
    description=(
        "Executes a credit or debit operation on the specified account atomically with row-level locking. "
        "Enforces positive amounts, sufficient balances for debits, and unique reference IDs."
    ),
    responses={
        201: {"model": TransactionResponse, "description": "Transaction recorded successfully"},
        400: {"model": ErrorResponse, "description": "Insufficient funds or invalid input"},
        404: {"model": ErrorResponse, "description": "Account not found"},
        409: {"model": ErrorResponse, "description": "Duplicate reference ID"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def create_account_transaction(
    account_id: UUID,
    tx_in: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionResponse:
    tx = service.process_transaction(account_id=account_id, tx_data=tx_in)
    return TransactionResponse.model_validate(tx)


@router.get(
    "/{account_id}/transactions",
    response_model=PaginatedResponse[TransactionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get paginated transaction history",
    description=(
        "Retrieves a paginated list of transactions for the specified account, sorted latest-first "
        "by created_at. Returns pagination metadata including total records and total pages."
    ),
    responses={
        200: {"model": PaginatedResponse[TransactionResponse], "description": "Transaction history"},
        404: {"model": ErrorResponse, "description": "Account not found"},
        422: {"model": ErrorResponse, "description": "Invalid pagination parameters"},
    },
)
def get_account_transactions(
    account_id: UUID,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    service: TransactionService = Depends(get_transaction_service),
) -> PaginatedResponse[TransactionResponse]:
    return service.get_history(account_id=account_id, page=page, limit=limit)
