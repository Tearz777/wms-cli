from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerResponse

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=CustomerResponse)
async def create_customer(obj: CustomerCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Customer).where(Customer.name.ilike(obj.name)))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Nama pelanggan sudah ada")
    new_cust = Customer(name=obj.name)
    db.add(new_cust)
    await db.commit()
    await db.refresh(new_cust)
    return new_cust

@router.get("/", response_model=list[CustomerResponse])
async def list_customers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.is_active == True))
    return result.scalars().all()
