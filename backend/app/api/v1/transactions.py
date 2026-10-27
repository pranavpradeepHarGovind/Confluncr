from fastapi import APIRouter, Depends, status
from app.api.deps import get_transaction_service
from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionDirectCreate, TransactionResponse, TransactionCreate
from app.schemas.common import ErrorResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a transaction",
    description="Processes a credit or debit operation on an account with row-level locking.",
    responses={
        201: {"model": TransactionResponse, "description": "Transaction recorded successfully"},
        400: {"model": ErrorResponse, "description": "Insufficient funds or invalid input"},
        404: {"model": ErrorResponse, "description": "Account not found"},
        409: {"model": ErrorResponse, "description": "Duplicate reference ID"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def create_transaction(
    tx_in: TransactionDirectCreate,
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionResponse:
    tx_create = TransactionCreate(
        type=tx_in.type,
        amount=tx_in.amount,
        description=tx_in.description,
        reference_id=tx_in.reference_id,
    )
    tx = service.process_transaction(account_id=tx_in.account_id, tx_data=tx_create)
    return TransactionResponse.model_validate(tx)
