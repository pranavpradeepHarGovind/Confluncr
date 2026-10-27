from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator, field_serializer
from app.models.transaction import TransactionType


def validate_positive_two_decimal_amount(v: Decimal) -> Decimal:
    if v <= Decimal("0"):
        raise ValueError("Amount must be strictly positive")
    
    # Check max 2 decimal places
    exponent = v.as_tuple().exponent
    if isinstance(exponent, int) and exponent < -2:
        raise ValueError("Amount cannot have more than 2 decimal places")
        
    # Quantize to 2 decimal places for consistent storage
    return v.quantize(Decimal("0.01"))


class TransactionCreate(BaseModel):
    type: TransactionType = Field(..., description="Transaction type: credit or debit")
    amount: Decimal = Field(..., description="Positive amount with up to 2 decimal places")
    description: str = Field(..., min_length=1, max_length=500, description="Description of the transaction")
    reference_id: str = Field(..., min_length=1, max_length=100, description="Unique reference ID per account")

    @field_validator("amount")
    @classmethod
    def check_amount(cls, v: Decimal) -> Decimal:
        return validate_positive_two_decimal_amount(v)

    @field_validator("description", "reference_id")
    @classmethod
    def check_non_empty_strings(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or whitespace only")
        return trimmed


class TransactionDirectCreate(TransactionCreate):
    account_id: UUID = Field(..., description="Target account ID")


class TransactionResponse(BaseModel):
    id: UUID
    account_id: UUID
    type: str
    amount: Decimal
    description: str
    reference_id: str
    balance_after: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("amount")
    def serialize_amount(self, amount: Decimal, _info) -> str:
        return f"{amount:.2f}"

    @field_serializer("balance_after")
    def serialize_balance_after(self, balance_after: Decimal, _info) -> str:
        return f"{balance_after:.2f}"
