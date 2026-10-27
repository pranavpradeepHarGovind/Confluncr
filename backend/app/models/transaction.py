import uuid
from decimal import Decimal
from enum import Enum
from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
    func,
    Uuid,
)
from sqlalchemy.orm import relationship
from app.database import Base


class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    account_id = Column(
        Uuid,
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    type = Column(String(10), nullable=False)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    description = Column(String(500), nullable=False)
    reference_id = Column(String(100), nullable=False)
    balance_after = Column(Numeric(precision=18, scale=2), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    account = relationship("Account", back_populates="transactions")

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transaction_positive_amount"),
        CheckConstraint("type IN ('credit', 'debit')", name="ck_transaction_type"),
        UniqueConstraint("account_id", "reference_id", name="uq_account_reference"),
        Index("ix_transactions_account_created", "account_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id}, account_id={self.account_id}, "
            f"type='{self.type}', amount={self.amount}, ref='{self.reference_id}')>"
        )
