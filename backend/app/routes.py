"""API routes: jobs, resume upload, ranking, results."""
from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Job, Resume
from app.schemas import JobCreate, JobOut, RankResponse, ResumeOut
from app.services import llm_service
from app.services.pdf_service import extract_text_from_pdf
from app.services.ranking_service import rank_job

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "llm_available": llm_service.is_available()}


@router.post("/jobs", response_model=JobOut)
def create_job(payload: JobCreate, db: Session = Depends(get_db)) -> Job:
    if not payload.description.strip():
        raise HTTPException(400, "Job description cannot be empty.")
    job = Job(title=payload.title.strip() or "Untitled Job", description=payload.description)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    return job


@router.post("/jobs/{job_id}/resumes", response_model=list[ResumeOut])
async def upload_resumes(
    job_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> list[ResumeOut]:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found.")

    os.makedirs(settings.upload_dir, exist_ok=True)
    created: list[Resume] = []

    for f in files:
        if not f.filename or not f.filename.lower().endswith(".pdf"):
            raise HTTPException(400, f"Only PDF files are supported: {f.filename}")

        stored_name = f"{uuid.uuid4().hex}.pdf"
        stored_path = os.path.join(settings.upload_dir, stored_name)
        with open(stored_path, "wb") as out:
            out.write(await f.read())

        try:
            text = extract_text_from_pdf(stored_path)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(422, f"Failed to read PDF {f.filename}: {exc}") from exc

        resume = Resume(
            job_id=job.id,
            filename=f.filename,
            stored_path=stored_path,
            raw_text=text,
        )
        db.add(resume)
        created.append(resume)

    db.commit()
    for r in created:
        db.refresh(r)
    return [ResumeOut.from_model(r) for r in created]


@router.post("/jobs/{job_id}/rank", response_model=RankResponse)
def rank(job_id: int, db: Session = Depends(get_db)) -> RankResponse:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    if not job.resumes:
        raise HTTPException(400, "No resumes uploaded for this job yet.")

    ranked = rank_job(db, job)
    return RankResponse(
        job=JobOut.model_validate(job),
        results=[ResumeOut.from_model(r) for r in ranked],
    )


@router.get("/jobs/{job_id}/results", response_model=RankResponse)
def results(job_id: int, db: Session = Depends(get_db)) -> RankResponse:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found.")
    ranked = sorted(job.resumes, key=lambda r: (r.rank is None, r.rank or 0))
    return RankResponse(
        job=JobOut.model_validate(job),
        results=[ResumeOut.from_model(r) for r in ranked],
    )
