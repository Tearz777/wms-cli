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

### POS (v1.7 — Stable)
- 🧾 Income recording (Pemasukan)
- 💸 Expense recording (Pengeluaran) with categories
- 🔢 Unique transaction ID system (anti-fraud timestamp encoding)
- 📊 Independent daily / weekly / monthly counters
- 📋 Daily report — transactions, top item, expense list, gross profit
- 🕐 NTP time server — Surabaya timezone (anti-fraud timestamp)
- 🔍 Sales detail lookup by date
- 📦 Item recap per day — sorted by quantity
- 🔎 Price lookup from DB_HARGA with paginated search
- 📂 Submenu — Transaksi & Laporan separated
- 🎨 ASCII art header via pyfiglet
- 💾 JSON-based transaction database
- 🛠️ Input validation with price sanity check
- ♻️ Universal save function `save_trx()`

---

## Tech Stack

- **Language:** Python 3.12
- **Database:** JSON (local flat-file)
- **Dependencies:** `os`, `json`, `datetime`, `ntplib`, `pyfiglet`, `shutil`
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
│   │       ├── pos_cli_v1.py
│   │       ├── pos_cli_v1_5.py
│   │       ├── pos_cli_v1_6.py
│   │       └── pos_cli_v1_7.py          ← stable
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

### DB_HARGA.json
```json
{
  "produk": {
    "kategori": {
      "nama barang": { "harga": 0, "satuan": "pcs" }
    }
  }
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
| `YYY` | Weekly counter (resets every month) |
| `ZZZ` | Monthly counter (resets every year) |

All three counters are **independent** of each other.

Timestamps are sourced from NTP server (`id.pool.ntp.org`) with fallback to local clock if offline. Each transaction records `sumber_waktu: "NTP"` or `"LOKAL"` for audit purposes.

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
python pos_cli_v1_7.py
```

> Make sure the `database/` folder exists at `../../database/` relative to the script, or adjust the path in the source file.

Install dependencies:
```bash
pip install ntplib pyfiglet --break-system-packages
```

---

## Roadmap

```
WMS v2.5     ✅ Stable
POS v1.0     ✅ Stable
POS v1.5     ✅ Stable
POS v1.6     ✅ Stable
POS v1.7     ✅ Stable
    │
    ├── POS v1.8   → Beverage variants + consignment tracking & payment
    │
    ├── POS+WMS v2.0 → Integration: stock auto-deduct on sale, modular architecture
    │
    ├── ERP CLI    → Combined: financial reports, hutang/piutang, restock alerts
    │
    └── Web ERP    → Flask/Django, owner vs kasir access control
```

### Detailed Backlog
- [x] `simpan_transaksi()` universal function (v1.5)
- [x] Separate counters for pemasukan & pengeluaran (v1.5 bugfix)
- [x] Daily sales report / Laporan Harian (v1.5)
- [x] NTP time server — Surabaya timezone (v1.6)
- [x] Sales detail lookup by date (v1.6)
- [x] Item recap per day (v1.6)
- [x] Submenu Transaksi & Laporan (v1.7)
- [x] Price lookup from DB_HARGA with pagination (v1.7)
- [x] ASCII art header — pyfiglet (v1.7)
- [x] Counter reset bug fix — both jenis reset on date change (v1.7)
- [x] Code refactor — helper functions, DRY architecture (v1.7)
- [ ] Beverage variants + consignment tracking & payment (v1.8)
- [ ] WMS auto stock deduction on POS sale (POS+WMS v2.0)
- [ ] Modular architecture — split into multiple .py files (v2.0)
- [ ] Owner vs kasir role access (Web ERP)

---

## Changelog

### POS v1.7
- Submenu Transaksi (Pemasukan/Pengeluaran) & Laporan (Daily/Detail/Recap) separated
- Price lookup from DB_HARGA — keyword search with paginated results (5 per page)
- ASCII art header via pyfiglet (`mini` font)
- `trx_id_call()` refactored — merged pemasukan & pengeluaran into single function with `jenis` param
- Counter reset bug fix — both pemasukan & pengeluaran counters now reset correctly on date change
- Helper functions extracted: `get_trx_harian()`, `hitung_total()`, `rekap_item()`, `item_terlaris()`, `list_pengeluaran()`
- `header()` utility function — reusable report header
- `menu_map.get()` pattern for cleaner menu routing
- Added `pyfiglet` and `shutil` to dependencies

### POS v1.6
- NTP time server integration (`id.pool.ntp.org`) — Surabaya timezone (WIB UTC+7)
- Fallback to local clock if NTP unavailable + warning display
- `sumber_waktu` field added to every transaction (NTP / LOKAL)
- Sales detail — lookup penjualan by date with per-transaction breakdown
- Item recap — all items sold per day, sorted by quantity

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

### POS (v1.7 — Stabil)
- 🧾 Pencatatan pemasukan (multi-item)
- 💸 Pencatatan pengeluaran dengan kategori
- 🔢 Format ID transaksi unik (timestamp dibalik — anti-fraud)
- 📊 Counter harian / mingguan / bulanan yang independen
- 📋 Laporan harian — transaksi, item terlaris, list pengeluaran, laba kotor
- 🕐 NTP time server — timezone Surabaya (anti-fraud timestamp)
- 🔍 Detail penjualan — lookup berdasarkan tanggal
- 📦 Rekap item per hari — diurutkan dari terbanyak
- 🔎 Lookup harga dari DB_HARGA dengan pencarian paginasi
- 📂 Submenu — Transaksi & Laporan dipisah
- 🎨 ASCII art header via pyfiglet
- 💾 Database transaksi berbasis JSON
- 🛠️ Validasi input + cek harga terlalu rendah
- ♻️ Fungsi simpan universal `save_trx()`

---

## Tech Stack

- **Bahasa:** Python 3.12
- **Database:** JSON (flat-file lokal)
- **Dependensi:** `os`, `json`, `datetime`, `ntplib`, `pyfiglet`, `shutil`
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
│   │       ├── pos_cli_v1.py
│   │       ├── pos_cli_v1_5.py
│   │       ├── pos_cli_v1_6.py
│   │       └── pos_cli_v1_7.py          ← stabil
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
| `YYY` | Counter mingguan (reset tiap ganti bulan) |
| `ZZZ` | Counter bulanan (reset tiap ganti tahun) |

Ketiga counter **independen** satu sama lain.

Timestamp diambil dari NTP server (`id.pool.ntp.org`) dengan fallback ke clock lokal jika offline. Setiap transaksi menyimpan field `sumber_waktu: "NTP"` atau `"LOKAL"` untuk keperluan audit.

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
python pos_cli_v1_7.py
```

Install dependensi:
```bash
pip install ntplib pyfiglet --break-system-packages
```

> Pastikan folder `database/` ada di `../../database/` relatif terhadap script, atau sesuaikan path di source code.

---

## Roadmap

```
WMS v2.5     ✅ Selesai
POS v1.0     ✅ Selesai
POS v1.5     ✅ Selesai
POS v1.6     ✅ Selesai
POS v1.7     ✅ Selesai
    │
    ├── POS v1.8   → Variasi wadah minuman + tracking & pembayaran konsinyasi
    │
    ├── POS+WMS v2.0 → Integrasi WMS, stok auto berkurang, arsitektur modular
    │
    ├── ERP CLI    → Gabung semua: laporan keuangan, hutang/piutang, alert restock
    │
    └── Web ERP    → Flask/Django, akses owner vs kasir
```

---

## Changelog

### POS v1.7
- Submenu Transaksi (Pemasukan/Pengeluaran) & Laporan (Daily/Detail/Recap) dipisah
- Lookup harga dari DB_HARGA — pencarian keyword dengan hasil paginasi (5 per halaman)
- ASCII art header via pyfiglet (font `mini`)
- `trx_id_call()` direfactor — pemasukan & pengeluaran digabung dengan parameter `jenis`
- Fix bug reset counter — kedua jenis counter kini reset dengan benar saat ganti hari/bulan/tahun
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
- Fix bug counter reset: mingguan reset tiap ganti bulan, bulanan reset tiap ganti tahun
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
