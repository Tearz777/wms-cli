from pydantic import BaseModel, Field
from typing import Optional, List


# ────────────────────────────────────────────────
# ITEMS
# ────────────────────────────────────────────────
class TransactionItemCreate(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    qty: int


class TransactionItemResponse(BaseModel):
    id: int
    product_name: str
    variant_name: str
    price: int
    qty: int
    subtotal: int

    class Config:
        from_attributes = True


# ────────────────────────────────────────────────
# PEMASUKAN
# ────────────────────────────────────────────────
class PemasukanCreate(BaseModel):
    # daftar item transaksi
    items: List[TransactionItemCreate] = Field(default_factory=list)

    # tambahan biaya / jasa / lain-lain
    extra_amount: int = 0
    extra_note: Optional[str] = None

    # pembayaran
    cash_received: int = 0
    customer_id: Optional[int] = None
    payment_method: str = "cash"   # cash | qris | hutang

    # catatan umum
    note: Optional[str] = None


# ────────────────────────────────────────────────
# PENGELUARAN
# ────────────────────────────────────────────────
class PengeluaranCreate(BaseModel):
    category: str   # konsumsi_karyawan | bayar_konsinyasi | operasional | lain_lain
    amount: int
    note: str


# ────────────────────────────────────────────────
# RESPONSE ITEM
# ────────────────────────────────────────────────
class TransactionResponse(BaseModel):
    id: int
    trx_id: str
    type: str
    total: int

    note: Optional[str] = None
    time_source: str
    created_at: str

    cash_received: int = 0
    payment_method: str = "cash"
    customer_id: Optional[int] = None
    cashier_name: Optional[str] = None

    items: List[TransactionItemResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True