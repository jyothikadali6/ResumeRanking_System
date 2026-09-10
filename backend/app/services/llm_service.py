"""Ollama integration: generate match reasoning for each resume.

Talks to a locally running Ollama server (`ollama serve`). If Ollama is
unavailable or disabled, callers get a graceful fallback so ranking still works
purely on the semantic + skill scores.
"""
from __future__ import annotations

import json

import httpx

from app.config import settings


def is_available() -> bool:
    """Quick health check against the Ollama server."""
    if not settings.use_llm:
        return False
    try:
        r = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=3.0)
        return r.status_code == 200
    except httpx.HTTPError:
        return False


def _generate(prompt: str, timeout: float = 60.0) -> str:
    """Call Ollama's /api/generate (non-streaming) and return the text."""
    resp = httpx.post(
        f"{settings.ollama_base_url}/api/generate",
        json={
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


def explain_match(
    job_description: str,
    resume_text: str,
    matched_skills: list[str],
    missing_skills: list[str],
) -> str:
    """Return a short, human-readable justification for the match.

    Returns a heuristic summary when the LLM is unavailable.
    """
    if not is_available():
        return _fallback_reason(matched_skills, missing_skills)

    prompt = f"""You are a technical recruiter. Assess how well a candidate's resume
matches a job description. Be concise and specific (3-4 sentences max).

JOB DESCRIPTION:
{job_description[:2500]}

RESUME (extracted text):
{resume_text[:3500]}

Skills the candidate has that the job wants: {", ".join(matched_skills) or "none detected"}
Job-required skills the candidate seems to be missing: {", ".join(missing_skills) or "none detected"}

Write a brief assessment of fit, highlighting key strengths and gaps.
Do not invent facts not present in the resume."""

    try:
        return _generate(prompt)
    except httpx.HTTPError:
        return _fallback_reason(matched_skills, missing_skills)


def llm_rerank_scores(
    job_description: str, resumes: list[dict]
) -> dict[int, float] | None:
    """Ask the LLM to score each resume 0-100 for job fit.

    `resumes` is a list of {"id", "text"} dicts. Returns {resume_id: score}
    normalised to 0..1, or None if the LLM is unavailable / parsing fails.
    """
    if not is_available() or not resumes:
        return None

    listing = "\n\n".join(
        f"[RESUME id={r['id']}]\n{r['text'][:2000]}" for r in resumes
    )
    prompt = f"""You are ranking candidates for a job. For EACH resume, give an
integer fit score from 0 (poor) to 100 (excellent) based ONLY on the job
description and resume text. Respond with STRICT JSON only, no prose:
{{"scores": [{{"id": <int>, "score": <int>}}, ...]}}

JOB DESCRIPTION:
{job_description[:2500]}

RESUMES:
{listing}"""

    try:
        raw = _generate(prompt, timeout=120.0)
        data = _parse_json(raw)
        if not data:
            return None
        return {
            int(item["id"]): max(0.0, min(1.0, float(item["score"]) / 100.0))
            for item in data.get("scores", [])
            if "id" in item and "score" in item
        }
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        return None


def _parse_json(raw: str) -> dict | None:
    """Best-effort extraction of a JSON object from an LLM response."""
    raw = raw.strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None


def _fallback_reason(matched: list[str], missing: list[str]) -> str:
    parts = []
    if matched:
        parts.append(f"Matches key skills: {', '.join(matched[:8])}.")
    else:
        parts.append("No explicitly required skills were detected in the resume.")
    if missing:
        parts.append(f"Missing/unclear: {', '.join(missing[:8])}.")
    parts.append("(Generated without LLM — based on skill overlap and semantic similarity.)")
    return " ".join(parts)
