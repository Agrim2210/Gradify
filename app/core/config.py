from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_ENV: str
    DB_URL: str
    DB_NAME: str
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


settings = Settings()
