from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.product import Product, ProductVariant
from typing import List

REQUIRED_FIELDS = {"nama", "harga"}
OPTIONAL_FIELDS = {"kategori", "ownership", "container", "stok", "lokasi"}

def validate_mapping(mappings: dict) -> list:
    """Validasi mapping — nama dan harga wajib ada."""
    errors = []
    mapped_fields = set(mappings.values())
    for req in REQUIRED_FIELDS:
        if req not in mapped_fields:
            errors.append(f"Field wajib tidak di-mapping: {req}")
    return errors

def apply_mapping(row: dict, mappings: dict) -> dict:
    """Terapkan mapping kolom → field ke satu baris data."""
    result = {}
    for col, field in mappings.items():
        if field != "skip" and col in row:
            result[field] = row[col]
    return result

async def import_products(
    db: AsyncSession,
    rows: List[dict],
    mappings: dict
) -> dict:
    """
    Import produk dari list of dicts.
    
    mappings contoh:
    {
        "Nama Barang": "nama",
        "Harga": "harga",
        "Kategori": "kategori",
        "Kolom X": "skip"
    }
    """
    errors = validate_mapping(mappings)
    if errors:
        return {"success": 0, "skipped": 0, "errors": errors}

    success = 0
    skipped = 0
    error_list = []

    for i, row in enumerate(rows):
        try:
            data = apply_mapping(row, mappings)

            nama = str(data.get("nama", "")).strip().lower()
            harga_raw = data.get("harga", 0)

            if not nama:
                skipped += 1
                continue

            try:
                harga = int(float(str(harga_raw).replace(",", "").replace(".", "")))
            except:
                error_list.append(f"Baris {i+1}: harga tidak valid ({harga_raw})")
                skipped += 1
                continue

            kategori = str(data.get("kategori", "umum")).strip().lower()
            ownership = str(data.get("ownership", "own")).strip().lower()
            container = str(data.get("container", "default")).strip().lower()
            stok = int(data.get("stok", 0)) if data.get("stok") else 0
            lokasi = str(data.get("lokasi", "Gudang 1")).strip()

            # Cek produk sudah ada
            existing = await db.execute(
                select(Product).where(
                    Product.name == nama,
                    Product.category == kategori,
                    Product.ownership == ownership
                )
            )
            product = existing.scalar_one_or_none()

            if not product:
                product = Product(
                    name=nama,
                    category=kategori,
                    ownership=ownership,
                    stock=stok,
                    location=lokasi
                )
                db.add(product)
                await db.flush()

            # Cek varian sudah ada
            v_existing = await db.execute(
                select(ProductVariant).where(
                    ProductVariant.product_id == product.id,
                    ProductVariant.container == container
                )
            )
            variant = v_existing.scalar_one_or_none()

            if not variant:
                variant = ProductVariant(
                    product_id=product.id,
                    container=container,
                    price=harga,
                    stock=stok
                )
                db.add(variant)
                success += 1
            else:
                # Update harga kalau varian sudah ada
                variant.price = harga
                success += 1

        except Exception as e:
            error_list.append(f"Baris {i+1}: {str(e)}")
            skipped += 1

    await db.commit()
    return {"success": success, "skipped": skipped, "errors": error_list}
