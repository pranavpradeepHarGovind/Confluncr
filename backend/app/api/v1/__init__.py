from fastapi import APIRouter
from app.api.v1.accounts import router as accounts_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.transfers import router as transfers_router

api_v1_router = APIRouter()
api_v1_router.include_router(accounts_router)
api_v1_router.include_router(transactions_router)
api_v1_router.include_router(transfers_router)

__all__ = ["api_v1_router"]
