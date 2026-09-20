import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gift Shop Admin & E-Commerce API"
    SECRET_KEY: str  # Must be passed via environment variables in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    DATABASE_URL: str  # Example: postgresql://user:password@host:5432/dbname
    UPLOAD_DIR: str = "app/uploads"

    class Config:
        env_file = ".env"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)