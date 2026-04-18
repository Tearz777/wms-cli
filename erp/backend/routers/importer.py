import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from database import get_db
from dependencies import require_role
from models.user import User
from services.importer.detector import (
    detect_format,
    preview_json,
    preview_xlsx_sheets,
    preview_xlsx_sheet,
    preview_csv,
    preview_sqlite_tables,
    preview_sqlite_table
)
from services.importer.product_importer import import_products
from services.importer.transaction_importer import import_transactions, parse_trx_warung
from services.importer.account_importer import import_accounts
import json

router = APIRouter(prefix="/import", tags=["Import"])

UPLOAD_DIR = os.path.expanduser("~/erp_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── UPLOAD & PREVIEW ──────────────────────────────
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    """Upload file dan return preview + info format."""
    ext = "." + file.filename.split(".")[-1].lower()
    try:
        detect_format(file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Simpan file sementara
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        if ext == ".json":
            return {"filepath": filepath, **preview_json(filepath)}
        elif ext == ".xlsx":
            return {"filepath": filepath, **preview_xlsx_sheets(filepath)}
        elif ext == ".csv":
            return {"filepath": filepath, **preview_csv(filepath)}
        elif ext in [".db", ".sqlite"]:
            return {"filepath": filepath, **preview_sqlite_tables(filepath)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal preview: {str(e)}")

# ── PREVIEW SHEET/TABLE ───────────────────────────
@router.post("/preview-sheet")
async def preview_sheet(
    filepath: str,
    sheet: str,
    current_user: User = Depends(require_role("admin", "Admin"))
):
    """Preview sheet XLSX atau tabel SQLite."""
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File tidak ditemukan")

    ext = "." + filepath.split(".")[-1].lower()
    try:
        if ext == ".xlsx":
            return preview_xlsx_sheet(filepath, sheet)
        elif ext in [".db", ".sqlite"]:
            return preview_sqlite_table(filepath, sheet)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal preview: {str(e)}")

# ── IMPORT PRODUK ─────────────────────────────────
@router.post("/products")
async def import_products_endpoint(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    """
    Import produk dari file yang sudah diupload.
    
    payload:
    {
        "filepath": "/tmp/erp_uploads/file.json",
        "type": "warung_harga" | "list" | "xlsx" | "csv" | "sqlite",
        "sheet": "Sheet1",        // untuk xlsx
        "table": "products",      // untuk sqlite
        "mappings": {             // untuk format asing
            "Nama Barang": "nama",
            "Harga": "harga",
            "Kolom X": "skip"
        }
    }
    """
    filepath = payload.get("filepath")
    data_type = payload.get("type")
    mappings = payload.get("mappings", {})

    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File tidak ditemukan")

    rows = []
    ext = "." + filepath.split(".")[-1].lower()

    if data_type == "warung_harga":
        preview = preview_json(filepath)
        rows = preview["sample"] if preview["rows"] <= 5 else _load_all_json_flat(filepath)
    elif ext == ".json":
        with open(filepath) as f:
            data = json.load(f)
        rows = data if isinstance(data, list) else [data]
    elif ext == ".xlsx":
        import pandas as pd
        sheet = payload.get("sheet", 0)
        df = pd.read_excel(filepath, sheet_name=sheet)
        rows = df.to_dict(orient="records")
    elif ext == ".csv":
        import pandas as pd
        df = pd.read_csv(filepath)
        rows = df.to_dict(orient="records")
    elif ext in [".db", ".sqlite"]:
        import sqlite3, pandas as pd
        table = payload.get("table")
        if not table:
            raise HTTPException(status_code=400, detail="Nama tabel wajib untuk SQLite")
        conn = sqlite3.connect(filepath)
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        conn.close()
        rows = df.to_dict(orient="records")

    return await import_products(db, rows, mappings if mappings else _auto_mapping(rows))

# ── IMPORT TRANSAKSI ──────────────────────────────
@router.post("/transactions")
async def import_transactions_endpoint(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    filepath = payload.get("filepath")
    mappings = payload.get("mappings", {})

    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File tidak ditemukan")

    ext = "." + filepath.split(".")[-1].lower()

    if ext == ".json":
        with open(filepath) as f:
            data = json.load(f)

        # Format warung transaksi
        if isinstance(data, dict) and ("pemasukan" in data or "pengeluaran" in data):
            rows = parse_trx_warung(data)
            return await import_transactions(db, rows, is_warung_format=True)

        rows = data if isinstance(data, list) else [data]
    elif ext == ".xlsx":
        import pandas as pd
        sheet = payload.get("sheet", 0)
        df = pd.read_excel(filepath, sheet_name=sheet)
        rows = df.to_dict(orient="records")
    elif ext == ".csv":
        import pandas as pd
        df = pd.read_csv(filepath)
        rows = df.to_dict(orient="records")
    elif ext in [".db", ".sqlite"]:
        import sqlite3, pandas as pd
        table = payload.get("table")
        if not table:
            raise HTTPException(status_code=400, detail="Nama tabel wajib untuk SQLite")
        conn = sqlite3.connect(filepath)
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        conn.close()
        rows = df.to_dict(orient="records")

    return await import_transactions(db, rows, mappings=mappings)

# ── IMPORT AKUN ───────────────────────────────────
@router.post("/accounts")
async def import_accounts_endpoint(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    filepath = payload.get("filepath")
    mappings = payload.get("mappings", {})

    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File tidak ditemukan")

    ext = "." + filepath.split(".")[-1].lower()

    if ext == ".json":
        with open(filepath) as f:
            data = json.load(f)
        rows = data if isinstance(data, list) else [data]
    elif ext == ".xlsx":
        import pandas as pd
        sheet = payload.get("sheet", 0)
        df = pd.read_excel(filepath, sheet_name=sheet)
        rows = df.to_dict(orient="records")
    elif ext == ".csv":
        import pandas as pd
        df = pd.read_csv(filepath)
        rows = df.to_dict(orient="records")
    elif ext in [".db", ".sqlite"]:
        import sqlite3, pandas as pd
        table = payload.get("table")
        if not table:
            raise HTTPException(status_code=400, detail="Nama tabel wajib untuk SQLite")
        conn = sqlite3.connect(filepath)
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        conn.close()
        rows = df.to_dict(orient="records")

    return await import_accounts(db, rows, mappings=mappings)

# ── HELPERS ───────────────────────────────────────
def _load_all_json_flat(filepath: str) -> list:
    """Load semua data dari warung JSON dan flatten."""
    with open(filepath) as f:
        data = json.load(f)
    result = []
    produk = data.get("produk", {})
    for kategori, ownership_dict in produk.items():
        for ownership, items in ownership_dict.items():
            for nama, variants in items.items():
                for container, harga in variants.items():
                    result.append({
                        "nama": nama,
                        "kategori": kategori,
                        "ownership": ownership,
                        "container": container,
                        "harga": harga
                    })
    return result

def _auto_mapping(rows: list) -> dict:
    """Auto mapping kalau kolom sudah sesuai field."""
    if not rows:
        return {}
    return {col: col for col in rows[0].keys()}
