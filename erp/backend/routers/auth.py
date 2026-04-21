from dependencies import get_current_user, require_role
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.user import User
from schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse
from utils.security import hash_password, verify_password, create_access_token
from dependencies import get_current_user
from typing import List
import re

router = APIRouter(prefix="/auth", tags=["Auth"])

def validate_username(username: str) -> str:
    username = username.lower().strip()
    if len(username) < 3:
        raise ValueError("Username minimal 3 karakter")
    if not re.match(r'^[a-z0-9][a-z0-9._-]*[a-z0-9]$', username) and len(username) > 1:
        raise ValueError("Username tidak boleh diakhiri tanda baca")
    if not re.match(r'^[a-z0-9._-]+$', username):
        raise ValueError("Username hanya boleh huruf, angka, titik, strip, underscore")
    return username

@router.post("/register", response_model=UserResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        username = validate_username(data.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username sudah dipakai")

    user = User(
        username=username,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
        role=data.role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    username = data.username.lower().strip()
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun nonaktif"
        )

    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(
        access_token=token,
        role=user.role,
        full_name=user.full_name
    )

@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

# ── GET semua user (admin & owner) ───────────────
@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin", "owner", "Owner"))
):
    result = await db.execute(select(User))
    return result.scalars().all()

# ── DELETE user (admin only) ──────────────────────
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Tidak bisa hapus akun sendiri")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    await db.delete(user)
    await db.commit()
    return {"message": f"User '{user.username}' berhasil dihapus"}

# ── TOGGLE aktif/nonaktif user ────────────────────
@router.patch("/users/{user_id}/toggle")
async def toggle_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "Admin"))
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Tidak bisa nonaktifkan akun sendiri")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    user.is_active = not user.is_active
    await db.commit()
    return {"message": f"User '{user.username}' {'diaktifkan' if user.is_active else 'dinonaktifkan'}", "is_active": user.is_active}
