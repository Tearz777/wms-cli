# NotaCore — ERP for Real Small Business Operations

NotaCore is a lightweight ERP system designed for **real warung operations** — managing stock, sales, and financial records in one integrated workflow.

> Built from hands-on experience, not assumptions.  
> 💡 Developed and maintained entirely on a **mobile phone via Termux** — no laptop.

---

## 🔄 How It Works

1. Add products and stock in WMS  
2. Record sales or expenses in POS  
3. Stock updates automatically on every transaction  
4. Financial journals are generated in real-time  
5. Reports (Profit & Loss, Balance Sheet) stay up-to-date  

---

## ⭐ Key Features

- **Integrated WMS + POS + Accounting** in one system  
- **Automatic journal entries** from every transaction  
- **Smart input parser** (natural input → structured data)  
- **Multi-format import** (Excel, CSV, JSON, SQLite)  
- **Optimized for low-end devices** (built with real constraints)  

---

## 🧱 Project Evolution

### ERP PWA (Active — v1.0)

Full-stack web ERP built with FastAPI and Vue 3, delivered as a Progressive Web App.

**This is the main product.**

---

### CLI Tools (Legacy — Stable)

The original foundation of NotaCore.

A Python-based WMS and POS running entirely in terminal, designed for simplicity and local-first operation.

Built from real warung needs, before evolving into a web-based ERP.

---

## ⚙️ Tech Stack

| Layer       | Tech                          |
|------------|-------------------------------|
| Backend     | FastAPI + SQLAlchemy + SQLite |
| Auth        | JWT (python-jose) + bcrypt    |
| Frontend    | Vue 3 + Vite + Bootstrap 5    |
| State       | Pinia                         |
| HTTP        | Axios                         |
| Environment | Termux (Android)              |

---

## 🚀 Quick Start

### Backend

```bash
cd erp/backend
pip install -r requirements.txt --break-system-packages
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```
cd erp/frontend
npm install
npm run dev
```
---

### First Setup

1. Register admin → POST /auth/register
2. Initialize COA → POST /accounting/init
3. Import products via UI

API docs: http://localhost:8000/docs
---

## 🗺️ Roadmap

```
ERP v1.0     🚧 Active
  ├── Core modules (WMS, POS, Accounting) ✅
  ├── Import system                      ✅
  ├── User management                   ✅
  └── PWA offline support               🔜

ERP v1.1     📋 Planned
  ├── Granular permissions
  ├── Consignment tracking
  ├── Unit conversion
  └── Supplier management

ERP v2.0     📋 Planned
  ├── Cloud deployment
  └── Multi-branch support
```

## 👤 About the Developer

### Thery Vissabillillah

* Background in accounting with 5+ years in warehouse & logistics
* Builds systems from real operational problems, not theory
* Develops entirely via Termux on Android — no traditional dev setup
>Dari warung, untuk warung.
>Built from the ground up, one problem at a time.

===

## 📦 Legacy CLI (Optional Reference)
* The CLI version represents the early stage of NotaCore:
* Local JSON-based database
* Terminal-based interface
* Strong focus on data integrity and simplicity
* It serves as the architectural foundation for the ERP system today.
