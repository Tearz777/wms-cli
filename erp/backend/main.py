from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from config import Settings
from routers import auth, wms, pos, accounting, importer
from routers import settings as settings_router
from routers import customer as customers_router

# PENTING: Impor semua models agar SQLAlchemy 'aware' terhadap semua tabel
import models.user
import models.product
import models.transaction
import models.account
import models.setting
import models.suppliers
import models.customer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Membuat tabel jika belum ada
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="NotaCore ERP API", lifespan=lifespan)

# CORS - Sesuaikan dengan IP Termux Anda jika perlu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(wms.router)
app.include_router(pos.router)
app.include_router(accounting.router)
app.include_router(importer.router)
app.include_router(settings_router.router)
app.include_router(settings_router.router)
app.include_router(customers_router.router)

@app.get("/")
async def root():
    return {"message": "NotaCore ERP API is running"}
