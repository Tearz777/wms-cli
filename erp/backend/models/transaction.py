from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    trx_id = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)           # pemasukan | pengeluaran
    cashier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    total = Column(Integer, nullable=False)
    note = Column(String, nullable=True)
    time_source = Column(String, default="system")  # NTP | system
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship("TransactionItem", back_populates="transaction")
    cashier = relationship("User")

class TransactionItem(Base):
    __tablename__ = "transaction_items"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    product_name = Column(String, nullable=False)   # snapshot nama
    variant_name = Column(String, nullable=False)   # snapshot varian
    price = Column(Integer, nullable=False)         # snapshot harga
    qty = Column(Integer, nullable=False)
    subtotal = Column(Integer, nullable=False)

    transaction = relationship("Transaction", back_populates="items")
