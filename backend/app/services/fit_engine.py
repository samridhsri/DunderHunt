from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Job, JobAnalysis, CandidateProfile
from app.prompts.prompts import (
    JobFitOutput,
    JOB_FIT_SYSTEM_INSTRUCTION,
    JOB_FIT_PROMPT_TEMPLATE
)
from app.core.llm import LLMProvider

class FitEngineService:
    @staticmethod
    async def evaluate_job_fit(db: AsyncSession, job_id: int) -> JobAnalysis:
        # Fetch job
        job_result = await db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        if not job:
            raise ValueError(f"Job with id {job_id} not found")

        # Fetch candidate profile (or create default if missing)
        profile_result = await db.execute(select(CandidateProfile).limit(1))
        profile = profile_result.scalar_one_or_none()
        
        if not profile:
            profile = CandidateProfile(
                name="Sam",
                skills={"Python": 8, "Machine Learning": 8, "Deep Learning": 7, "Backend": 6},
                target_roles=["Software Engineer", "AI Engineer", "ML Engineer"],
                target_locations=["New York, NY", "Remote"],
                work_authorization={"status": "US Citizen / Authorized"},
                excluded_companies=[]
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)

        # --- LAYER 1: Deterministic Filtering Rules ---
        desc_lower = job.description.lower()
        company_lower = job.company.lower()
        
        # Rule A: Excluded companies
        if any(exc.lower() in company_lower for exc in profile.excluded_companies if exc):
            analysis = JobAnalysis(
                job_id=job.id,
                technical_fit=0,
                experience_fit=0,
                education_fit=0,
                location_fit=0,
                authorization_fit=0,
                career_alignment=0,
                overall_score=0,
                strengths=[],
                concerns=["Company is explicitly listed in excluded companies list."],
                skill_gaps=[],
                resume_changes_needed=[],
                reasoning_summary="Instant SKIP due to excluded company match.",
                model_name="deterministic_rule",
                prompt_version="job_fit_v1"
            )
            job.fit_score = 0
            job.priority = "Skip"
            job.recommendation = "SKIP"
            job.status = "Saved"
            job.next_action = "Skip application"
            
            # Save or update existing analysis
            existing_ans = await db.execute(select(JobAnalysis).where(JobAnalysis.job_id == job.id))
            ans_rec = existing_ans.scalar_one_or_none()
            if ans_rec:
                await db.delete(ans_rec)
            db.add(analysis)
            await db.commit()
            await db.refresh(analysis)
            return analysis

        # Rule B: Strict Security Clearance / Citizenship violation if profile explicitly restricts it
        work_auth_status = str(profile.work_authorization.get("status", "")).lower()
        is_clearance_required = any(term in desc_lower for term in ["top secret", "ts/sci clearance", "us citizenship required"])
        if is_clearance_required and "citizen" not in work_auth_status:
            # Major penalty or skip
            auth_fit_override = 20
        else:
            auth_fit_override = 100

        # --- LAYER 2: AI Fit Evaluation ---
        # Format Work Experience
        exp_lines = []
        for exp in (profile.experience or []):
            role = exp.get("role", "Role")
            company = exp.get("company", "Company")
            dates = f"{exp.get('start_date', '')} - {exp.get('end_date', '')}"
            desc = exp.get("description", "")
            techs = ", ".join(exp.get("technologies", []))
            exp_lines.append(f"- {role} at {company} ({dates}): {desc} [Tech: {techs}]")
        exp_str = "\n".join(exp_lines) if exp_lines else "None specified"

        # Format Projects
        proj_lines = []
        for proj in (profile.projects or []):
            title = proj.get("title", "Project")
            role = proj.get("role", "")
            desc = proj.get("description", "")
            techs = ", ".join(proj.get("technologies", []))
            highlights = "; ".join(proj.get("highlights", []))
            proj_lines.append(f"- {title} ({role}): {desc} [Tech: {techs}] [Highlights: {highlights}]")
        proj_str = "\n".join(proj_lines) if proj_lines else "None specified"

        prompt = JOB_FIT_PROMPT_TEMPLATE.format(
            candidate_name=profile.name,
            target_roles=", ".join(profile.target_roles),
            target_locations=", ".join(profile.target_locations),
            skills=str(profile.skills),
            work_authorization=str(profile.work_authorization),
            excluded_companies=", ".join(profile.excluded_companies),
            work_experience=exp_str,
            projects=proj_str,
            company=job.company,
            title=job.title,
            location=job.location or "Remote",
            description=job.description[:4000]
        )

        ai_result: JobFitOutput = await LLMProvider.generate_structured(
            prompt=prompt,
            response_schema=JobFitOutput,
            model_name="gemini-2.5-flash",
            system_instruction=JOB_FIT_SYSTEM_INSTRUCTION
        )

        # Apply Layer 1 authorization override if applicable
        final_auth_fit = min(ai_result.authorization_fit, auth_fit_override)
        
        # Calculate Weighted Score according to formula
        # 30% Tech, 20% Role, 15% Exp, 15% Auth, 10% Loc, 5% Career, 5% Effort (assumed 85)
        computed_overall = int(
            (ai_result.technical_fit * 0.30) +
            (ai_result.career_alignment * 0.20) +
            (ai_result.experience_fit * 0.15) +
            (final_auth_fit * 0.15) +
            (ai_result.location_fit * 0.10) +
            (ai_result.education_fit * 0.05) +
            (85 * 0.05)
        )
        
        computed_overall = max(0, min(100, computed_overall))

        # Assign Priority and Recommendation
        if computed_overall >= 90:
            priority = "A"
            recommendation = "APPLY"
            next_action = "Apply to job posting"
        elif computed_overall >= 80:
            priority = "B"
            recommendation = "APPLY"
            next_action = "Review job detail & apply"
        elif computed_overall >= 70:
            priority = "C"
            recommendation = "SAVE"
            next_action = "Save for later review"
        else:
            priority = "Skip"
            recommendation = "SKIP"
            next_action = "Skip job"

        # Update Job model
        job.fit_score = computed_overall
        job.priority = priority
        job.recommendation = recommendation
        job.next_action = next_action

        # Create or Update JobAnalysis record
        existing_ans = await db.execute(select(JobAnalysis).where(JobAnalysis.job_id == job.id))
        analysis_rec = existing_ans.scalar_one_or_none()
        
        if analysis_rec:
            analysis_rec.technical_fit = ai_result.technical_fit
            analysis_rec.experience_fit = ai_result.experience_fit
            analysis_rec.education_fit = ai_result.education_fit
            analysis_rec.location_fit = ai_result.location_fit
            analysis_rec.authorization_fit = final_auth_fit
            analysis_rec.career_alignment = ai_result.career_alignment
            analysis_rec.overall_score = computed_overall
            analysis_rec.strengths = ai_result.strengths
            analysis_rec.concerns = ai_result.concerns
            analysis_rec.skill_gaps = ai_result.skill_gaps
            analysis_rec.resume_changes_needed = ai_result.resume_changes_needed
            analysis_rec.reasoning_summary = ai_result.reasoning_summary
            analysis_rec.model_name = "gemini-2.5-flash"
            analysis_rec.prompt_version = "job_fit_v2"
            analysis = analysis_rec
        else:
            analysis = JobAnalysis(
                job_id=job.id,
                technical_fit=ai_result.technical_fit,
                experience_fit=ai_result.experience_fit,
                education_fit=ai_result.education_fit,
                location_fit=ai_result.location_fit,
                authorization_fit=final_auth_fit,
                career_alignment=ai_result.career_alignment,
                overall_score=computed_overall,
                strengths=ai_result.strengths,
                concerns=ai_result.concerns,
                skill_gaps=ai_result.skill_gaps,
                resume_changes_needed=ai_result.resume_changes_needed,
                reasoning_summary=ai_result.reasoning_summary,
                model_name="gemini-2.5-flash",
                prompt_version="job_fit_v2"
            )
            db.add(analysis)

        await db.commit()
        await db.refresh(analysis)
        return analysis
