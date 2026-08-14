import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.models.models import Startup, StartupContact, CandidateProfile
from app.services.startup_service import StartupService

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        # Seed candidate profile
        profile = CandidateProfile(
            name="Sam",
            skills={"Python": 9, "FastAPI": 8, "React": 8},
            target_roles=["AI Engineer", "Software Engineer"],
            projects=[{"title": "DunderHunt Engine", "description": "Decision support AI system using FastAPI and React"}]
        )
        session.add(profile)
        await session.commit()
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_startup_enrichment(async_db: AsyncSession):
    enrichment = await StartupService.enrich_startup(async_db, "modal.com")
    assert enrichment.name is not None
    assert enrichment.domain == "modal.com"
    assert enrichment.company_size in ["1-15", "15-50", "50-200", "200+"]
    assert enrichment.funding_stage in ["Seed", "Series A", "Series B", "Bootstrapped", "Late Stage"]
    assert len(enrichment.tech_stack) > 0

@pytest.mark.asyncio
async def test_startup_contact_discovery(async_db: AsyncSession):
    startup = Startup(
        name="Modal",
        domain="modal.com",
        company_size="15-50",
        funding_stage="Series A",
        summary="Serverless Python infrastructure for AI/ML",
        tech_stack=["Python", "Rust", "Cloud"]
    )
    async_db.add(startup)
    await async_db.commit()
    await async_db.refresh(startup)

    contacts = await StartupService.discover_startup_contacts(async_db, startup)
    assert len(contacts) > 0
    c1 = contacts[0]
    assert c1.name is not None
    assert c1.title is not None # Designation
    assert c1.persona_type in ["FOUNDER", "ENG_LEAD", "RECRUITER", "PEER"]

@pytest.mark.asyncio
async def test_startup_pitch_generation(async_db: AsyncSession):
    startup = Startup(
        name="Modal",
        domain="modal.com",
        company_size="1-15",
        funding_stage="Seed",
        summary="Serverless Python cloud infrastructure",
        tech_stack=["Python", "FastAPI", "Docker"]
    )
    async_db.add(startup)
    await async_db.commit()
    await async_db.refresh(startup)

    contact = StartupContact(
        startup_id=startup.id,
        name="Erik Bernhardsson",
        title="Co-Founder & CEO",
        persona_type="FOUNDER",
        linkedin_url="https://linkedin.com/in/erikbern",
        activity_score=95
    )
    async_db.add(contact)
    await async_db.commit()
    await async_db.refresh(contact)

    pitch = await StartupService.generate_pitch(async_db, contact, channel="Email", purpose="Introduce myself")
    assert pitch.contact_id == contact.id
    assert pitch.contact_name == "Erik Bernhardsson"
    assert pitch.contact_title == "Co-Founder & CEO"
    assert pitch.draft_message is not None
    assert len(pitch.draft_message) > 10
