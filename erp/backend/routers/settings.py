import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from database import get_db
from models.setting import Setting
from models.user import User
from models.customer import Customer
from dependencies import get_current_user, require_role
from services.invoice_generator import get_setting, set_setting
from models.suppliers import Supplier
from schemas.setting import (
    SettingResponse,
    BusinessProfile,
    InvoiceFormat,
    ShiftConfig,
    GracePeriod,
    PrintSettings,
    QrisSettings,
    PaymentSettings,
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
)

router = APIRouter(prefix="/settings", tags=["Settings"])


# ── GET ALL SETTINGS ──────────────────────────────
@router.get("/", response_model=List[SettingResponse])
async def get_all_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Setting))
    return result.scalars().all()


# ── BUSINESS PROFILE ──────────────────────────────
@router.get("/business")
async def get_business_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "business_name":
            await get_setting(db, "business_name") or "",

        "business_address":
            await get_setting(db, "business_address") or "",

        "business_phone":
            await get_setting(db, "business_phone") or "",

        "business_email":
            await get_setting(db, "business_email") or ""
    }


@router.post("/business")
async def save_business_profile(
    data: BusinessProfile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "Admin", "owner", "Owner")
    )
):
    await set_setting(db, "business_name", data.business_name)
    await set_setting(db, "business_address", data.business_address or "")
    await set_setting(db, "business_phone", data.business_phone or "")
    await set_setting(db, "business_email", data.business_email or "")
    await db.commit()

    return {"message": "Business profile disimpan"}


# ── INVOICE FORMAT ────────────────────────────────
@router.get("/invoice-format")
async def get_invoice_format(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "format_pemasukan":
            await get_setting(db, "invoice_format_pemasukan") or "",

        "format_pengeluaran":
            await get_setting(db, "invoice_format_pengeluaran") or ""
    }


@router.post("/invoice-format")
async def save_invoice_format(
    data: InvoiceFormat,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "Admin", "owner", "Owner")
    )
):
    await set_setting(
        db,
        "invoice_format_pemasukan",
        data.format_pemasukan
    )

    await set_setting(
        db,
        "invoice_format_pengeluaran",
        data.format_pengeluaran
    )

    await db.commit()

    return {"message": "Format invoice disimpan"}


# ── SHIFT SETTINGS ────────────────────────────────
@router.get("/shifts")
async def get_shifts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw = await get_setting(db, "shifts")
    return {"shifts": json.loads(raw)} if raw else {"shifts": []}
    
# ── CURRENT SHIFT ────────────────────────────────
@router.get("/current-shift")
async def get_current_shift(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw = await get_setting(db, "shifts")
    grace_raw = await get_setting(db, "shift_grace_period") or "30"

    shifts = json.loads(raw) if raw else []
    grace = int(grace_raw)

    now = datetime.now()
    now_time = now.strftime("%H:%M")

    for shift in shifts:
        start = shift["start_time"]
        end = shift["end_time"]

        if start <= now_time <= end:
            return {
                "active": True,
                "name": shift["name"],
                "start_time": start,
                "end_time": end,
                "grace_period": grace
            }

    return {
        "active": False,
        "name": None,
        "start_time": None,
        "end_time": None,
        "grace_period": grace
    }


@router.post("/shifts")
async def save_shifts(
    data: ShiftConfig,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "Admin", "owner", "Owner")
    )
):
    await set_setting(
        db,
        "shifts",
        json.dumps([x.model_dump() for x in data.shifts])
    )

    await db.commit()

    return {"message": "Shift disimpan"}


@router.get("/grace-period")
async def get_grace_period(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    val = await get_setting(db, "shift_grace_period") or "30"
    return {"minutes": int(val)}


@router.post("/grace-period")
async def save_grace_period(
    data: GracePeriod,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "Admin", "owner", "Owner")
    )
):
    await set_setting(
        db,
        "shift_grace_period",
        str(data.minutes)
    )

    await db.commit()

    return {"message": "Grace period disimpan"}


# ── PRINT SETTINGS ────────────────────────────────
@router.get("/print", response_model=PrintSettings)
async def get_print_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    width = await get_setting(db, "paper_width") or "58"
    return {"paper_width": int(width)}


@router.post("/print")
async def save_print_settings(
    data: PrintSettings,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "Admin", "owner", "Owner")
    )
):
    await set_setting(
        db,
        "paper_width",
        str(data.paper_width)
    )

    await db.commit()

    return {"message": "Print settings disimpan"}


# ── QRIS SETTINGS ─────────────────────────────────
@router.get("/qris", response_model=QrisSettings)
async def get_qris_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "qris_image_url":
            await get_setting(db, "qris_image_url") or ""
    }


@router.post("/qris")
async def save_qris_settings(
    data: QrisSettings,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "Admin", "owner", "Owner")
    )
):
    await set_setting(
        db,
        "qris_image_url",
        data.qris_image_url or ""
    )

    await db.commit()

    return {"message": "QRIS disimpan"}


# ── PAYMENT SETTINGS ──────────────────────────────
@router.get("/payment", response_model=PaymentSettings)
async def get_payment_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "cash_enabled":
            (await get_setting(db, "cash_enabled") or "1") == "1",

        "qris_enabled":
            (await get_setting(db, "qris_enabled") or "1") == "1",

        "hutang_enabled":
            (await get_setting(db, "hutang_enabled") or "1") == "1",

        "default_method":
            await get_setting(db, "default_method") or "",

        "require_customer_hutang":
            (await get_setting(
                db,
                "require_customer_hutang"
            ) or "1") == "1"
    }


@router.post("/payment")
async def save_payment_settings(
    data: PaymentSettings,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "Admin", "owner", "Owner")
    )
):
    await set_setting(
        db,
        "cash_enabled",
        "1" if data.cash_enabled else "0"
    )

    await set_setting(
        db,
        "qris_enabled",
        "1" if data.qris_enabled else "0"
    )

    await set_setting(
        db,
        "hutang_enabled",
        "1" if data.hutang_enabled else "0"
    )

    await set_setting(
        db,
        "default_method",
        data.default_method or ""
    )

    await set_setting(
        db,
        "require_customer_hutang",
        "1" if data.require_customer_hutang else "0"
    )

    await db.commit()

    return {"message": "Payment settings disimpan"}


# ── CUSTOMERS ─────────────────────────────────────
@router.get("/customers", response_model=List[CustomerResponse])
async def get_customers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Customer).order_by(Customer.name)
    )
    return result.scalars().all()


@router.post("/customers", response_model=CustomerResponse)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = Customer(
        name=data.name,
        phone=data.phone
    )

    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    return customer

@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")

    if data.name is not None:
        customer.name = data.name
    if data.phone is not None:
        customer.phone = data.phone
    if data.credit_limit is not None:
      customer.credit_limit = data.credit_limit
    if data.notes is not None:
        customer.notes = data.notes

    await db.commit()
    await db.refresh(customer)
    return customer

# ── SUPPLIERS ─────────────────────────────────────
@router.get("/suppliers", response_model=List[SupplierResponse])
async def get_suppliers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Supplier).order_by(Supplier.name)
    )
    return result.scalars().all()


@router.post("/suppliers", response_model=SupplierResponse)
async def create_supplier(
    data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "Admin", "owner", "Owner")
    )
):
    supplier = Supplier(
        name=data.name,
        address=data.address,
        phone=data.phone
    )
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return supplier


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "Admin", "owner", "Owner")
    )
):
    result = await db.execute(
        select(Supplier).where(Supplier.id == supplier_id)
    )
    supplier = result.scalar_one_or_none()

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier tidak ditemukan")

    if data.name is not None:
        supplier.name = data.name
    if data.address is not None:
        supplier.address = data.address
    if data.phone is not None:
        supplier.phone = data.phone
    if data.is_active is not None:
        supplier.is_active = data.is_active

    await db.commit()
    await db.refresh(supplier)
    return supplier


@router.delete("/suppliers/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "Admin", "owner", "Owner")
    )
):
    result = await db.execute(
        select(Supplier).where(Supplier.id == supplier_id)
    )
    supplier = result.scalar_one_or_none()

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier tidak ditemukan")

    await db.delete(supplier)
    await db.commit()
    return {"message": "Supplier dihapus"}
    
# ── PAYMENT SETTINGS ─────────────────────────────
@router.get("/payment-config")
async def get_payment_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw_denominations = await get_setting(db, "cash_denominations")
    denominations = json.loads(raw_denominations) if raw_denominations else [
        1000, 2000, 5000, 10000, 20000, 50000, 100000
    ]

    return {
        "cash_enabled": (await get_setting(db, "cash_enabled") or "1") == "1",
        "qris_enabled": (await get_setting(db, "qris_enabled") or "1") == "1",
        "hutang_enabled": (await get_setting(db, "hutang_enabled") or "1") == "1",
        "cash_denominations": denominations,
        "qris_image": await get_setting(db, "qris_image") or "",
        "hutang_default_limit": float(await get_setting(db, "hutang_default_limit") or "0")
    }


@router.post("/payment-config")
async def save_payment_config(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "Admin", "owner", "Owner")
    )
):
    if "cash_enabled" in data:
        await set_setting(db, "cash_enabled", "1" if data["cash_enabled"] else "0")
    if "qris_enabled" in data:
        await set_setting(db, "qris_enabled", "1" if data["qris_enabled"] else "0")
    if "hutang_enabled" in data:
        await set_setting(db, "hutang_enabled", "1" if data["hutang_enabled"] else "0")
    if "cash_denominations" in data:
        await set_setting(db, "cash_denominations", json.dumps(data["cash_denominations"]))
    if "qris_image" in data:
        await set_setting(db, "qris_image", data["qris_image"])
    if "hutang_default_limit" in data:
        await set_setting(db, "hutang_default_limit", str(data["hutang_default_limit"]))

    await db.commit()
    return {"message": "Payment config disimpan"}