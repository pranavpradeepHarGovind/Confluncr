from fastapi import APIRouter, Depends, status
from app.api.deps import get_transaction_service
from app.services.transaction_service import TransactionService
from app.schemas.transfer import TransferCreate, TransferResponse
from app.schemas.common import ErrorResponse

router = APIRouter(prefix="/transfers", tags=["Transfers"])


@router.post(
    "",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Transfer funds between two accounts",
    description=(
        "Executes an atomic transfer between two distinct accounts. Acquires exclusive row locks "
        "in deterministic order to prevent deadlocks under concurrency. Checks balance and rolls "
        "back completely if any error occurs."
    ),
    responses={
        201: {"model": TransferResponse, "description": "Transfer executed successfully"},
        400: {"model": ErrorResponse, "description": "Insufficient funds or invalid input"},
        404: {"model": ErrorResponse, "description": "Source or destination account not found"},
        409: {"model": ErrorResponse, "description": "Duplicate reference ID"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def create_transfer(
    transfer_in: TransferCreate,
    service: TransactionService = Depends(get_transaction_service),
) -> TransferResponse:
    return service.process_transfer(transfer_in)
