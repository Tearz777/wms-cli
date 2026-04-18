from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.account import Account
from typing import List

REQUIRED_FIELDS = {"nama", "type"}
VALID_TYPES = {"asset", "liability", "equity", "income", "expense"}

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

async def import_accounts(
    db: AsyncSession,
    rows: List[dict],
    mappings: dict = None
) -> dict:
    success = 0
    skipped = 0
    error_list = []

    if mappings:
        errors = validate_mapping(mappings)
        if errors:
            return {"success": 0, "skipped": 0, "errors": errors}

    for i, row in enumerate(rows):
        try:
            data = apply_mapping(row, mappings) if mappings else row

            nama = str(data.get("nama", "")).strip()
            tipe = str(data.get("type", "")).strip().lower()

            if not nama:
                skipped += 1
                continue

            if tipe not in VALID_TYPES:
                error_list.append(f"Baris {i+1}: tipe akun tidak valid ({tipe}). Pilih: {', '.join(VALID_TYPES)}")
                skipped += 1
                continue

            # Cek duplikat
            existing = await db.execute(
                select(Account).where(Account.name == nama)
            )
            if existing.scalar_one_or_none():
                skipped += 1
                continue

            acc = Account(name=nama, type=tipe)
            db.add(acc)
            success += 1

        except Exception as e:
            error_list.append(f"Baris {i+1}: {str(e)}")
            skipped += 1

    await db.commit()
    return {"success": success, "skipped": skipped, "errors": error_list}
