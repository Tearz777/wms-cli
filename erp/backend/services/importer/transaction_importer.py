from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.transaction import Transaction, TransactionItem
from typing import List
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))

REQUIRED_FIELDS = {"trx_id", "type", "total"}

def validate_mapping(mappings: dict) -> list:
    errors = []
    mapped_fields = set(mappings.values())
    for req in REQUIRED_FIELDS:
        if req not in mapped_fields:
            errors.append(f"Field wajib tidak di-mapping: {req}")
    return errors

def apply_mapping(row: dict, mappings: dict) -> dict:
    result = {}
    for col, field in mappings.items():
        if field != "skip" and col in row:
            result[field] = row[col]
    return result

def parse_trx_warung(data: dict) -> List[dict]:
    """Parse format DB_TRX_WARUNG.json ke list of dicts."""
    result = []

    for trx_id, trx in data.get("pemasukan", {}).items():
        items = []
        for item in trx.get("items", []):
            items.append({
                "product_name": item.get("Nama", ""),
                "variant_name": item.get("Varian", "default"),
                "price": item.get("Harga", 0),
                "qty": item.get("Qty", 1),
                "subtotal": item.get("Sub Total", 0)
            })
        result.append({
            "trx_id": trx_id,
            "type": "pemasukan",
            "total": trx.get("total", 0),
            "note": None,
            "tanggal": trx.get("tanggal", ""),
            "waktu": trx.get("waktu", ""),
            "time_source": trx.get("sumber_waktu", "system"),
            "items": items
        })

    for trx_id, trx in data.get("pengeluaran", {}).items():
        result.append({
            "trx_id": trx_id,
            "type": "pengeluaran",
            "total": trx.get("total", 0),
            "note": trx.get("keterangan", ""),
            "tanggal": trx.get("tanggal", ""),
            "waktu": trx.get("waktu", ""),
            "time_source": trx.get("sumber_waktu", "system"),
            "items": []
        })

    return result

async def import_transactions(
    db: AsyncSession,
    rows: List[dict],
    mappings: dict = None,
    is_warung_format: bool = False
) -> dict:
    success = 0
    skipped = 0
    error_list = []

    if not is_warung_format and mappings:
        errors = validate_mapping(mappings)
        if errors:
            return {"success": 0, "skipped": 0, "errors": errors}

    for i, row in enumerate(rows):
        try:
            if not is_warung_format and mappings:
                data = apply_mapping(row, mappings)
            else:
                data = row

            trx_id = str(data.get("trx_id", "")).strip()
            trx_type = str(data.get("type", "pemasukan")).strip()
            total = int(float(str(data.get("total", 0))))
            note = data.get("note", None)
            time_source = data.get("time_source", "import")

            if not trx_id:
                skipped += 1
                continue

            # Cek duplikat
            existing = await db.execute(
                select(Transaction).where(Transaction.trx_id == trx_id)
            )
            if existing.scalar_one_or_none():
                skipped += 1
                continue

            trx = Transaction(
                trx_id=trx_id,
                type=trx_type,
                total=total,
                note=note,
                time_source=time_source
            )
            db.add(trx)
            await db.flush()

            for item in data.get("items", []):
                ti = TransactionItem(
                    transaction_id=trx.id,
                    product_name=item.get("product_name", ""),
                    variant_name=item.get("variant_name", "default"),
                    price=item.get("price", 0),
                    qty=item.get("qty", 1),
                    subtotal=item.get("subtotal", 0)
                )
                db.add(ti)

            success += 1

        except Exception as e:
            error_list.append(f"Baris {i+1}: {str(e)}")
            skipped += 1

    await db.commit()
    return {"success": success, "skipped": skipped, "errors": error_list}
