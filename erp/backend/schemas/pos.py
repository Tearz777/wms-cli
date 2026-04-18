from pydantic import BaseModel
from typing import Optional, List

# ── ITEMS ─────────────────────────────────────────
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

# ── PEMASUKAN ─────────────────────────────────────
class PemasukanCreate(BaseModel):
    items: Optional[List[TransactionItemCreate]] = []
    extra_amount: Optional[int] = 0       # untuk lain-lain
    extra_note: Optional[str] = None      # keterangan lain-lain
    note: Optional[str] = None

# ── PENGELUARAN ───────────────────────────────────
class PengeluaranCreate(BaseModel):
    category: str   # konsumsi_karyawan | bayar_konsinyasi | operasional | lain_lain
    amount: int
    note: str       # wajib ada keterangan

# ── RESPONSE ──────────────────────────────────────
class TransactionResponse(BaseModel):
    id: int
    trx_id: str
    type: str
    total: int
    note: Optional[str] = None
    time_source: str
    created_at: str
    items: List[TransactionItemResponse] = []

    class Config:
        from_attributes = True
