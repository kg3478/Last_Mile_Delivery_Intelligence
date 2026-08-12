import os
import duckdb
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Base declarative class for SQLAlchemy ORM models
Base = declarative_base()

# Use DATABASE_URL when configured; otherwise fall back to local SQLite.
sqlite_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "lastmile.db"
)
sqlite_fallback_url = f"sqlite+aiosqlite:///{sqlite_path}"

db_url = settings.DATABASE_URL or sqlite_fallback_url

engine_kwargs = {
    "echo": False,
    "future": True,
}

# SQLite requires check_same_thread=False for async local development.
if db_url.startswith("sqlite+aiosqlite://"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    """Dependency for obtaining an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_duckdb_connection():
    """Returns a DuckDB connection for high-performance analytical queries."""
    duckdb_path = os.path.join(settings.DATA_DIR, "analytics.duckdb")
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    return duckdb.connect(duckdb_path)

async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
