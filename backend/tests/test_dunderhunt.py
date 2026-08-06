import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.models.models import CandidateProfile, Job
from app.schemas.schemas import JobIngestRequest
from app.services.ingestion import IngestionService, generate_canonical_fingerprint
from app.services.fit_engine import FitEngineService

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

@pytest.mark.asyncio
async def test_canonical_fingerprint():
    fp1 = generate_canonical_fingerprint("Notion", "Software Engineer", "New York, NY")
    fp2 = generate_canonical_fingerprint("notion", "SOFTWARE ENGINEER", "new york, ny")
    assert fp1 == fp2

@pytest.mark.asyncio
async def test_job_ingestion_and_deduplication(async_db: AsyncSession):
    req1 = JobIngestRequest(company="Notion", title="Software Engineer", location="New York", job_description="Python ML position")
    job1, is_new1 = await IngestionService.process_job_ingest(async_db, req1)
    assert is_new1 is True
    assert job1.company == "Notion"

    # Ingest duplicate
    req2 = JobIngestRequest(company="notion", title="software engineer", location="new york", job_description="Duplicate job")
    job2, is_new2 = await IngestionService.process_job_ingest(async_db, req2)
    assert is_new2 is False
    assert job1.id == job2.id

@pytest.mark.asyncio
async def test_fit_engine_evaluation(async_db: AsyncSession):
    req = JobIngestRequest(company="Notion", title="Software Engineer, New Grad", location="New York, NY", job_description="Python, Machine Learning, Deep Learning position for new grad")
    job, _ = await IngestionService.process_job_ingest(async_db, req)
    
    analysis = await FitEngineService.evaluate_job_fit(async_db, job.id)
    assert analysis.overall_score >= 70
    assert job.priority in ["A", "B", "C"]
    assert job.recommendation in ["APPLY", "SAVE"]
