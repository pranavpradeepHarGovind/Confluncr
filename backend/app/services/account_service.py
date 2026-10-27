from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.account_repository import AccountRepository
from app.models.account import Account
from app.api.exceptions import AccountNotFoundException


class AccountService:
    def __init__(self, db: Session):
        self.db = db
        self.account_repo = AccountRepository(db)

    def create_account(self, name: str) -> Account:
        """Create a new account with zero balance within transaction."""
        try:
            account = self.account_repo.create(name=name)
            self.db.commit()
            self.db.refresh(account)
            return account
        except Exception:
            self.db.rollback()
            raise

    def get_account(self, account_id: UUID) -> Account:
        """Retrieve account or raise 404 AccountNotFoundException."""
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise AccountNotFoundException(account_id)
        return account

    def list_accounts(self, skip: int = 0, limit: int = 100) -> List[Account]:
        """List all accounts."""
        return self.account_repo.list_all(skip=skip, limit=limit)
