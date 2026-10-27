from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.account import Account


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str) -> Account:
        """Create a new account with an initial balance of zero."""
        account = Account(
            name=name,
            balance=Decimal("0.00"),
        )
        self.db.add(account)
        self.db.flush()
        return account

    def get_by_id(self, account_id: UUID) -> Optional[Account]:
        """Retrieve account by ID without row lock."""
        return (
            self.db.query(Account)
            .filter(Account.id == account_id)
            .first()
        )

    def get_by_id_for_update(self, account_id: UUID) -> Optional[Account]:
        """Retrieve account by ID with exclusive row-level lock (FOR UPDATE)."""
        return (
            self.db.query(Account)
            .filter(Account.id == account_id)
            .with_for_update()
            .first()
        )

    def get_multiple_for_update_deterministic(self, account_ids: List[UUID]) -> List[Account]:
        """
        Lock multiple accounts in deterministic ID order to strictly avoid deadlocks.
        """
        sorted_ids = sorted(account_ids, key=lambda x: str(x))
        accounts = []
        for aid in sorted_ids:
            acc = self.get_by_id_for_update(aid)
            if acc:
                accounts.append(acc)
        return accounts

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Account]:
        """List all accounts ordered by created_at descending."""
        return (
            self.db.query(Account)
            .order_by(Account.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_balance(self, account: Account, new_balance: Decimal) -> Account:
        """Update account balance within current transaction."""
        account.balance = new_balance
        self.db.flush()
        return account
