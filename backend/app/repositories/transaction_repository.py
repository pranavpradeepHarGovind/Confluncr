from typing import Optional, List, Tuple
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.transaction import Transaction, TransactionType


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        account_id: UUID,
        type: TransactionType | str,
        amount: Decimal,
        description: str,
        reference_id: str,
        balance_after: Decimal,
    ) -> Transaction:
        """Create an immutable transaction record."""
        type_str = type.value if isinstance(type, TransactionType) else str(type)
        transaction = Transaction(
            account_id=account_id,
            type=type_str,
            amount=amount,
            description=description,
            reference_id=reference_id,
            balance_after=balance_after,
        )
        self.db.add(transaction)
        self.db.flush()
        return transaction

    def get_by_reference(self, account_id: UUID, reference_id: str) -> Optional[Transaction]:
        """Check for existing transaction reference for the specified account."""
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.account_id == account_id,
                Transaction.reference_id == reference_id,
            )
            .first()
        )

    def list_by_account_paginated(
        self,
        account_id: UUID,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[Transaction], int]:
        """
        List transactions for account ordered latest-first by created_at DESC.
        Returns (items, total_count).
        """
        query = self.db.query(Transaction).filter(Transaction.account_id == account_id)
        
        total_records = query.with_entities(func.count(Transaction.id)).scalar() or 0
        
        offset = (page - 1) * limit
        items = (
            query.order_by(Transaction.created_at.desc(), Transaction.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total_records
