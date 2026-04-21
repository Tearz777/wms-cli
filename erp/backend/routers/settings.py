import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from database import get_db
from models.setting import Setting
from schemas.setting import BusinessProfile, InvoiceFormat, SettingResponse, ShiftConfig, ShiftItem, GracePeriod
from dependencies import get_current_user, require_role
from models.user import User
from services.invoice_generator import get_setting, set_setting
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))

router = APIRouter(prefix="/settings", tags=["Settings"])

# ── GET semua settings ────────────────────────────
@router.get("/", response_model=List[SettingResponse])
async def get_all_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Setting))
    return result.scalars().all()

# ── GET business profile ──────────────────────────
@router.get("/business", response_model=dict)
async def get_business_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    keys = ["business_name", "business_address", "business_phone", "business_email"]
    profile = {}
    for key in keys:
        profile[key] = await get_setting(db, key)
    return profile

# ── UPDATE business profile ───────────────────────
@router.post("/business")
async def update_business_profile(
    data: BusinessProfile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin", "owner", "Owner"))
):
    await set_setting(db, "business_name", data.business_name)
    if data.business_address:
        await set_setting(db, "business_address", data.business_address)
    if data.business_phone:
        await set_setting(db, "business_phone", data.business_phone)
    if data.business_email:
        await set_setting(db, "business_email", data.business_email)
    await db.commit()
    return {"message": "Business profile berhasil disimpan"}

# ── GET invoice format ────────────────────────────
@router.get("/invoice-format", response_model=dict)
async def get_invoice_format(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "format_pemasukan": await get_setting(db, "invoice_format_pemasukan"),
        "format_pengeluaran": await get_setting(db, "invoice_format_pengeluaran"),
        "placeholders": [
            "{YY} — tahun 2 digit",
            "{YYYY} — tahun 4 digit",
            "{MM} — bulan",
            "{DD} — tanggal",
            "{HH} — jam",
            "{MIN} — menit",
            "{DAILY} — counter harian",
            "{WEEKLY} — counter mingguan",
            "{MONTHLY} — counter bulanan",
            "{RANDOM} — angka random 3 digit",
            "{NAMA_USAHA} — nama usaha (maks 6 karakter)"
        ]
    }

# ── UPDATE invoice format ─────────────────────────
@router.post("/invoice-format")
async def update_invoice_format(
    data: InvoiceFormat,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    await set_setting(db, "invoice_format_pemasukan", data.format_pemasukan)
    await set_setting(db, "invoice_format_pengeluaran", data.format_pengeluaran)
    await db.commit()

    # Preview
    from services.invoice_generator import generate_invoice_number
    preview_pemasukan = await generate_invoice_number(db, "pemasukan")
    preview_pengeluaran = await generate_invoice_number(db, "pengeluaran")

    return {
        "message": "Invoice format berhasil disimpan",
        "preview": {
            "pemasukan": preview_pemasukan,
            "pengeluaran": preview_pengeluaran
        }
    }
# ── GET shift config ──────────────────────────────
@router.get("/shifts")
async def get_shifts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw = await get_setting(db, "shifts")
    if not raw:
        return {"shifts": []}
    return {"shifts": json.loads(raw)}

# ── UPDATE shift config ───────────────────────────
@router.post("/shifts")
async def update_shifts(
    data: ShiftConfig,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin", "owner", "Owner"))
):
    await set_setting(db, "shifts", json.dumps([s.model_dump() for s in data.shifts]))
    await db.commit()
    return {"message": f"{len(data.shifts)} shift berhasil disimpan"}

@router.get("/current-shift")
async def get_current_shift(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw = await get_setting(db, "shifts")
    if not raw:
        return {"shift": None, "message": "Belum ada konfigurasi shift"}

    shifts = json.loads(raw)
    now = datetime.now(WIB)
    current_time = now.strftime("%H:%M")

    # Grace period 30 menit
    grace = await get_setting(db, "shift_grace_period") or "30"
    grace_minutes = int(grace)

    for shift in shifts:
        start = shift["start_time"]
        end = shift["end_time"]

        # Handle overnight shift (misal 22:00 - 06:00)
        if start <= end:
            in_shift = start <= current_time <= end
        else:
            in_shift = current_time >= start or current_time <= end

        # Cek grace period — waktu setelah shift selesai
        end_dt = datetime.strptime(end, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day, tzinfo=WIB
        )
        grace_end = end_dt + timedelta(minutes=grace_minutes)
        in_grace = end_dt <= now <= grace_end

        if in_shift or in_grace:
            return {
                "shift": shift,
                "status": "grace" if in_grace else "active",
                "grace_period_minutes": grace_minutes
            }

    return {"shift": None, "message": "Tidak ada shift aktif saat ini"}


@router.post("/grace-period")
async def set_grace_period(
    data: GracePeriod,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin", "owner", "Owner"))
):
    await set_setting(db, "shift_grace_period", str(data.minutes))
    await db.commit()
    return {"message": f"Grace period diset ke {data.minutes} menit"}
