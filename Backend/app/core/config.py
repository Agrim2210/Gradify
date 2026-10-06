from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Gradify"
    APP_ENV: str = "development"
    DB_URL: str = ""
    DATABASE_URL: str | None = None
    DB_NAME: str = "gradify_db"
    PORT: int = 8000
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_OUTBOX_POLL_SECONDS: int = 5
    CELERY_OUTBOX_BATCH_SIZE: int = 100
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_SENDER_EMAIL: str | None = None
    FRONTEND_URL: str = "http://localhost:5173"
    B2_ENDPOINT_URL: str = ""
    B2_APPLICATION_KEY_ID: str = ""
    B2_APPLICATION_KEY: str = ""
    B2_BUCKET_NAME: str = ""
    B2_REGION_NAME: str = "us-west-004"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @model_validator(mode="after")
    def assemble_db_url(self) -> "Settings":
        url = self.DB_URL or self.DATABASE_URL or ""
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        self.DB_URL = url
        return self


settings = Settings()
