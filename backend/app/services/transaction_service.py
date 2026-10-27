import math
from datetime import datetime, timezone
from decimal import Decimal
from typing import Tuple, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
)
from app.schemas.transfer import TransferCreate, TransferResponse
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.api.exceptions import (
    AccountNotFoundException,
    InsufficientFundsException,
    DuplicateReferenceException,
    InvalidInputException,
)


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.account_repo = AccountRepository(db)
        self.transaction_repo = TransactionRepository(db)

    def process_transaction(
        self,
        account_id: UUID,
        tx_data: TransactionCreate,
    ) -> Transaction:
        """
        Processes a credit or debit transaction atomically.
        Uses PostgreSQL row-level locking (FOR UPDATE) to prevent race conditions.
        Ensures balance changes and transaction records are atomic.
        """
        try:
            # 1. Acquire exclusive lock on the account
            account = self.account_repo.get_by_id_for_update(account_id)
            if not account:
                raise AccountNotFoundException(account_id)

            # 2. Check for duplicate reference ID for this account
            existing_tx = self.transaction_repo.get_by_reference(
                account_id=account_id,
                reference_id=tx_data.reference_id,
            )
            if existing_tx:
                raise DuplicateReferenceException(
                    reference_id=tx_data.reference_id,
                    account_id=account_id,
                )

            # 3. Process according to type
            if tx_data.type == TransactionType.DEBIT:
                if account.balance < tx_data.amount:
                    raise InsufficientFundsException(
                        current_balance=account.balance,
                        required_amount=tx_data.amount,
                    )
                new_balance = account.balance - tx_data.amount
            elif tx_data.type == TransactionType.CREDIT:
                new_balance = account.balance + tx_data.amount
            else:
                raise InvalidInputException(f"Unsupported transaction type '{tx_data.type}'")

            # 4. Update account balance
            self.account_repo.update_balance(account, new_balance)

            # 5. Insert transaction record
            transaction = self.transaction_repo.create(
                account_id=account_id,
                type=tx_data.type,
                amount=tx_data.amount,
                description=tx_data.description,
                reference_id=tx_data.reference_id,
                balance_after=new_balance,
            )

            # 6. Commit transaction atomically
            self.db.commit()
            self.db.refresh(transaction)
            return transaction

        except IntegrityError as e:
            self.db.rollback()
            err_msg = str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
            if "uq_account_reference" in err_msg or "unique" in err_msg:
                raise DuplicateReferenceException(
                    reference_id=tx_data.reference_id,
                    account_id=account_id,
                )
            if "ck_account_balance_non_negative" in err_msg:
                raise InsufficientFundsException(
                    current_balance="0.00",
                    required_amount=tx_data.amount,
                )
            raise
        except Exception:
            self.db.rollback()
            raise

    def get_history(
        self,
        account_id: UUID,
        page: int = 1,
        limit: int = 10,
    ) -> PaginatedResponse[TransactionResponse]:
        """
        Retrieve paginated transaction history sorted latest-first.
        Validates account existence first.
        """
        # Ensure account exists
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise AccountNotFoundException(account_id)

        items, total_records = self.transaction_repo.list_by_account_paginated(
            account_id=account_id,
            page=page,
            limit=limit,
        )

        total_pages = math.ceil(total_records / limit) if total_records > 0 else 0

        pagination_meta = PaginationMeta(
            current_page=page,
            limit=limit,
            total_records=total_records,
            total_pages=total_pages,
        )

        transaction_responses = [
            TransactionResponse.model_validate(tx) for tx in items
        ]

        return PaginatedResponse(
            items=transaction_responses,
            pagination=pagination_meta,
        )

    def process_transfer(
        self,
        transfer_data: TransferCreate,
    ) -> TransferResponse:
        """
        Executes an atomic transfer between two distinct accounts.
        Applies deterministic row locking (ordered by account UUID) to strictly prevent deadlocks.
        """
        if transfer_data.source_account_id == transfer_data.destination_account_id:
            raise InvalidInputException("Source and destination accounts must be distinct.")

        # Determine lock ordering: lowest ID first
        sorted_ids = sorted(
            [transfer_data.source_account_id, transfer_data.destination_account_id],
            key=lambda x: str(x),
        )

        try:
            # Acquire locks in deterministic order
            locked_accounts = {}
            for aid in sorted_ids:
                acc = self.account_repo.get_by_id_for_update(aid)
                if not acc:
                    raise AccountNotFoundException(aid)
                locked_accounts[aid] = acc

            source = locked_accounts[transfer_data.source_account_id]
            dest = locked_accounts[transfer_data.destination_account_id]

            # References for auditability
            src_ref = f"{transfer_data.reference_id}-OUT"
            dest_ref = f"{transfer_data.reference_id}-IN"

            # Check duplicate reference on source or destination
            if self.transaction_repo.get_by_reference(source.id, src_ref):
                raise DuplicateReferenceException(
                    reference_id=transfer_data.reference_id,
                    account_id=source.id,
                )
            if self.transaction_repo.get_by_reference(dest.id, dest_ref):
                raise DuplicateReferenceException(
                    reference_id=transfer_data.reference_id,
                    account_id=dest.id,
                )

            # Check balance
            if source.balance < transfer_data.amount:
                raise InsufficientFundsException(
                    current_balance=source.balance,
                    required_amount=transfer_data.amount,
                )

            # Calculate balances
            new_source_balance = source.balance - transfer_data.amount
            new_dest_balance = dest.balance + transfer_data.amount

            # Update balances
            self.account_repo.update_balance(source, new_source_balance)
            self.account_repo.update_balance(dest, new_dest_balance)

            # Record debit on source
            debit_tx = self.transaction_repo.create(
                account_id=source.id,
                type=TransactionType.DEBIT,
                amount=transfer_data.amount,
                description=f"Transfer to {dest.name}: {transfer_data.description}",
                reference_id=src_ref,
                balance_after=new_source_balance,
            )

            # Record credit on destination
            credit_tx = self.transaction_repo.create(
                account_id=dest.id,
                type=TransactionType.CREDIT,
                amount=transfer_data.amount,
                description=f"Transfer from {source.name}: {transfer_data.description}",
                reference_id=dest_ref,
                balance_after=new_dest_balance,
            )

            # Atomic commit
            self.db.commit()
            self.db.refresh(debit_tx)
            self.db.refresh(credit_tx)

            return TransferResponse(
                transfer_reference=transfer_data.reference_id,
                source_transaction=TransactionResponse.model_validate(debit_tx),
                destination_transaction=TransactionResponse.model_validate(credit_tx),
                amount=transfer_data.amount,
                timestamp=datetime.now(timezone.utc),
            )

        except IntegrityError as e:
            self.db.rollback()
            err_msg = str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
            if "uq_account_reference" in err_msg or "unique" in err_msg:
                raise DuplicateReferenceException(
                    reference_id=transfer_data.reference_id
                )
            if "ck_account_balance_non_negative" in err_msg:
                raise InsufficientFundsException(
                    current_balance="0.00",
                    required_amount=transfer_data.amount,
                )
            raise
        except Exception:
            self.db.rollback()
            raise
