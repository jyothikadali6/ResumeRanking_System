"""Sentence-Transformers embeddings + FAISS cosine similarity.

We L2-normalise vectors and use a FAISS inner-product index, which makes the
inner product equivalent to cosine similarity. For the JD-vs-resumes use case
we build a small index of resume vectors and query it with the JD vector.
"""
from __future__ import annotations

import functools

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings


@functools.lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


def embed(texts: list[str]) -> np.ndarray:
    """Return L2-normalised float32 embeddings, shape (n, dim)."""
    model = _model()
    vecs = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vecs.astype("float32")


def similarity_scores(jd_text: str, resume_texts: list[str]) -> list[float]:
    """Cosine similarity of each resume to the JD, in [0, 1].

    Uses a FAISS inner-product index over the resume vectors and queries with
    the JD vector. Raw cosine (in [-1, 1]) is rescaled to [0, 1].
    """
    if not resume_texts:
        return []

    jd_vec = embed([jd_text])          # (1, dim)
    resume_vecs = embed(resume_texts)  # (n, dim)

    dim = resume_vecs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(resume_vecs)

    # Search all resumes; sims[0] holds cosine sims aligned to FAISS ids.
    sims, ids = index.search(jd_vec, len(resume_texts))

    # Reorder back to the original resume order.
    ordered = [0.0] * len(resume_texts)
    for score, idx in zip(sims[0], ids[0]):
        if idx == -1:
            continue
        ordered[idx] = float((score + 1.0) / 2.0)  # [-1,1] -> [0,1]
    return ordered
