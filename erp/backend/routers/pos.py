from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime
from database import get_db
from models.product import Product, ProductVariant, StockMovement
from models.transaction import Transaction, TransactionItem
from models.user import User
from schemas.pos import PemasukanCreate, PengeluaranCreate, TransactionResponse
from dependencies import get_current_user, require_role
from services.smart_parser import extract_smart_input
from services.accounting import create_journal_from_transaction
from datetime import datetime, timezone, timedelta
from services.invoice_generator import generate_invoice_number
from typing import Optional
from datetime import datetime, timezone, timedelta, date


router = APIRouter(prefix="/pos", tags=["POS"])

VALID_PENGELUARAN = ["konsumsi_karyawan", "bayar_konsinyasi", "operasional", "lain_lain"]

WIB = timezone(timedelta(hours=7))

def generate_trx_id(type: str) -> str:
    now = datetime.now(WIB)
    prefix = "TRX" if type == "pemasukan" else "TRXK"
    return f"{prefix}-{now.strftime('%y%d%m-%M%H')}-{now.microsecond % 1000:03d}"

def format_time(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(WIB).strftime("%d/%m/%Y %H:%M")


# ── PEMASUKAN ─────────────────────────────────────
@router.post("/pemasukan", response_model=TransactionResponse)
async def create_pemasukan(
    data: PemasukanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = 0
    item_records = []

    for item in data.items:
        # Ambil produk
        p_result = await db.execute(
            select(Product).where(Product.id == item.product_id)
        )
        product = p_result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail=f"Produk ID {item.product_id} tidak ditemukan")

        # Ambil varian kalau ada
        variant = None
        price = 0
        variant_name = "default"

        if item.variant_id:
            v_result = await db.execute(
                select(ProductVariant).where(ProductVariant.id == item.variant_id)
            )
            variant = v_result.scalar_one_or_none()
            if not variant:
                raise HTTPException(status_code=404, detail=f"Varian ID {item.variant_id} tidak ditemukan")
            price = variant.price
            variant_name = variant.container
        elif product.variants:
            # Ambil varian pertama kalau tidak dispesifikasi
            v_result = await db.execute(
                select(ProductVariant)
                .where(ProductVariant.product_id == product.id)
                .where(ProductVariant.is_active == True)
            )
            first_variant = v_result.scalars().first()
            if first_variant:
                price = first_variant.price
                variant_name = first_variant.container
                variant = first_variant
        # Validasi stok
        if product.stock < item.qty:
            raise HTTPException(status_code=400, detail=f"Stok {product.name} tidak cukup. Stok tersedia: {product.stock}")
	            
        subtotal = price * item.qty
        total += subtotal


        item_records.append({
            "product": product,
            "variant": variant,
            "variant_name": variant_name,
            "price": price,
            "qty": item.qty,
            "subtotal": subtotal
        })

    # Tambah extra (lain-lain)
    if data.extra_amount:
        total += data.extra_amount

    # Buat transaksi
    trx_id = await generate_invoice_number(db, "pemasukan")
    if not trx_id:
        raise HTTPException(
        status_code=400,
        detail="Format invoice belum dikonfigurasi. Silakan atur di Settings → Invoice Format.")
    trx = Transaction(
        trx_id=trx_id,
        type="pemasukan",
        cashier_id=current_user.id,
        total=total,
        note=data.note,
        time_source="system"
    )
    db.add(trx)
    await db.flush()

    # Buat items
    for rec in item_records:
        ti = TransactionItem(
            transaction_id=trx.id,
            product_name=rec["product"].name,
            variant_name=rec["variant_name"],
            price=rec["price"],
            qty=rec["qty"],
            subtotal=rec["subtotal"]
        )
        db.add(ti)

    await create_journal_from_transaction(db, trx)
    await db.commit()

    result = await db.execute(
        select(Transaction)
        .options(selectinload(Transaction.items))
        .where(Transaction.id == trx.id)
    )
    trx = result.scalar_one()

    return {
        "id": trx.id,
        "trx_id": trx.trx_id,
        "type": trx.type,
        "total": trx.total,
        "note": trx.note,
        "time_source": trx.time_source,
        "created_at": format_time(trx.created_at),
        "items": trx.items
    }

# ── PENGELUARAN ───────────────────────────────────
@router.post("/pengeluaran", response_model=TransactionResponse)
async def create_pengeluaran(
    data: PengeluaranCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.category not in VALID_PENGELUARAN:
        raise HTTPException(status_code=400, detail=f"Kategori tidak valid. Pilih: {', '.join(VALID_PENGELUARAN)}")

    # Smart parser — cek apakah ada pembelian stok
    p_result = await db.execute(select(Product).where(Product.is_active == True))
    all_products = p_result.scalars().all()
    product_names = [p.name.lower() for p in all_products]

    parsed = extract_smart_input(data.note, product_names)

    if parsed and parsed["matched"]:
        # Auto stock movement
        matched_product = next((p for p in all_products if p.name.lower() == parsed["product"].lower()), None)
        if matched_product:
            matched_product.stock += parsed["qty"]
            movement = StockMovement(
                product_id=matched_product.id,
                type="in",
                qty=parsed["qty"],
                note=f"Auto dari pengeluaran: {data.note}",
                created_by=current_user.id
            )
            db.add(movement)


    trx_id = await generate_invoice_number(db, "pengeluaran")
    if not trx_id:
        raise HTTPException(
        status_code=400,
        detail="Format invoice belum dikonfigurasi. Silakan atur di Settings → Invoice Format.")

    trx = Transaction(
        trx_id=trx_id,
        type="pengeluaran",
        cashier_id=current_user.id,
        total=data.amount,
        note=f"[{data.category}] {data.note}",
        time_source="system"
    )
    db.add(trx)	
    await create_journal_from_transaction(db, trx,category=data.category)
    await db.commit()

    result = await db.execute(
        select(Transaction)
        .options(selectinload(Transaction.items))
        .where(Transaction.id == trx.id)
    )
    trx = result.scalar_one()

    return {
        "id": trx.id,
        "trx_id": trx.trx_id,
        "type": trx.type,
        "total": trx.total,
        "note": trx.note,
        "time_source": trx.time_source,
        "created_at": format_time(trx.created_at),
        "items": trx.items
    }

# ── GET transaksi ─────────────────────────────────
@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    filter: Optional[str] = "all",
    start_date: Optional[str] = None,  # YYYY-MM-DD
    end_date: Optional[str] = None,    # YYYY-MM-DD
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now = datetime.now(WIB)
    query = select(Transaction).options(selectinload(Transaction.items))

    # Custom range prioritas kalau ada
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=WIB)
        end = datetime.strptime(end_date, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59, tzinfo=WIB
        )
        query = query.where(Transaction.created_at >= start.astimezone(timezone.utc))
        query = query.where(Transaction.created_at <= end.astimezone(timezone.utc))

    elif filter == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.where(Transaction.created_at >= start.astimezone(timezone.utc))
    elif filter == "week":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.where(Transaction.created_at >= start.astimezone(timezone.utc))
    elif filter == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query = query.where(Transaction.created_at >= start.astimezone(timezone.utc))
    elif filter == "year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        query = query.where(Transaction.created_at >= start.astimezone(timezone.utc))

    query = query.order_by(Transaction.created_at.desc())
    result = await db.execute(query)
    transactions = result.scalars().all()

    return [
        {
            "id": t.id,
            "trx_id": t.trx_id,
            "type": t.type,
            "total": t.total,
            "note": t.note,
            "time_source": t.time_source,
            "created_at": format_time(t.created_at),
            "items": t.items
        }
        for t in transactions
    ]


# ── VOID transaksi ────────────────────────────────
@router.delete("/transactions/{trx_id}")
async def void_transaction(
    trx_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin", "owner", "Owner"))
):
    result = await db.execute(
        select(Transaction)
        .options(selectinload(Transaction.items))
        .where(Transaction.trx_id == trx_id)
    )
    trx = result.scalar_one_or_none()
    if not trx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    # Kembalikan stok kalau pemasukan
    if trx.type == "pemasukan":
        for item in trx.items:
            p_result = await db.execute(
                select(Product).where(Product.name == item.product_name)
            )
            product = p_result.scalar_one_or_none()
            if product:
                product.stock += item.qty
                movement = StockMovement(
                    product_id=product.id,
                    type="in",
                    qty=item.qty,
                    note=f"Void transaksi {trx_id}",
                    created_by=current_user.id
                )
                db.add(movement)

    await db.delete(trx)
    await db.commit()
    return {"message": f"Transaksi {trx_id} berhasil di-void"}
