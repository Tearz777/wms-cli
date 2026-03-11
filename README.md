# Python WMS + POS CLI

A lightweight **Warehouse Management System (WMS)** and **Point of Sale (POS)** built entirely in Python CLI.

Developed from real warung operational needs — focused on simplicity, local data storage, and zero external dependencies.

> 💡 Built and maintained on a mobile phone via **Termux** — no laptop required.

---

## Features

### WMS (v2.5 — Stable)
- 📦 Inventory tracking
- ➕ Stock in (barang masuk)
- ➖ Stock out (barang keluar)
- ⚠️ Restock alert system
- 💾 JSON-based local database
- 🖥️ CLI menu interface
- 🛠️ Input validation

### POS (v1.0 — Stable)
- 🧾 Income recording (Pemasukan)
- 💸 Expense recording (Pengeluaran) with categories
- 🔢 Unique transaction ID system (anti-fraud timestamp encoding)
- 📊 Independent daily / weekly / monthly counters
- 💾 JSON-based transaction database
- 🛠️ Input validation with price sanity check

---

## Tech Stack

- **Language:** Python 3.12
- **Database:** JSON (local flat-file)
- **Dependencies:** Standard library only — `os`, `json`, `datetime`
- **Environment:** Termux (Android) / Any Python 3.x terminal

---

## Project Structure

```
python-wms-cli/
│
├── src/
│   ├── WMS/
│   │   ├── v1/
│   │   │   └── wms_cli_v1.py
│   │   └── v2/
│   │       ├── wms_cli_v2.0.py
│   │       └── wms_cli_v2_5.py          ← stable
│   ├── POS/
│   │   └── v1/
│   │       └── pos_cli_v1.py            ← stable
│   └── POS+WMS/
│       ├── v1/
│       ├── v2/
│       └── v3/
│
├── database/
│   ├── WMS_DB.json
│   ├── DB_HARGA.json
│   └── DB_TRX.json
│
├── README.md
├── .gitignore
└── LICENSE
```

---

## Database Structure

### WMS_DB.json
```json
{
  "kopi": { "stok": 10, "min_stok": 3 },
  "gula": { "stok": 5, "min_stok": 2 }
}
```

### DB_TRX.json
```json
{
  "counter": {
    "pemasukan_harian": 1,
    "pemasukan_mingguan": 1,
    "pemasukan_bulanan": 1,
    "pengeluaran_harian": 1,
    "pengeluaran_mingguan": 1,
    "pengeluaran_bulanan": 1,
    "hari_aktif": "",
    "minggu_aktif": "",
    "bulan_aktif": "",
    "tahun_aktif": ""
  },
  "pemasukan": {},
  "pengeluaran": {}
}
```

### DB_HARGA.json *(used in POS v2+)*
```json
{
  "produk": {}
}
```

---

## Transaction ID Format

```
Pemasukan  : TRX-YYDDMM-MMHH-XXX-YYY-ZZZ
Pengeluaran: TRXK-YYDDMM-MMHH-XXX-YYY-ZZZ
```

| Part | Meaning |
|------|---------|
| `YYDDMM` | Year-Day-Month (deliberately reversed — anti-fraud) |
| `MMHH` | Minute-Hour (deliberately reversed — anti-fraud) |
| `XXX` | Daily counter (resets every day) |
| `YYY` | Weekly counter (resets every moth) |
| `ZZZ` | Monthly counter (rests every year) |

All three counters are **independent** of each other.

---

## How to Run

### WMS
```bash
cd src/WMS/v2
python wms_cli_v2_5.py
```

### POS
```bash
cd src/POS/v1
python pos_cli_v1.py
```

> Make sure the `database/` folder exists at `../../database/` relative to the script, or adjust the path in the source file.

---

## Roadmap

```
WMS v2.5     ✅ Stable
POS v1.0     ✅ Stable
    │
    ├── POS v1.5   → Refactor: universal simpan_transaksi(), fix shared counter bug
    ├── POS v2.0   → Price lookup from DB_HARGA + Surabaya time server (anti-fraud)
    ├── POS v3.0   → Beverage container/size variations
    ├── POS v3.1   → Consignment tracking (input)
    ├── POS v3.2   → Consignment payment & reporting
    │
    ├── POS+WMS v1 → Integration: stock auto-deduct on sale
    │
    ├── ERP CLI    → Combined: financial reports, hutang/piutang, restock alerts
    │
    └── Web ERP    → Flask/Django, owner vs kasir access control
```

### Detailed Backlog
- [x] `simpan_transaksi()` universal function (v1.5)
- [x] Separate counters for pemasukan & pengeluaran (v1.5 bugfix)
- [ ] Price lookup from DB_HARGA (v2.0)
- [ ] NTP time server — Surabaya timezone (v2.0)
- [x] Daily sales report / Laporan Harian (v2.0)
- [ ] Beverage variants — container & size pricing (v3.0)
- [ ] Consignment tracking — martabak, cenil, jajan 2k, etc. (v3.1/v3.2)
- [ ] WMS auto stock deduction on POS sale (POS+WMS v1)
- [ ] Owner vs kasir role access (Web ERP)

---

## Changelog

### POS v1.5
- Refactor: simpan_transaksi() universal → save_trx()
- Fix counter reset bug: mingguan reset tiap ganti bulan, bulanan reset tiap ganti tahun
- Tambah tahun_aktif di counter DB
- Daily Report (Laporan Harian) — jumlah transaksi, item terlaris, list pengeluaran, laba kotor

### POS v1.0
- Income recording (Pemasukan) with multi-item support
- Expense recording (Pengeluaran) with 5 categories
- Unique transaction ID with anti-fraud timestamp encoding
- Independent daily/weekly/monthly counters
- Price sanity check (warns if price ≤ Rp100)
- JSON persistence for all transactions

### WMS v2.5
- Code refactoring — descriptive function & variable names
- Wrapped main loop into `main()` function
- Fixed logic bug in `barang_keluar()`
- Added `if __name__ == "__main__"` guard
- Added `os.system("clear")` for cleaner display

### WMS v2.0
- JSON database persistence
- Auto load / save database
- Local inventory storage

### WMS v1.0
- Initial CLI warehouse management system
- Stock in / stock out
- Restock alert
- CLI menu system

---

## Author

**Thery Vissabillillah**
- SMK Accounting graduate with 5+ years warehouse/logistics experience
- Building real-world Python tools from scratch — on mobile via Termux
- Long-term goal: lightweight ERP for small businesses and UMKM

---

---

# Versi Bahasa Indonesia

# Python WMS + POS CLI

Sistem **Manajemen Gudang (WMS)** dan **Point of Sale (POS)** berbasis CLI yang dibangun sepenuhnya dengan Python.

Dikembangkan dari kebutuhan operasional warung nyata — fokus pada kesederhanaan, penyimpanan data lokal, dan tanpa dependensi eksternal.

> 💡 Dibangun dan dikelola dari **HP via Termux** — tanpa laptop.

---

## Fitur

### WMS (v2.5 — Stabil)
- 📦 Pencatatan stok
- ➕ Barang masuk
- ➖ Barang keluar
- ⚠️ Alert restock otomatis
- 💾 Database lokal berbasis JSON
- 🖥️ Antarmuka menu CLI
- 🛠️ Validasi input

### POS (v1.0 — Stabil)
- 🧾 Pencatatan pemasukan (multi-item)
- 💸 Pencatatan pengeluaran dengan kategori
- 🔢 Format ID transaksi unik (timestamp dibalik — anti-fraud)
- 📊 Counter harian / mingguan / bulanan yang independen
- 💾 Database transaksi berbasis JSON
- 🛠️ Validasi input + cek harga terlalu rendah

---

## Tech Stack

- **Bahasa:** Python 3.12
- **Database:** JSON (flat-file lokal)
- **Dependensi:** Standard library saja — `os`, `json`, `datetime`
- **Environment:** Termux (Android) / Terminal Python 3.x manapun

---

## Struktur Project

```
python-wms-cli/
│
├── src/
│   ├── WMS/
│   │   ├── v1/
│   │   │   └── wms_cli_v1.py
│   │   └── v2/
│   │       ├── wms_cli_v2.0.py
│   │       └── wms_cli_v2_5.py          ← stabil
│   ├── POS/
│   │   └── v1/
│   │       └── pos_cli_v1.py            ← stabil
│   └── POS+WMS/
│       ├── v1/
│       ├── v2/
│       └── v3/
│
├── database/
│   ├── WMS_DB.json
│   ├── DB_HARGA.json
│   └── DB_TRX.json
│
├── README.md
├── .gitignore
└── LICENSE
```

---

## Format ID Transaksi

```
Pemasukan  : TRX-YYDDMM-MMHH-XXX-YYY-ZZZ
Pengeluaran: TRXK-YYDDMM-MMHH-XXX-YYY-ZZZ
```

| Bagian | Keterangan |
|--------|------------|
| `YYDDMM` | Tahun-Tanggal-Bulan (sengaja dibalik — anti-fraud) |
| `MMHH` | Menit-Jam (sengaja dibalik — anti-fraud) |
| `XXX` | Counter harian (reset tiap hari) |
| `YYY` | Counter mingguan (reset tiap minggu) |
| `ZZZ` | Counter bulanan (reset tiap bulan) |

Ketiga counter **independen** satu sama lain.

---

## Cara Menjalankan

### WMS
```bash
cd src/WMS/v2
python wms_cli_v2_5.py
```

### POS
```bash
cd src/POS/v1
python pos_cli_v1.py
```

> Pastikan folder `database/` ada di `../../database/` relatif terhadap script, atau sesuaikan path di source code.

---

## Roadmap

```
WMS v2.5     ✅ Selesai
POS v1.0     ✅ Selesai
    │
    ├── POS v1.5   → Refactor: simpan_transaksi() universal, fix bug counter
    ├── POS v2.0   → Lookup harga dari DB_HARGA + time server Surabaya
    ├── POS v3.0   → Variasi wadah & ukuran minuman
    ├── POS v3.1   → Tracking konsinyasi (input)
    ├── POS v3.2   → Pembayaran & laporan konsinyasi
    │
    ├── POS+WMS v1 → Integrasi: stok auto berkurang saat transaksi POS
    │
    ├── ERP CLI    → Gabung semua: laporan keuangan, hutang/piutang, alert restock
    │
    └── Web ERP    → Flask/Django, akses owner vs kasir
```

---

## Changelog

### POS v1.0
- Pencatatan pemasukan multi-item
- Pencatatan pengeluaran dengan 5 kategori
- Format ID transaksi unik dengan encoding anti-fraud
- Counter harian/mingguan/bulanan independen
- Cek harga terlalu rendah (warning jika ≤ Rp100)
- Semua transaksi tersimpan di JSON

### WMS v2.5
- Refactoring kode — nama fungsi & variabel lebih deskriptif
- Main loop dibungkus dalam fungsi `main()`
- Fix bug logika di `barang_keluar()`
- Tambah guard `if __name__ == "__main__"`
- Tambah `os.system("clear")` untuk tampilan lebih bersih

### WMS v2.0
- Database JSON persisten
- Auto load/save database
- Penyimpanan inventori lokal

### WMS v1.0
- Sistem manajemen gudang CLI pertama
- Barang masuk / barang keluar
- Alert restock
- Sistem menu CLI

---

## Tentang Developer

**Thery Vissabillillah**
- Lulusan SMK Akuntansi, 5+ tahun pengalaman di gudang/logistik
- Membangun tools Python dari nol — dari HP via Termux
- Tujuan jangka panjang: ERP ringan untuk usaha kecil dan UMKM
