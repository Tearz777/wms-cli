from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from database import get_db
from models.account import Account, JournalEntry
from schemas.accounting import AccountCreate, AccountResponse, JournalEntryCreate, JournalEntryResponse, PeriodRequest
from dependencies import get_current_user, require_role
from models.user import User
from services.accounting import get_laba_rugi, get_neraca, generate_closing_entries
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))

router = APIRouter(prefix="/accounting", tags=["Accounting"])

# ── INIT COA DEFAULT ──────────────────────────────
@router.post("/init", tags=["Accounting"])
async def init_coa(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    """Inisialisasi Chart of Accounts default warung."""
    default_accounts = [
        {"name": "Kas", "type": "asset"},
        {"name": "Piutang Pelanggan", "type": "asset"},
        {"name": "Persediaan Barang", "type": "asset"},
        {"name": "Hutang Konsinyasi", "type": "liability"},
        {"name": "Modal", "type": "equity"},
        {"name": "Laba Ditahan", "type": "equity"},
        {"name": "Pendapatan Penjualan", "type": "income"},
        {"name": "Pendapatan Lain-lain", "type": "income"},
        {"name": "Harga Pokok Penjualan", "type": "expense"},
        {"name": "Beban Konsumsi Karyawan", "type": "expense"},
        {"name": "Beban Operasional", "type": "expense"},
        {"name": "Beban Lain-lain", "type": "expense"},
    ]

    created = []
    for acc in default_accounts:
        # Cek sudah ada atau belum
        existing = await db.execute(
            select(Account).where(Account.name == acc["name"])
        )
        if not existing.scalar_one_or_none():
            new_acc = Account(name=acc["name"], type=acc["type"])
            db.add(new_acc)
            created.append(acc["name"])

    await db.commit()
    return {"message": f"{len(created)} akun berhasil dibuat", "accounts": created}

# ── GET SEMUA AKUN ────────────────────────────────
@router.get("/accounts", response_model=List[AccountResponse])
async def get_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Account))
    return result.scalars().all()

# ── TAMBAH AKUN ───────────────────────────────────
@router.post("/accounts", response_model=AccountResponse)
async def create_account(
    data: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    existing = await db.execute(select(Account).where(Account.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Akun sudah ada")

    acc = Account(name=data.name, type=data.type)
    db.add(acc)
    await db.commit()
    await db.refresh(acc)
    return acc

# ── JURNAL MANUAL ─────────────────────────────────
@router.post("/journal", response_model=JournalEntryResponse)
async def create_journal(
    data: JournalEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    entry = JournalEntry(
        description=data.description,
        debit_account_id=data.debit_account_id,
        credit_account_id=data.credit_account_id,
        amount=data.amount,
        reference_trx_id=data.reference_trx_id
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return {
        "id": entry.id,
        "date": str(entry.date),
        "description": entry.description,
        "debit_account_id": entry.debit_account_id,
        "credit_account_id": entry.credit_account_id,
        "amount": entry.amount,
        "reference_trx_id": entry.reference_trx_id
    }

# ── GET JURNAL UMUM ───────────────────────────────
@router.get("/journal", response_model=List[JournalEntryResponse])
async def get_journal(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(JournalEntry).order_by(JournalEntry.date.asc())
    )
    entries = result.scalars().all()
    return [
        {
            "id": e.id,
            "date": str(e.date),
            "description": e.description,
            "debit_account_id": e.debit_account_id,
            "credit_account_id": e.credit_account_id,
            "amount": e.amount,
            "reference_trx_id": e.reference_trx_id
        }
        for e in entries
    ]

# ── LAPORAN LABA RUGI ─────────────────────────────
@router.post("/laporan/laba-rugi")
async def laporan_laba_rugi(
    data: PeriodRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin", "owner", "Owner"))
):
    return await get_laba_rugi(db, data.start_date, data.end_date)

# ── LAPORAN NERACA ────────────────────────────────
@router.get("/laporan/neraca")
async def laporan_neraca(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin", "owner", "Owner"))
):
    return await get_neraca(db)

# ── CLOSING ENTRIES ───────────────────────────────
@router.post("/closing")
async def closing(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    today = datetime.now(WIB).strftime("%Y-%m-%d")
    entries = await generate_closing_entries(db, today)
    await db.commit()
    return {"message": f"{len(entries)} closing entries berhasil dibuat", "period_end": today}
