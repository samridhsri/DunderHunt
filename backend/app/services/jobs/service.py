from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Job, Application

class JobService:
    @staticmethod
    async def get_job(db: AsyncSession, job_id: int) -> Optional[Job]:
        res = await db.execute(select(Job).where(Job.id == job_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def update_outreach_status(db: AsyncSession, job_id: int, enabled: bool, status_str: str) -> None:
        res = await db.execute(select(Application).where(Application.job_id == job_id))
        app_rec = res.scalar_one_or_none()
        if not app_rec:
            app_rec = Application(job_id=job_id, outreach_enabled=enabled, outreach_status=status_str)
            db.add(app_rec)
        else:
            app_rec.outreach_enabled = enabled
            app_rec.outreach_status = status_str
        await db.commit()
