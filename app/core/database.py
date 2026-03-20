from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import text
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    # Enable pgvector extension in its own transaction so a failure doesn't
    # poison the subsequent create_all transaction.
    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    except Exception:
        # pgvector not installed on this server — semantic search disabled, rest of app works fine
        pass

    # Create tables in a clean, separate transaction
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
