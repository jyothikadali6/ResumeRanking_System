"""Orchestrates the full ranking pipeline for a job's resumes.

Pipeline per job:
  1. Preprocess JD + resume texts (spaCy lemmatisation).
  2. Semantic similarity via Sentence-Transformers + FAISS.
  3. Skill extraction + overlap score (spaCy PhraseMatcher).
  4. Optional LLM (Ollama) fit score to blend in + reasoning per resume.
  5. Weighted blend -> final score -> rank 1..N (1 = best).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Job, Resume
from app.services import embedding_service, llm_service, nlp_service


def rank_job(db: Session, job: Job) -> list[Resume]:
    resumes: list[Resume] = list(job.resumes)
    if not resumes:
        return []

    jd_raw = job.description
    jd_clean = nlp_service.preprocess(jd_raw)
    jd_skills = nlp_service.extract_skills(jd_raw)

    resume_clean = [nlp_service.preprocess(r.raw_text) for r in resumes]

    # 1) Semantic similarity (0..1), aligned to `resumes` order.
    semantic = embedding_service.similarity_scores(jd_clean, resume_clean)

    # 2) Skill overlap per resume.
    resume_skill_sets = [nlp_service.extract_skills(r.raw_text) for r in resumes]
    skill_scores = [
        nlp_service.skill_overlap_score(rs, jd_skills) for rs in resume_skill_sets
    ]

    # 3) Optional LLM fit scores (0..1) keyed by resume id.
    llm_scores = llm_service.llm_rerank_scores(
        jd_raw,
        [{"id": r.id, "text": r.raw_text} for r in resumes],
    )

    # 4) Blend into a final score. Carry the original index so we can look up
    #    the correct skill set after sorting (avoids relying on object identity).
    blended: list[tuple[int, Resume, float, float, float]] = []
    for idx, (r, sem, skill) in enumerate(zip(resumes, semantic, skill_scores)):
        base = settings.semantic_weight * sem + settings.skill_weight * skill
        if llm_scores and r.id in llm_scores:
            # Blend the LLM opinion in equally with the base signal.
            final = 0.5 * base + 0.5 * llm_scores[r.id]
        else:
            final = base
        blended.append((idx, r, final, sem, skill))

    # 5) Sort desc by final score, assign ranks, persist per-resume fields.
    blended.sort(key=lambda x: x[2], reverse=True)

    for rank, (idx, r, final, sem, skill) in enumerate(blended, start=1):
        matched = sorted(resume_skill_sets[idx] & jd_skills)
        missing = sorted(jd_skills - resume_skill_sets[idx])

        r.rank = rank
        r.score = round(final * 100, 2)
        r.semantic_score = round(sem * 100, 2)
        r.skill_score = round(skill * 100, 2)
        r.matched_skills = ",".join(matched)
        r.missing_skills = ",".join(missing)
        r.reasoning = llm_service.explain_match(jd_raw, r.raw_text, matched, missing)

    db.commit()

    ranked = sorted(resumes, key=lambda r: r.rank or 10**9)
    for r in ranked:
        db.refresh(r)
    return ranked
