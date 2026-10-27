from typing import Generic, List, Optional, TypeVar, Any
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class PaginationMeta(BaseModel):
    current_page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Number of records per page")
    total_records: int = Field(..., ge=0, description="Total number of matching records")
    total_pages: int = Field(..., ge=0, description="Total number of pages")

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    pagination: PaginationMeta

    model_config = ConfigDict(from_attributes=True)


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error explanation")
    details: Optional[Any] = Field(None, description="Detailed validation breakdown or context")


class ErrorResponse(BaseModel):
    error: ErrorDetail
