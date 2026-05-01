from pydantic import BaseModel
from typing import Optional, List

# Schema untuk produk dalam konteks supplier
class SupplierProductItem(BaseModel):
    product_id: int
    price: Optional[int] = None

class SupplierProductOut(BaseModel):
    product_id: int
    name: str
    price: Optional[int] = None

    class Config:
        from_attributes = True

# Create & Update
class SupplierCreate(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    products: Optional[List[SupplierProductItem]] = []

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

# Output
class SupplierOut(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    products: List[SupplierProductOut] = []

    class Config:
        from_attributes = True