from pydantic import BaseModel
from typing import Optional, List

class VariantCreate(BaseModel):
    container: str
    price: int
    stock: int = 0

class VariantResponse(BaseModel):
    id: int
    container: str
    price: int
    stock: int
    is_active: bool

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    category: str           # minuman | makanan
    ownership: str          # own | konsinyasi
    stock: int = 0
    location: str = "Gudang 1"
    variants: List[VariantCreate] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    ownership: Optional[str] = None
    stock: Optional[int] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    ownership: str
    stock: int
    location: str
    is_active: bool
    variants: List[VariantResponse] = []

    class Config:
        from_attributes = True

class StockAdjust(BaseModel):
    qty: int
    type: str               # in | out | adjustment
    variant_id: Optional[int] = None
    note: Optional[str] = None
