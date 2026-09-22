"""
Central application configuration.
Loads values from the .env file so no secrets are hard-coded.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "shaheen_school_erp"

    # JWT
    JWT_SECRET_KEY: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    APP_NAME: str = "Shaheen Model Girls High School ERP"
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000"

    # Frontend (used to build links inside emails, e.g. password reset)
    FRONTEND_BASE_URL: str = "http://localhost:8080/frontend"

    # Email / SMTP — leave SMTP_HOST empty to run in "dev mode": instead of
    # sending real email, the email content (including the reset link) is
    # logged to the console and written to backend/uploads/dev_emails/ so the
    # full password-reset flow is testable without real mail credentials.
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "no-reply@shaheenmodelschool.edu.pk"
    SMTP_FROM_NAME: str = "Shaheen Model Girls High School"
    SMTP_USE_TLS: bool = True

    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_PROFILE_PHOTO_MB: int = 2
    MAX_HOMEWORK_ATTACHMENT_MB: int = 10

    @property
    def DATABASE_URL(self) -> str:
     password = quote_plus(self.DB_PASSWORD)

     return (
        f"mysql+pymysql://{self.DB_USER}:{password}"
        f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
     )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
