import os
import duckdb
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Base declarative class for SQLAlchemy ORM models
Base = declarative_base()

# Use SQLite with aiosqlite for standalone local execution (no PostgreSQL required)
sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "lastmile.db")
db_url = f"sqlite+aiosqlite:///{sqlite_path}"

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False}
)

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
