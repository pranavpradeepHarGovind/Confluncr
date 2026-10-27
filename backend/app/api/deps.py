from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService


def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    return AccountService(db)


def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(db)
