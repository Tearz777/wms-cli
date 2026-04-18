import re
import difflib
from typing import Optional

TRIGGER_WORDS = ["beli", "restok", "purchase", "tambah stok"]

def extract_smart_input(note: str, product_names: list[str]) -> Optional[dict]:
    """
    Parse keterangan pengeluaran untuk deteksi pembelian stok.
    
    Contoh:
    - "beli rokok Surya 16 x 10" → {product: "rokok surya 16", qty: 10}
    - "restok mie goreng 5"      → {product: "mie goreng", qty: 5}
    """
    note_lower = note.lower().strip()

    # Cek trigger word
    triggered = False
    for trigger in TRIGGER_WORDS:
        if note_lower.startswith(trigger):
            note_lower = note_lower[len(trigger):].strip()
            triggered = True
            break

    if not triggered:
        return None

    # Cari qty di akhir string
    # Pattern: "nama produk x 10" atau "nama produk 10"
    match = re.search(r'(?:x\s*)?(\d+)\s*$', note_lower)
    if not match:
        return None

    qty = int(match.group(1))
    product_query = note_lower[:match.start()].strip().rstrip('x').strip()

    if not product_query:
        return None

    # Fuzzy match ke daftar produk
    matches = difflib.get_close_matches(
        product_query,
        product_names,
        n=1,
        cutoff=0.5
    )

    if not matches:
        return {
            "matched": False,
            "query": product_query,
            "qty": qty,
            "product": None
        }

    return {
        "matched": True,
        "query": product_query,
        "qty": qty,
        "product": matches[0]
    }
