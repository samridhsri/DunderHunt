import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Integer, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship as sa_relationship
from app.core.database import Base

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)

class CandidateProfile(Base):
    __tablename__ = "candidate_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), default="Sam")
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    # Structured JSON data
    education: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    experience: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    projects: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    skills: Mapped[Dict[str, int]] = mapped_column(JSON, default=dict)  # {"Python": 8, "ML": 8}
    target_roles: Mapped[List[str]] = mapped_column(JSON, default=list)
    target_locations: Mapped[List[str]] = mapped_column(JSON, default=list)
    remote_preference: Mapped[str] = mapped_column(String(50), default="Flexible")
    work_authorization: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    preferred_industries: Mapped[List[str]] = mapped_column(JSON, default=list)
    excluded_companies: Mapped[List[str]] = mapped_column(JSON, default=list)
    salary_preferences: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    resume_versions: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    remote_type: Mapped[Optional[str]] = mapped_column(String(50), default="Hybrid") # Remote, Onsite, Hybrid
    employment_type: Mapped[Optional[str]] = mapped_column(String(50), default="Full-time")
    
    description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preferred_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    application_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    
    # Fit & Decision
    fit_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # 0 - 100
    priority: Mapped[str] = mapped_column(String(10), default="B") # A, B, C, Skip
    recommendation: Mapped[str] = mapped_column(String(50), default="APPLY") # APPLY, SAVE, SKIP
    
    # State tracking: Discovered, Analyzing, Saved, Applied, Outreach, OA, Interview, Offer, Rejected, Withdrawn
    status: Mapped[str] = mapped_column(String(50), default="Discovered")
    next_action: Mapped[str] = mapped_column(String(255), default="Review Fit Analysis")
    next_action_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    fingerprint: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    
    # Relationships
    analysis: Mapped[Optional["JobAnalysis"]] = sa_relationship("JobAnalysis", back_populates="job", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    application: Mapped[Optional["Application"]] = sa_relationship("Application", back_populates="job", uselist=False, cascade="all, delete-orphan")
    contacts: Mapped[List["JobContact"]] = sa_relationship("JobContact", back_populates="job", cascade="all, delete-orphan")
    outreach_state: Mapped[Optional["OutreachStateRecord"]] = sa_relationship("OutreachStateRecord", back_populates="job", uselist=False, cascade="all, delete-orphan", lazy="selectin")

class JobAnalysis(Base):
    __tablename__ = "job_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    
    technical_fit: Mapped[int] = mapped_column(Integer, default=80)
    experience_fit: Mapped[int] = mapped_column(Integer, default=80)
    education_fit: Mapped[int] = mapped_column(Integer, default=80)
    location_fit: Mapped[int] = mapped_column(Integer, default=80)
    authorization_fit: Mapped[int] = mapped_column(Integer, default=100)
    career_alignment: Mapped[int] = mapped_column(Integer, default=80)
    overall_score: Mapped[int] = mapped_column(Integer, default=80)
    
    strengths: Mapped[List[str]] = mapped_column(JSON, default=list)
    concerns: Mapped[List[str]] = mapped_column(JSON, default=list)
    skill_gaps: Mapped[List[str]] = mapped_column(JSON, default=list)
    resume_changes_needed: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    reasoning_summary: Mapped[str] = mapped_column(Text, default="")
    model_name: Mapped[str] = mapped_column(String(100), default="gemini-2.5-flash")
    prompt_version: Mapped[str] = mapped_column(String(50), default="job_fit_v1")
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    
    job: Mapped["Job"] = sa_relationship("Job", back_populates="analysis")

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(255))
    team: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    relationship: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) # e.g. "NYU alumni", "Met at conference", "Public contact"
    
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    personal_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    source: Mapped[str] = mapped_column(String(100), default="public_web")
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    
    company_confidence: Mapped[float] = mapped_column(Float, default=0.9)
    role_confidence: Mapped[float] = mapped_column(Float, default=0.85)
    freshness_score: Mapped[float] = mapped_column(Float, default=0.9)
    relationship_score: Mapped[float] = mapped_column(Float, default=0.0)
    role_relevance_score: Mapped[float] = mapped_column(Float, default=0.8)
    overall_score: Mapped[int] = mapped_column(Integer, default=85)
    
    company_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    role_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    verification_confidence: Mapped[float] = mapped_column(Float, default=0.9)
    last_verified_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    
    jobs: Mapped[List["JobContact"]] = sa_relationship("JobContact", back_populates="contact")
    outreach_events: Mapped[List["OutreachEvent"]] = sa_relationship("OutreachEvent", back_populates="contact")

class JobContact(Base):
    __tablename__ = "job_contacts"

    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), primary_key=True)
    
    recommended: Mapped[bool] = mapped_column(Boolean, default=True)
    recommendation_reason: Mapped[str] = mapped_column(Text, default="")
    selected: Mapped[bool] = mapped_column(Boolean, default=False)
    
    job: Mapped["Job"] = sa_relationship("Job", back_populates="contacts")
    contact: Mapped["Contact"] = sa_relationship("Contact", back_populates="jobs")

class OutreachStateRecord(Base):
    __tablename__ = "outreach_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    
    # State Enum: OFF, ENABLED, CHOOSING_CONTACT, DISCOVERING, CONTACT_SELECTED, DRAFTING, DRAFT_READY, SENT, FOLLOW_UP_AVAILABLE, FOLLOWED_UP
    state: Mapped[str] = mapped_column(String(50), default="OFF")
    selected_contact_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    
    channel: Mapped[str] = mapped_column(String(50), default="LinkedIn") # LinkedIn, Email, Other
    purpose: Mapped[str] = mapped_column(String(100), default="Introduce myself") # Introduce myself, Ask about the team, Ask for advice, Ask for referral
    
    current_draft: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    draft_subject: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    draft_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    
    job: Mapped["Job"] = sa_relationship("Job", back_populates="outreach_state")
    selected_contact: Mapped[Optional["Contact"]] = sa_relationship("Contact", lazy="selectin")

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    
    # State tracking: Discovered, Analyzing, Saved, Applied, Outreach, OA, Interview, Offer, Rejected, Withdrawn
    status: Mapped[str] = mapped_column(String(50), default="Discovered")
    resume_version: Mapped[Optional[str]] = mapped_column(String(100), default="Resume v1")
    
    applied_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    application_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    
    outreach_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    outreach_status: Mapped[str] = mapped_column(String(50), default="OFF")
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    next_followup_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    job: Mapped["Job"] = sa_relationship("Job", back_populates="application")

class OutreachEvent(Base):
    __tablename__ = "outreach_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"))
    
    channel: Mapped[str] = mapped_column(String(50), default="LinkedIn")
    subject: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    
    status: Mapped[str] = mapped_column(String(50), default="sent") # sent, replied, no_response
    response_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    is_follow_up: Mapped[bool] = mapped_column(Boolean, default=False)
    sequence_number: Mapped[int] = mapped_column(Integer, default=1)
    
    follow_up_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    follow_up_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    job: Mapped["Job"] = sa_relationship("Job")
    contact: Mapped["Contact"] = sa_relationship("Contact", back_populates="outreach_events")

class SearchCache(Base):
    __tablename__ = "search_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cache_key: Mapped[str] = mapped_column(String(255), unique=True, index=True) # company|role|search_version
    company: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[str] = mapped_column(String(255))
    
    query_count: Mapped[int] = mapped_column(Integer, default=4)
    raw_results: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    filtered_results: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    search_version: Mapped[str] = mapped_column(String(50), default="v1")
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

