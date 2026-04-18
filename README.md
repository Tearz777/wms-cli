# NotaCore — Lightweight ERP for Small Business

A lightweight **Warehouse Management System (WMS)**, **Point of Sale (POS)**, and **ERP Web App** built from real warung operational needs.

> 💡 Built and maintained entirely on a **mobile phone via Termux** — no laptop required.

---

## Projects

### 1. ERP PWA (Active — v1.0)

Full-stack web ERP with FastAPI backend + Vue 3 frontend, built as PWA.

### 2. CLI Tools (Legacy — Stable)

Python CLI tools for WMS and POS — the origin of this project.

---

## ERP PWA Features

### 🔐 Auth

* JWT-based login
* Role-based access: Admin, Owner, Kasir
* User management (add, activate/deactivate, delete)

### 📦 WMS

* Product & variant management
* Stock tracking per product & variant
* Stock movement history
* Smart parser — auto-restock from expense notes
* Import from Excel, JSON, CSV, SQLite

### 🛒 POS

* Sales input with product autocomplete
* Expense recording with categories
* Smart parser — "beli kopi racik x 5" auto-updates stock
* Transaction history & void with auto stock rollback
* Auto journal entry on every transaction

### 📒 Accounting

* Chart of Accounts (COA) — default + custom
* Auto journal from POS transactions
* Manual journal entry & closing entries
* Reports: Laba Rugi, Neraca

### 📥 Import

* Upload file → auto detect format
* Multi-sheet XLSX, multi-table SQLite support
* Auto header detection + dynamic column mapping
* Import target: Products, Transactions, Accounts

---

## ERP Tech Stack

| Layer       | Tech                          |
| ----------- | ----------------------------- |
| Backend     | FastAPI + SQLAlchemy + SQLite |
| Auth        | JWT (python-jose) + bcrypt    |
| Frontend    | Vue 3 + Vite + Bootstrap 5    |
| State       | Pinia                         |
| HTTP        | Axios                         |
| Environment | Termux (Android)              |

---

## ERP Quick Start

### Backend

```bash
cd erp/backend
pip install -r requirements.txt --break-system-packages
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd erp/frontend
npm install
npm run dev
```

### First Setup

1. Register admin: `POST /auth/register`
2. Init COA: `POST /accounting/init`
3. Import produk lewat menu Import di UI

API docs: `http://localhost:8000/docs`

---

## ERP Roadmap

```
ERP v1.0     🚧 Active
  ├── Auth (JWT + roles)            ✅
  ├── WMS (product + stock)         ✅
  ├── POS (transaction + void)      ✅
  ├── Accounting (journal + report) ✅
  ├── Import (multi-format)         ✅
  ├── User management               ✅
  └── PWA (offline support)         🔜

ERP v1.1     📋 Planned
  ├── Granular permission per user
  ├── Consignment tracking
  ├── Unit conversion (pack → satuan)
  └── Supplier management

ERP v2.0     📋 Planned
  ├── Cloud deployment
  └── Multi-branch support
```

---

## ERP Project Structure

```
erp/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── routers/
│   └── services/
└── frontend/
    └── src/
        ├── views/
        ├── stores/
        ├── router/
        └── utils/
```

---

## CLI Tools (Legacy)

> Dokumentasi tools CLI original sebelum NotaCore ERP PWA.

---

Sistem **Manajemen Gudang (WMS)** dan **Point of Sale (POS)** berbasis CLI yang dibangun sepenuhnya dengan Python.

Dikembangkan dari kebutuhan operasional warung nyata — fokus pada kesederhanaan, penyimpanan data lokal, dan tanpa dependensi eksternal.

> 💡 Dibangun dan dikelola dari **HP via Termux** — tanpa laptop.

---

## Fitur

### WMS (v2.6 — Stabil)
- 📦 Pencatatan stok
- ➕ Barang masuk
- ➖ Barang keluar
- ⚠️ Alert restock otomatis
- 💾 Database lokal berbasis JSON
- 🖥️ Antarmuka menu CLI
- 🛠️ Validasi input
- 📐 Tampilan adaptif sesuai lebar terminal

### POS (v1.8 — Stabil)
- 🧾 Pencatatan pemasukan dengan varian produk
- 💸 Pencatatan pengeluaran dengan kategori
- 🔢 Format ID transaksi unik (timestamp dibalik + suffix random — anti-fraud)
- 📊 Counter harian / mingguan / bulanan yang independen
- 📋 Laporan harian — transaksi, item terlaris, list pengeluaran, laba kotor
- 🕐 NTP time server dengan cache — timezone Surabaya
- 🔍 Detail penjualan — lookup berdasarkan tanggal, diurutkan per jam
- 📦 Rekap item per hari — termasuk breakdown varian
- 🔎 Lookup harga dari DB_HARGA dengan paginasi
- 📂 Universal menu engine — fungsi menu yang reusable
- 🎨 ASCII art header via pyfiglet + nama hari Indonesia
- 🛡️ Anti-corrupt database — recovery options + backup .bak otomatis
- 📥 Import Excel — mapping kolom dinamis
- ✍️ Input manual DB — dengan duplicate handling
- 💾 Database terpisah: DB_HARGA_WARUNG.json + DB_TRX_WARUNG.json
- 🛠️ Validasi input lengkap

---

## Tech Stack

- **Bahasa:** Python 3.13
- **Database:** JSON (flat-file lokal)
- **Dependensi:** `os`, `json`, `datetime`, `ntplib`, `pyfiglet`, `shutil`, `pandas`, `openpyxl`
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
│   │       ├── wms_cli_v2_5.py
│   │       └── wms_cli_v2_6.py          ← stabil
│   ├── POS/
│   │   └── v1/
│   │       ├── pos_cli_v1.py
│   │       ├── pos_cli_v1_5.py
│   │       ├── pos_cli_v1_6.py
│   │       ├── pos_cli_v1_7.py
│   │       └── pos_cli_1.8.py           ← stabil
│   └── POS+WMS/
│       ├── v1/
│       ├── v2/
│       └── v3/
│
├── database/
│   ├── WMS_DB.json
│   ├── DB_HARGA.json
│   ├── DB_HARGA_WARUNG.json
│   ├── DB_TRX.json
│   └── DB_TRX_WARUNG.json
│
├── README.md
├── .gitignore
└── LICENSE
```

---

## Format ID Transaksi

```
Pemasukan  : TRX-YYDDMM-MMHH-XXX-YYY-ZZZ-RRR
Pengeluaran: TRXK-YYDDMM-MMHH-XXX-YYY-ZZZ-RRR
```

| Bagian | Keterangan |
|--------|------------|
| `YYDDMM` | Tahun-Tanggal-Bulan (sengaja dibalik — anti-fraud) |
| `MMHH` | Menit-Jam (sengaja dibalik — anti-fraud) |
| `XXX` | Counter harian (reset tiap hari) |
| `YYY` | Counter mingguan (reset tiap minggu) |
| `ZZZ` | Counter bulanan (reset tiap tahun) |
| `RRR` | Suffix random 3 digit (anti-tebak) |

Ketiga counter **independen** satu sama lain.

Timestamp diambil dari NTP server (`id.pool.ntp.org`) dengan cache offset — sync sekali, pakai terus. Fallback ke clock lokal jika offline.

---

## Cara Menjalankan

### WMS
```bash
cd src/WMS/v2
python wms_cli_v2_6.py
```

### POS
```bash
cd src/POS/v1
python pos_cli_1.8.py
```

Install dependensi:
```bash
pip install ntplib pyfiglet pandas openpyxl --break-system-packages
```

> Pastikan folder `database/` ada di `../../database/` relatif terhadap script, atau sesuaikan path di source code.

---

## Roadmap

```
WMS v2.5     ✅ Selesai
WMS v2.6     ✅ Selesai
POS v1.7     ✅ Selesai
POS v1.8     ✅ Selesai
    │
    ├── POS v1.9   → Refactor & persiapan modularisasi
    │
    ├── WMS v2.7   → Inventory usability: search, laporan, status stok OK/LOW/OUT
    ├── WMS v2.8   → Inventory intelligence: log pergerakan stok, threshold alert
    ├── WMS v2.9   → Integration readiness: API-like functions untuk POS
    │
    ├── POS v2.0   → Full modularisasi (arsitektur multi-.py)
    ├── POS v2.x   → Pengembangan fitur di atas arsitektur modular
    ├── POS v2.9   → Integration readiness
    │
    └── POS+WMS v3.0 → Merge penuh: stok auto berkurang, restock alert, inventory log
         │
         ├── ERP CLI  → Laporan keuangan, hutang/piutang, COGS, profit
         └── Web ERP  → Flask/FastAPI, akses owner vs kasir
```

---

## Changelog

### POS v1.8
- Warung mode — struktur DB_HARGA baru: kategori → tipe → nama → varian → harga
- Varian produk — wadah/ukuran per item (gelas kopi, cangkir, gelas es, dll)
- Tipe produk — own vs konsinyasi
- Import Excel — mapping kolom dinamis, preview sebelum import
- Input manual DB — dengan duplicate handling dan opsi overwrite
- Anti-corrupt DB — recovery saat JSONDecodeError + backup .bak otomatis
- NTP cache — sync offset sekali, reuse untuk efisiensi
- Suffix random 3 digit pada ID transaksi (anti-tebak)
- Universal menu engine — fungsi `menu()` yang reusable
- Nama hari Indonesia di header (Senin-Minggu)
- Detail penjualan diurutkan berdasarkan waktu transaksi
- Rekap item include breakdown varian
- Laporan harian dengan input tanggal (Enter = hari ini)
- Tambah `pandas` + `openpyxl` ke dependensi
- DB terpisah: DB_HARGA_WARUNG.json + DB_TRX_WARUNG.json

### WMS v2.6
- Refactor global — gaya konsisten dengan POS v1.7
- Docstrings ditambahkan ke semua fungsi
- Fix bug `barang_keluar()` — stok limit kini hanya warning, tidak memblokir
- Tampilan adaptif sesuai lebar terminal via `shutil.get_terminal_size()`
- Pola `menu_map` untuk routing menu yang lebih bersih
- Tambah feedback `Press Enter...` saat input tidak valid

### POS v1.7
- Submenu Transaksi (Pemasukan/Pengeluaran) & Laporan (Daily/Detail/Recap) dipisah
- Lookup harga dari DB_HARGA — pencarian keyword dengan hasil paginasi (5 per halaman)
- ASCII art header via pyfiglet (font `mini`)
- `trx_id_call()` direfactor — digabung dengan parameter `jenis`
- Fix bug reset counter — kedua jenis counter kini reset dengan benar
- Helper functions diekstrak: `get_trx_harian()`, `hitung_total()`, `rekap_item()`, `item_terlaris()`, `list_pengeluaran()`
- Fungsi `header()` — reusable header laporan
- Pola `menu_map.get()` untuk routing menu yang lebih bersih
- Tambah `pyfiglet` dan `shutil` ke dependensi

### POS v1.6
- Integrasi NTP time server (`id.pool.ntp.org`) — timezone WIB (UTC+7)
- Fallback ke clock lokal jika NTP tidak tersedia + tampilkan warning
- Field `sumber_waktu` ditambahkan ke setiap transaksi (NTP / LOKAL)
- Detail penjualan — lookup berdasarkan tanggal dengan breakdown per transaksi
- Rekap item — semua item terjual per hari, diurutkan dari terbanyak

### POS v1.5
- Refactor: `save_trx()` universal menggantikan kode simpan yang panjang
- Fix bug counter reset
- Tambah `tahun_aktif` di struktur counter DB
- Laporan Harian: jumlah transaksi, item terlaris, list pengeluaran, laba kotor

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
