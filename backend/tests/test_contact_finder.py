import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.core.database import Base
from app.models.models import Job, Contact, SearchCache
from app.schemas.schemas import JobIngestRequest
from app.services.ingestion import IngestionService
from app.services.contact_finder import (
    build_search_queries,
    filter_candidates_python,
    ContactFinderService
)

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

def test_query_generation_bounds():
    queries = build_search_queries("Notion", "AI Engineer", "AI Platform", "Machine Learning")
    assert 3 <= len(queries) <= 5
    assert '"Notion" "AI Engineer" hiring manager' in queries
    assert '"Notion" "AI Engineer" recruiter' in queries
    assert '"Notion" "AI Platform" engineering manager' in queries
    assert '"Notion" "Machine Learning" engineer' in queries

def test_python_deterministic_filtering():
    raw_candidates = [
        {
            "name": "Sarah Chen",
            "company": "Notion",
            "title": "Engineering Manager - AI Team",
            "linkedin_url": "https://linkedin.com/in/sarahchen"
        },
        {
            "name": "John Smith",
            "company": "Notion",
            "title": "Senior ML Engineer",
            "linkedin_url": "https://linkedin.com/in/johnsmith"
        },
        {
            "name": "Mike Recruiter",
            "company": "Notion",
            "title": "Technical Recruiter",
            "linkedin_url": "https://linkedin.com/in/mikerecruiter"
        },
        {
            "name": "Ex Employee",
            "company": "Notion",
            "title": "Ex-Engineering Manager at Notion",
            "linkedin_url": "https://linkedin.com/in/exemployee"
        },
        {
            "name": "David Exec",
            "company": "Notion",
            "title": "Chief Financial Officer",
            "linkedin_url": "https://linkedin.com/in/davidcfo"
        },
        {
            "name": "Sarah Chen", # Duplicate
            "company": "Notion",
            "title": "Engineering Manager",
            "linkedin_url": "https://linkedin.com/in/sarahchen"
        }
    ]

    filtered = filter_candidates_python(raw_candidates, "AI Engineer", "Notion")

    # Should keep Sarah, John, Mike (3 candidates)
    # Should remove Ex Employee (ex-), David Exec (CFO), and Sarah duplicate
    names = [c["name"] for c in filtered]
    assert "Sarah Chen" in names
    assert "John Smith" in names
    assert "Mike Recruiter" in names
    assert "Ex Employee" not in names
    assert "David Exec" not in names
    assert len(filtered) == 3

@pytest.mark.asyncio
async def test_search_cache_creation_and_hit(async_db: AsyncSession):
    req = JobIngestRequest(company="Stripe", title="Infrastructure Engineer", location="Remote", job_description="Go and distributed systems")
    job, _ = await IngestionService.process_job_ingest(async_db, req)

    # 1st call: Misses cache, computes and stores in SearchCache
    contacts1 = await ContactFinderService.find_and_rank_contacts(async_db, job.id)
    assert len(contacts1) > 0

    cache_res = await async_db.execute(select(SearchCache).where(SearchCache.company == "Stripe"))
    cache_entry = cache_res.scalar_one_or_none()
    assert cache_entry is not None
    assert cache_entry.cache_key == "stripe|infrastructure engineer|v8"
    assert cache_entry.query_count == 4

    # 2nd call: Uses SearchCache
    contacts2 = await ContactFinderService.find_and_rank_contacts(async_db, job.id)
    assert len(contacts2) == len(contacts1)
    assert {c.name for c in contacts2} == {c.name for c in contacts1}
