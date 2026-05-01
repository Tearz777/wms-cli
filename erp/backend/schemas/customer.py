from pydantic import BaseModel
from typing import Optional

class CustomerBase(BaseModel):
    name: str
    phone: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    phone: Optional[str] = None
    credit_limit: float
    created_at: str = ""

    class Config:
        from_attributes = True