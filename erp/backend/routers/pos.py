from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from database import get_db
from dependencies import get_current_user, require_role

from models.user import User
from models.product import Product, ProductVariant, StockMovement
from models.transaction import Transaction, TransactionItem
from models.account import JournalEntry

from schemas.pos import (
    PemasukanCreate,
    PengeluaranCreate,
    TransactionResponse
)

from services.smart_parser import extract_smart_input
from services.accounting import create_journal_from_transaction
from services.invoice_generator import generate_invoice_number, get_setting


router = APIRouter(prefix="/pos", tags=["POS"])

VALID_PENGELUARAN = [
    "konsumsi_karyawan",
    "bayar_konsinyasi",
    "operasional",
    "lain_lain"
]

WIB = timezone(timedelta(hours=7))


# ────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────
def format_time(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(WIB).strftime("%d/%m/%Y %H:%M")


# ────────────────────────────────────────────────
# PEMASUKAN
# ────────────────────────────────────────────────
@router.post("/pemasukan", response_model=TransactionResponse)
async def create_pemasukan(
    data: PemasukanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = 0
    item_records = []

    # =========================
    # VALIDASI ITEM + HITUNG TOTAL
    # =========================
    for item in data.items:
        p_result = await db.execute(
            select(Product).where(Product.id == item.product_id)
        )
        product = p_result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Produk ID {item.product_id} tidak ditemukan"
            )

        variant = None
        variant_name = "default"
        price = 0

        if item.variant_id:
            v_result = await db.execute(
                select(ProductVariant).where(
                    ProductVariant.id == item.variant_id
                )
            )
            variant = v_result.scalar_one_or_none()

            if not variant:
                raise HTTPException(
                    status_code=404,
                    detail=f"Varian ID {item.variant_id} tidak ditemukan"
                )

            price = variant.price
            variant_name = variant.container

        else:
            v_result = await db.execute(
                select(ProductVariant)
                .where(ProductVariant.product_id == product.id)
                .where(ProductVariant.is_active == True)
            )
            first_variant = v_result.scalars().first()

            if first_variant:
                variant = first_variant
                price = first_variant.price
                variant_name = first_variant.container

        # cek stok
        if product.stock < item.qty:
            raise HTTPException(
                status_code=400,
                detail=f"Stok {product.name} tidak cukup"
            )

        product.stock -= item.qty

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

    # biaya tambahan
    if data.extra_amount:
        total += data.extra_amount

    # =========================
    # NORMALISASI PAYMENT
    # =========================
    method = (data.payment_method or "cash").lower()

    if method not in ["cash", "qris", "hutang"]:
        method = "cash"

    cash_received = data.cash_received or 0

    if method == "qris":
        cash_received = total

    if method == "hutang":
        cash_received = 0

        if not data.customer_id:
            raise HTTPException(
                status_code=400,
                detail="Customer wajib dipilih untuk transaksi hutang"
            )

    if method == "cash":
        if cash_received < total:
            raise HTTPException(
                status_code=400,
                detail="Uang bayar kurang"
            )

    # =========================
    # INVOICE
    # =========================
    trx_id = await generate_invoice_number(db, "pemasukan")

    if not trx_id:
        raise HTTPException(
            status_code=400,
            detail="Format invoice belum dikonfigurasi"
        )

    # =========================
    # BUAT TRANSAKSI
    # =========================
    trx = Transaction(
        trx_id=trx_id,
        type="pemasukan",
        cashier_id=current_user.id,
        total=total,
        cash_received=cash_received,
        customer_id=data.customer_id,
        payment_method=method,
        note=data.note,
        time_source="system"
    )

    db.add(trx)
    await db.flush()

    # =========================
    # BUAT ITEM
    # =========================
    for rec in item_records:
        db.add(
            TransactionItem(
                transaction_id=trx.id,
                product_name=rec["product"].name,
                variant_name=rec["variant_name"],
                price=rec["price"],
                qty=rec["qty"],
                subtotal=rec["subtotal"]
            )
        )

    # =========================
    # JOURNAL
    # =========================
    
    await db.commit()
    
    # reload
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
        "cash_received": trx.cash_received,
        "payment_method": trx.payment_method,
        "customer_id": trx.customer_id,
        "note": trx.note,
        "time_source": trx.time_source,
        "created_at": format_time(trx.created_at),
        "items": trx.items
    }


# ────────────────────────────────────────────────
# PENGELUARAN
# ────────────────────────────────────────────────
@router.post("/pengeluaran", response_model=TransactionResponse)
async def create_pengeluaran(
    data: PengeluaranCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.category not in VALID_PENGELUARAN:
        raise HTTPException(
            status_code=400,
            detail="Kategori tidak valid"
        )

    # smart parser
    p_result = await db.execute(
        select(Product).where(Product.is_active == True)
    )
    all_products = p_result.scalars().all()
    product_names = [p.name.lower() for p in all_products]

    parsed = extract_smart_input(data.note, product_names)

    if parsed and parsed["matched"]:
        matched = next(
            (
                p for p in all_products
                if p.name.lower() == parsed["product"].lower()
            ),
            None
        )

        if matched:
            matched.stock += parsed["qty"]

            db.add(
                StockMovement(
                    product_id=matched.id,
                    type="in",
                    qty=parsed["qty"],
                    note=f"Auto dari pengeluaran: {data.note}",
                    created_by=current_user.id
                )
            )

    trx_id = await generate_invoice_number(db, "pengeluaran")

    if not trx_id:
        raise HTTPException(
            status_code=400,
            detail="Format invoice belum dikonfigurasi"
        )

    trx = Transaction(
        trx_id=trx_id,
        type="pengeluaran",
        cashier_id=current_user.id,
        total=data.amount,
        note=f"[{data.category}] {data.note}",
        time_source="system"
    )

    db.add(trx)
    await db.flush()

    await create_journal_from_transaction(
        db,
        trx,
        category=data.category
    )
    

    await create_journal_from_transaction(
        db,
        trx,
        category=data.category
    )

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
        "cash_received": 0,
        "payment_method": "cash",
        "customer_id": None,
        "note": trx.note,
        "time_source": trx.time_source,
        "created_at": format_time(trx.created_at),
        "items": trx.items
    }
    
# ────────────────────────────────────────────────
# PRINT STRUK
# ────────────────────────────────────────────────
@router.get("/print/{trx_id}", response_class=HTMLResponse)
async def print_struk(
    trx_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Transaction)
        .options(selectinload(Transaction.items))
        .where(Transaction.trx_id == trx_id)
    )
    trx = result.scalar_one_or_none()

    if not trx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    # ambil setting bisnis
    business_name    = await get_setting(db, "business_name") or "Toko"
    business_address = await get_setting(db, "business_address") or ""
    business_phone   = await get_setting(db, "business_phone") or ""
    paper_width = await get_setting(db, "paper_width") or "58"
    if paper_width == "80":
      width_px = "302px"
    elif paper_width == "210":
      width_px = "794px"
    else:
      width_px = "216px"

    # build item rows
    item_rows = ""
    if trx.items:
        for item in trx.items:
            item_rows += f"""
        <tr>
          <td>{item.product_name}<br>
            <small>{item.variant_name} x{item.qty}</small>
          </td>
          <td style="text-align:right">
            {'{:,}'.format(item.subtotal).replace(',', '.')}
          </td>
        </tr>"""
    else:
        note_text = trx.note or "-"
        if note_text.startswith("["):
            try:
                kategori = note_text.split("]")[0].replace("[", "").strip()
                keterangan = note_text.split("]")[1].strip()
            except:
                kategori = "pengeluaran"
                keterangan = note_text
        else:
            kategori = "pengeluaran"
            keterangan = note_text

        kategori_label = {
            "operasional": "Operasional",
            "konsumsi_karyawan": "Konsumsi Karyawan",
            "bayar_konsinyasi": "Bayar Konsinyasi",
            "lain_lain": "Lain-lain"
        }.get(kategori, kategori.title())

        item_rows += f"""
        <tr>
          <td>
            <small>{kategori_label}</small><br>
            {keterangan}
          </td>
          <td style="text-align:right">
            {'{:,}'.format(trx.total).replace(',', '.')}
          </td>
        </tr>"""

    # kembalian
    kembalian = ""
    if trx.payment_method == "cash" and trx.cash_received:
        selisih = int(trx.cash_received) - trx.total
        kembalian = f"""
        <tr>
          <td>Bayar</td>
          <td style="text-align:right">{'{:,}'.format(int(trx.cash_received)).replace(',', '.')}</td>
        </tr>
        <tr>
          <td>Kembali</td>
          <td style="text-align:right">{'{:,}'.format(selisih).replace(',', '.')}</td>
        </tr>"""
        
    metode = (trx.payment_method or "cash").upper()
    waktu  = format_time(trx.created_at)
    kasir = ""
    if trx.cashier_id:
        from models.user import User as UserModel
        u_result = await db.execute(
            select(UserModel).where(UserModel.id == trx.cashier_id)
        )
        u = u_result.scalar_one_or_none()
        kasir = u.full_name if u else "Unknown"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family: monospace;
    font-size: 12px;
    width: {width_px};
    padding: 8px;
  }}
  h2 {{ font-size: 14px; text-align: center; margin-bottom: 2px; }}
  .center {{ text-align: center; }}
  .divider {{ border-top: 1px dashed #000; margin: 6px 0; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td {{ padding: 2px 0; vertical-align: top; }}
  .total-row td {{ font-weight: bold; border-top: 1px dashed #000; padding-top: 4px; }}
  @media print {{
    @page {{ margin: 0; size: {width_px} auto; }}
    body {{ width: {width_px}; }}
  }}
</style>
</head>
<body>
  <h2>{business_name}</h2>
  <div class="center">{business_address}</div>
  <div class="center">{business_phone}</div>
  <div class="divider"></div>
  <div>No: {trx.trx_id}</div>
  <div>Waktu: {waktu}</div>
  <div>Metode: {metode}</div>
  <div>Kasir: {kasir}</div>
  <div class="divider"></div>
  <table>
    {item_rows}
    <tr class="total-row">
      <td>TOTAL</td>
      <td style="text-align:right">{'{:,}'.format(trx.total).replace(',', '.')}</td>
    </tr>
    {kembalian}
  </table>
  <div class="divider"></div>
  <div class="center">Terima kasih!</div>
  <script>window.onload = function() {{ window.print(); }}</script>
</body>
</html>"""

    return HTMLResponse(content=html)
    
# ────────────────────────────────────────────────
# VOID TRANSAKSI
# ────────────────────────────────────────────────
@router.delete("/transactions/{trx_id}")
async def void_transaction(
    trx_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "Admin", "owner", "Owner")
    )
):
    result = await db.execute(
        select(Transaction)
        .options(selectinload(Transaction.items))
        .where(Transaction.trx_id == trx_id)
    )
    trx = result.scalar_one_or_none()

    if not trx:
        raise HTTPException(
            status_code=404,
            detail="Transaksi tidak ditemukan"
        )

    # rollback stok untuk pemasukan
    if trx.type == "pemasukan":
        for item in trx.items:
            p_result = await db.execute(
                select(Product).where(
                    Product.name == item.product_name
                )
            )
            product = p_result.scalar_one_or_none()

            if product:
                product.stock += item.qty

    # hapus journal entries
    await db.execute(
        delete(JournalEntry).where(
            JournalEntry.reference_trx_id == trx.id
        )
    )

    # hapus transaksi (cascade hapus items)
    await db.delete(trx)
    await db.commit()

    return {"message": f"Transaksi {trx_id} berhasil di-void"}
    
# ────────────────────────────────────────────────
# LIST TRANSAKSI
# ────────────────────────────────────────────────
@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    filter: str = "all",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Transaction).options(
        selectinload(Transaction.items),
        selectinload(Transaction.cashier)
    ).order_by(Transaction.created_at.desc())

    result = await db.execute(query)
    rows = result.scalars().all()

    return [
        {
            "id": trx.id,
            "trx_id": trx.trx_id,
            "type": trx.type,
            "total": trx.total,
            "cash_received": trx.cash_received or 0,
            "payment_method": getattr(trx, "payment_method", "cash"),
            "customer_id": trx.customer_id,
            "note": trx.note,
            "time_source": trx.time_source,
            "created_at": format_time(trx.created_at),
            "items": trx.items,
            "cashier_name": trx.cashier.full_name if trx.cashier else "-"
        }
        for trx in rows
    ]