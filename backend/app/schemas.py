"""Pydantic schemas for request/response bodies."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobCreate(BaseModel):
    title: str = "Untitled Job"
    description: str


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    created_at: datetime


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    filename: str
    rank: int | None = None
    score: float | None = None
    semantic_score: float | None = None
    skill_score: float | None = None
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    reasoning: str = ""
    created_at: datetime

    @classmethod
    def from_model(cls, r) -> "ResumeOut":
        def split(s: str) -> list[str]:
            return [x for x in (s or "").split(",") if x.strip()]

        return cls(
            id=r.id,
            job_id=r.job_id,
            filename=r.filename,
            rank=r.rank,
            score=r.score,
            semantic_score=r.semantic_score,
            skill_score=r.skill_score,
            matched_skills=split(r.matched_skills),
            missing_skills=split(r.missing_skills),
            reasoning=r.reasoning or "",
            created_at=r.created_at,
        )


class RankResponse(BaseModel):
    job: JobOut
    results: list[ResumeOut]
