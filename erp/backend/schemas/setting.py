from pydantic import BaseModel
from typing import Optional, List

class SettingUpdate(BaseModel):
    value: Optional[str] = None

class SettingResponse(BaseModel):
    key: str
    value: Optional[str] = None

    class Config:
        from_attributes = True

class BusinessProfile(BaseModel):
    business_name: str
    business_address: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[str] = None

class InvoiceFormat(BaseModel):
    format_pemasukan: str
    format_pengeluaran: str
class ShiftCreate(BaseModel):
    name: str           # Shift Pagi, Shift Siang, dll
    start_time: str     # Format HH:MM
    end_time: str       # Format HH:MM

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
    start_time: str  # HH:MM
    end_time: str    # HH:MM

class ShiftConfig(BaseModel):
    shifts: list[ShiftItem]
    
class GracePeriod(BaseModel):
    minutes: int = 30
