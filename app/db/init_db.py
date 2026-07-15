"""
init_db.py
──────────
Creates all tables on app startup (idempotent — safe to run every time).
Uses checkfirst=True so existing tables are not dropped or modified.
"""

from app.db.database import Base, engine

# Import models so SQLAlchemy registers them with Base.metadata
import app.db.models  # noqa: F401


async def init_db() -> None:
    """Create all tables if they don't already exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
