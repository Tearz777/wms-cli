from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone, timedelta
from models.account import Account, JournalEntry
from models.transaction import Transaction

WIB = timezone(timedelta(hours=7))

# ── AUTO JURNAL DARI POS ───────────────────────────
async def create_journal_from_transaction(
    db: AsyncSession,
    trx: Transaction,
    category: str = None
):
    # Ambil akun Kas
    kas = await db.execute(select(Account).where(Account.name == "Kas"))
    kas = kas.scalar_one_or_none()

    if trx.type == "pemasukan":
        # Ambil akun Pendapatan Penjualan
        income = await db.execute(
            select(Account).where(Account.name == "Pendapatan Penjualan")
        )
        income = income.scalar_one_or_none()

        if kas and income:
            entry = JournalEntry(
                description=f"Penjualan - {trx.trx_id}",
                debit_account_id=kas.id,
                credit_account_id=income.id,
                amount=trx.total,
                reference_trx_id=trx.trx_id
            )
            db.add(entry)

    elif trx.type == "pengeluaran":
        # Tentukan akun beban berdasarkan kategori
        category_map = {
            "konsumsi_karyawan": "Beban Konsumsi Karyawan",
            "bayar_konsinyasi": "Hutang Konsinyasi",
            "operasional": "Beban Operasional",
            "lain_lain": "Beban Lain-lain"
        }
        beban_name = category_map.get(category, "Beban Lain-lain")

        beban = await db.execute(
            select(Account).where(Account.name == beban_name)
        )
        beban = beban.scalar_one_or_none()

        if kas and beban:
            entry = JournalEntry(
                description=f"Pengeluaran [{category}] - {trx.trx_id}",
                debit_account_id=beban.id,
                credit_account_id=kas.id,
                amount=trx.total,
                reference_trx_id=trx.trx_id
            )
            db.add(entry)

    await db.flush()

# ── CLOSING ENTRIES ────────────────────────────────
async def generate_closing_entries(db: AsyncSession, period_end: str):
    """Auto generate closing entries akhir periode."""

    # Ambil semua akun income & expense
    incomes = await db.execute(
        select(Account).where(Account.type == "income")
    )
    expenses = await db.execute(
        select(Account).where(Account.type == "expense")
    )
    laba_ditahan = await db.execute(
        select(Account).where(Account.name == "Laba Ditahan")
    )

    incomes = incomes.scalars().all()
    expenses = expenses.scalars().all()
    laba_ditahan = laba_ditahan.scalar_one_or_none()

    if not laba_ditahan:
        return []

    entries = []

    # Close income → Laba Ditahan
    for acc in incomes:
        # Hitung total saldo akun
        total = await _get_account_balance(db, acc.id, "credit")
        if total > 0:
            entry = JournalEntry(
                description=f"Closing - {acc.name} [{period_end}]",
                debit_account_id=acc.id,
                credit_account_id=laba_ditahan.id,
                amount=total,
                reference_trx_id=f"CLOSING-{period_end}"
            )
            db.add(entry)
            entries.append(entry)

    # Close expense → Laba Ditahan
    for acc in expenses:
        total = await _get_account_balance(db, acc.id, "debit")
        if total > 0:
            entry = JournalEntry(
                description=f"Closing - {acc.name} [{period_end}]",
                debit_account_id=laba_ditahan.id,
                credit_account_id=acc.id,
                amount=total,
                reference_trx_id=f"CLOSING-{period_end}"
            )
            db.add(entry)
            entries.append(entry)

    await db.flush()
    return entries

# ── HELPER: SALDO AKUN ────────────────────────────
async def _get_account_balance(db: AsyncSession, account_id: int, side: str) -> int:
    """Hitung saldo akun berdasarkan sisi debit/credit."""
    if side == "debit":
        result = await db.execute(
            select(JournalEntry).where(JournalEntry.debit_account_id == account_id)
        )
    else:
        result = await db.execute(
            select(JournalEntry).where(JournalEntry.credit_account_id == account_id)
        )
    entries = result.scalars().all()
    return sum(e.amount for e in entries)

# ── LAPORAN LABA RUGI ─────────────────────────────
async def get_laba_rugi(db: AsyncSession, start_date: str, end_date: str) -> dict:
    start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=WIB)
    end = datetime.strptime(end_date, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59, tzinfo=WIB
    )

    # Semua income account
    incomes = await db.execute(select(Account).where(Account.type == "income"))
    incomes = incomes.scalars().all()

    # Semua expense account
    expenses = await db.execute(select(Account).where(Account.type == "expense"))
    expenses = expenses.scalars().all()

    income_detail = []
    total_income = 0
    for acc in incomes:
        entries = await db.execute(
            select(JournalEntry).where(
                and_(
                    JournalEntry.credit_account_id == acc.id,
                    JournalEntry.date >= start,
                    JournalEntry.date <= end
                )
            )
        )
        entries = entries.scalars().all()
        total = sum(e.amount for e in entries)
        total_income += total
        income_detail.append({"account": acc.name, "total": total})

    expense_detail = []
    total_expense = 0
    for acc in expenses:
        entries = await db.execute(
            select(JournalEntry).where(
                and_(
                    JournalEntry.debit_account_id == acc.id,
                    JournalEntry.date >= start,
                    JournalEntry.date <= end
                )
            )
        )
        entries = entries.scalars().all()
        total = sum(e.amount for e in entries)
        total_expense += total
        expense_detail.append({"account": acc.name, "total": total})

    return {
        "periode": f"{start_date} s/d {end_date}",
        "pendapatan": income_detail,
        "total_pendapatan": total_income,
        "beban": expense_detail,
        "total_beban": total_expense,
        "laba_bersih": total_income - total_expense
    }

# ── LAPORAN NERACA ────────────────────────────────
async def get_neraca(db: AsyncSession) -> dict:
    aset = await db.execute(select(Account).where(Account.type == "asset"))
    liabilitas = await db.execute(select(Account).where(Account.type == "liability"))
    ekuitas = await db.execute(select(Account).where(Account.type == "equity"))

    aset = aset.scalars().all()
    liabilitas = liabilitas.scalars().all()
    ekuitas = ekuitas.scalars().all()

    async def get_balance(accounts, side):
        result = []
        total = 0
        for acc in accounts:
            bal = await _get_account_balance(db, acc.id, side)
            result.append({"account": acc.name, "saldo": bal})
            total += bal
        return result, total

    aset_detail, total_aset = await get_balance(aset, "debit")
    liabilitas_detail, total_liabilitas = await get_balance(liabilitas, "credit")
    ekuitas_detail, total_ekuitas = await get_balance(ekuitas, "credit")

    return {
        "aset": aset_detail,
        "total_aset": total_aset,
        "liabilitas": liabilitas_detail,
        "total_liabilitas": total_liabilitas,
        "ekuitas": ekuitas_detail,
        "total_ekuitas": total_ekuitas,
        "balance_check": total_aset == (total_liabilitas + total_ekuitas)
    }
