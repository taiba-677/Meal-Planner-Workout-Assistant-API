from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
import json

from app.core.config import settings

# ── Async Engine ────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.database_url,
    echo=False,          # Set True to log SQL queries during development
    pool_pre_ping=True,  # Verify connections before use (handles stale conns)
    pool_size=10,
    max_overflow=20,
    json_serializer=lambda obj: json.dumps(obj, indent=4),
)

# ── Session Factory ─────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Objects remain accessible after commit
)


# ── Base for ORM Models ─────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── FastAPI Dependency ───────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    """
    Yields an async DB session per request.
    Automatically closes the session when the request is done.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
