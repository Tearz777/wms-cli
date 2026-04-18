from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)  # income | expense | asset | equity

    debit_entries = relationship("JournalEntry", foreign_keys="JournalEntry.debit_account_id", back_populates="debit_account")
    credit_entries = relationship("JournalEntry", foreign_keys="JournalEntry.credit_account_id", back_populates="credit_account")

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(String, nullable=False)
    debit_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    credit_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    reference_trx_id = Column(String, nullable=True)  # link ke Transaction.trx_id

    debit_account = relationship("Account", foreign_keys=[debit_account_id], back_populates="debit_entries")
    credit_account = relationship("Account", foreign_keys=[credit_account_id], back_populates="credit_entries")

