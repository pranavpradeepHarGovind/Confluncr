from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator, field_serializer


class AccountCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Mandatory account holder name")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Account name cannot be empty or whitespace only")
        return trimmed


class AccountResponse(BaseModel):
    id: UUID
    name: str
    balance: Decimal = Field(..., description="Current account balance in Decimal")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("balance")
    def serialize_balance(self, balance: Decimal, _info) -> str:
        return f"{balance:.2f}"
