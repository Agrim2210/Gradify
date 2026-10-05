from sqlalchemy.ext.asyncio import (create_async_engine,
async_sessionmaker,AsyncSession)
from app.core.config import settings
engine=create_async_engine(
    url=settings.DB_URL,
    echo=True,
    pool_size=20,
    max_overflow=30
)
SessionLocal=async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
