import re
import random
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.setting import Setting

WIB = timezone(timedelta(hours=7))

PLACEHOLDERS = {
    "{YY}": lambda now: now.strftime("%y"),
    "{YYYY}": lambda now: now.strftime("%Y"),
    "{MM}": lambda now: now.strftime("%m"),
    "{DD}": lambda now: now.strftime("%d"),
    "{HH}": lambda now: now.strftime("%H"),
    "{MIN}": lambda now: now.strftime("%M"),
    "{RANDOM}": lambda now: str(random.randint(100, 999)),
}

async def get_setting(db: AsyncSession, key: str, default: str = "") -> str | None:
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    return setting.value if setting else None

async def set_setting(db: AsyncSession, key: str, value: str):
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.add(setting)
    await db.flush()

async def get_counter(db: AsyncSession, period: str) -> int:
    """Get counter value untuk periode tertentu (daily/weekly/monthly)."""
    now = datetime.now(WIB)

    period_map = {
        "daily": now.strftime("%Y-%m-%d"),
        "weekly": now.strftime("%Y-W%W"),
        "monthly": now.strftime("%Y-%m"),
    }

    period_key = f"counter_{period}_period"
    counter_key = f"counter_{period}_value"

    current_period = period_map[period]
    saved_period = await get_setting(db, period_key)

    if saved_period != current_period:
        # Reset counter
        await set_setting(db, period_key, current_period)
        await set_setting(db, counter_key, "1")
        return 1
    else:
        saved_value = await get_setting(db, counter_key)
        new_value = (int(saved_value) + 1) if saved_value else 1
        await set_setting(db, counter_key, str(new_value))
        return new_value

async def generate_invoice_number(
    db: AsyncSession,
    trx_type: str
) -> str | None:
    """Generate nomor faktur dari format yang disimpan di settings."""
    
    format_key = f"invoice_format_{trx_type}"
    fmt = await get_setting(db, format_key)

    if not fmt:
        return None  # Format belum diset → POS nonaktif

    now = datetime.now(WIB)

    # Replace static placeholders
    result = fmt
    for placeholder, fn in PLACEHOLDERS.items():
        result = result.replace(placeholder, fn(now))

    # Replace counter placeholders
    if "{DAILY}" in result:
        daily = await get_counter(db, "daily")
        result = result.replace("{DAILY}", f"{daily:03d}")

    if "{WEEKLY}" in result:
        weekly = await get_counter(db, "weekly")
        result = result.replace("{WEEKLY}", f"{weekly:03d}")

    if "{MONTHLY}" in result:
        monthly = await get_counter(db, "monthly")
        result = result.replace("{MONTHLY}", f"{monthly:03d}")

    # Replace business name
    business_name = await get_setting(db, "business_name")
    if business_name and "{NAMA_USAHA}" in result:
        clean = re.sub(r'\s+', '', business_name).upper()[:6]
        result = result.replace("{NAMA_USAHA}", clean)

    return result
