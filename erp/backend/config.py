from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "NotaCore"
    SECRET_KEY: str = "ganti-ini-nanti"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 jam
    DATABASE_URL: str = "sqlite+aiosqlite:///./erp.db"
    TIMEZONE: str = "Asia/Makassar"  # WIB = UTC+7, Surabaya

    class Config:
        env_file = ".env"

settings = Settings()
