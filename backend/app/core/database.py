from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Handle sqlite async URL mapping
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite://"):
    db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(db_url, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Safe migration check for SQLite columns
        if "sqlite" in db_url:
            from sqlalchemy import text
            migrations = [
                "ALTER TABLE candidate_profile ADD COLUMN projects JSON DEFAULT '[]'",
                "ALTER TABLE contacts ADD COLUMN relationship VARCHAR(255)",
                "ALTER TABLE contacts ADD COLUMN company_verified BOOLEAN DEFAULT 1",
                "ALTER TABLE contacts ADD COLUMN role_verified BOOLEAN DEFAULT 1",
                "ALTER TABLE contacts ADD COLUMN verification_confidence FLOAT DEFAULT 0.9",
                "ALTER TABLE contacts ADD COLUMN last_verified_at DATETIME",
                "ALTER TABLE outreach_events ADD COLUMN channel VARCHAR(50) DEFAULT 'LinkedIn'",
                "ALTER TABLE outreach_events ADD COLUMN subject TEXT",
                "ALTER TABLE outreach_events ADD COLUMN message TEXT",
                "ALTER TABLE outreach_events ADD COLUMN sent_at DATETIME",
                "ALTER TABLE outreach_events ADD COLUMN status VARCHAR(50) DEFAULT 'sent'",
                "ALTER TABLE outreach_events ADD COLUMN response_at DATETIME",
                "ALTER TABLE outreach_events ADD COLUMN is_follow_up BOOLEAN DEFAULT 0",
                "ALTER TABLE outreach_events ADD COLUMN sequence_number INTEGER DEFAULT 1",
                "ALTER TABLE outreach_events ADD COLUMN follow_up_allowed BOOLEAN DEFAULT 1",
                "ALTER TABLE outreach_events ADD COLUMN follow_up_at DATETIME",
            ]
            for stmt in migrations:
                try:
                    await conn.execute(text(stmt))
                except Exception:
                    pass # Column already exists
