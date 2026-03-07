# Python WMS CLI

Mini Warehouse Management System (WMS) berbasis Command Line Interface (CLI) yang dibuat menggunakan Python.
Proyek ini merupakan latihan membangun sistem manajemen stok sederhana yang nantinya dapat berkembang menjadi POS atau ERP kecil.

Project ini dikembangkan langsung dari kebutuhan operasional warung nyata, sehingga fokus utamanya adalah:

- pencatatan stok
- pergerakan barang
- kontrol restock
- penyimpanan data lokal

---

## Features

### Current features:

- 📦 Inventory tracking
- ➕ Stock in (barang masuk)
- ➖ Stock out (barang keluar)
- ⚠ Restock alert system
- 💾 JSON database persistence
- 🖥 CLI menu interface
- 🛠 Input validation

---

## Tech Stack

- Python 3
- JSON (local database)
- Standard Python libraries

## Modules used:

json
os
datetime

---

Project Structure
`````
python-wms-cli/
│
├── notebooks/
├── src/
│   ├── v1/
│   │   └── wms_cli_v1.py
│   └── v2/
│       ├── wms_cli_v2.0.py
│       └── wms_cli_v2_5.py
├── database/
│   └── wms_db.json
├── README.md
├── .gitignore
├── LICENSE
└── screenshot.png
`````
---

## Database Structure

The system uses a JSON-based inventory database.

Example:

{
 "kopi": {
  "stok": 10,
  "min_stok": 3
 },
 "gula": {
  "stok": 5,
  "min_stok": 2
 }
}

This structure allows the system to scale later with additional fields such as:

- price
- category
- supplier
- barcode

---

## How to Run

Run the program from terminal:

python wms_cli_v1.py

python wms_cli_v2.py

Or using Termux:

python wms_cli_v1.py

python wms_cli_v2.py

---

## Future Roadmap

### Planned upgrades:

- Transaction logging
- POS CLI integration
- Daily sales reports
- Inventory analytics
- Web interface

---

Author

Created by Thery Vissabillillah

Background:

- SMK Accounting graduate
- Learning Python through real-world business problems
- Building small business management tools

---

## Project Goal

This project is part of a long-term goal to build a lightweight ERP system for small businesses and UMKM.

Starting from:
```
Inventory System
↓
POS System
↓
ERP CLI
↓
Web ERP
```

### Planned upgrades:

- [ ] Transaction logging dengan timestamp
- [ ] Owner / kasir access control
- [ ] POS CLI integration (v3.0)
- [ ] Daily sales reports
- [ ] Hutang / piutang tracking
- [ ] Inventory analytics
- [ ] ERP CLI
- [ ] Web ERP (Flask/Django)
---

## Changelog

### v1.0
- Initial CLI warehouse management system
- Stock in / stock out
- Restock alert
- CLI menu system

### v2.0
- JSON database persistence
- Auto load / save database
- Inventory stored locally

### v2.5
- Code refactoring
- Renamed functions to descriptive names
- Renamed variables to descriptive names
- Wrapped main loop into main() function
- Fixed logic bug in barang_keluar()
- Added if __name__ == "__main__" guard
- Added os.system("clear") for cleaner CLI display

### v3.0 (On Progress)
- POS CLI integration
- Transaction logging
- Daily sales summary

## Screenshot

Example CLI interface:

![WMS CLI Screenshot](screenshot.png)
