from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ── CHART OF ACCOUNTS ─────────────────────────────
class AccountCreate(BaseModel):
    name: str
    type: str  # asset | liability | equity | income | expense

class AccountResponse(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        from_attributes = True

# ── JOURNAL ENTRY ─────────────────────────────────
class JournalEntryCreate(BaseModel):
    date: Optional[str] = None
    description: str
    debit_account_id: int
    credit_account_id: int
    amount: int
    reference_trx_id: Optional[str] = None

class JournalEntryResponse(BaseModel):
    id: int
    date: str
    description: str
    debit_account_id: int
    credit_account_id: int
    amount: int
    reference_trx_id: Optional[str] = None

    class Config:
        from_attributes = True

# ── LAPORAN ───────────────────────────────────────
class PeriodRequest(BaseModel):
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
