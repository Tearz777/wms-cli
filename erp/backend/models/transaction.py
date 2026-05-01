from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from .customer import Customer


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    trx_id = Column(String, unique=True, index=True, nullable=False)

    # pemasukan / pengeluaran
    type = Column(String, nullable=False)

    # user kasir
    cashier_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # nominal
    total = Column(Integer, nullable=False)
    cash_received = Column(Float, default=0)

    # metode bayar
    payment_method = Column(
        String,
        default="cash"
    )  # cash | qris | hutang

    # customer (untuk hutang / histori)
    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=True
    )

    # catatan
    note = Column(String, nullable=True)

    # sumber waktu
    time_source = Column(
        String,
        default="system"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # relasi
    items = relationship(
        "TransactionItem",
        back_populates="transaction",
        cascade="all, delete-orphan"
    )

    cashier = relationship("User")

    customer = relationship(
        "Customer",
        back_populates="transactions"
    )


class TransactionItem(Base):
    __tablename__ = "transaction_items"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id"),
        nullable=False
    )

    # snapshot data saat transaksi
    product_name = Column(String, nullable=False)
    variant_name = Column(String, nullable=False)

    price = Column(Integer, nullable=False)
    qty = Column(Integer, nullable=False)
    subtotal = Column(Integer, nullable=False)

    transaction = relationship(
        "Transaction",
        back_populates="items"
    )