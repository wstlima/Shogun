"""Database engine and async session management for Gensui.

Completely independent from Shogun's database — uses its own gensui.db.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from gensui.config import gensui_settings

# ── Detect backend ────────────────────────────────────────────
_is_sqlite = gensui_settings.gensui_database_url.startswith("sqlite")

# ── Engine ────────────────────────────────────────────────────
if _is_sqlite:
    engine = create_async_engine(
        gensui_settings.gensui_database_url,
        echo=gensui_settings.debug,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    engine = create_async_engine(
        gensui_settings.gensui_database_url,
        echo=gensui_settings.debug,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

# ── Session Factory ───────────────────────────────────────────
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
