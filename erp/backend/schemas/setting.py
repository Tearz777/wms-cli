from pydantic import BaseModel
from typing import Optional, List


# ── GENERIC SETTING ───────────────────────────────
class SettingUpdate(BaseModel):
    value: Optional[str] = None


class SettingResponse(BaseModel):
    key: str
    value: Optional[str] = None

    class Config:
        from_attributes = True


# ── BUSINESS PROFILE ──────────────────────────────
class BusinessProfile(BaseModel):
    business_name: str
    business_address: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[str] = None


# ── INVOICE FORMAT ────────────────────────────────
class InvoiceFormat(BaseModel):
    format_pemasukan: str
    format_pengeluaran: str


# ── SHIFT ─────────────────────────────────────────
class ShiftCreate(BaseModel):
    name: str
    start_time: str
    end_time: str


class ShiftResponse(BaseModel):
    id: int
    name: str
    start_time: str
    end_time: str
    is_active: bool

    class Config:
        from_attributes = True


class ShiftItem(BaseModel):
    name: str
    start_time: str
    end_time: str


class ShiftConfig(BaseModel):
    shifts: List[ShiftItem]


class GracePeriod(BaseModel):
    minutes: int = 30


# ── PRINT SETTINGS ────────────────────────────────
class PrintSettings(BaseModel):
    paper_width: int = 58


# ── QRIS SETTINGS ─────────────────────────────────
class QrisSettings(BaseModel):
    qris_image_url: Optional[str] = ""


# ── PAYMENT SETTINGS ──────────────────────────────
class PaymentSettings(BaseModel):
    cash_enabled: bool = True
    qris_enabled: bool = True
    hutang_enabled: bool = True
    default_method: Optional[str] = ""
    require_customer_hutang: bool = True


# ── CUSTOMER ──────────────────────────────────────
class CustomerCreate(BaseModel):
    name: str
    phone: str
    credit_limit: float = 0
    notes: Optional[str] = None

class CustomerResponse(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None
    credit_limit: float = 0
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    credit_limit: Optional[float] = None
    notes: Optional[str] = None
        
# ── SUPPLIER ──────────────────────────────────────
class SupplierCreate(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class SupplierResponse(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
        
