import json
import sqlite3
import pandas as pd
from pathlib import Path

SUPPORTED_FORMATS = {".json", ".xlsx", ".csv", ".db", ".sqlite"}

def detect_format(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Format tidak didukung: {ext}")
    return ext

def has_header(row: list) -> bool:
    text_count = sum(1 for cell in row if isinstance(cell, str) and not cell.replace('.','').replace('-','').isdigit())
    return text_count > len(row) / 2

def get_column_labels(n: int) -> list:
    labels = []
    for i in range(n):
        label = ""
        j = i
        while True:
            label = chr(65 + (j % 26)) + label
            j = j // 26 - 1
            if j < 0:
                break
        labels.append(label)
    return labels

# ── JSON ──────────────────────────────────────────
def preview_json(filepath: str, rows: int = 5) -> dict:
    with open(filepath, "r") as f:
        data = json.load(f)

    # Format warung harga
    if isinstance(data, dict) and "produk" in data:
        flat = _flatten_warung_json(data)
        return {
            "format": "json",
            "type": "warung_harga",
            "rows": len(flat),
            "columns": list(flat[0].keys()) if flat else [],
            "sample": flat[:rows],
            "needs_mapping": False
        }

    # Format warung transaksi
    if isinstance(data, dict) and ("pemasukan" in data or "pengeluaran" in data):
        from .transaction_importer import parse_trx_warung
        flat = parse_trx_warung(data)
        return {
            "format": "json",
            "type": "warung_trx",
            "rows": len(flat),
            "columns": ["trx_id", "type", "total", "note", "tanggal", "items"],
            "sample": flat[:rows],
            "needs_mapping": False
        }

    # Format list of dicts
    if isinstance(data, list) and data:
        return {
            "format": "json",
            "type": "list",
            "rows": len(data),
            "columns": list(data[0].keys()),
            "sample": data[:rows],
            "needs_mapping": True
        }

    # Format dict biasa
    if isinstance(data, dict):
        return {
            "format": "json",
            "type": "dict",
            "rows": 1,
            "columns": list(data.keys()),
            "sample": [data],
            "needs_mapping": True
        }

def _flatten_warung_json(data: dict) -> list:
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

# ── XLSX ──────────────────────────────────────────
def preview_xlsx_sheets(filepath: str) -> dict:
    xl = pd.ExcelFile(filepath)
    return {
        "format": "xlsx",
        "sheets": xl.sheet_names
    }

def preview_xlsx_sheet(filepath: str, sheet: str, rows: int = 5) -> dict:
    df_raw = pd.read_excel(filepath, sheet_name=sheet, header=None)
    first_row = df_raw.iloc[0].tolist()

    if has_header(first_row):
        df = pd.read_excel(filepath, sheet_name=sheet)
        columns = list(df.columns)
        sample = df.head(rows).to_dict(orient="records")
        has_hdr = True
    else:
        df = df_raw
        columns = get_column_labels(len(df.columns))
        df.columns = columns
        sample = df.head(rows).to_dict(orient="records")
        has_hdr = False

    return {
        "format": "xlsx",
        "sheet": sheet,
        "has_header": has_hdr,
        "rows": len(df),
        "columns": columns,
        "sample": sample,
        "needs_mapping": True
    }

# ── CSV ───────────────────────────────────────────
def preview_csv(filepath: str, rows: int = 5) -> dict:
    df_raw = pd.read_csv(filepath, header=None)
    first_row = df_raw.iloc[0].tolist()

    if has_header(first_row):
        df = pd.read_csv(filepath)
        columns = list(df.columns)
        sample = df.head(rows).to_dict(orient="records")
        has_hdr = True
    else:
        df = df_raw
        columns = get_column_labels(len(df.columns))
        df.columns = columns
        sample = df.head(rows).to_dict(orient="records")
        has_hdr = False

    return {
        "format": "csv",
        "has_header": has_hdr,
        "rows": len(df),
        "columns": columns,
        "sample": sample,
        "needs_mapping": True
    }

# ── SQLITE ────────────────────────────────────────
def preview_sqlite_tables(filepath: str) -> dict:
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    conn.close()
    return {
        "format": "sqlite",
        "tables": tables
    }

def preview_sqlite_table(filepath: str, table: str, rows: int = 5) -> dict:
    conn = sqlite3.connect(filepath)
    df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT {rows}", conn)
    total = pd.read_sql_query(f"SELECT COUNT(*) as c FROM {table}", conn).iloc[0]["c"]
    conn.close()

    return {
        "format": "sqlite",
        "table": table,
        "rows": total,
        "columns": list(df.columns),
        "sample": df.to_dict(orient="records"),
        "needs_mapping": True
    }
