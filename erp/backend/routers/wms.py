from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from database import get_db
from models.product import Product, ProductVariant, StockMovement
from schemas.wms import ProductCreate, ProductUpdate, ProductResponse, StockAdjust
from dependencies import get_current_user, require_role
from models.user import User

router = APIRouter(prefix="/wms", tags=["WMS"])

# ── GET semua produk ──────────────────────────────
@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.variants))
        .where(Product.is_active == True)
    )
    return result.scalars().all()

# ── GET produk by ID ──────────────────────────────
@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.variants))
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    return product

# ── CREATE produk ─────────────────────────────────
@router.post("/products", response_model=ProductResponse)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    product = Product(
        name=data.name,
        category=data.category,
        ownership=data.ownership,
        stock=data.stock,
        location=data.location
    )
    db.add(product)
    await db.flush()

    for v in data.variants:
        variant = ProductVariant(
            product_id=product.id,
            container=v.container,
            price=v.price,
            stock=v.stock
        )
        db.add(variant)

    await db.commit()

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.variants))
        .where(Product.id == product.id)
    )
    return result.scalar_one()

# ── UPDATE produk ─────────────────────────────────
@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.variants))
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(product, field, value)

    await db.commit()

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.variants))
        .where(Product.id == product_id)
    )
    return result.scalar_one()

# ── ADJUST stok ───────────────────────────────────
@router.post("/products/{product_id}/stock", response_model=ProductResponse)
async def adjust_stock(
    product_id: int,
    data: StockAdjust,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin", "owner", "Owner"))
):
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.variants))
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")

    if data.type == "in":
        product.stock += data.qty
    elif data.type == "out":
        if product.stock < data.qty:
            raise HTTPException(status_code=400, detail="Stok tidak cukup")
        product.stock -= data.qty
    elif data.type == "adjustment":
        product.stock = data.qty

    if data.variant_id:
        v_result = await db.execute(
            select(ProductVariant).where(ProductVariant.id == data.variant_id)
        )
        variant = v_result.scalar_one_or_none()
        if variant:
            if data.type == "in":
                variant.stock += data.qty
            elif data.type == "out":
                variant.stock -= data.qty
            elif data.type == "adjustment":
                variant.stock = data.qty

    movement = StockMovement(
        product_id=product_id,
        variant_id=data.variant_id,
        type=data.type,
        qty=data.qty,
        note=data.note,
        created_by=current_user.id
    )
    db.add(movement)
    await db.commit()

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.variants))
        .where(Product.id == product_id)
    )
    return result.scalar_one()

# ── DEACTIVATE produk (admin & owner) ────────────
@router.patch("/products/{product_id}/deactivate", response_model=ProductResponse)
async def deactivate_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin", "owner", "Owner"))
):
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.variants))
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")

    product.is_active = False
    await db.commit()

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.variants))
        .where(Product.id == product_id)
    )
    return result.scalar_one()

# ── DELETE produk (owner only) ────────────────────
@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("owner", "Owner"))
):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")

    await db.delete(product)
    await db.commit()
    return {"message": f"Produk '{product.name}' berhasil dihapus"}
