from typing import Any, Optional
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


class AccountNotFoundException(AppException):
    def __init__(self, account_id: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="ACCOUNT_NOT_FOUND",
            message=f"Account with ID '{account_id}' was not found.",
            details={"account_id": str(account_id)},
        )


class InsufficientFundsException(AppException):
    def __init__(self, current_balance: Any, required_amount: Any):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INSUFFICIENT_FUNDS",
            message=f"Insufficient balance. Current balance is {current_balance}, but {required_amount} is required.",
            details={
                "current_balance": str(current_balance),
                "required_amount": str(required_amount),
            },
        )


class DuplicateReferenceException(AppException):
    def __init__(self, reference_id: str, account_id: Any = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="DUPLICATE_REFERENCE_ID",
            message=f"A transaction with reference_id '{reference_id}' already exists for this account.",
            details={"reference_id": reference_id, "account_id": str(account_id) if account_id else None},
        )


class InvalidInputException(AppException):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_INPUT",
            message=message,
            details=details,
        )


def register_exception_handlers(app):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Format Pydantic errors into readable structure
        details = []
        for error in exc.errors():
            loc = " -> ".join(str(l) for l in error.get("loc", []))
            details.append({
                "field": loc,
                "message": error.get("msg"),
                "type": error.get("type"),
            })
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Input validation failed. Please check the submitted fields.",
                    "details": details,
                }
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        # Database constraint violation catch-all
        err_str = str(exc.orig).lower() if hasattr(exc, "orig") else str(exc).lower()
        if "uq_account_reference" in err_str or "unique constraint" in err_str:
            code = "DUPLICATE_REFERENCE_ID"
            msg = "Duplicate reference ID detected for account."
            status_code = status.HTTP_409_CONFLICT
        elif "ck_account_balance_non_negative" in err_str:
            code = "INSUFFICIENT_FUNDS"
            msg = "Operation rejected: Account balance cannot become negative."
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            code = "DATABASE_INTEGRITY_ERROR"
            msg = "Database integrity constraint violated."
            status_code = status.HTTP_409_CONFLICT

        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": code,
                    "message": msg,
                    "details": None,
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        code_map = {
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
        }
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": code_map.get(exc.status_code, "HTTP_ERROR"),
                    "message": str(exc.detail),
                    "details": None,
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected server error occurred.",
                    "details": None,
                }
            },
        )
