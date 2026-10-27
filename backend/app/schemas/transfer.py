from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, model_validator, field_validator
from app.schemas.transaction import TransactionResponse, validate_positive_two_decimal_amount


class TransferCreate(BaseModel):
    source_account_id: UUID = Field(..., description="ID of source account to debit")
    destination_account_id: UUID = Field(..., description="ID of destination account to credit")
    amount: Decimal = Field(..., description="Transfer amount")
    description: str = Field(..., min_length=1, max_length=500, description="Transfer description")
    reference_id: str = Field(..., min_length=1, max_length=100, description="Unique reference ID for this transfer")

    @field_validator("amount")
    @classmethod
    def check_amount(cls, v: Decimal) -> Decimal:
        return validate_positive_two_decimal_amount(v)

    @field_validator("description", "reference_id")
    @classmethod
    def check_non_empty(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or whitespace only")
        return trimmed

    @model_validator(mode="after")
    def check_different_accounts(self) -> "TransferCreate":
        if self.source_account_id == self.destination_account_id:
            raise ValueError("Source and destination accounts must be different")
        return self


class TransferResponse(BaseModel):
    transfer_reference: str
    source_transaction: TransactionResponse
    destination_transaction: TransactionResponse
    amount: Decimal
    timestamp: datetime
