"""Database models: Job, Resume."""
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), default="Untitled Job")
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(512))
    stored_path: Mapped[str] = mapped_column(String(1024))
    raw_text: Mapped[str] = mapped_column(Text, default="")

    # Ranking results (populated after ranking runs)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    semantic_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    skill_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    matched_skills: Mapped[str] = mapped_column(Text, default="")   # comma-separated
    missing_skills: Mapped[str] = mapped_column(Text, default="")   # comma-separated
    reasoning: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    job: Mapped["Job"] = relationship(back_populates="resumes")
